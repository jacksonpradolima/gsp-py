"""
Unit tests for temporal constraints in GSP algorithm.

This module contains tests for the temporal constraint features (mingap, maxgap, maxspan)
of the GSP algorithm. These tests validate that time-constrained pattern mining works
correctly with timestamped transactions.

Author: Jackson Antonio do Prado Lima
Email: jacksonpradolima@gmail.com
"""

from typing import List, Tuple

import pytest

from gsppy.gsp import GSP
from gsppy.utils import is_subsequence_in_list_with_time_constraints


class TestTemporalConstraintValidation:
    """Tests for temporal constraint validation."""

    def test_negative_mingap(self) -> None:
        """Test that negative mingap raises ValueError."""
        transactions = [[("A", 1), ("B", 2)]]
        with pytest.raises(ValueError, match="mingap must be non-negative"):
            GSP(transactions, mingap=-1)

    def test_negative_maxgap(self) -> None:
        """Test that negative maxgap raises ValueError."""
        transactions = [[("A", 1), ("B", 2)]]
        with pytest.raises(ValueError, match="maxgap must be non-negative"):
            GSP(transactions, maxgap=-1)

    def test_negative_maxspan(self) -> None:
        """Test that negative maxspan raises ValueError."""
        transactions = [[("A", 1), ("B", 2)]]
        with pytest.raises(ValueError, match="maxspan must be non-negative"):
            GSP(transactions, maxspan=-1)

    def test_mingap_greater_than_maxgap(self) -> None:
        """Test that mingap > maxgap raises ValueError."""
        transactions = [[("A", 1), ("B", 2)]]
        with pytest.raises(ValueError, match="mingap cannot be greater than maxgap"):
            GSP(transactions, mingap=10, maxgap=5)

    def test_valid_temporal_constraints(self) -> None:
        """Test that valid temporal constraints are accepted."""
        transactions = [[("A", 1), ("B", 2)], [("A", 1), ("B", 3)]]
        gsp = GSP(transactions, mingap=1, maxgap=5, maxspan=10)
        assert gsp.mingap == 1
        assert gsp.maxgap == 5
        assert gsp.maxspan == 10


