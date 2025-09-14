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
from typing import Any, Dict, List, Tuple, cast

from .utils import split_into_batches, is_subsequence_in_list

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
) -> Dict[Tuple[str, ...], int]:
    """Choose the best available backend for support counting.

    Backend selection is controlled by the env var GSPPY_BACKEND:
    - "rust": require Rust extension (raise if missing)
    - "python": force pure-Python fallback
    - otherwise: try Rust first and fall back to Python
    """
    backend = _env_backend()

    if backend == "python":
        return support_counts_python(transactions, candidates, min_support_abs, batch_size)

    if backend == "rust":
        if not _rust_available:
            raise RuntimeError("GSPPY_BACKEND=rust but Rust extension _gsppy_rust is not available")
        # use rust
        enc_tx, inv_vocab, vocab = _get_encoded_transactions(transactions)
        enc_cands = _encode_candidates(candidates, vocab)
        result = cast(List[Tuple[List[int], int]], _compute_supports_rust(enc_tx, enc_cands, int(min_support_abs)))
        out: Dict[Tuple[str, ...], int] = {}
        for enc_cand, freq in result:
            out[tuple(inv_vocab[i] for i in enc_cand)] = int(freq)
        return out

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
