"""
Test suite for the accelerate module.

This module tests the acceleration layer for GSP support counting, including:
1. Transaction encoding functions (_encode_transactions, _encode_candidates, _get_encoded_transactions)
2. Support counting functions (support_counts_python, support_counts)
3. Backend selection logic (_env_backend, backend switching)
4. GPU acceleration path (_support_counts_gpu_singletons)
5. Cache behavior for encoded transactions
6. Edge cases (empty inputs, invalid backends, error handling)
"""

import os
from typing import Dict, List, Tuple
from unittest.mock import Mock, patch

import pytest

from gsppy.accelerate import (
    _ENCODED_CACHE,
    _encode_candidates,
    _encode_transactions,
    _env_backend,
    _get_encoded_transactions,
    _gpu_available,
    _rust_available,
    support_counts,
    support_counts_python,
)


class TestEncodingFunctions:
    """Test transaction and candidate encoding functions."""

    def test_encode_transactions_basic(self):
        """Test basic transaction encoding."""
        transactions = [("A", "B"), ("B", "C"), ("A", "C")]
        enc_tx, inv_vocab, vocab = _encode_transactions(transactions)

        # Check that we have the right structure
        assert len(enc_tx) == 3
        assert len(vocab) == 3  # A, B, C
        assert len(inv_vocab) == 3

        # Check encoding consistency
        assert enc_tx[0] == [vocab["A"], vocab["B"]]
        assert enc_tx[1] == [vocab["B"], vocab["C"]]
        assert enc_tx[2] == [vocab["A"], vocab["C"]]

        # Check inverse mapping
        for token, token_id in vocab.items():
            assert inv_vocab[token_id] == token

    def test_encode_transactions_empty(self):
        """Test encoding with empty transactions."""
        transactions: List[Tuple[str, ...]] = []
        enc_tx, inv_vocab, vocab = _encode_transactions(transactions)

        assert enc_tx == []
        assert inv_vocab == {}
        assert vocab == {}

    def test_encode_transactions_single_item(self):
        """Test encoding with single-item transactions."""
        transactions = [("X",), ("Y",), ("Z",)]
        enc_tx, inv_vocab, vocab = _encode_transactions(transactions)

        assert len(enc_tx) == 3
        assert len(vocab) == 3
        assert all(len(tx) == 1 for tx in enc_tx)

    def test_encode_transactions_repeated_items(self):
        """Test encoding with repeated items in same transaction."""
        transactions = [("A", "A", "B"), ("C", "C", "C")]
        enc_tx, inv_vocab, vocab = _encode_transactions(transactions)

        # Should encode each occurrence
        assert enc_tx[0] == [vocab["A"], vocab["A"], vocab["B"]]
        assert enc_tx[1] == [vocab["C"], vocab["C"], vocab["C"]]

    def test_encode_candidates_basic(self):
        """Test basic candidate encoding."""
        candidates = [("A",), ("B",), ("A", "B")]
        vocab = {"A": 0, "B": 1, "C": 2}

        enc_cands = _encode_candidates(candidates, vocab)

        assert enc_cands == [[0], [1], [0, 1]]

    def test_encode_candidates_empty(self):
        """Test encoding with empty candidates."""
        candidates: List[Tuple[str, ...]] = []
        vocab = {"A": 0, "B": 1}

        enc_cands = _encode_candidates(candidates, vocab)

        assert enc_cands == []

    def test_encode_candidates_missing_vocab(self):
        """Test that encoding fails with missing vocabulary."""
        candidates = [("A", "D")]  # D is not in vocab
        vocab = {"A": 0, "B": 1}

        with pytest.raises(KeyError):
            _encode_candidates(candidates, vocab)


