"""
Unit tests for custom hooks functionality in the GSP algorithm.

This module tests the hook functions (preprocess_fn, postprocess_fn, candidate_filter_fn)
that allow users to customize the GSP mining pipeline with lambda expressions and
arbitrary callables.

Tests include:
- Preprocessing hooks for data transformation
- Postprocessing hooks for result filtering
- Candidate filtering with lambda expressions
- Error handling for user-provided hooks
- Integration with existing features (temporal constraints, dataframes)
- Edge cases (None values, empty results, errors in hooks)

Author: Jackson Antonio do Prado Lima
Email: jacksonpradolima@gmail.com
"""

from typing import Any, Dict, List, Tuple

import pytest

from gsppy.gsp import GSP


def _convert_itemset_to_prefix(itemset, prefix: str) -> Tuple[str, ...]:
    """Helper to add prefix to itemset items."""
    if itemset:
        return tuple(prefix + item if isinstance(item, str) else str(item) for item in itemset)
    return itemset


def _convert_transaction_with_prefix(tx, prefix: str) -> Tuple[Tuple[str, ...], ...]:
    """Helper to convert transaction with prefix."""
    converted_tx = []
    for itemset in tx:
        converted_itemset = _convert_itemset_to_prefix(itemset, prefix)
        converted_tx.append(converted_itemset)
    return tuple(converted_tx)


@pytest.fixture
def simple_transactions() -> List[List[str]]:
    """
    Fixture to provide a simple dataset for testing hooks.

    Returns:
        list: A list of simple transactions for hook testing.
    """
    return [
        ["A", "B", "C"],
        ["A", "C", "D"],
        ["B", "C", "E"],
        ["A", "B", "C"],
        ["A", "C", "D"],
    ]


@pytest.fixture
def timestamped_transactions() -> List[List[Tuple[str, float]]]:
    """
    Fixture to provide timestamped transactions for testing hooks with temporal data.

    Returns:
        list: A list of timestamped transactions.
    """
    return [
        [("A", 1.0), ("B", 2.0), ("C", 3.0)],
        [("A", 1.0), ("C", 2.5), ("D", 4.0)],
        [("B", 1.0), ("C", 2.0), ("E", 3.5)],
        [("A", 0.5), ("B", 1.5), ("C", 3.0)],
    ]


