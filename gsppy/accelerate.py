"""
Optional acceleration layer for GSP support counting.

This module attempts to use a Rust extension for the hot loop
(support counting via contiguous subsequence search). If the Rust
module is unavailable, it gracefully falls back to the pure-Python
implementation.

Control backend via env var:
- GSPPY_BACKEND=rust  -> require Rust extension (raise if missing)
- GSPPY_BACKEND=python -> force Python implementation
- unset/other          -> try Rust first, then fallback to Python
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Tuple, Optional, cast

from .utils import split_into_batches, is_subsequence_in_list

# Optional GPU (CuPy) support
_gpu_available = False
try:  # pragma: no cover - optional dependency path
    import cupy as _cp_mod  # type: ignore[import-not-found]

    cp = cast(Any, _cp_mod)

    try:
        _gpu_available = cp.cuda.runtime.getDeviceCount() > 0  # type: ignore[attr-defined]
    except Exception:
        _gpu_available = False
except Exception:  # pragma: no cover - optional dependency path
    cp = None  # type: ignore[assignment]
    _gpu_available = False

# Simple per-process cache for encoded transactions keyed by the list object's id
_ENCODED_CACHE: Dict[int, Tuple[List[List[int]], Dict[int, str], Dict[str, int], int]] = {}


def _get_encoded_transactions(
    transactions: List[Tuple[str, ...]],
) -> Tuple[List[List[int]], Dict[int, str], Dict[str, int]]:
    """Return encoded transactions using a small in-memory cache.

    Cache key is the id() of the transactions list and we also track the number of
    transactions to detect trivial changes. This assumes transactions aren't mutated after
    GSP is constructed (which is the common case).
    """
    key = id(transactions)
    cached = _ENCODED_CACHE.get(key)
    if cached is not None:
        enc_tx, inv_vocab, vocab, n_tx = cached
        if n_tx == len(transactions):
            return enc_tx, inv_vocab, vocab
    enc_tx, inv_vocab, vocab = _encode_transactions(transactions)
    _ENCODED_CACHE[key] = (enc_tx, inv_vocab, vocab, len(transactions))
    return enc_tx, inv_vocab, vocab


# Try importing the Rust extension
_rust_available = False
_compute_supports_rust: Any = None
try:
    from _gsppy_rust import compute_supports_py as _compute_supports_rust  # type: ignore

    _rust_available = True
except Exception:
    _compute_supports_rust = None
    _rust_available = False


def _env_backend() -> str:
    return os.environ.get("GSPPY_BACKEND", "auto").lower()


def _encode_transactions(transactions: List[Tuple[str, ...]]) -> Tuple[List[List[int]], Dict[int, str], Dict[str, int]]:
    """Encode transactions of strings into integer IDs.

    Parameters:
        transactions: List of transactions where each transaction is a tuple of strings.

    Returns:
        A tuple of:
        - enc_tx: List[List[int]] encoded transactions
        - inv_vocab: Dict[int, str] mapping back from id to original string
        - vocab: Dict[str, int] mapping from original string to integer id
    """
    vocab: Dict[str, int] = {}
    enc_tx: List[List[int]] = []
    for t in transactions:
        row: List[int] = []
        for s in t:
            if s not in vocab:
                vocab[s] = len(vocab)
            row.append(vocab[s])
        enc_tx.append(row)
    inv_vocab = {v: k for k, v in vocab.items()}
    return enc_tx, inv_vocab, vocab


def _encode_candidates(candidates: List[Tuple[str, ...]], vocab: Dict[str, int]) -> List[List[int]]:
    """Encode candidate patterns using a provided vocabulary mapping."""
    return [[vocab[s] for s in cand] for cand in candidates]


def _support_counts_gpu_singletons(
    enc_tx: List[List[int]],
    cand_ids: List[int],
    min_support_abs: int,
    vocab_size: int,
) -> List[Tuple[List[int], int]]:
    """GPU-accelerated support counts for singleton candidates using CuPy.

    This computes the number of transactions containing each candidate item ID.
    It uniquifies items per transaction on CPU to preserve presence semantics,
    then performs a single bincount on GPU.
    """
    # Ensure one contribution per transaction
    unique_rows: List[List[int]] = [list(set(row)) for row in enc_tx]
    if not unique_rows:
        return []

    # Flatten to a 1D list of item ids, then move to GPU
    flat: List[int] = [item for row in unique_rows for item in row]
    if not flat:
        return []

    cp_flat = cp.asarray(flat, dtype=cp.int32)  # type: ignore[name-defined]
    counts = cp.bincount(cp_flat, minlength=vocab_size)  # type: ignore[attr-defined]
    counts_host: Any = counts.get()  # back to host as a NumPy array

    out: List[Tuple[List[int], int]] = []
    for cid in cand_ids:
        freq = int(counts_host[cid])
        if freq >= min_support_abs:
            out.append(([cid], freq))
    return out


def support_counts_python(
    transactions: List[Tuple[str, ...]],
    candidates: List[Tuple[str, ...]],
    min_support_abs: int,
    batch_size: int = 100,
) -> Dict[Tuple[str, ...], int]:
    """Pure-Python fallback for support counting (single-process).

    Evaluates each candidate pattern's frequency across all transactions
    using the same contiguous-subsequence semantics as the Rust backend.

    Note: This implementation is single-process and optimized for simplicity.
    Heavy workloads may benefit from the Rust backend.
    """
    # Simple non-multiprocessing version to avoid import cycles.
    results: Dict[Tuple[str, ...], int] = {}
    for batch in split_into_batches(candidates, batch_size):
        for cand in batch:
            freq = sum(1 for t in transactions if is_subsequence_in_list(cand, t))
            if freq >= min_support_abs:
                results[cand] = freq
    return results


def support_counts(
    transactions: List[Tuple[str, ...]],
    candidates: List[Tuple[str, ...]],
    min_support_abs: int,
    batch_size: int = 100,
    backend: Optional[str] = None,
) -> Dict[Tuple[str, ...], int]:
    """Choose the best available backend for support counting.

    Backend selection is controlled by the `backend` argument when provided,
    otherwise by the env var GSPPY_BACKEND:
    - "rust": require Rust extension (raise if missing)
    - "gpu": try GPU path when available (currently singletons optimized),
              fall back to CPU for the rest
    - "python": force pure-Python fallback
    - otherwise: try Rust first and fall back to Python
    """
    backend_sel = (backend or _env_backend()).lower()

    if backend_sel == "gpu":
        if not _gpu_available:
            raise RuntimeError("GSPPY_BACKEND=gpu but CuPy GPU is not available")
        # Encode once
        enc_tx, inv_vocab, vocab = _get_encoded_transactions(transactions)
        enc_cands = _encode_candidates(candidates, vocab)

        # Partition candidates into singletons and non-singletons
        singletons: List[Tuple[int, Tuple[str, ...]]] = []
        others: List[Tuple[List[int], Tuple[str, ...]]] = []
        # Pair original and encoded candidates; lengths should match
        assert len(candidates) == len(enc_cands), "Encoded candidates length mismatch"
        for orig, enc in zip(candidates, enc_cands):  # noqa: B905 - lengths checked above
            if len(enc) == 1:
                singletons.append((enc[0], orig))
            else:
                others.append((enc, orig))

        out: Dict[Tuple[str, ...], int] = {}

        # GPU path for singletons
        if singletons:
            vocab_size = max(vocab.values()) + 1 if vocab else 0
            gpu_res = _support_counts_gpu_singletons(
                enc_tx=enc_tx,
                cand_ids=[cid for cid, _ in singletons],
                min_support_abs=min_support_abs,
                vocab_size=vocab_size,
            )
            # Map back to original strings
            cand_by_id: Dict[int, Tuple[str, ...]] = {cid: orig for cid, orig in singletons}
            for enc_cand, freq in gpu_res:
                cid = enc_cand[0]
                out[cand_by_id[cid]] = int(freq)

        # Fallback for others (prefer rust when available)
        if others:
            if _rust_available:
                try:
                    other_enc = [enc for enc, _ in others]
                    res = cast(
                        List[Tuple[List[int], int]], _compute_supports_rust(enc_tx, other_enc, int(min_support_abs))
                    )
                    for enc_cand, freq in res:
                        out[tuple(inv_vocab[i] for i in enc_cand)] = int(freq)
                except Exception:
                    # fallback to python
                    out.update(
                        support_counts_python(transactions, [orig for _, orig in others], min_support_abs, batch_size)
                    )
            else:
                out.update(
                    support_counts_python(transactions, [orig for _, orig in others], min_support_abs, batch_size)
                )

        return out

    if backend_sel == "python":
        return support_counts_python(transactions, candidates, min_support_abs, batch_size)

    if backend_sel == "rust":
        if not _rust_available:
            raise RuntimeError("GSPPY_BACKEND=rust but Rust extension _gsppy_rust is not available")
        # use rust
        enc_tx, inv_vocab, vocab = _get_encoded_transactions(transactions)
        enc_cands = _encode_candidates(candidates, vocab)
        result = cast(List[Tuple[List[int], int]], _compute_supports_rust(enc_tx, enc_cands, int(min_support_abs)))
        out_rust: Dict[Tuple[str, ...], int] = {}
        for enc_cand, freq in result:
            out_rust[tuple(inv_vocab[i] for i in enc_cand)] = int(freq)
        return out_rust

    # auto: try rust then fallback
    if _rust_available:
        enc_tx, inv_vocab, vocab = _get_encoded_transactions(transactions)
        enc_cands = _encode_candidates(candidates, vocab)
        try:
            result = cast(List[Tuple[List[int], int]], _compute_supports_rust(enc_tx, enc_cands, int(min_support_abs)))
            out2: Dict[Tuple[str, ...], int] = {}
            for enc_cand, freq in result:
                out2[tuple(inv_vocab[i] for i in enc_cand)] = int(freq)
            return out2
        except Exception:
            pass

    return support_counts_python(transactions, candidates, min_support_abs, batch_size)