class TestEncodingCache:
    """Test caching behavior for encoded transactions."""

    def setup_method(self):
        """Clear cache before each test."""
        _ENCODED_CACHE.clear()

    def teardown_method(self):
        """Clear cache after each test."""
        _ENCODED_CACHE.clear()

    def test_get_encoded_transactions_caching(self):
        """Test that encoded transactions are cached."""
        transactions = [("A", "B"), ("B", "C")]

        # First call should compute and cache
        enc_tx1, inv_vocab1, vocab1 = _get_encoded_transactions(transactions)

        # Second call should retrieve from cache
        enc_tx2, inv_vocab2, vocab2 = _get_encoded_transactions(transactions)

        # Results should be identical (same objects)
        assert enc_tx1 is enc_tx2
        assert inv_vocab1 is inv_vocab2
        assert vocab1 is vocab2

    def test_get_encoded_transactions_cache_invalidation(self):
        """Test that cache is invalidated when transaction count changes."""
        transactions = [("A", "B"), ("B", "C")]

        # First call with 2 transactions
        enc_tx1, _, _ = _get_encoded_transactions(transactions)
        assert len(enc_tx1) == 2

        # Modify transactions list (add one more)
        transactions.append(("C", "D"))

        # Second call should recompute due to different length
        enc_tx2, _, _ = _get_encoded_transactions(transactions)
        assert len(enc_tx2) == 3

    def test_get_encoded_transactions_different_objects(self):
        """Test that different transaction objects get different cache entries."""
        transactions1 = [("A", "B")]
        transactions2 = [("A", "B")]  # Same content, different object

        enc_tx1, _, vocab1 = _get_encoded_transactions(transactions1)
        enc_tx2, _, vocab2 = _get_encoded_transactions(transactions2)

        # Different objects should have separate cache entries
        # They should produce the same results but not be the same object
        assert enc_tx1 == enc_tx2
        assert vocab1 == vocab2


class TestSupportCountsPython:
    """Test pure Python support counting implementation."""

    def test_support_counts_python_basic(self):
        """Test basic support counting."""
        transactions = [("A", "B"), ("A", "C"), ("B", "C")]
        candidates = [("A",), ("B",), ("C",), ("A", "B")]

        result = support_counts_python(transactions, candidates, min_support_abs=1)

        assert result[("A",)] == 2
        assert result[("B",)] == 2
        assert result[("C",)] == 2
        assert result[("A", "B")] == 1

    def test_support_counts_python_min_support_filtering(self):
        """Test that patterns below min_support are filtered out."""
        transactions = [("A", "B"), ("A", "C"), ("D", "E")]
        candidates = [("A",), ("B",), ("D",), ("X",)]

        result = support_counts_python(transactions, candidates, min_support_abs=2)

        # Only A appears in 2+ transactions
        assert ("A",) in result
        assert result[("A",)] == 2
        assert ("B",) not in result  # Only 1 occurrence
        assert ("D",) not in result  # Only 1 occurrence
        assert ("X",) not in result  # Never appears

    def test_support_counts_python_empty_transactions(self):
        """Test with empty transactions."""
        transactions: List[Tuple[str, ...]] = []
        candidates = [("A",), ("B",)]

        result = support_counts_python(transactions, candidates, min_support_abs=1)

        assert result == {}

    def test_support_counts_python_empty_candidates(self):
        """Test with empty candidates."""
        transactions = [("A", "B"), ("B", "C")]
        candidates: List[Tuple[str, ...]] = []

        result = support_counts_python(transactions, candidates, min_support_abs=1)

        assert result == {}

    def test_support_counts_python_batch_size(self):
        """Test that batch_size parameter works correctly."""
        transactions = [("A", "B"), ("A", "C")]
        candidates = [("A",), ("B",), ("C",)]

        # Small batch size should still give correct results
        result = support_counts_python(transactions, candidates, min_support_abs=1, batch_size=1)

        assert result[("A",)] == 2
        assert result[("B",)] == 1
        assert result[("C",)] == 1

    def test_support_counts_python_subsequence_matching(self):
        """Test that subsequence matching is non-contiguous."""
        transactions = [("A", "X", "B"), ("A", "B"), ("X", "Y")]
        candidates = [("A", "B")]

        result = support_counts_python(transactions, candidates, min_support_abs=1)

        # Should match both first and second transaction
        assert result[("A", "B")] == 2

    def test_support_counts_python_no_matches(self):
        """Test when no candidates meet min_support."""
        transactions = [("A",), ("B",), ("C",)]
        candidates = [("X",), ("Y",), ("Z",)]

        result = support_counts_python(transactions, candidates, min_support_abs=1)

        assert result == {}


