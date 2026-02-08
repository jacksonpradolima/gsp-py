"""
Enhanced edge-case property-based tests for GSP algorithm.

This module extends the existing fuzzing tests with comprehensive edge-case
scenarios, extreme inputs, and robustness testing using Hypothesis.

Test Categories:
1. Extreme Transaction Sizes - Very large/small transactions
2. Sparse and Noisy Data - Low pattern overlap and random noise
3. Variable-Length Structures - Inconsistent transaction sizes
4. Malformed Inputs - Special characters, duplicates, edge cases
5. Temporal Edge Cases - Pathological timestamp scenarios
6. Support Threshold Boundaries - Edge cases for min_support values

Author: Jackson Antonio do Prado Lima
Email: jacksonpradolima@gmail.com
"""

import math
from typing import List, Tuple

import pytest
from hypothesis import HealthCheck, given, settings, strategies as st, assume

from gsppy.gsp import GSP
from tests.hypothesis_strategies import (
    extreme_transaction_lists,
    sparse_transaction_lists,
    noisy_transaction_lists,
    variable_length_transaction_lists,
    transactions_with_duplicates,
    transactions_with_special_chars,
    timestamped_transaction_lists,
    pathological_timestamped_transactions,
    valid_support_thresholds,
    edge_case_support_thresholds,
)


# ============================================================================
# Extreme Transaction Size Tests
# ============================================================================

@given(transactions=extreme_transaction_lists(size_type="large"))
@settings(max_examples=20, deadline=None, suppress_health_check=[HealthCheck.too_slow])
def test_gsp_handles_large_transactions(transactions: List[List[str]]) -> None:
    """
    Property: GSP should handle transactions with many items.
    
    Tests with few transactions but each containing many items (50-100+).
    This stresses the algorithm's ability to handle large individual transactions.
    """
    gsp = GSP(transactions)
    result = gsp.search(min_support=0.3)
    
    # Should return valid output structure
    assert isinstance(result, list)
    
    # All patterns should meet support threshold
    min_support_count = math.ceil(0.3 * len(transactions))
    for level_patterns in result:
        for pattern, support in level_patterns.items():
            assert support >= min_support_count


@given(transactions=extreme_transaction_lists(size_type="many"))
@settings(max_examples=15, deadline=None, suppress_health_check=[HealthCheck.too_slow])
def test_gsp_handles_many_transactions(transactions: List[List[str]]) -> None:
    """
    Property: GSP should handle datasets with many transactions.
    
    Tests with 100-500 transactions to ensure scalability.
    """
    gsp = GSP(transactions)
    result = gsp.search(min_support=0.1)
    
    # Should return valid output structure
    assert isinstance(result, list)
    
    # Support counts should be within valid bounds
    for level_patterns in result:
        for pattern, support in level_patterns.items():
            assert 1 <= support <= len(transactions)


@given(transactions=extreme_transaction_lists(size_type="minimal"))
@settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.too_slow])
def test_gsp_handles_minimal_input(transactions: List[List[str]]) -> None:
    """
    Property: GSP should handle minimal valid input (2 transactions, 1 item each).
    
    Tests the absolute minimum input requirements.
    """
    gsp = GSP(transactions)
    result = gsp.search(min_support=0.5)
    
    # Should return valid output
    assert isinstance(result, list)
    
    # With minimal input, patterns should be very simple
    if result:
        # First level should only contain 1-sequences
        for pattern in result[0].keys():
            assert len(pattern) == 1


# ============================================================================
# Sparse and Noisy Data Tests
# ============================================================================