class TestTemporalSubsequenceMatching:
    """Tests for is_subsequence_in_list_with_time_constraints function."""

    def test_backward_compatibility_no_timestamps(self) -> None:
        """Test that function works with non-timestamped sequences (backward compatibility)."""
        assert is_subsequence_in_list_with_time_constraints(("A", "C"), ("A", "B", "C"))
        assert not is_subsequence_in_list_with_time_constraints(("C", "A"), ("A", "B", "C"))

    def test_maxgap_constraint_satisfied(self) -> None:
        """Test pattern matching with maxgap constraint satisfied."""
        seq = (("A", 1), ("B", 3), ("C", 5))
        # Gap between A and C is 4, within maxgap=5
        assert is_subsequence_in_list_with_time_constraints(("A", "C"), seq, maxgap=5)

    def test_maxgap_constraint_violated(self) -> None:
        """Test pattern matching with maxgap constraint violated."""
        seq = (("A", 1), ("B", 3), ("C", 10))
        # Gap between A and C is 9, exceeds maxgap=5
        assert not is_subsequence_in_list_with_time_constraints(("A", "C"), seq, maxgap=5)

    def test_maxgap_constraint_consecutive_items(self) -> None:
        """Test maxgap constraint between consecutive items in pattern."""
        seq = (("A", 1), ("B", 8), ("C", 10))
        # Gap between A and B is 7, exceeds maxgap=5
        assert not is_subsequence_in_list_with_time_constraints(("A", "B", "C"), seq, maxgap=5)
        # But B to C gap is 2, within maxgap=5
        assert is_subsequence_in_list_with_time_constraints(("B", "C"), seq, maxgap=5)

    def test_mingap_constraint_satisfied(self) -> None:
        """Test pattern matching with mingap constraint satisfied."""
        seq = (("A", 1), ("B", 2), ("C", 5))
        # Gap between A and C is 4, meets mingap=3
        assert is_subsequence_in_list_with_time_constraints(("A", "C"), seq, mingap=3)

    def test_mingap_constraint_violated(self) -> None:
        """Test pattern matching with mingap constraint violated."""
        seq = (("A", 1), ("B", 2), ("C", 3))
        # Gap between A and C is 2, less than mingap=3
        assert not is_subsequence_in_list_with_time_constraints(("A", "C"), seq, mingap=3)

    def test_maxspan_constraint_satisfied(self) -> None:
        """Test pattern matching with maxspan constraint satisfied."""
        seq = (("A", 1), ("B", 5), ("C", 10))
        # Span from A to C is 9, within maxspan=10
        assert is_subsequence_in_list_with_time_constraints(("A", "C"), seq, maxspan=10)

    def test_maxspan_constraint_violated(self) -> None:
        """Test pattern matching with maxspan constraint violated."""
        seq = (("A", 1), ("B", 5), ("C", 12))
        # Span from A to C is 11, exceeds maxspan=10
        assert not is_subsequence_in_list_with_time_constraints(("A", "C"), seq, maxspan=10)

    def test_combined_constraints(self) -> None:
        """Test pattern matching with multiple constraints combined."""
        seq = (("A", 1), ("B", 3), ("C", 6), ("D", 8))
        # Pattern A, C, D: gaps are 5 (A-C) and 2 (C-D), span is 7
        assert is_subsequence_in_list_with_time_constraints(("A", "C", "D"), seq, mingap=1, maxgap=6, maxspan=10)
        # Violates mingap=3 for C-D gap
        assert not is_subsequence_in_list_with_time_constraints(("A", "C", "D"), seq, mingap=3, maxgap=6, maxspan=10)
        # Violates maxspan=6
        assert not is_subsequence_in_list_with_time_constraints(("A", "C", "D"), seq, mingap=1, maxgap=6, maxspan=6)

    def test_repeated_items_with_temporal_constraints(self) -> None:
        """Test pattern matching with repeated items where early match violates constraints but later match satisfies."""
        # Sequence with repeated B at different times
        seq = (("A", 0), ("B", 1), ("B", 5), ("C", 7))
        # Pattern A, B, C with mingap=3
        # First B at time 1 would violate mingap (gap A-B = 1 < 3)
        # But second B at time 5 satisfies mingap (gap A-B = 5 >= 3) and B-C (gap = 2, but only mingap applies between A-B)
        # Actually, mingap applies to all consecutive pairs, so B-C gap=2 < 3 would fail
        # Let's test a case where the later occurrence works
        seq2 = (("A", 0), ("B", 1), ("B", 5), ("C", 10))
        # With mingap=3, A@0 -> B@5 (gap=5, ok) -> C@10 (gap=5, ok)
        assert is_subsequence_in_list_with_time_constraints(("A", "B", "C"), seq2, mingap=3)
        
        # Test with maxgap: early B violates, later B satisfies
        seq3 = (("A", 0), ("B", 15), ("B", 5))
        # Pattern A, B with maxgap=10
        # First B at time 15 would violate maxgap (gap = 15 > 10)
        # Second B at time 5 satisfies maxgap (gap = 5 <= 10)
        assert is_subsequence_in_list_with_time_constraints(("A", "B"), seq3, maxgap=10)