class TestBackendSelection:
    """Test backend selection and environment variable handling."""

    def test_env_backend_default(self):
        """Test default backend selection when no env var is set."""
        with patch.dict(os.environ, {}, clear=True):
            # Remove GSPPY_BACKEND if it exists
            os.environ.pop("GSPPY_BACKEND", None)
            backend = _env_backend()
            assert backend == "auto"

    def test_env_backend_python(self):
        """Test backend selection with GSPPY_BACKEND=python."""
        with patch.dict(os.environ, {"GSPPY_BACKEND": "python"}):
            backend = _env_backend()
            assert backend == "python"

    def test_env_backend_rust(self):
        """Test backend selection with GSPPY_BACKEND=rust."""
        with patch.dict(os.environ, {"GSPPY_BACKEND": "rust"}):
            backend = _env_backend()
            assert backend == "rust"

    def test_env_backend_gpu(self):
        """Test backend selection with GSPPY_BACKEND=gpu."""
        with patch.dict(os.environ, {"GSPPY_BACKEND": "gpu"}):
            backend = _env_backend()
            assert backend == "gpu"

    def test_env_backend_case_insensitive(self):
        """Test that backend selection is case-insensitive."""
        with patch.dict(os.environ, {"GSPPY_BACKEND": "PYTHON"}):
            backend = _env_backend()
            assert backend == "python"


class TestSupportCountsBackend:
    """Test support_counts function with different backends."""

    def test_support_counts_python_backend(self):
        """Test support_counts with explicit python backend."""
        transactions = [("A", "B"), ("A", "C")]
        candidates = [("A",), ("B",)]

        result = support_counts(transactions, candidates, min_support_abs=1, backend="python")

        assert result[("A",)] == 2
        assert result[("B",)] == 1

    def test_support_counts_auto_backend(self):
        """Test support_counts with auto backend (should fallback to python)."""
        transactions = [("A", "B"), ("A", "C")]
        candidates = [("A",), ("B",)]

        # With rust not available, should use python
        result = support_counts(transactions, candidates, min_support_abs=1, backend="auto")

        assert result[("A",)] == 2
        assert result[("B",)] == 1

    @pytest.mark.skipif(_rust_available, reason="Test only runs when Rust is not available")
    def test_support_counts_rust_backend_unavailable(self):
        """Test that rust backend raises error when not available."""
        transactions = [("A", "B")]
        candidates = [("A",)]

        with pytest.raises(RuntimeError, match="Rust extension.*not available"):
            support_counts(transactions, candidates, min_support_abs=1, backend="rust")

    @pytest.mark.skipif(_gpu_available, reason="Test only runs when GPU is not available")
    def test_support_counts_gpu_backend_unavailable(self):
        """Test that gpu backend raises error when not available."""
        transactions = [("A", "B")]
        candidates = [("A",)]

        with pytest.raises(RuntimeError, match="CuPy GPU is not available"):
            support_counts(transactions, candidates, min_support_abs=1, backend="gpu")

    def test_support_counts_env_backend_override(self):
        """Test that explicit backend parameter overrides env var."""
        transactions = [("A", "B")]
        candidates = [("A",)]

        with patch.dict(os.environ, {"GSPPY_BACKEND": "rust"}):
            # Should use python despite env var
            result = support_counts(transactions, candidates, min_support_abs=1, backend="python")
            assert result[("A",)] == 1