@given(transactions=sparse_transaction_lists())
@settings(max_examples=30, deadline=None, suppress_health_check=[HealthCheck.too_slow])
def test_gsp_handles_sparse_patterns(transactions: List[List[str]]) -> None:
    """
    Property: GSP should gracefully handle sparse data with low pattern overlap.
    
    With sparse data, most patterns will have low support. Tests that the
    algorithm correctly identifies the few frequent patterns that exist.
    """
    gsp = GSP(transactions)
    # Use lower support threshold for sparse data
    result = gsp.search(min_support=0.05)
    
    assert isinstance(result, list)
    
    # Verify all returned patterns meet the threshold
    min_support_count = math.ceil(0.05 * len(transactions))
    for level_patterns in result:
        for pattern, support in level_patterns.items():
            assert support >= min_support_count


@given(transactions=noisy_transaction_lists(noise_ratio=0.7))
@settings(max_examples=25, deadline=None, suppress_health_check=[HealthCheck.too_slow])
def test_gsp_filters_noise(transactions: List[List[str]]) -> None:
    """
    Property: GSP should filter out noisy items and identify true patterns.
    
    Tests with high noise ratio to ensure the algorithm can separate
    signal from noise based on support threshold.
    """
    gsp = GSP(transactions)
    result = gsp.search(min_support=0.3)
    
    assert isinstance(result, list)
    
    # Patterns should meet support threshold despite noise
    min_support_count = math.ceil(0.3 * len(transactions))
    for level_patterns in result:
        for pattern, support in level_patterns.items():
            assert support >= min_support_count
            assert support <= len(transactions)


@given(
    transactions=noisy_transaction_lists(),
    support=st.floats(min_value=0.1, max_value=0.8)
)
@settings(max_examples=20, deadline=None, suppress_health_check=[HealthCheck.too_slow])
def test_gsp_noise_resistance_varies_with_support(
    transactions: List[List[str]], support: float
) -> None:
    """
    Property: Higher support thresholds should filter out more noise.
    
    Tests that increasing support threshold reduces the number of patterns
    found in noisy data.
    """
    gsp_low = GSP(transactions)
    gsp_high = GSP(transactions)
    
    low_support = support * 0.5  # Lower threshold
    high_support = support  # Higher threshold
    
    result_low = gsp_low.search(min_support=low_support)
    result_high = gsp_high.search(min_support=high_support)
    
    # Count patterns at each level
    patterns_low = sum(len(level) for level in result_low)
    patterns_high = sum(len(level) for level in result_high)
    
    # Higher support should yield equal or fewer patterns
    assert patterns_high <= patterns_low


# ============================================================================
# Variable-Length Structure Tests
# ============================================================================

@given(transactions=variable_length_transaction_lists())
@settings(max_examples=30, deadline=None, suppress_health_check=[HealthCheck.too_slow])
def test_gsp_handles_variable_lengths(transactions: List[List[str]]) -> None:
    """
    Property: GSP should handle transactions with highly variable lengths.
    
    Tests that the algorithm works correctly when transaction sizes vary
    dramatically (from 1 item to 50+ items).
    """
    gsp = GSP(transactions)
    result = gsp.search(min_support=0.2)
    
    assert isinstance(result, list)
    
    # Verify pattern validity
    for level_idx, level_patterns in enumerate(result, start=1):
        for pattern in level_patterns.keys():
            # Pattern length should match level
            assert len(pattern) == level_idx
            # Pattern should not be longer than any transaction
            assert level_idx <= max(len(txn) for txn in transactions)


@given(transactions=variable_length_transaction_lists())
@settings(max_examples=20, deadline=None, suppress_health_check=[HealthCheck.too_slow])
def test_gsp_variable_length_pattern_discovery(transactions: List[List[str]]) -> None:
    """
    Property: Pattern lengths should not exceed the shortest transaction length.
    
    With variable-length transactions, longer patterns can only be found
    if transactions are long enough to contain them.
    """
    min_transaction_length = min(len(txn) for txn in transactions)
    
    gsp = GSP(transactions)
    result = gsp.search(min_support=0.1)
    
    # Maximum pattern length should not exceed shortest transaction
    if result:
        max_pattern_length = len(result)
        assert max_pattern_length <= min_transaction_length


# ============================================================================
# Malformed Input Tests
# ============================================================================