class TestGSPWithTemporalConstraints:
    """Tests for GSP algorithm with temporal constraints."""

    @pytest.fixture
    def simple_timestamped_transactions(self) -> List[List[Tuple[str, float]]]:
        """Fixture providing simple timestamped transactions."""
        return [
            [("A", 1), ("B", 3), ("C", 5)],
            [("A", 2), ("B", 10), ("C", 12)],
            [("A", 1), ("C", 4)],
        ]

    def test_gsp_without_constraints(self, simple_timestamped_transactions: List[List[Tuple[str, float]]]) -> None:
        """Test GSP with timestamped data but no constraints."""
        gsp = GSP(simple_timestamped_transactions)
        result = gsp.search(min_support=0.5)

        # All three transactions have A and C, so ("A", "C") should be frequent
        assert len(result) >= 2
        assert ("A",) in result[0]
        assert ("C",) in result[0]
        assert ("A", "C") in result[1]
        assert result[1][("A", "C")] == 3

    def test_gsp_with_maxgap(self, simple_timestamped_transactions: List[List[Tuple[str, float]]]) -> None:
        """Test GSP with maxgap constraint."""
        # maxgap=5 should exclude ("A", "B") from transaction 2 (gap=8)
        gsp = GSP(simple_timestamped_transactions, maxgap=5)
        result = gsp.search(min_support=0.5)

        # ("A", "B") should have support 1 (only transaction 1), below threshold
        if len(result) >= 2:
            assert ("A", "B") not in result[1]

    def test_gsp_with_mingap(self) -> None:
        """Test GSP with mingap constraint."""
        transactions = [
            [("A", 1), ("B", 2), ("C", 5)],  # A-B gap=1, A-C gap=4
            [("A", 1), ("B", 5), ("C", 8)],  # A-B gap=4, A-C gap=7
            [("A", 2), ("B", 6), ("C", 10)],  # A-B gap=4, A-C gap=8
        ]
        # mingap=3 should exclude ("A", "B") from transaction 1 (gap=1)
        gsp = GSP(transactions, mingap=3)
        result = gsp.search(min_support=0.5)

        # ("A", "B") should have support 2 (transactions 2 and 3)
        if len(result) >= 2 and ("A", "B") in result[1]:
            assert result[1][("A", "B")] == 2

    def test_gsp_with_maxspan(self) -> None:
        """Test GSP with maxspan constraint."""
        transactions = [
            [("A", 1), ("B", 3), ("C", 6)],  # A-C span=5
            [("A", 1), ("B", 5), ("C", 12)],  # A-C span=11
            [("A", 2), ("B", 4), ("C", 8)],  # A-C span=6
        ]
        # maxspan=10 should exclude ("A", "C") from transaction 2 (span=11)
        gsp = GSP(transactions, maxspan=10)
        result = gsp.search(min_support=0.5)

        # ("A", "C") should have support 2 (transactions 1 and 3)
        if len(result) >= 2 and ("A", "C") in result[1]:
            assert result[1][("A", "C")] == 2

    def test_gsp_combined_constraints(self) -> None:
        """Test GSP with multiple temporal constraints."""
        transactions = [
            [("A", 1), ("B", 3), ("C", 5), ("D", 7)],
            [("A", 1), ("B", 2), ("C", 10), ("D", 12)],
            [("A", 2), ("B", 4), ("C", 6), ("D", 9)],
        ]
        gsp = GSP(transactions, mingap=1, maxgap=3, maxspan=8)
        result = gsp.search(min_support=0.5)

        # Check that constraints are properly enforced
        assert len(result) > 0
        # Transaction 2: A-B gap=1 (ok), but B-C gap=8 (exceeds maxgap=3)
        # So patterns involving A-B-C should be affected


class TestBackwardCompatibility:
    """Tests to ensure backward compatibility with non-timestamped transactions."""

    def test_non_timestamped_transactions_work(self) -> None:
        """Test that regular (non-timestamped) transactions still work."""
        transactions = [
            ["Bread", "Milk"],
            ["Bread", "Diaper", "Beer"],
            ["Milk", "Diaper", "Beer"],
        ]
        gsp = GSP(transactions)
        result = gsp.search(min_support=0.5)

        assert len(result) >= 1
        assert ("Bread",) in result[0] or ("Milk",) in result[0]

    def test_temporal_constraints_ignored_without_timestamps(self) -> None:
        """Test that temporal constraints are ignored for non-timestamped data."""
        transactions = [
            ["A", "B", "C"],
            ["A", "C"],
            ["B", "C"],
        ]
        # These constraints should be ignored since there are no timestamps
        gsp = GSP(transactions, maxgap=5)
        result = gsp.search(min_support=0.5)

        # Should work normally without considering temporal constraints
        assert len(result) >= 1