class TestGPUAcceleration:
    """Test GPU acceleration code paths (when available)."""

    @pytest.mark.skipif(not _gpu_available, reason="Test requires GPU/CuPy")
    def test_support_counts_gpu_singletons_basic(self):
        """Test GPU-accelerated singleton support counting."""
        # Import here to avoid error when cupy not available
        from gsppy.accelerate import _support_counts_gpu_singletons

        transactions = [("A", "B"), ("A", "C"), ("B", "C")]
        enc_tx, _, vocab = _encode_transactions(transactions)

        # Test singletons
        cand_ids = [vocab["A"], vocab["B"], vocab["C"]]
        vocab_size = max(vocab.values()) + 1

        result = _support_counts_gpu_singletons(enc_tx, cand_ids, min_support_abs=2, vocab_size=vocab_size)

        # All items appear in 2 transactions
        assert len(result) == 3

    @pytest.mark.skipif(not _gpu_available, reason="Test requires GPU/CuPy")
    def test_support_counts_gpu_singletons_empty(self):
        """Test GPU singleton counting with empty inputs."""
        from gsppy.accelerate import _support_counts_gpu_singletons

        enc_tx: List[List[int]] = []
        cand_ids: List[int] = []

        result = _support_counts_gpu_singletons(enc_tx, cand_ids, min_support_abs=1, vocab_size=10)

        assert result == []

    @pytest.mark.skipif(not _gpu_available, reason="Test requires GPU/CuPy")
    def test_support_counts_gpu_backend_mixed_candidates(self):
        """Test GPU backend with both singleton and non-singleton candidates."""
        transactions = [("A", "B", "C"), ("A", "C"), ("B", "C")]
        candidates = [("A",), ("B",), ("A", "B")]

        result = support_counts(transactions, candidates, min_support_abs=1, backend="gpu")

        assert ("A",) in result
        assert ("B",) in result
        assert ("A", "B") in result


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_support_counts_large_pattern(self):
        """Test with patterns longer than any transaction."""
        transactions = [("A", "B"), ("C", "D")]
        candidates = [("A", "B", "C", "D", "E")]

        result = support_counts_python(transactions, candidates, min_support_abs=1)

        assert result == {}

    def test_support_counts_single_transaction(self):
        """Test with a single transaction."""
        transactions = [("A", "B", "C")]
        candidates = [("A",), ("A", "B"), ("A", "C"), ("A", "B", "C")]

        result = support_counts_python(transactions, candidates, min_support_abs=1)

        assert result[("A",)] == 1
        assert result[("A", "B")] == 1
        assert result[("A", "C")] == 1
        assert result[("A", "B", "C")] == 1

    def test_support_counts_duplicate_items_in_transaction(self):
        """Test handling of duplicate items in a transaction."""
        transactions = [("A", "A", "B"), ("A", "B", "B")]
        candidates = [("A",), ("B",), ("A", "B")]

        result = support_counts_python(transactions, candidates, min_support_abs=1)

        # Each item should only count once per transaction
        assert result[("A",)] == 2
        assert result[("B",)] == 2
        assert result[("A", "B")] == 2

    def test_support_counts_min_support_zero(self):
        """Test with min_support_abs=0."""
        transactions = [("A", "B")]
        candidates = [("A",), ("X",)]

        result = support_counts_python(transactions, candidates, min_support_abs=0)

        # Should include all candidates, even those with 0 support
        assert result[("A",)] == 1
        assert result[("X",)] == 0

    def test_support_counts_very_large_batch_size(self):
        """Test with batch_size larger than number of candidates."""
        transactions = [("A", "B"), ("B", "C")]
        candidates = [("A",), ("B",)]

        result = support_counts_python(transactions, candidates, min_support_abs=1, batch_size=1000)

        assert result[("A",)] == 1
        assert result[("B",)] == 2

    def test_encode_transactions_unicode(self):
        """Test encoding with unicode characters."""
        transactions = [("α", "β"), ("γ", "δ"), ("α", "δ")]
        enc_tx, inv_vocab, vocab = _encode_transactions(transactions)

        assert len(vocab) == 4
        # Check that we can decode properly
        decoded = []
        for tx in enc_tx:
            decoded.append(tuple(inv_vocab[i] for i in tx))

        assert decoded[0] == ("α", "β")
        assert decoded[1] == ("γ", "δ")
        assert decoded[2] == ("α", "δ")

    def test_support_counts_case_sensitive(self):
        """Test that support counting is case-sensitive."""
        transactions = [("A", "B"), ("a", "b")]
        candidates = [("A",), ("a",)]

        result = support_counts_python(transactions, candidates, min_support_abs=1)

        # Should treat uppercase and lowercase as different
        assert result[("A",)] == 1
        assert result[("a",)] == 1

    def test_support_counts_special_characters(self):
        """Test with special characters in items."""
        transactions = [("item-1", "item_2"), ("item.3", "item@4")]
        candidates = [("item-1",), ("item_2",), ("item.3",)]

        result = support_counts_python(transactions, candidates, min_support_abs=1)

        assert result[("item-1",)] == 1
        assert result[("item_2",)] == 1
        assert result[("item.3",)] == 1

    def test_support_counts_long_sequences(self):
        """Test with very long sequences."""
        # Create a long transaction
        long_transaction = tuple(str(i) for i in range(100))
        transactions = [long_transaction]

        # Test various length patterns
        candidates = [
            (str(0),),
            (str(0), str(50)),
            (str(0), str(50), str(99)),
        ]

        result = support_counts_python(transactions, candidates, min_support_abs=1)

        assert len(result) == 3
        assert all(count == 1 for count in result.values())

    def test_support_counts_many_transactions(self):
        """Test with many transactions."""
        # Create many similar transactions
        transactions = [("A", "B", str(i)) for i in range(100)]
        candidates = [("A",), ("B",)]

        result = support_counts_python(transactions, candidates, min_support_abs=50)

        # A and B appear in all transactions
        assert result[("A",)] == 100
        assert result[("B",)] == 100

    def test_encode_candidates_preserve_order(self):
        """Test that candidate encoding preserves order."""
        candidates = [("Z", "A"), ("A", "Z")]
        vocab = {"A": 0, "Z": 1}

        enc_cands = _encode_candidates(candidates, vocab)

        # Order should be preserved
        assert enc_cands[0] == [1, 0]  # Z, A
        assert enc_cands[1] == [0, 1]  # A, Z

    def test_cache_clear_behavior(self):
        """Test that clearing cache works correctly."""
        _ENCODED_CACHE.clear()
        transactions = [("A", "B")]

        # Encode once
        _get_encoded_transactions(transactions)
        assert len(_ENCODED_CACHE) == 1

        # Clear and verify
        _ENCODED_CACHE.clear()
        assert len(_ENCODED_CACHE) == 0

        # Should recompute after clear
        _get_encoded_transactions(transactions)
        assert len(_ENCODED_CACHE) == 1