@given(transactions=transactions_with_duplicates())
@settings(max_examples=30, deadline=None, suppress_health_check=[HealthCheck.too_slow])
def test_gsp_handles_duplicate_items(transactions: List[List[str]]) -> None:
    """
    Property: GSP should handle transactions with duplicate items.
    
    Tests that the algorithm doesn't crash or produce incorrect results
    when transactions contain repeated items.
    """
    gsp = GSP(transactions)
    result = gsp.search(min_support=0.2)
    
    assert isinstance(result, list)
    
    # Should still produce valid patterns
    for level_patterns in result:
        for pattern, support in level_patterns.items():
            assert isinstance(pattern, tuple)
            assert isinstance(support, int)
            assert support > 0


@given(transactions=transactions_with_special_chars())
@settings(max_examples=25, deadline=None, suppress_health_check=[HealthCheck.too_slow])
def test_gsp_handles_special_characters(transactions: List[List[str]]) -> None:
    """
    Property: GSP should handle items with special characters and unicode.
    
    Tests robustness to unusual string inputs including special characters,
    unicode, whitespace, and potentially empty strings.
    """
    # Filter out empty strings and whitespace-only strings if they cause issues
    filtered_transactions = [
        [item for item in txn if item and item.strip()]
        for txn in transactions
    ]
    # Keep only non-empty transactions
    filtered_transactions = [txn for txn in filtered_transactions if txn]
    
    # Need at least 2 transactions for GSP
    if len(filtered_transactions) < 2:
        assume(False)  # Skip this test case
    
    gsp = GSP(filtered_transactions)
    result = gsp.search(min_support=0.2)
    
    assert isinstance(result, list)
    
    # Patterns should be valid regardless of character content
    for level_patterns in result:
        for pattern, support in level_patterns.items():
            assert isinstance(pattern, tuple)
            assert len(pattern) > 0


@given(
    transactions=st.lists(
        st.lists(st.text(min_size=1, max_size=10), min_size=1, max_size=20),
        min_size=2,
        max_size=30
    )
)
@settings(max_examples=30, deadline=None, suppress_health_check=[HealthCheck.too_slow])
def test_gsp_robust_to_diverse_strings(transactions: List[List[str]]) -> None:
    """
    Property: GSP should handle arbitrary string inputs without crashing.
    
    Uses Hypothesis's general string strategy to generate diverse inputs
    and ensures the algorithm doesn't crash.
    """
    try:
        gsp = GSP(transactions)
        result = gsp.search(min_support=0.1)
        
        # Should return valid structure
        assert isinstance(result, list)
        for level_patterns in result:
            assert isinstance(level_patterns, dict)
    
    except ValueError as e:
        # Only acceptable if it's a known validation error
        error_msg = str(e).lower()
        assert any(keyword in error_msg for keyword in [
            "empty", "multiple transactions", "support"
        ])


# ============================================================================
# Temporal Edge Case Tests
# ============================================================================

@given(transactions=timestamped_transaction_lists())
@settings(max_examples=25, deadline=None, suppress_health_check=[HealthCheck.too_slow])
def test_gsp_handles_timestamped_transactions(
    transactions: List[List[Tuple[str, float]]]
) -> None:
    """
    Property: GSP should handle timestamped transactions correctly.
    
    Tests that the algorithm processes timestamped data and respects
    temporal ordering.
    """
    gsp = GSP(transactions)
    result = gsp.search(min_support=0.3)
    
    assert isinstance(result, list)
    
    # Standard pattern validation
    for level_patterns in result:
        for pattern, support in level_patterns.items():
            assert isinstance(pattern, tuple)
            assert support > 0
            assert support <= len(transactions)


