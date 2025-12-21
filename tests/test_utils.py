"""
Test suite for utility functions in the utils module.

This module tests the following functions:
1. `split_into_batches`: Ensures a list of items is properly split into smaller batches for efficient processing.
2. `is_subsequence_in_list`: Validates the detection of subsequences within a given list.
3. `generate_joined_candidates`: Tests the logic for generating candidate sequences by joining frequent patterns.

Each function is tested for standard cases, edge cases, and error handling to ensure robustness.
"""

from typing import Dict, List, Tuple

from gsppy.utils import split_into_batches, is_subsequence_in_list, generate_candidates_from_previous


def test_split_into_batches():
    """
    Test the `split_into_batches` utility function.
    """
    # Test with exact batches
    items = [("1",), ("2",), ("3",), ("4",), ("5",)]
    batch_size = 2
    result = list(split_into_batches(items, batch_size))
    assert result == [[("1",), ("2",)], [("3",), ("4",)], [("5",)]], "Failed exact batch split"

    # Test with a batch size greater than the number of items
    batch_size = 10
    result = list(split_into_batches(items, batch_size))
    assert result == [items], "Failed large batch size handling"

    # Test with batch size of 1
    batch_size = 1
    result = list(split_into_batches(items, batch_size))
    assert result == [[("1",)], [("2",)], [("3",)], [("4",)], [("5",)]], "Failed batch size of 1"

    # Test empty input
    items: List[Tuple[str]] = []
    batch_size = 3
    result = list(split_into_batches(items, batch_size))
    assert not result, "Failed empty input"


def test_is_subsequence_in_list():
    """
    Test the `is_subsequence_in_list` utility function.
    """
    # Test when the subsequence is present (contiguous)
    assert is_subsequence_in_list((1, 2), (0, 1, 2, 3)), "Failed to find contiguous subsequence"
    assert is_subsequence_in_list((3,), (0, 1, 2, 3)), "Failed single-element subsequence"

    # Test when the subsequence is present (non-contiguous)
    assert is_subsequence_in_list((1, 3), (0, 1, 2, 3)), "Failed to find non-contiguous subsequence"
    assert is_subsequence_in_list((0, 2), (0, 1, 2, 3)), "Failed to find non-contiguous subsequence"
    assert is_subsequence_in_list((0, 3), (0, 1, 2, 3)), "Failed to find non-contiguous subsequence"

    # Test when the subsequence is not present (wrong order or missing elements)
    assert not is_subsequence_in_list((3, 1), (0, 1, 2, 3)), "Incorrectly found reversed subsequence"
    assert not is_subsequence_in_list((4,), (0, 1, 2, 3)), "Incorrectly found non-existent subsequence"
    assert not is_subsequence_in_list((2, 1), (0, 1, 2, 3)), "Incorrectly found out-of-order subsequence"

    # Test when input sequence or subsequence is empty
    assert not is_subsequence_in_list((), (0, 1, 2, 3)), "Incorrect positive result for empty subsequence"
    assert not is_subsequence_in_list((1,), ()), "Incorrect positive result for empty sequence"

    # Test when subsequence length exceeds sequence
    assert not is_subsequence_in_list((1, 2, 3, 4), (1, 2, 3)), "Failed to reject long subsequence"


def test_is_subsequence_contiguous_vs_non_contiguous():
    """
    Test cases that demonstrate the difference between contiguous and non-contiguous matching.

    The current implementation uses non-contiguous (ordered) matching.
    This test documents patterns that would differ between the two approaches.
    """
    # Pattern that appears with gaps (non-contiguous)
    # In contiguous mode: would NOT match
    # In non-contiguous mode: DOES match
    assert is_subsequence_in_list(("a", "c"), ("a", "b", "c")), (
        "Non-contiguous: ('a', 'c') should match in ('a', 'b', 'c')"
    )
    assert is_subsequence_in_list(("a", "d"), ("a", "b", "c", "d")), (
        "Non-contiguous: ('a', 'd') should match in ('a', 'b', 'c', 'd')"
    )
    assert is_subsequence_in_list((1, 4), (1, 2, 3, 4, 5)), (
        "Non-contiguous: (1, 4) should match in (1, 2, 3, 4, 5)"
    )

    # Pattern that appears contiguously (would match in both modes)
    assert is_subsequence_in_list(("a", "b"), ("a", "b", "c")), (
        "Contiguous: ('a', 'b') should match in ('a', 'b', 'c')"
    )
    assert is_subsequence_in_list((2, 3), (1, 2, 3, 4)), (
        "Contiguous: (2, 3) should match in (1, 2, 3, 4)"
    )

    # Pattern with wrong order (would NOT match in either mode)
    assert not is_subsequence_in_list(("c", "a"), ("a", "b", "c")), (
        "Wrong order: ('c', 'a') should NOT match in ('a', 'b', 'c')"
    )
    assert not is_subsequence_in_list((3, 1), (1, 2, 3, 4)), (
        "Wrong order: (3, 1) should NOT match in (1, 2, 3, 4)"
    )


def test_is_subsequence_with_gaps():
    """
    Test non-contiguous matching with various gap sizes.
    """
    # Small gap
    assert is_subsequence_in_list(("x", "z"), ("x", "y", "z")), "Failed with 1 element gap"

    # Medium gap
    assert is_subsequence_in_list(("a", "e"), ("a", "b", "c", "d", "e")), "Failed with 3 element gap"

    # Large gap
    assert is_subsequence_in_list((1, 10), (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)), "Failed with 8 element gap"

    # Multiple gaps in longer pattern
    assert is_subsequence_in_list((1, 3, 5), (1, 2, 3, 4, 5)), "Failed with multiple gaps"
    assert is_subsequence_in_list(("a", "c", "e"), ("a", "b", "c", "d", "e")), "Failed with multiple gaps"

    # No gap (adjacent elements still work)
    assert is_subsequence_in_list((1, 2), (1, 2, 3)), "Failed with no gap (contiguous)"


def test_generate_candidates_from_previous():
    """
    Test the `generate_candidates_from_previous` utility function.
    """
    # Test if candidates are generated correctly
    prev_patterns = {
        ("1", "2"): 3,
        ("2", "3"): 4,
        ("3", "4"): 5,
        ("1", "3"): 2,  # Non-joinable with others as a k-1 match
    }
    result = set(generate_candidates_from_previous(prev_patterns))

    # Expected candidates: joining ("1", "2") with ("2", "3") and ("2", "3") with ("3", "4")
    expected = {("1", "2", "3"), ("2", "3", "4")}
    assert expected.issubset(result), f"Missing expected candidates. Got {result}, expected at least {expected}"

    # Test with no joinable patterns
    prev_patterns = {("1",): 3, ("2",): 4}
    result = set(generate_candidates_from_previous(prev_patterns))

    # For single-element disjoint patterns, candidates may still be generated but GSP will filter later
    assert result == {("1", "2"), ("2", "1")}, f"Unexpected disjoint candidates. Got {result}"

    # Test with empty patterns
    prev_patterns: Dict[Tuple[str, ...], int] = {}
    result = set(generate_candidates_from_previous(prev_patterns))
    assert result == set(), f"Failed empty input handling. Got {result}"