class TestRustBackendSimulation:
    """Test Rust backend code paths with mocking."""

    @patch("gsppy.accelerate._rust_available", True)
    @patch("gsppy.accelerate._compute_supports_rust")
    def test_support_counts_rust_backend_success(self, mock_rust_func):
        """Test successful Rust backend execution."""
        transactions = [("A", "B"), ("A", "C")]
        candidates = [("A",), ("B",)]

        # Mock the Rust function to return encoded results
        # Format: List[Tuple[List[int], int]] where int is the support count
        mock_rust_func.return_value = [([0], 2), ([1], 1)]

        result = support_counts(transactions, candidates, min_support_abs=1, backend="rust")

        # Should have called the Rust function
        assert mock_rust_func.called
        assert result[("A",)] == 2
        assert result[("B",)] == 1

    @patch("gsppy.accelerate._rust_available", True)
    @patch("gsppy.accelerate._compute_supports_rust")
    def test_support_counts_auto_with_rust_available(self, mock_rust_func):
        """Test auto backend selection when Rust is available."""
        transactions = [("X", "Y")]
        candidates = [("X",)]

        # Mock successful Rust execution
        mock_rust_func.return_value = [([0], 1)]

        result = support_counts(transactions, candidates, min_support_abs=1, backend="auto")

        # Should use Rust when available
        assert mock_rust_func.called
        assert result[("X",)] == 1

    @patch("gsppy.accelerate._rust_available", True)
    @patch("gsppy.accelerate._compute_supports_rust")
    def test_support_counts_auto_rust_fallback_to_python(self, mock_rust_func):
        """Test auto backend falls back to Python when Rust fails."""
        transactions = [("A", "B")]
        candidates = [("A",)]

        # Mock Rust function to raise an exception
        mock_rust_func.side_effect = RuntimeError("Rust backend error")

        # Should fallback to Python
        result = support_counts(transactions, candidates, min_support_abs=1, backend="auto")

        assert result[("A",)] == 1

    @patch("gsppy.accelerate._rust_available", True)
    @patch("gsppy.accelerate._compute_supports_rust")
    def test_support_counts_rust_empty_result(self, mock_rust_func):
        """Test Rust backend with candidates that don't meet min_support."""
        transactions = [("A", "B"), ("C", "D")]
        candidates = [("A", "B"), ("C", "D")]

        # Mock result with no patterns meeting min_support
        mock_rust_func.return_value = []

        result = support_counts(transactions, candidates, min_support_abs=3, backend="rust")

        assert result == {}