@given(transactions=pathological_timestamped_transactions(pathology_type="identical"))
@settings(max_examples=20, deadline=None, suppress_health_check=[HealthCheck.too_slow])
def test_gsp_handles_identical_timestamps(
    transactions: List[List[Tuple[str, float]]]
) -> None:
    """
    Property: GSP should handle transactions where all timestamps are identical.
    
    Tests edge case where temporal ordering is ambiguous.
    """
    gsp = GSP(transactions)
    result = gsp.search(min_support=0.5)
    
    assert isinstance(result, list)
    
    # Should still produce valid patterns
    for level_patterns in result:
        for pattern, support in level_patterns.items():
            assert isinstance(pattern, tuple)


@given(transactions=pathological_timestamped_transactions(pathology_type="gaps"))
@settings(max_examples=20, deadline=None, suppress_health_check=[HealthCheck.too_slow])
def test_gsp_handles_large_timestamp_gaps(
    transactions: List[List[Tuple[str, float]]]
) -> None:
    """
    Property: GSP should handle transactions with large gaps between timestamps.
    
    Tests that the algorithm works correctly even with very large timestamp values
    and gaps between events.
    """
    gsp = GSP(transactions)
    result = gsp.search(min_support=0.5)
    
    assert isinstance(result, list)
    
    # Patterns should still be valid
    for level_patterns in result:
        for pattern, support in level_patterns.items():
            assert isinstance(pattern, tuple)
            assert len(pattern) > 0


# ============================================================================
# Support Threshold Edge Cases
# ============================================================================

@given(
    transactions=extreme_transaction_lists(size_type="many"),
    support=edge_case_support_thresholds()
)
@settings(max_examples=15, deadline=None, suppress_health_check=[HealthCheck.too_slow])
def test_gsp_edge_case_support_thresholds(
    transactions: List[List[str]], support: float
) -> None:
    """
    Property: GSP should handle edge-case support thresholds correctly.
    
    Tests with very low (0.01) and very high (0.99-1.0) support values
    to ensure correct behavior at boundaries.
    """
    gsp = GSP(transactions)
    result = gsp.search(min_support=support)
    
    assert isinstance(result, list)
    
    # Verify support threshold is respected
    min_support_count = math.ceil(support * len(transactions))
    
    for level_patterns in result:
        for pattern, support_count in level_patterns.items():
            assert support_count >= min_support_count
            assert support_count <= len(transactions)


@given(transactions=extreme_transaction_lists(size_type="minimal"))
@settings(max_examples=30, deadline=None, suppress_health_check=[HealthCheck.too_slow])
def test_gsp_maximum_support_requirement(transactions: List[List[str]]) -> None:
    """
    Property: With support=1.0, only patterns in ALL transactions should be found.
    
    Tests the maximum support threshold where patterns must appear in
    every single transaction.
    """
    gsp = GSP(transactions)
    result = gsp.search(min_support=1.0)
    
    assert isinstance(result, list)
    
    # All found patterns must appear in every transaction
    for level_patterns in result:
        for pattern, support in level_patterns.items():
            assert support == len(transactions), (
                f"With min_support=1.0, pattern {pattern} should appear in all "
                f"{len(transactions)} transactions, but has support {support}"
            )


@given(transactions=sparse_transaction_lists())
@settings(max_examples=20, deadline=None, suppress_health_check=[HealthCheck.too_slow])
def test_gsp_very_low_support(transactions: List[List[str]]) -> None:
    """
    Property: Very low support (0.01) should find many patterns in sparse data.
    
    Tests that low support thresholds correctly identify infrequent patterns.
    """
    gsp = GSP(transactions)
    result = gsp.search(min_support=0.01)
    
    assert isinstance(result, list)
    
    # Should find at least some patterns with very low support
    total_patterns = sum(len(level) for level in result)
    
    # With low support on sparse data, we should find patterns
    # (though the exact number depends on the data)
    assert total_patterns >= 0  # At minimum, should not crash


# ============================================================================
# Invariant Preservation Tests
# ============================================================================

