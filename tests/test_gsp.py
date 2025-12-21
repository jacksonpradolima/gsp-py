"""
Unit tests for the GSP (Generalized Sequential Pattern) algorithm.

This module contains tests for various scenarios including edge cases,
benchmarking, and normal use cases of the GSP algorithm. The tests use
`pytest` for assertions and include fixtures for reusable data.

Tests include:
- Empty transactions.
- Single transaction.
- High minimum support filtering.
- Typical supermarket transactions with known frequent patterns.
- Randomly generated transactions for flexibility.
- Large transactions with repetitive items.
- Partial matches and benchmarking.

Author: Jackson Antonio do Prado Lima
Email: jacksonpradolima@gmail.com
"""

import re
import random
from typing import List

import pytest
from pytest_benchmark.fixture import BenchmarkFixture  # type: ignore

from gsppy.gsp import GSP


@pytest.fixture
def supermarket_transactions() -> List[List[str]]:
    """
    Fixture to provide a dataset representing supermarket transactions.

    Returns:
        list: A list of transactions, where each transaction is a list of items.
    """
    return [
        ["Bread", "Milk"],
        ["Bread", "Diaper", "Beer", "Eggs"],
        ["Milk", "Diaper", "Beer", "Coke"],
        ["Bread", "Milk", "Diaper", "Beer"],
        ["Bread", "Milk", "Diaper", "Coke"],
    ]


@pytest.fixture
def random_transactions() -> List[List[str]]:
    """
    Fixture to generate a random dataset of transactions.

    Returns:
        list: A list of transactions with random items and varying lengths.
    """
    return [[random.choice(["A", "B", "C", "D", "E"]) for _ in range(random.randint(2, 10))] for _ in range(100)]


def test_empty_transactions() -> None:
    """
    Test the GSP algorithm with an empty dataset.

    Asserts:
        - A ValueError is raised indicating that the dataset is empty.
    """
    transactions: List[List[str]] = []
    with pytest.raises(ValueError, match="Input transactions are empty"):
        GSP(transactions)


def test_single_transaction() -> None:
    """
    Test the GSP algorithm with a single transaction.

    Asserts:
        - A ValueError is raised indicating that GSP requires multiple transactions.
    """
    transactions = [["A", "B", "C"]]
    with pytest.raises(ValueError, match="GSP requires multiple transactions"):
        GSP(transactions)


@pytest.mark.parametrize(
    "min_support, expected_error",
    [
        (-0.1, re.escape("Minimum support must be in the range (0.0, 1.0]")),
        (0.0, re.escape("Minimum support must be in the range (0.0, 1.0]")),
        (1.1, re.escape("Minimum support must be in the range (0.0, 1.0]")),
    ],
)
def test_invalid_min_support(
    supermarket_transactions: List[List[str]], min_support: float, expected_error: str
) -> None:
    """
    Test the GSP algorithm with invalid minimum support values.

    Asserts:
        - A ValueError is raised if the min_support is outside the valid range.
    """
    gsp = GSP(supermarket_transactions)
    with pytest.raises(ValueError, match=expected_error):
        gsp.search(min_support=min_support)


def test_valid_min_support_edge(supermarket_transactions: List[List[str]]) -> None:
    """
    Test the GSP algorithm with a valid edge value for min_support.

    Asserts:
        - The algorithm runs successfully when min_support is set to 1.0.
    """
    gsp = GSP(supermarket_transactions)
    result = gsp.search(min_support=1.0)  # Only patterns supported by ALL transactions should remain
    assert not result, "Expected no frequent patterns with min_support = 1.0"


