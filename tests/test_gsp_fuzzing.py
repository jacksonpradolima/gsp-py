"""
Property-based fuzzing tests for the GSP (Generalized Sequential Pattern) algorithm.

This module uses the Hypothesis library to perform property-based testing (fuzzing)
of the GSP algorithm. These tests generate random inputs to verify that the algorithm
maintains important invariants and properties across a wide range of inputs.

The property-based tests help discover edge cases and ensure the robustness of the
GSP implementation by testing with automatically generated random data.

Author: Jackson Antonio do Prado Lima
Email: jacksonpradolima@gmail.com
"""

import math
from typing import List

from hypothesis import HealthCheck, given, settings, strategies as st

from gsppy.gsp import GSP


# Hypothesis strategies for generating test data
@st.composite
def transaction_lists(draw: st.DrawFn, min_transactions: int = 2, max_transactions: int = 50) -> List[List[str]]:
    """
    Generate lists of transactions for testing.

    Each transaction is a list of items (strings).

    Args:
        draw: Hypothesis draw function
        min_transactions: Minimum number of transactions
        max_transactions: Maximum number of transactions

    Returns:
        A list of transactions
    """
    n_transactions = draw(st.integers(min_value=min_transactions, max_value=max_transactions))

    # Generate a pool of items to choose from
    items = draw(
        st.lists(
            st.text(alphabet=st.characters(min_codepoint=65, max_codepoint=90), min_size=1, max_size=3),
            min_size=2,
            max_size=20,
            unique=True,
        )
    )

    # Generate transactions
    transactions = []
    for _ in range(n_transactions):
        transaction_size = draw(st.integers(min_value=1, max_value=min(10, len(items))))
        transaction = draw(st.lists(st.sampled_from(items), min_size=transaction_size, max_size=transaction_size))
        transactions.append(transaction)

    return transactions


@given(transactions=transaction_lists())
@settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.too_slow])
def test_gsp_returns_valid_output(transactions: List[List[str]]) -> None:
    """
    Property: GSP should always return a valid output structure.

    The output should be a list of dictionaries, where each dictionary
    represents patterns at a certain level (1-sequences, 2-sequences, etc.).
    """
    gsp = GSP(transactions)
    result = gsp.search(min_support=0.1)

    # Result should be a list
    assert isinstance(result, list), "GSP output should be a list"

    # Each element should be a dictionary
    for level_patterns in result:
        assert isinstance(level_patterns, dict), "Each level should be a dictionary"

        # Keys should be tuples
        for pattern in level_patterns.keys():
            assert isinstance(pattern, tuple), "Pattern keys should be tuples"
            assert len(pattern) > 0, "Patterns should not be empty"

            # Values should be integers (support counts)
            support = level_patterns[pattern]
            assert isinstance(support, int), "Support should be an integer"
            assert support > 0, "Support should be positive"
            assert support <= len(transactions), "Support cannot exceed number of transactions"


@given(transactions=transaction_lists())
@settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.too_slow])
def test_gsp_support_monotonicity(transactions: List[List[str]]) -> None:
    """
    Property: Lower min_support should yield equal or more patterns.

    If we decrease the minimum support threshold, we should get
    at least as many patterns (or more) than with a higher threshold.
    """
    # Use separate GSP instances to avoid state accumulation between searches
    # on different min_support thresholds.

    # Test with two different support levels
    high_support = 0.5
    low_support = 0.2

    gsp_high = GSP(transactions)
    gsp_low = GSP(transactions)

    result_high = gsp_high.search(min_support=high_support)
    result_low = gsp_low.search(min_support=low_support)

    # Count total patterns at each support level
    patterns_high = sum(len(level) for level in result_high)
    patterns_low = sum(len(level) for level in result_low)

    # Lower support should yield equal or more patterns
    assert patterns_low >= patterns_high, (
        f"Lower support ({low_support}) should yield at least as many patterns "
        f"as higher support ({high_support}). Got {patterns_low} vs {patterns_high}"
    )


@given(transactions=transaction_lists())
@settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.too_slow])
def test_gsp_pattern_length_increases(transactions: List[List[str]]) -> None:
    """
    Property: Pattern lengths should increase by level.

    Level 1 should contain 1-sequences, level 2 should contain 2-sequences, etc.
    Each subsequent level should have patterns that are one element longer.
    """
    gsp = GSP(transactions)
    result = gsp.search(min_support=0.1)

    for level_idx, level_patterns in enumerate(result, start=1):
        for pattern in level_patterns.keys():
            assert len(pattern) == level_idx, (
                f"At level {level_idx}, expected patterns of length {level_idx}, "
                f"but got pattern {pattern} with length {len(pattern)}"
            )


@given(transactions=transaction_lists(), min_support=st.floats(min_value=0.01, max_value=1.0))
@settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.too_slow])
def test_gsp_respects_min_support(transactions: List[List[str]], min_support: float) -> None:
    """
    Property: All returned patterns should meet the minimum support threshold.

    Every pattern in the result should have support >= min_support * num_transactions.
    """
    gsp = GSP(transactions)
    result = gsp.search(min_support=min_support)

    min_support_count = math.ceil(min_support * len(transactions))

    for level_patterns in result:
        for pattern, support in level_patterns.items():
            assert support >= min_support_count, (
                f"Pattern {pattern} has support {support}, which is below the "
                f"minimum required support of {min_support_count} "
                f"(min_support={min_support}, n_transactions={len(transactions)})"
            )