class TestPreprocessHooks:
    """Tests for preprocess_fn hook functionality."""

    def test_preprocess_uppercase(self, simple_transactions: List[List[str]]) -> None:
        """Test preprocessing hook that converts items to uppercase."""

        # Note: preprocess_fn receives transactions in normalized format (tuples of tuples)
        # For simple transactions, this is: ((item1,), (item2,), ...)
        # We need to handle the tuple format
        def preprocess(txs: Any) -> Any:
            # txs is a list of tuples of tuples
            result = []
            for tx in txs:
                # Each tx is a tuple of tuples (itemset format)
                converted_tx = []
                for itemset in tx:
                    # Each itemset is a tuple of items
                    if itemset:
                        converted_itemset = tuple(item.upper() if isinstance(item, str) else item for item in itemset)
                        converted_tx.append(converted_itemset)
                result.append(tuple(converted_tx))
            return result

        gsp = GSP(simple_transactions)
        patterns = gsp.search(min_support=0.4, preprocess_fn=preprocess)

        # Verify patterns were found (even though preprocessing doesn't change much for already uppercase)
        assert len(patterns) > 0

    def test_preprocess_filter_transactions(self, simple_transactions: List[List[str]]) -> None:
        """Test preprocessing hook that filters transactions."""

        # Filter out transactions without 'B'
        def preprocess(txs: Any) -> Any:
            # txs is a list of tuples of tuples (itemset format)
            # Need to check if any itemset contains 'B'
            result = []
            for tx in txs:
                # Check if any itemset in the transaction contains 'B'
                has_b = any("B" in itemset for itemset in tx)
                if has_b:
                    result.append(tx)
            return result

        gsp = GSP(simple_transactions)
        patterns = gsp.search(min_support=0.5, preprocess_fn=preprocess)

        # After filtering, only 3 transactions have 'B'
        # Patterns should reflect this subset
        assert len(patterns) > 0
        # 'B' should be frequent in the filtered set
        assert any(("B",) in level for level in patterns)

    def test_preprocess_add_prefix(self, simple_transactions: List[List[str]]) -> None:
        """Test preprocessing hook that adds a prefix to items."""

        def preprocess(txs: Any) -> Any:
            # Handle tuple format from normalized transactions
            return [_convert_transaction_with_prefix(tx, "PREFIX_") for tx in txs]

        gsp = GSP(simple_transactions)
        # Use lower min_support since items are transformed
        patterns = gsp.search(min_support=0.2, preprocess_fn=preprocess)

        # Verify patterns were found and contain the prefix
        # Note: With transformation, support counts will be the same but items have prefix
        assert len(patterns) > 0
        for level in patterns:
            for pattern in level.keys():
                # All items in patterns should have the prefix
                assert all(item.startswith("PREFIX_") for item in pattern)

    def test_preprocess_returns_none(self, simple_transactions: List[List[str]]) -> None:
        """Test that returning None from preprocess_fn uses original transactions."""
        preprocess = lambda _txs: None

        gsp = GSP(simple_transactions)
        patterns = gsp.search(min_support=0.4, preprocess_fn=preprocess)

        # Should work with original transactions
        assert len(patterns) > 0

    def test_preprocess_error_handling(self, simple_transactions: List[List[str]]) -> None:
        """Test error handling when preprocess_fn raises an exception."""

        def bad_preprocess(_txs: Any) -> Any:
            raise ValueError("Intentional error in preprocessing")

        gsp = GSP(simple_transactions)
        with pytest.raises(RuntimeError, match="Error in preprocess_fn"):
            gsp.search(min_support=0.4, preprocess_fn=bad_preprocess)


class TestPostprocessHooks:
    """Tests for postprocess_fn hook functionality."""

    def test_postprocess_filter_by_support(self, simple_transactions: List[List[str]]) -> None:
        """Test postprocessing hook that filters patterns by support."""

        # Keep only patterns with support > 2
        def postprocess(patterns: Any) -> Any:
            return [{k: v for k, v in level.items() if v > 2} for level in patterns]

        gsp = GSP(simple_transactions)
        patterns = gsp.search(min_support=0.3, postprocess_fn=postprocess)

        # Verify all returned patterns have support > 2
        for level in patterns:
            for support in level.values():
                assert support > 2

    def test_postprocess_limit_pattern_length(self, simple_transactions: List[List[str]]) -> None:
        """Test postprocessing hook that limits pattern length."""

        # Keep only the first level (1-sequences)
        postprocess = lambda patterns: patterns[:1] if patterns else []

        gsp = GSP(simple_transactions)
        patterns = gsp.search(min_support=0.3, postprocess_fn=postprocess)

        # Should only have 1 level
        assert len(patterns) <= 1

    def test_postprocess_add_metadata(self, simple_transactions: List[List[str]]) -> None:
        """Test postprocessing hook that adds metadata to results."""

        # Add a summary level with total patterns
        def postprocess(patterns: Any) -> Any:
            # Count total patterns across all levels
            total = sum(len(level) for level in patterns)
            # Return patterns with metadata as first element (this changes the format)
            return [{"_metadata": {"total_patterns": total}}] + patterns

        gsp = GSP(simple_transactions)
        patterns = gsp.search(min_support=0.3, postprocess_fn=postprocess)

        # First element should be metadata
        assert "_metadata" in patterns[0]
        assert "total_patterns" in patterns[0]["_metadata"]  # type: ignore

    def test_postprocess_returns_none(self, simple_transactions: List[List[str]]) -> None:
        """Test that returning None from postprocess_fn uses original results."""
        postprocess = lambda _patterns: None

        gsp = GSP(simple_transactions)
        patterns = gsp.search(min_support=0.4, postprocess_fn=postprocess)

        # Should work with original patterns
        assert len(patterns) > 0

    def test_postprocess_error_handling(self, simple_transactions: List[List[str]]) -> None:
        """Test error handling when postprocess_fn raises an exception."""

        def bad_postprocess(_patterns: Any) -> Any:
            raise ValueError("Intentional error in postprocessing")

        gsp = GSP(simple_transactions)
        with pytest.raises(RuntimeError, match="Error in postprocess_fn"):
            gsp.search(min_support=0.4, postprocess_fn=bad_postprocess)


