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

import pytest
from gsppy.gsp import GSP

@pytest.fixture
def supermarket_transactions():
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
def random_transactions():
    """
    Fixture to generate a random dataset of transactions.

    Returns:
        list: A list of transactions with random items and varying lengths.
    """
    import random
    return [[random.choice(['A', 'B', 'C', 'D', 'E']) for _ in range(random.randint(2, 10))] for _ in range(100)]


def test_empty_transactions():
    """
    Test the GSP algorithm with an empty dataset.

    Asserts:
        - A ValueError is raised indicating that the dataset is empty.
    """
    transactions = []
    with pytest.raises(ValueError, match="Input transactions are empty"):
        GSP(transactions)


def test_single_transaction():
    """
    Test the GSP algorithm with a single transaction.

    Asserts:
        - A ValueError is raised indicating that GSP requires multiple transactions.
    """
    transactions = [['A', 'B', 'C']]
    with pytest.raises(ValueError, match="GSP requires multiple transactions"):
        GSP(transactions)


def test_no_frequent_items(supermarket_transactions):
    """
    Test the GSP algorithm with a high minimum support value.

    Asserts:
        - The result should be an empty list due to filtering out all items.
    """
    gsp = GSP(supermarket_transactions)
    result = gsp.search(min_support=0.9)  # High minimum support
    assert not result, "High minimum support should filter out all items."


def test_frequent_patterns(supermarket_transactions):
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


def test_random_transactions(random_transactions):
    """
    Test the GSP algorithm with a random dataset.

    Asserts:
        - The result should contain some frequent patterns with a low minimum support.
    """
    gsp = GSP(random_transactions)
    result = gsp.search(min_support=0.1)  # Low support to ensure some patterns emerge
    assert len(result) > 0, "Random transactions should yield some frequent patterns with low min_support."


def test_large_transactions():
    """
    Test the GSP algorithm with a large single transaction.

    Asserts:
        - A ValueError is raised indicating that GSP requires multiple transactions.
    """
    transactions = [['A'] * 1000]  # Single transaction with 1000 identical items
    with pytest.raises(ValueError, match="GSP requires multiple transactions to find meaningful patterns."):
        GSP(transactions)


def test_partial_match(supermarket_transactions):
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
def test_benchmark(benchmark, supermarket_transactions, min_support):
    """
    Benchmark the GSP algorithm's performance using the supermarket dataset.

    Uses:
        pytest-benchmark: To measure execution time.
    """
    gsp = GSP(supermarket_transactions)
    benchmark(gsp.search, min_support=min_support)