def test_min_support_valid(supermarket_transactions: List[List[str]]) -> None:
    """
    Test the GSP algorithm with a minimum support set just above 0.0.

    Asserts:
        - Frequent patterns are generated correctly for a low min_support threshold.
    """
    gsp = GSP(supermarket_transactions)
    result = gsp.search(min_support=0.2)  # At least 1 transaction should support the pattern

    # All items should appear as 1-item patterns
    level_1_patterns = {("Bread",), ("Milk",), ("Diaper",), ("Beer",), ("Coke",), ("Eggs",)}
    result_level_1 = set(result[0].keys())  # Extract patterns from Level 1

    assert result_level_1 == level_1_patterns, f"Level 1 patterns mismatch. Got {result_level_1}"


def test_no_frequent_items(supermarket_transactions: List[List[str]]) -> None:
    """
    Test the GSP algorithm with a high minimum support value.

    Asserts:
        - The result should be an empty list due to filtering out all items.
    """
    gsp = GSP(supermarket_transactions)
    result = gsp.search(min_support=0.9)  # High minimum support
    assert not result, "High minimum support should filter out all items."


def test_worker_batch_static_method(supermarket_transactions: List[List[str]]) -> None:
    """
    Test the _worker_batch method directly for checkpoint validation.

    Asserts:
        - Candidates below the minimum support are filtered out.
        - Candidates meeting the minimum support are returned with correct counts.
    """
    batch = [("Bread",), ("Milk",), ("Diaper",), ("Eggs",)]  # 1-sequence candidates
    transactions = [tuple(t) for t in supermarket_transactions]
    min_support = 3  # Absolute support count
    expected = [(("Bread",), 4), (("Milk",), 4), (("Diaper",), 4)]

    # Call the '_worker_batch' method
    # This test accesses `_worker_batch` to test internal functionality
    results = GSP._worker_batch(batch, transactions, min_support)  # pylint: disable=protected-access
    assert results == expected, f"Expected results {expected}, but got {results}"


def test_frequent_patterns(supermarket_transactions: List[List[str]]) -> None:
    """
    Test the GSP algorithm with supermarket transactions and a realistic minimum support.

    Asserts:
        - The frequent patterns should match the expected result.
        - Non-contiguous patterns are correctly detected.
    """
    gsp = GSP(supermarket_transactions)
    result = gsp.search(min_support=0.3)
    expected = [
        {("Bread",): 4, ("Milk",): 4, ("Diaper",): 4, ("Beer",): 3, ("Coke",): 2},
        {
            ("Bread", "Milk"): 3,
            ("Bread", "Diaper"): 3,
            ("Bread", "Beer"): 2,
            ("Milk", "Diaper"): 3,
            ("Milk", "Beer"): 2,
            ("Milk", "Coke"): 2,
            ("Diaper", "Beer"): 3,
            ("Diaper", "Coke"): 2,
        },
        {
            ("Bread", "Milk", "Diaper"): 2,
            ("Bread", "Diaper", "Beer"): 2,
            ("Milk", "Diaper", "Beer"): 2,
            ("Milk", "Diaper", "Coke"): 2,
        },
    ]
    assert result == expected, "Frequent patterns do not match expected results."


def test_random_transactions(random_transactions: List[List[str]]) -> None:
    """
    Test the GSP algorithm with a random dataset.

    Asserts:
        - The result should contain some frequent patterns with a low minimum support.
    """
    gsp = GSP(random_transactions)
    result = gsp.search(min_support=0.1)  # Low support to ensure some patterns emerge
    assert len(result) > 0, "Random transactions should yield some frequent patterns with low min_support."


def test_large_transactions() -> None:
    """
    Test the GSP algorithm with a large single transaction.

    Asserts:
        - A ValueError is raised indicating that GSP requires multiple transactions.
    """
    transactions = [["A"] * 1000]  # Single transaction with 1000 identical items
    with pytest.raises(ValueError, match="GSP requires multiple transactions to find meaningful patterns."):
        GSP(transactions)