class TestCandidateFilterHooks:
    """Tests for candidate_filter_fn hook functionality."""

    def test_candidate_filter_lambda_length(self, simple_transactions: List[List[str]]) -> None:
        """Test candidate filtering with lambda expression based on pattern length."""
        # Only keep patterns with length <= 2
        filter_fn = lambda candidate, _support, _ctx: len(candidate) <= 2

        gsp = GSP(simple_transactions)
        patterns = gsp.search(min_support=0.3, candidate_filter_fn=filter_fn)

        # Verify no patterns longer than 2
        for level in patterns:
            for pattern in level.keys():
                assert len(pattern) <= 2

    def test_candidate_filter_lambda_support(self, simple_transactions: List[List[str]]) -> None:
        """Test candidate filtering based on support threshold."""
        # Keep candidates with support >= 3
        filter_fn = lambda _candidate, support, _ctx: support >= 3

        gsp = GSP(simple_transactions)
        patterns = gsp.search(min_support=0.3, candidate_filter_fn=filter_fn)

        # Verify all patterns have support >= 3
        for level in patterns:
            for support in level.values():
                assert support >= 3

    def test_candidate_filter_by_content(self, simple_transactions: List[List[str]]) -> None:
        """Test candidate filtering based on pattern content."""
        # Only keep patterns containing 'A'
        filter_fn = lambda candidate, _support, _ctx: "A" in candidate

        gsp = GSP(simple_transactions)
        patterns = gsp.search(min_support=0.3, candidate_filter_fn=filter_fn)

        # Verify all patterns contain 'A'
        for level in patterns:
            for pattern in level.keys():
                assert "A" in pattern

    def test_candidate_filter_using_context(self, simple_transactions: List[List[str]]) -> None:
        """Test candidate filtering using context information."""

        # Filter based on context - keep if support is at least 1.5x the min support count
        def filter_fn(_candidate: Tuple[str, ...], support: int, context: Dict[str, Any]) -> bool:
            min_support = context.get("min_support_count", 0)
            return support >= min_support * 1.5

        gsp = GSP(simple_transactions)
        patterns = gsp.search(min_support=0.3, candidate_filter_fn=filter_fn)

        # Should have fewer patterns due to stricter filtering
        assert len(patterns) > 0

    def test_candidate_filter_k_level(self, simple_transactions: List[List[str]]) -> None:
        """Test candidate filtering using k_level from context."""

        # Only keep patterns at level 1 and 2
        def filter_fn(_candidate: Tuple[str, ...], _support: int, context: Dict[str, Any]) -> bool:
            k_level = context.get("k_level", 1)
            return k_level <= 2

        gsp = GSP(simple_transactions)
        patterns = gsp.search(min_support=0.3, candidate_filter_fn=filter_fn)

        # Should have at most 2 levels
        assert len(patterns) <= 2

    def test_candidate_filter_complex_logic(self, simple_transactions: List[List[str]]) -> None:
        """Test candidate filtering with complex logic combining multiple criteria."""

        def filter_fn(candidate: Tuple[str, ...], support: int, _context: Dict[str, Any]) -> bool:
            # Complex logic: keep if (length <= 2 AND support >= 3) OR starts with 'A'
            return (len(candidate) <= 2 and support >= 3) or (candidate[0] == "A" if candidate else False)

        gsp = GSP(simple_transactions)
        patterns = gsp.search(min_support=0.3, candidate_filter_fn=filter_fn)

        # Verify all patterns satisfy the complex condition
        for level in patterns:
            for pattern, support in level.items():
                condition_met = (len(pattern) <= 2 and support >= 3) or (pattern[0] == "A" if pattern else False)
                assert condition_met

    def test_candidate_filter_none(self, simple_transactions: List[List[str]]) -> None:
        """Test that None candidate_filter_fn doesn't affect results."""
        gsp = GSP(simple_transactions)
        patterns_without_filter = gsp.search(min_support=0.4)

        gsp2 = GSP(simple_transactions)
        patterns_with_none_filter = gsp2.search(min_support=0.4, candidate_filter_fn=None)

        # Results should be the same
        assert patterns_without_filter == patterns_with_none_filter

    def test_candidate_filter_error_handling(self, simple_transactions: List[List[str]]) -> None:
        """Test error handling when candidate_filter_fn raises an exception."""

        def bad_filter(_candidate: Tuple[str, ...], _support: int, _context: Dict[str, Any]) -> bool:
            raise ValueError("Intentional error in filter")

        gsp = GSP(simple_transactions)
        with pytest.raises(RuntimeError, match="Error in candidate_filter_fn"):
            gsp.search(min_support=0.4, candidate_filter_fn=bad_filter)