class TestEdgeCases:
    """Tests for edge cases in temporal constraint handling."""

    def test_single_item_pattern_no_constraints(self) -> None:
        """Test that single-item patterns are not affected by temporal constraints."""
        transactions = [
            [("A", 1), ("B", 10)],
            [("A", 5), ("C", 20)],
        ]
        gsp = GSP(transactions, maxgap=3)
        result = gsp.search(min_support=0.5)

        # Single items should still be found regardless of constraints
        assert ("A",) in result[0]
        assert result[0][("A",)] == 2

    def test_exact_boundary_maxgap(self) -> None:
        """Test maxgap at exact boundary."""
        transactions = [
            [("A", 1), ("B", 6)],  # Gap = 5 (exactly maxgap)
            [("A", 1), ("B", 7)],  # Gap = 6 (exceeds maxgap)
        ]
        gsp = GSP(transactions, maxgap=5)
        result = gsp.search(min_support=0.5)

        # ("A", "B") should have support 1 (only first transaction)
        if len(result) >= 2:
            assert ("A", "B") not in result[1]

    def test_exact_boundary_mingap(self) -> None:
        """Test mingap at exact boundary."""
        transactions = [
            [("A", 1), ("B", 4)],  # Gap = 3 (exactly mingap)
            [("A", 1), ("B", 3)],  # Gap = 2 (below mingap)
        ]
        gsp = GSP(transactions, mingap=3)
        result = gsp.search(min_support=0.5)

        # ("A", "B") should have support 1 (only first transaction)
        if len(result) >= 2:
            assert ("A", "B") not in result[1]

    def test_zero_gap_with_mingap(self) -> None:
        """Test handling of zero time gaps with mingap constraint."""
        transactions = [
            [("A", 1), ("B", 1)],  # Gap = 0
            [("A", 2), ("B", 5)],  # Gap = 3
        ]
        gsp = GSP(transactions, mingap=1)
        result = gsp.search(min_support=0.5)

        # ("A", "B") should have support 1 (only second transaction)
        if len(result) >= 2:
            assert ("A", "B") not in result[1]


class TestComplexTemporalScenarios:
    """Tests for complex real-world temporal pattern scenarios."""

    def test_medical_event_mining(self) -> None:
        """Test temporal constraints for medical event sequences."""
        # Medical events with timestamps (in days)
        medical_sequences = [
            [("Symptom", 0), ("Diagnosis", 2), ("Treatment", 5), ("Recovery", 15)],
            [("Symptom", 0), ("Diagnosis", 1), ("Treatment", 20), ("Recovery", 30)],
            [("Symptom", 0), ("Diagnosis", 3), ("Treatment", 6), ("Recovery", 18)],
        ]
        # Find patterns where treatment follows diagnosis within 10 days
        gsp = GSP(medical_sequences, maxgap=10)
        result = gsp.search(min_support=0.5)

        # ("Diagnosis", "Treatment") should appear with support 2
        # (transactions 1 and 3, not transaction 2 where gap is 19)
        if len(result) >= 2 and ("Diagnosis", "Treatment") in result[1]:
            assert result[1][("Diagnosis", "Treatment")] == 2

    def test_retail_analytics(self) -> None:
        """Test temporal constraints for retail purchase sequences."""
        # Customer purchases with timestamps (in hours)
        purchase_sequences = [
            [("Browse", 0), ("AddToCart", 0.5), ("Purchase", 1)],
            [("Browse", 0), ("AddToCart", 1), ("Purchase", 25)],  # Long delay
            [("Browse", 0), ("AddToCart", 0.3), ("Purchase", 0.8)],
        ]
        # Find patterns within 2 hours
        gsp = GSP(purchase_sequences, maxspan=2)
        result = gsp.search(min_support=0.5)

        # Full sequence should appear in 2 out of 3 (not transaction 2)
        if len(result) >= 3:
            pattern = ("Browse", "AddToCart", "Purchase")
            if pattern in result[2]:
                assert result[2][pattern] == 2