def test_partial_match(supermarket_transactions: List[List[str]]) -> None:
    """
    Test the GSP algorithm with additional partial matches.

    Asserts:
        - Frequent patterns are generated correctly for the given transactions.
    """
    transactions = supermarket_transactions + [["Diaper", "Milk"]]
    gsp = GSP(transactions)
    result = gsp.search(min_support=0.3)  # Adjusted minimum support to match more patterns

    # Debug output to inspect generated frequent patterns
    print("Generated frequent patterns:", result)

    # Check for the presence of valid frequent patterns
    expected_patterns_level_1 = {("Bread",), ("Milk",), ("Diaper",), ("Beer",)}
    expected_patterns_level_2 = {("Bread", "Milk"), ("Milk", "Diaper"), ("Diaper", "Beer")}

    # Convert results to sets for easier comparison
    result_level_1 = set(result[0].keys())
    assert result_level_1 >= expected_patterns_level_1, f"Level 1 patterns mismatch. Got {result_level_1}"

    # Add a condition to avoid IndexError for empty results
    if len(result) > 1:
        result_level_2 = set(result[1].keys())
        assert result_level_2 >= expected_patterns_level_2, f"Level 2 patterns mismatch. Got {result_level_2}"


def test_non_contiguous_subsequences() -> None:
    """
    Test the GSP algorithm correctly detects non-contiguous subsequences (Issue #115).

    This test validates that patterns like ('a', 'c') are detected even when
    they appear with gaps in sequences like ['a', 'b', 'c'].

    Asserts:
        - Non-contiguous patterns are correctly identified with proper support.
    """
    sequences = [
        ["a", "b", "c"],
        ["a", "c"],
        ["b", "c", "a"],
        ["a", "b", "c", "d"],
    ]

    gsp = GSP(sequences)
    result = gsp.search(min_support=0.5)

    # Expected: ('a', 'c') should be found with support = 3
    # It appears in: ['a', 'b', 'c'], ['a', 'c'], ['a', 'b', 'c', 'd']
    assert len(result) >= 2, "Expected at least 2 levels of patterns"

    level_2_patterns = result[1]
    assert ("a", "c") in level_2_patterns, f"Pattern ('a', 'c') not found in level 2. Got {level_2_patterns}"
    assert level_2_patterns[("a", "c")] == 3, f"Expected support 3 for ('a', 'c'), got {level_2_patterns[('a', 'c')]}"


def test_contiguous_vs_non_contiguous_patterns() -> None:
    """
    Comprehensive test demonstrating the difference between contiguous and non-contiguous patterns.

    This test shows patterns that would ONLY be found in non-contiguous matching (current implementation)
    vs patterns that would be found in BOTH contiguous and non-contiguous matching.

    The current implementation uses non-contiguous (ordered) matching, which is the standard GSP behavior.
    """
    sequences = [
        ["X", "Y", "Z"],  # Contains X->Y, Y->Z, X->Z (contiguous: X->Y, Y->Z only)
        ["X", "Z"],  # Contains X->Z (contiguous: X->Z)
        ["Y", "Z", "X"],  # Contains Y->Z, Y->X, Z->X (contiguous: Y->Z, Z->X only)
        ["X", "Y", "Z", "W"],  # Contains many patterns
    ]

    gsp = GSP(sequences)
    result = gsp.search(min_support=0.5)  # Need at least 2/4 sequences

    # Level 2 patterns
    level_2_patterns = result[1] if len(result) >= 2 else {}

    # Patterns that would be found in BOTH contiguous and non-contiguous:
    # ('X', 'Y') appears contiguously in: ['X', 'Y', 'Z'], ['X', 'Y', 'Z', 'W']
    # ('Y', 'Z') appears contiguously in: ['X', 'Y', 'Z'], ['Y', 'Z', 'X'], ['X', 'Y', 'Z', 'W']
    assert ("X", "Y") in level_2_patterns, "('X', 'Y') should be found (contiguous in 2 sequences)"
    assert ("Y", "Z") in level_2_patterns, "('Y', 'Z') should be found (contiguous in 3 sequences)"

    # Pattern that would ONLY be found in non-contiguous matching:
    # ('X', 'Z') appears with gap in: ['X', 'Y', 'Z'], ['X', 'Y', 'Z', 'W']
    # and contiguously in: ['X', 'Z']
    # Total support = 3 (>= 2 threshold)
    assert ("X", "Z") in level_2_patterns, (
        "('X', 'Z') should be found with non-contiguous matching. "
        "This pattern has gaps in some sequences but is still ordered."
    )
    assert level_2_patterns[("X", "Z")] == 3, f"Expected support 3 for ('X', 'Z'), got {level_2_patterns[('X', 'Z')]}"