class TestCombinedHooks:
    """Tests for using multiple hooks together."""

    def test_all_hooks_combined(self, simple_transactions: List[List[str]]) -> None:
        """Test using all three hooks together."""

        # Preprocessing: add prefix (handles normalized tuple format)
        def preprocess(txs: Any) -> Any:
            return [_convert_transaction_with_prefix(tx, "TEST_") for tx in txs]

        # Candidate filter: keep length <= 2
        filter_fn = lambda candidate, _support, _ctx: len(candidate) <= 2

        # Postprocessing: keep only patterns with support >= 2
        postprocess = lambda patterns: [{k: v for k, v in level.items() if v >= 2} for level in patterns]

        gsp = GSP(simple_transactions)
        patterns = gsp.search(
            min_support=0.3, preprocess_fn=preprocess, candidate_filter_fn=filter_fn, postprocess_fn=postprocess
        )

        # Verify all conditions are met
        for level in patterns:
            for pattern, support in level.items():
                # Has prefix from preprocessing
                assert all(item.startswith("TEST_") for item in pattern)
                # Length constraint from candidate filter
                assert len(pattern) <= 2
                # Support constraint from postprocessing
                assert support >= 2

    def test_hooks_with_temporal_constraints(self, timestamped_transactions: List[List[Tuple[str, float]]]) -> None:
        """Test hooks with temporal constraints enabled."""
        # Candidate filter that works with temporal patterns
        filter_fn = lambda candidate, _support, _ctx: len(candidate) <= 2

        gsp = GSP(timestamped_transactions, maxgap=5.0)
        patterns = gsp.search(min_support=0.5, candidate_filter_fn=filter_fn)

        # Verify patterns are limited by filter
        for level in patterns:
            for pattern in level.keys():
                assert len(pattern) <= 2


class TestHookBackwardCompatibility:
    """Tests to ensure hooks are backward compatible."""

    def test_no_hooks_specified(self, simple_transactions: List[List[str]]) -> None:
        """Test that GSP works as before when no hooks are specified."""
        gsp = GSP(simple_transactions)
        patterns = gsp.search(min_support=0.4)

        # Should work normally
        assert len(patterns) > 0
        # Verify basic pattern structure
        for level in patterns:
            assert isinstance(level, dict)

    def test_partial_hooks(self, simple_transactions: List[List[str]]) -> None:
        """Test that specifying only some hooks works correctly."""
        # Only preprocess, no other hooks
        preprocess = lambda txs: txs

        gsp = GSP(simple_transactions)
        patterns = gsp.search(min_support=0.4, preprocess_fn=preprocess)
        assert len(patterns) > 0

        # Only candidate filter, no other hooks
        filter_fn = lambda _candidate, _support, _ctx: True

        gsp2 = GSP(simple_transactions)
        patterns2 = gsp2.search(min_support=0.4, candidate_filter_fn=filter_fn)
        assert len(patterns2) > 0

        # Only postprocess, no other hooks
        postprocess = lambda patterns: patterns

        gsp3 = GSP(simple_transactions)
        patterns3 = gsp3.search(min_support=0.4, postprocess_fn=postprocess)
        assert len(patterns3) > 0