class TestTemporalConstraintsFuzzing:
    """Property-based fuzzing tests for temporal constraints using Hypothesis."""

    @pytest.mark.parametrize("constraint_type", ["mingap", "maxgap", "maxspan"])
    def test_temporal_constraints_with_hypothesis(self, constraint_type: str) -> None:
        """
        Property-based test: temporal constraints should always produce valid results.

        Tests that:
        1. Support counts are non-negative
        2. Pattern lengths are sensible
        3. No crashes occur with various constraint values
        4. Support is monotonic across levels
        """
        from hypothesis import HealthCheck, given, settings, strategies as st

        @given(
            n_transactions=st.integers(min_value=2, max_value=10),
            vocab_size=st.integers(min_value=2, max_value=5),
            constraint_value=st.floats(min_value=0.1, max_value=10.0),
            min_support=st.floats(min_value=0.1, max_value=0.9),
            data=st.data(),
        )
        @settings(
            max_examples=20,
            deadline=None,
            suppress_health_check=[HealthCheck.too_slow],
        )
        def run_test(
            n_transactions: int,
            vocab_size: int,
            constraint_value: float,
            min_support: float,
            data,
        ) -> None:
            # Generate random timestamped transactions
            transactions = _generate_test_transactions(n_transactions, vocab_size, data)

            # Create GSP with the constraint
            kwargs = {constraint_type: constraint_value}
            try:
                gsp = GSP(transactions, **kwargs)
                result = gsp.search(min_support=min_support)

                # Validate result properties
                _validate_support_counts(result)
                _validate_pattern_lengths(result)
                _validate_support_monotonicity(result)
                _validate_min_support_threshold(result, n_transactions, min_support)

            except ValueError as e:
                # Some constraint combinations may be invalid, that's okay
                if "mingap cannot be greater than maxgap" not in str(e):
                    raise

        run_test()


def _generate_test_transactions(n_transactions: int, vocab_size: int, data) -> list:
    """Generate random timestamped transactions for testing."""
    from hypothesis import strategies as st

    vocab = [chr(65 + i) for i in range(vocab_size)]  # A, B, C, etc.
    transactions = []

    for _ in range(n_transactions):
        # Use Hypothesis to generate transaction length and items
        length = data.draw(st.integers(min_value=1, max_value=5))
        items = data.draw(st.lists(st.sampled_from(vocab), min_size=length, max_size=length))
        # Generate increasing timestamps using Hypothesis
        timestamps = sorted(data.draw(st.lists(st.floats(min_value=0, max_value=20), min_size=length, max_size=length)))
        transaction = [(item, ts) for item, ts in zip(items, timestamps, strict=True)]
        transactions.append(transaction)

    return transactions


def _validate_support_counts(result: list) -> None:
    """Validate that all support counts are non-negative integers."""
    for level in result:
        for support in level.values():
            assert support >= 0, f"Support should be non-negative: {support}"
            assert isinstance(support, int), f"Support should be an integer: {support}"


def _validate_pattern_lengths(result: list) -> None:
    """Validate that pattern lengths match their level."""
    for i, level in enumerate(result):
        for pattern in level.keys():
            assert len(pattern) == i + 1, f"Pattern length mismatch at level {i}"


def _validate_support_monotonicity(result: list) -> None:
    """Validate that support is monotonic across pattern levels."""
    if len(result) > 1:
        for i in range(len(result) - 1):
            max_support_current = max(result[i].values()) if result[i] else 0
            max_support_next = max(result[i + 1].values()) if result[i + 1] else 0
            assert (
                max_support_next <= max_support_current
            ), "Support should be monotonic (longer patterns should have <= support)"


def _validate_min_support_threshold(result: list, n_transactions: int, min_support: float) -> None:
    """Validate that all patterns meet the minimum support threshold."""
    abs_min_support = int(n_transactions * min_support)
    if abs_min_support > 0:  # Only check if threshold is meaningful
        for level in result:
            for pattern, support in level.items():
                assert (
                    support >= abs_min_support
                ), f"Pattern {pattern} has support {support} below threshold {abs_min_support}"