def test_non_contiguous_with_longer_gaps() -> None:
    """
    Test non-contiguous matching with longer gaps between elements.

    This demonstrates that the algorithm correctly finds patterns even when
    there are multiple elements between the pattern elements.
    """
    sequences = [
        ["A", "B", "C", "D", "E"],  # Contains A->E with 3 elements in between
        ["A", "X", "Y", "Z", "E"],  # Contains A->E with 3 different elements in between
        ["A", "E"],  # Contains A->E with no gap
        ["E", "A"],  # Does NOT contain A->E (wrong order)
    ]

    gsp = GSP(sequences)
    result = gsp.search(min_support=0.5)  # Need at least 2/4 sequences

    # ('A', 'E') should be found with support = 3
    level_2_patterns = result[1] if len(result) >= 2 else {}
    assert ("A", "E") in level_2_patterns, "('A', 'E') should be found despite large gaps"
    assert level_2_patterns[("A", "E")] == 3, f"Expected support 3 for ('A', 'E'), got {level_2_patterns[('A', 'E')]}"

    # ('E', 'A') should NOT be found (wrong order)
    assert ("E", "A") not in level_2_patterns, "('E', 'A') should not be found (wrong order)"


def test_order_sensitivity() -> None:
    """
    Test that the algorithm is sensitive to order - patterns must appear in sequence order.

    This verifies that even with non-contiguous matching, the order of elements matters.
    """
    sequences = [
        ["P", "Q", "R"],  # Contains P->Q, P->R, Q->R
        ["P", "R", "Q"],  # Contains P->R, P->Q, R->Q
        ["Q", "P", "R"],  # Contains Q->P, Q->R, P->R
        ["R", "Q", "P"],  # Contains R->Q, R->P, Q->P
    ]

    gsp = GSP(sequences)
    result = gsp.search(min_support=0.5)  # Need at least 2/4 sequences

    level_2_patterns = result[1] if len(result) >= 2 else {}

    # ('P', 'R') appears in correct order in: ['P', 'Q', 'R'], ['P', 'R', 'Q'], ['Q', 'P', 'R']
    assert ("P", "R") in level_2_patterns, "('P', 'R') should be found (support = 3)"
    assert level_2_patterns[("P", "R")] == 3

    # ('Q', 'P') appears in correct order in: ['Q', 'P', 'R'], ['R', 'Q', 'P']
    assert ("Q", "P") in level_2_patterns, "('Q', 'P') should be found (support = 2)"
    assert level_2_patterns[("Q", "P")] == 2

    # ('R', 'P') appears in correct order in: ['R', 'Q', 'P']
    # Support = 1, below threshold of 2
    assert ("R", "P") not in level_2_patterns, "('R', 'P') should not be found (support = 1, below threshold)"


@pytest.mark.parametrize("min_support", [0.1, 0.2, 0.3, 0.4, 0.5])
def test_benchmark(benchmark: BenchmarkFixture, supermarket_transactions: List[List[str]], min_support: float) -> None:
    """
    Benchmark the GSP algorithm's performance using the supermarket dataset.

    Uses:
        pytest-benchmark: To measure execution time.
    """
    gsp = GSP(supermarket_transactions)
    benchmark(gsp.search, min_support=min_support)