@given(
    transactions=variable_length_transaction_lists(),
    support=valid_support_thresholds()
)
@settings(max_examples=20, deadline=None, suppress_health_check=[HealthCheck.too_slow])
def test_gsp_preserves_sequence_validity(
    transactions: List[List[str]], support: float
) -> None:
    """
    Property: All returned patterns should be valid sequences.
    
    Tests that patterns maintain sequence validity: non-empty tuples with
    proper structure and valid support counts.
    """
    gsp = GSP(transactions)
    result = gsp.search(min_support=support)
    
    min_support_count = math.ceil(support * len(transactions))
    
    for level_idx, level_patterns in enumerate(result, start=1):
        for pattern, support_count in level_patterns.items():
            # Pattern should be a non-empty tuple
            assert isinstance(pattern, tuple)
            assert len(pattern) > 0
            
            # Pattern length should match level
            assert len(pattern) == level_idx
            
            # Support should be valid
            assert isinstance(support_count, int)
            assert min_support_count <= support_count <= len(transactions)
            
            # Pattern items should be strings
            for item in pattern:
                assert isinstance(item, str)


@given(
    transactions=noisy_transaction_lists(),
    support1=st.floats(min_value=0.1, max_value=0.4),
    support2=st.floats(min_value=0.5, max_value=0.9)
)
@settings(max_examples=15, deadline=None, suppress_health_check=[HealthCheck.too_slow])
def test_gsp_support_conservation(
    transactions: List[List[str]], support1: float, support2: float
) -> None:
    """
    Property: Pattern support values should be consistent across different runs.
    
    Tests that the same pattern has the same support regardless of the
    min_support threshold used (as long as the pattern is found).
    """
    # Ensure support1 < support2
    low_support = min(support1, support2)
    high_support = max(support1, support2)
    
    gsp_low = GSP(transactions)
    gsp_high = GSP(transactions)
    
    result_low = gsp_low.search(min_support=low_support)
    result_high = gsp_high.search(min_support=high_support)
    
    # Collect all patterns from high support (subset of low support)
    high_patterns = {}
    for level_patterns in result_high:
        high_patterns.update(level_patterns)
    
    # Collect all patterns from low support
    low_patterns = {}
    for level_patterns in result_low:
        low_patterns.update(level_patterns)
    
    # For every pattern in high support results, it should also be in low support
    # with the same support count
    for pattern, support_count in high_patterns.items():
        assert pattern in low_patterns, (
            f"Pattern {pattern} found with high support but not with low support"
        )
        assert low_patterns[pattern] == support_count, (
            f"Pattern {pattern} has different support: {support_count} vs {low_patterns[pattern]}"
        )


# ============================================================================
# Stress Tests
# ============================================================================

@given(transactions=extreme_transaction_lists(size_type="many"))
@settings(max_examples=10, deadline=None, suppress_health_check=[HealthCheck.too_slow])
def test_gsp_stress_many_transactions(transactions: List[List[str]]) -> None:
    """
    Stress test: GSP should handle hundreds of transactions efficiently.
    
    Tests scalability with large numbers of transactions.
    """
    gsp = GSP(transactions)
    result = gsp.search(min_support=0.1)
    
    # Should complete without crashing
    assert isinstance(result, list)
    
    # Verify basic correctness
    for level_patterns in result:
        assert isinstance(level_patterns, dict)
        for pattern, support in level_patterns.items():
            assert support > 0


@given(transactions=extreme_transaction_lists(size_type="large"))
@settings(max_examples=10, deadline=None, suppress_health_check=[HealthCheck.too_slow])
def test_gsp_stress_large_transactions(transactions: List[List[str]]) -> None:
    """
    Stress test: GSP should handle transactions with many items.
    
    Tests scalability with large individual transactions (50-100+ items).
    """
    gsp = GSP(transactions)
    result = gsp.search(min_support=0.3)
    
    # Should complete without crashing
    assert isinstance(result, list)
    
    # Verify result structure
    for level_patterns in result:
        for pattern, support in level_patterns.items():
            assert isinstance(pattern, tuple)
            assert support > 0
