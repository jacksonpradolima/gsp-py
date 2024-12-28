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
    # Test when the subsequence is present
    assert is_subsequence_in_list((1, 2), (0, 1, 2, 3)), "Failed to find subsequence"
    assert is_subsequence_in_list((3,), (0, 1, 2, 3)), "Failed single-element subsequence"

    # Test when the subsequence is not present
    assert not is_subsequence_in_list((1, 3), (0, 1, 2, 3)), "Incorrectly found non-contiguous subsequence"
    assert not is_subsequence_in_list((4,), (0, 1, 2, 3)), "Incorrectly found non-existent subsequence"

    # Test when input sequence or subsequence is empty
    assert not is_subsequence_in_list((), (0, 1, 2, 3)), "Incorrect positive result for empty subsequence"
    assert not is_subsequence_in_list((1,), ()), "Incorrect positive result for empty sequence"

    # Test when subsequence length exceeds sequence
    assert not is_subsequence_in_list((1, 2, 3, 4), (1, 2, 3)), "Failed to reject long subsequence"


def test_generate_candidates_from_previous():
    """
    Test the `generate_candidates_from_previous` utility function.
    """
    # Test if candidates are generated correctly
    prev_patterns = {
        ("1", "2"): 3,
        ("2", "3"): 4,
        ("3", "4"): 5,
        ("1", "3"): 2  # Non-joinable with others as a k-1 match
    }
    result = set(generate_candidates_from_previous(prev_patterns))

    # Expected candidates: joining ("1", "2") with ("2", "3") and ("2", "3") with ("3", "4")
    expected = {("1", "2", "3"), ("2", "3", "4")}
    assert expected.issubset(result), f"Missing expected candidates. Got {result}, expected at least {expected}"

    # Test with no joinable patterns
    prev_patterns = {
        ("1",): 3,
        ("2",): 4
    }
    result = set(generate_candidates_from_previous(prev_patterns))

    # For single-element disjoint patterns, candidates may still be generated but GSP will filter later
    assert result == {("1", "2"), ("2", "1")}, f"Unexpected disjoint candidates. Got {result}"

    # Test with empty patterns
    prev_patterns: Dict[Tuple[str, ...], int] = {}
    result = set(generate_candidates_from_previous(prev_patterns))
    assert result == set(), f"Failed empty input handling. Got {result}"
