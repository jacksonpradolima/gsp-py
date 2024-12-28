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
        ['Bread', 'Milk'],
        ['Bread', 'Diaper', 'Beer', 'Eggs'],
        ['Milk', 'Diaper', 'Beer', 'Coke'],
        ['Bread', 'Milk', 'Diaper', 'Beer'],
        ['Bread', 'Milk', 'Diaper', 'Coke']
    ]


@pytest.fixture
def random_transactions() -> List[List[str]]:
    """
    Fixture to generate a random dataset of transactions.

    Returns:
        list: A list of transactions with random items and varying lengths.
    """
    return [[random.choice(['A', 'B', 'C', 'D', 'E']) for _ in range(random.randint(2, 10))] for _ in range(100)]


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
    transactions = [['A', 'B', 'C']]
    with pytest.raises(ValueError, match="GSP requires multiple transactions"):
        GSP(transactions)


@pytest.mark.parametrize(
    "min_support, expected_error",
    [
        (-0.1, re.escape("Minimum support must be in the range (0.0, 1.0]")),
        (0.0, re.escape("Minimum support must be in the range (0.0, 1.0]")),
        (1.1, re.escape("Minimum support must be in the range (0.0, 1.0]")),
    ]
)
def test_invalid_min_support(supermarket_transactions: List[List[str]], min_support: float,
                             expected_error: str) -> None:
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
    level_1_patterns = {('Bread',), ('Milk',), ('Diaper',), ('Beer',), ('Coke',), ('Eggs',)}
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
    batch = [('Bread',), ('Milk',), ('Diaper',), ('Eggs',)]  # 1-sequence candidates
    transactions = [tuple(t) for t in supermarket_transactions]
    min_support = 3  # Absolute support count
    expected = [(('Bread',), 4), (('Milk',), 4), (('Diaper',), 4)]

    # Call the '_worker_batch' method
    # This test accesses `_worker_batch` to test internal functionality
    results = GSP._worker_batch(batch, transactions, min_support)  # pylint: disable=protected-access
    assert results == expected, f"Expected results {expected}, but got {results}"


def test_frequent_patterns(supermarket_transactions: List[List[str]]) -> None:
    """
    Test the GSP algorithm with supermarket transactions and a realistic minimum support.

    Asserts:
        - The frequent patterns should match the expected result.
    """
    gsp = GSP(supermarket_transactions)
    result = gsp.search(min_support=0.3)
    expected = [
        {('Bread',): 4, ('Milk',): 4, ('Diaper',): 4, ('Beer',): 3, ('Coke',): 2},
        {('Bread', 'Milk'): 3, ('Milk', 'Diaper'): 3, ('Diaper', 'Beer'): 3},
        {('Bread', 'Milk', 'Diaper'): 2, ('Milk', 'Diaper', 'Beer'): 2}
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
    transactions = [['A'] * 1000]  # Single transaction with 1000 identical items
    with pytest.raises(ValueError, match="GSP requires multiple transactions to find meaningful patterns."):
        GSP(transactions)


def test_partial_match(supermarket_transactions: List[List[str]]) -> None:
    """
    Test the GSP algorithm with additional partial matches.

    Asserts:
        - Frequent patterns are generated correctly for the given transactions.
    """
    transactions = supermarket_transactions + [['Diaper', 'Milk']]
    gsp = GSP(transactions)
    result = gsp.search(min_support=0.3)  # Adjusted minimum support to match more patterns

    # Debug output to inspect generated frequent patterns
    print("Generated frequent patterns:", result)

    # Check for the presence of valid frequent patterns
    expected_patterns_level_1 = {('Bread',), ('Milk',), ('Diaper',), ('Beer',)}
    expected_patterns_level_2 = {('Bread', 'Milk'), ('Milk', 'Diaper'), ('Diaper', 'Beer')}

    # Convert results to sets for easier comparison
    result_level_1 = set(result[0].keys())
    assert result_level_1 >= expected_patterns_level_1, f"Level 1 patterns mismatch. Got {result_level_1}"

    # Add a condition to avoid IndexError for empty results
    if len(result) > 1:
        result_level_2 = set(result[1].keys())
        assert result_level_2 >= expected_patterns_level_2, f"Level 2 patterns mismatch. Got {result_level_2}"


@pytest.mark.parametrize("min_support", [0.1, 0.2, 0.3, 0.4, 0.5])
def test_benchmark(benchmark: BenchmarkFixture, supermarket_transactions: List[List[str]], min_support: float) -> None:
    """
    Benchmark the GSP algorithm's performance using the supermarket dataset.

    Uses:
        pytest-benchmark: To measure execution time.
    """
    gsp = GSP(supermarket_transactions)
    benchmark(gsp.search, min_support=min_support)