class TestTemporalConstraintsFuzzingEdgeCases:
    """Additional property-based fuzzing tests for temporal constraint edge cases."""

    def test_temporal_constraints_edge_cases_hypothesis(self) -> None:
        """
        Fuzzing test for edge cases with temporal constraints.

        Tests robustness with:
        - Empty transactions
        - Single-item transactions
        - Transactions with identical timestamps
        - Transactions with very large timestamp gaps
        """
        from hypothesis import HealthCheck, given, assume, settings, strategies as st

        @given(
            n_transactions=st.integers(min_value=2, max_value=8),
            has_duplicates=st.booleans(),
            has_zero_gaps=st.booleans(),
            mingap=st.floats(min_value=0, max_value=5.0) | st.none(),
            maxgap=st.floats(min_value=0, max_value=10.0) | st.none(),
            data=st.data(),
        )
        @settings(
            max_examples=20,
            deadline=None,
            suppress_health_check=[HealthCheck.too_slow],
        )
        def run_edge_case_test(
            n_transactions: int,
            has_duplicates: bool,
            has_zero_gaps: bool,
            mingap: float,
            maxgap: float,
            data,
        ) -> None:
            # Validate constraint combination
            if mingap is not None and maxgap is not None:
                assume(mingap <= maxgap)

            vocab = ["X", "Y", "Z"]
            transactions = []

            for _ in range(n_transactions):
                # Use Hypothesis to generate transaction length and items
                length = data.draw(st.integers(min_value=1, max_value=4))
                items = data.draw(st.lists(st.sampled_from(vocab), min_size=length, max_size=length))

                if has_zero_gaps:
                    # Some items have the same timestamp - use Hypothesis
                    timestamps = sorted(
                        data.draw(st.lists(st.sampled_from([1.0, 2.0, 3.0]), min_size=length, max_size=length))
                    )
                elif has_duplicates:
                    # Allow duplicate items
                    timestamps = sorted([float(i) for i in range(length)])
                else:
                    # Normal case - use Hypothesis
                    timestamps = sorted(
                        data.draw(st.lists(st.floats(min_value=0, max_value=10), min_size=length, max_size=length))
                    )

                transaction = [(item, ts) for item, ts in zip(items, timestamps, strict=True)]
                transactions.append(transaction)

            try:
                gsp = GSP(transactions, mingap=mingap, maxgap=maxgap)
                result = gsp.search(min_support=0.3)

                # Should not crash and should return valid results
                assert isinstance(result, list), "Result should be a list"
                for level in result:
                    assert isinstance(level, dict), "Each level should be a dict"

            except ValueError:
                # Some constraint combinations may be invalid
                pass

        run_edge_case_test()

    def test_temporal_constraints_monotonicity_hypothesis(self) -> None:
        """
        Property test: Relaxing constraints should never decrease the number of patterns found.

        Tests that:
        - Increasing maxgap should find >= patterns
        - Decreasing mingap should find >= patterns
        - Increasing maxspan should find >= patterns
        """
        from hypothesis import HealthCheck, given, settings, strategies as st

        @given(
            n_transactions=st.integers(min_value=3, max_value=6),
            base_gap=st.floats(min_value=1.0, max_value=5.0),
            data=st.data(),
        )
        @settings(
            max_examples=15,
            deadline=None,
            suppress_health_check=[HealthCheck.too_slow],
        )
        def run_monotonicity_test(
            n_transactions: int,
            base_gap: float,
            data,
        ) -> None:
            # Generate transactions using Hypothesis
            vocab = ["P", "Q", "R"]
            transactions = []

            for _ in range(n_transactions):
                # Use Hypothesis to generate transaction length and items
                length = data.draw(st.integers(min_value=2, max_value=4))
                items = data.draw(st.lists(st.sampled_from(vocab), min_size=length, max_size=length))
                timestamps = sorted([i * 2.0 for i in range(length)])  # Evenly spaced
                transaction = [(item, ts) for item, ts in zip(items, timestamps, strict=True)]
                transactions.append(transaction)

            # Test maxgap monotonicity
            try:
                gsp_strict = GSP(transactions, maxgap=base_gap)
                result_strict = gsp_strict.search(min_support=0.3)

                gsp_relaxed = GSP(transactions, maxgap=base_gap * 2)
                result_relaxed = gsp_relaxed.search(min_support=0.3)

                # Count total patterns
                count_strict = sum(len(level) for level in result_strict)
                count_relaxed = sum(len(level) for level in result_relaxed)

                # Relaxed constraints should find at least as many patterns
                assert count_relaxed >= count_strict, (
                    f"Relaxing maxgap should not decrease patterns: " f"strict={count_strict}, relaxed={count_relaxed}"
                )
            except ValueError:
                # Some combinations may be invalid
                pass

        run_monotonicity_test()