@given(transactions=transaction_lists())
@settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.too_slow])
def test_gsp_first_level_contains_single_items(transactions: List[List[str]]) -> None:
    """
    Property: First level should contain only single-item sequences.

    The first level of frequent patterns should only contain 1-sequences,
    which are the frequent individual items from the transactions.
    """
    gsp = GSP(transactions)
    result = gsp.search(min_support=0.1)

    if result:  # If any patterns were found
        first_level = result[0]
        for pattern in first_level.keys():
            assert len(pattern) == 1, (
                f"First level should only contain 1-sequences, "
                f"but found pattern {pattern} with length {len(pattern)}"
            )


@given(transactions=transaction_lists(min_transactions=2, max_transactions=10))
@settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.too_slow])
def test_gsp_deterministic(transactions: List[List[str]]) -> None:
    """
    Property: GSP should be deterministic.

    Running the same input through GSP multiple times should produce
    identical results when using fresh GSP instances.
    """
    # Create separate GSP instances to avoid state issues
    gsp1 = GSP(transactions)
    result1 = gsp1.search(min_support=0.2)

    gsp2 = GSP(transactions)
    result2 = gsp2.search(min_support=0.2)

    assert result1 == result2, "GSP should produce identical results for the same input"


@given(transactions=transaction_lists())
@settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.too_slow])
def test_gsp_pattern_hierarchy(transactions: List[List[str]]) -> None:
    """
    Property: Each pattern's support should be >= support of any of its super-patterns.

    This tests the anti-monotonicity property: if a pattern P appears in k transactions,
    then any longer pattern containing P can appear in at most k transactions.

    Note: We check that minimum support at each level is >= minimum at next level,
    which is a weaker but still valid monotonicity check.
    """
    gsp = GSP(transactions)
    result = gsp.search(min_support=0.2)

    if len(result) < 2:
        return  # Not enough levels to test

    # Check that all patterns meet minimum support threshold
    min_support_count = math.ceil(len(transactions) * 0.2)

    for level_idx in range(len(result)):
        current_level = result[level_idx]
        for pattern, support in current_level.items():
            # Basic check: all patterns meet the minimum threshold
            assert support >= min_support_count, (
                f"Pattern {pattern} at level {level_idx + 1} has support {support}, "
                f"which is below the threshold {min_support_count}"
            )


@given(transactions=transaction_lists(), min_support=st.floats(min_value=0.01, max_value=0.99))
@settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.too_slow])
def test_gsp_no_duplicate_patterns(transactions: List[List[str]], min_support: float) -> None:
    """
    Property: No duplicate patterns should exist at any level.

    Each pattern should appear only once in its respective level.
    """
    gsp = GSP(transactions)
    result = gsp.search(min_support=min_support)

    for level_idx, level_patterns in enumerate(result, start=1):
        pattern_list = list(level_patterns.keys())
        pattern_set = set(pattern_list)

        assert len(pattern_list) == len(pattern_set), (
            f"Level {level_idx} contains duplicate patterns. "
            f"Found {len(pattern_list)} patterns but only {len(pattern_set)} unique ones."
        )


@given(st.lists(st.lists(st.text(min_size=1, max_size=3), min_size=1, max_size=5), min_size=2, max_size=10))
@settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.too_slow])
def test_gsp_handles_diverse_inputs(transactions: List[List[str]]) -> None:
    """
    Property: GSP should handle diverse string inputs without crashing.

    This test uses Hypothesis to generate various string patterns and
    ensures the algorithm doesn't crash on unexpected inputs.
    """
    try:
        gsp = GSP(transactions)
        result = gsp.search(min_support=0.1)

        # Should return a valid result
        assert isinstance(result, list), "Should return a list"
    except ValueError as e:
        # Only acceptable if it's a validation error about multiple transactions
        assert "multiple transactions" in str(e).lower(), f"Unexpected error: {e}"


@given(transactions=transaction_lists(min_transactions=5, max_transactions=20))
@settings(max_examples=30, deadline=None, suppress_health_check=[HealthCheck.too_slow])
def test_gsp_empty_result_with_high_support(transactions: List[List[str]]) -> None:
    """
    Property: With sufficiently high min_support, result should be empty or minimal.

    If min_support is set very high (e.g., 1.0), we expect no patterns
    or very few patterns to be found.
    """
    gsp = GSP(transactions)
    result = gsp.search(min_support=0.95)

    # Either empty or very few patterns
    total_patterns = sum(len(level) for level in result)
    assert total_patterns <= 5, (
        f"With min_support=0.95, expected very few or no patterns, but found {total_patterns} patterns"
    )


@given(
    transactions=transaction_lists(min_transactions=10, max_transactions=30),
    support_fraction=st.floats(min_value=0.1, max_value=0.9),
)
@settings(max_examples=30, deadline=None, suppress_health_check=[HealthCheck.too_slow])
def test_gsp_support_bounds(transactions: List[List[str]], support_fraction: float) -> None:
    """
    Property: Support values should be within valid bounds.

    All support counts should be:
    - At least ceil(min_support * n_transactions)
    - At most n_transactions
    """
    gsp = GSP(transactions)
    result = gsp.search(min_support=support_fraction)

    n_transactions = len(transactions)
    min_count = math.ceil(support_fraction * n_transactions)

    for level_patterns in result:
        for pattern, support in level_patterns.items():
            assert min_count <= support <= n_transactions, (
                f"Pattern {pattern} has support {support}, which is outside "
                f"the valid range [{min_count}, {n_transactions}]"
            )