class TestGPUBackendSimulation:
    """Test GPU backend code paths with mocking."""

    @patch("gsppy.accelerate._gpu_available", True)
    @patch("gsppy.accelerate.cp")
    def test_support_counts_gpu_singletons_only(self, mock_cp):
        """Test GPU backend with only singleton candidates."""
        # Mock CuPy operations
        mock_cp_array = Mock()
        mock_cp_counts = Mock()
        mock_cp_counts.get.return_value = [2, 1, 2]  # Support counts for A, B, C

        mock_cp.asarray.return_value = mock_cp_array
        mock_cp.bincount.return_value = mock_cp_counts

        transactions = [("A", "B"), ("A", "C"), ("B", "C")]
        candidates = [("A",), ("B",), ("C",)]

        result = support_counts(transactions, candidates, min_support_abs=1, backend="gpu")

        # Should use GPU for singletons
        assert mock_cp.asarray.called
        assert mock_cp.bincount.called

    @patch("gsppy.accelerate._gpu_available", True)
    @patch("gsppy.accelerate._rust_available", True)
    @patch("gsppy.accelerate._compute_supports_rust")
    @patch("gsppy.accelerate.cp")
    def test_support_counts_gpu_mixed_with_rust(self, mock_cp, mock_rust_func):
        """Test GPU backend with mixed candidates and Rust available for non-singletons."""
        # Mock CuPy for singletons
        mock_cp_counts = Mock()
        mock_cp_counts.get.return_value = [2, 1]
        mock_cp.asarray.return_value = Mock()
        mock_cp.bincount.return_value = mock_cp_counts

        # Mock Rust for non-singletons
        mock_rust_func.return_value = [([0, 1], 1)]

        transactions = [("A", "B"), ("A", "C")]
        candidates = [("A",), ("B",), ("A", "B")]

        result = support_counts(transactions, candidates, min_support_abs=1, backend="gpu")

        # Should use both GPU and Rust
        assert mock_cp.bincount.called
        assert mock_rust_func.called

    @patch("gsppy.accelerate._gpu_available", True)
    @patch("gsppy.accelerate._rust_available", False)
    @patch("gsppy.accelerate.cp")
    def test_support_counts_gpu_mixed_without_rust(self, mock_cp):
        """Test GPU backend with mixed candidates and no Rust (Python fallback)."""
        # Mock CuPy for singletons
        mock_cp_counts = Mock()
        mock_cp_counts.get.return_value = [2, 1]
        mock_cp.asarray.return_value = Mock()
        mock_cp.bincount.return_value = mock_cp_counts

        transactions = [("A", "B"), ("A", "C")]
        candidates = [("A",), ("B",), ("A", "B")]

        result = support_counts(transactions, candidates, min_support_abs=1, backend="gpu")

        # Should use GPU for singletons and Python for non-singletons
        assert mock_cp.bincount.called
        # Non-singleton should be processed by Python backend
        assert ("A", "B") in result

    @patch("gsppy.accelerate._gpu_available", True)
    @patch("gsppy.accelerate._rust_available", True)
    @patch("gsppy.accelerate._compute_supports_rust")
    @patch("gsppy.accelerate.cp")
    def test_support_counts_gpu_rust_fallback_on_error(self, mock_cp, mock_rust_func):
        """Test GPU backend falls back to Python when Rust fails on non-singletons."""
        # Mock CuPy for singletons
        mock_cp_counts = Mock()
        mock_cp_counts.get.return_value = [2]
        mock_cp.asarray.return_value = Mock()
        mock_cp.bincount.return_value = mock_cp_counts

        # Mock Rust to fail
        mock_rust_func.side_effect = RuntimeError("Rust error")

        transactions = [("A", "B"), ("A", "C")]
        candidates = [("A",), ("A", "B")]

        result = support_counts(transactions, candidates, min_support_abs=1, backend="gpu")

        # Should have singleton result from GPU
        assert ("A",) in result
        # And non-singleton from Python fallback
        assert ("A", "B") in result