class TestHookEdgeCases:
    """Tests for edge cases in hook functionality."""

    def test_preprocess_returns_empty_list(self, simple_transactions: List[List[str]]) -> None:
        """Test handling when preprocess_fn returns empty transaction list."""
        preprocess = lambda _txs: []

        gsp = GSP(simple_transactions)
        # Should handle empty transactions gracefully (may return empty patterns or raise)
        patterns = gsp.search(min_support=0.4, preprocess_fn=preprocess)
        # If it doesn't raise, patterns should be empty or minimal
        assert isinstance(patterns, list)

    def test_candidate_filter_rejects_all(self, simple_transactions: List[List[str]]) -> None:
        """Test when candidate_filter_fn rejects all candidates."""
        filter_fn = lambda _candidate, _support, _ctx: False

        gsp = GSP(simple_transactions)
        patterns = gsp.search(min_support=0.4, candidate_filter_fn=filter_fn)

        # Should return empty or minimal patterns
        total_patterns = sum(len(level) for level in patterns)
        assert total_patterns == 0

    def test_postprocess_returns_empty_list(self, simple_transactions: List[List[str]]) -> None:
        """Test when postprocess_fn returns empty list."""
        postprocess = lambda _patterns: []

        gsp = GSP(simple_transactions)
        patterns = gsp.search(min_support=0.4, postprocess_fn=postprocess)

        # Should return empty list
        assert len(patterns) == 0

    def test_hooks_with_return_sequences(self, simple_transactions: List[List[str]]) -> None:
        """Test that hooks work with return_sequences=True."""
        filter_fn = lambda candidate, _support, _ctx: len(candidate) <= 2

        gsp = GSP(simple_transactions)
        patterns = gsp.search(min_support=0.4, candidate_filter_fn=filter_fn, return_sequences=True)

        # Should return Sequence objects
        assert isinstance(patterns, list)
        if patterns and patterns[0]:
            from gsppy.sequence import Sequence

            assert isinstance(patterns[0][0], Sequence)

    def test_state_restoration_on_exception(self, simple_transactions: List[List[str]]) -> None:
        """Test that preprocessing state is restored even when exceptions occur during mining."""
        gsp = GSP(simple_transactions)
        
        # Store original state
        original_transactions = gsp.transactions
        original_candidates = gsp.unique_candidates
        original_max_size = gsp.max_size
        
        # Create a preprocessing function that modifies transactions
        def modify_preprocess(txs):
            # Add an extra itemset to each transaction
            return [tx + (("EXTRA",),) for tx in txs]
        
        # Create a candidate filter that raises an exception
        def failing_filter(candidate, support, ctx):
            if "B" in candidate:
                raise ValueError("Intentional test error")
            return True
        
        # Attempt search with both preprocessing and failing filter
        try:
            gsp.search(min_support=0.3, preprocess_fn=modify_preprocess, candidate_filter_fn=failing_filter)
            assert False, "Expected exception was not raised"
        except (ValueError, RuntimeError):
            pass  # Expected exception
        
        # Verify state was restored despite the exception
        assert gsp.transactions == original_transactions, "Transactions should be restored"
        assert gsp.unique_candidates == original_candidates, "Candidates should be restored"
        assert gsp.max_size == original_max_size, "max_size should be restored"
        
        # Verify GSP instance can still be reused successfully
        patterns = gsp.search(min_support=0.4)
        assert len(patterns) > 0, "GSP should work after exception recovery"