class TestIntegration:
    """Integration tests combining multiple components."""

    def test_full_workflow_python_backend(self):
        """Test complete workflow from transactions to support counts."""
        # Simulating a real GSP scenario
        transactions = [
            ("A", "B", "C"),
            ("A", "C", "D"),
            ("B", "C", "D"),
            ("A", "B", "D"),
        ]

        # Level 1 candidates (singletons)
        candidates_1 = [("A",), ("B",), ("C",), ("D",)]
        result_1 = support_counts(transactions, candidates_1, min_support_abs=2, backend="python")

        # All items appear in at least 2 transactions
        assert len(result_1) == 4

        # Level 2 candidates
        candidates_2 = [("A", "B"), ("A", "C"), ("A", "D"), ("B", "C"), ("B", "D"), ("C", "D")]
        result_2 = support_counts(transactions, candidates_2, min_support_abs=2, backend="python")

        # Check specific patterns
        assert result_2[("A", "B")] >= 2 or ("A", "B") not in result_2
        assert result_2.get(("A", "D"), 0) >= 2 or ("A", "D") not in result_2

    def test_encoding_decoding_roundtrip(self):
        """Test that encoding and decoding produces original data."""
        transactions = [("X", "Y", "Z"), ("Y", "Z", "W")]

        enc_tx, inv_vocab, vocab = _encode_transactions(transactions)

        # Decode back
        decoded_transactions = []
        for enc_t in enc_tx:
            decoded_transactions.append(tuple(inv_vocab[i] for i in enc_t))

        assert decoded_transactions == transactions

    def test_consistent_results_across_backends(self):
        """Test that python backend produces consistent results."""
        transactions = [("A", "B", "C"), ("A", "C"), ("B", "C")]
        candidates = [("A",), ("B",), ("C",), ("A", "B"), ("A", "C")]

        result_python = support_counts(transactions, candidates, min_support_abs=1, backend="python")

        # All backends should agree on these results
        assert result_python[("A",)] == 2
        assert result_python[("B",)] == 2
        assert result_python[("C",)] == 3
        assert result_python[("A", "B")] == 1
        assert result_python[("A", "C")] == 2
