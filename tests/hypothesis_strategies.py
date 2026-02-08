"""
Modular Hypothesis strategies for GSP testing.

This module provides reusable Hypothesis strategies for generating test data
for the GSP (Generalized Sequential Pattern) algorithm. These strategies can be
composed and extended to create comprehensive property-based tests.

The strategies are designed to be:
- Modular: Each strategy focuses on a specific aspect of test data generation
- Composable: Strategies can be combined to create complex test scenarios
- Extensible: New strategies can be added without modifying existing ones

Usage Example:
    ```python
    from hypothesis import given
    from tests.hypothesis_strategies import transaction_lists, extreme_transaction_lists
    
    @given(transactions=transaction_lists())
    def test_gsp_property(transactions):
        gsp = GSP(transactions)
        result = gsp.search(min_support=0.1)
        assert isinstance(result, list)
    ```

Author: Jackson Antonio do Prado Lima
Email: jacksonpradolima@gmail.com
"""

from typing import List, Tuple

from hypothesis import strategies as st

# ============================================================================
# Basic Strategies - Building Blocks
# ============================================================================

@st.composite
def item_strings(
    draw: st.DrawFn,
    min_size: int = 1,
    max_size: int = 3,
    alphabet: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
) -> str:
    """
    Generate simple item strings for transactions.
    
    Args:
        draw: Hypothesis draw function
        min_size: Minimum length of item string
        max_size: Maximum length of item string
        alphabet: Character set to use for items
        
    Returns:
        A string representing an item
    """
    return draw(st.text(
        alphabet=st.characters(whitelist_categories=(), whitelist_characters=alphabet),
        min_size=min_size,
        max_size=max_size
    ))


@st.composite
def item_pool(
    draw: st.DrawFn,
    min_items: int = 2,
    max_items: int = 20,
    item_min_size: int = 1,
    item_max_size: int = 3
) -> List[str]:
    """
    Generate a pool of unique items to choose from for transactions.
    
    Args:
        draw: Hypothesis draw function
        min_items: Minimum number of unique items in the pool
        max_items: Maximum number of unique items in the pool
        item_min_size: Minimum size of each item string
        item_max_size: Maximum size of each item string
        
    Returns:
        A list of unique item strings
    """
    return draw(st.lists(
        item_strings(min_size=item_min_size, max_size=item_max_size),
        min_size=min_items,
        max_size=max_items,
        unique=True
    ))


# ============================================================================
# Standard Transaction Strategies
# ============================================================================

@st.composite
def transaction_lists(
    draw: st.DrawFn,
    min_transactions: int = 2,
    max_transactions: int = 50,
    min_transaction_size: int = 1,
    max_transaction_size: int = 10,
    min_items: int = 2,
    max_items: int = 20
) -> List[List[str]]:
    """
    Generate lists of transactions for standard testing.
    
    This is the primary strategy for general-purpose GSP testing.
    Each transaction is a list of items (strings).
    
    Args:
        draw: Hypothesis draw function
        min_transactions: Minimum number of transactions
        max_transactions: Maximum number of transactions
        min_transaction_size: Minimum items per transaction
        max_transaction_size: Maximum items per transaction
        min_items: Minimum unique items in the item pool
        max_items: Maximum unique items in the item pool
        
    Returns:
        A list of transactions (each transaction is a list of items)
    """
    n_transactions = draw(st.integers(min_value=min_transactions, max_value=max_transactions))
    
    # Generate a pool of items to choose from
    items = draw(item_pool(min_items=min_items, max_items=max_items))
    
    # Generate transactions
    transactions = []
    for _ in range(n_transactions):
        transaction_size = draw(st.integers(
            min_value=min_transaction_size,
            max_value=min(max_transaction_size, len(items))
        ))
        transaction = draw(st.lists(
            st.sampled_from(items),
            min_size=transaction_size,
            max_size=transaction_size
        ))
        transactions.append(transaction)
    
    return transactions


# ============================================================================
# Edge Case Strategies
# ============================================================================

@st.composite
def extreme_transaction_lists(
    draw: st.DrawFn,
    size_type: str = "large"
) -> List[List[str]]:
    """
    Generate extreme transaction lists for stress testing.
    
    Args:
        draw: Hypothesis draw function
        size_type: Type of extreme case - "large", "many", or "minimal"
            - "large": Few transactions with very many items each
            - "many": Many transactions with moderate items each
            - "minimal": Minimal valid input (2 transactions, 1 item each)
            
    Returns:
        A list of transactions with extreme characteristics
    """
    if size_type == "large":
        # Few transactions with many items
        n_transactions = draw(st.integers(min_value=2, max_value=10))
        items = draw(item_pool(min_items=50, max_items=200))
        transactions = []
        for _ in range(n_transactions):
            transaction_size = draw(st.integers(min_value=50, max_value=min(100, len(items))))
            transaction = draw(st.lists(
                st.sampled_from(items),
                min_size=transaction_size,
                max_size=transaction_size
            ))
            transactions.append(transaction)
        return transactions
    
    elif size_type == "many":
        # Many transactions with moderate items
        n_transactions = draw(st.integers(min_value=100, max_value=500))
        items = draw(item_pool(min_items=10, max_items=30))
        transactions = []
        for _ in range(n_transactions):
            transaction_size = draw(st.integers(min_value=2, max_value=min(15, len(items))))
            transaction = draw(st.lists(
                st.sampled_from(items),
                min_size=transaction_size,
                max_size=transaction_size
            ))
            transactions.append(transaction)
        return transactions
    
    else:  # minimal
        # Minimal valid input
        items = draw(item_pool(min_items=1, max_items=3))
        return [
            [draw(st.sampled_from(items))],
            [draw(st.sampled_from(items))]
        ]


@st.composite
def sparse_transaction_lists(
    draw: st.DrawFn,
    min_transactions: int = 10,
    max_transactions: int = 50
) -> List[List[str]]:
    """
    Generate transactions with sparse patterns (low overlap between transactions).
    
    This tests scenarios where most patterns will have low support.
    
    Args:
        draw: Hypothesis draw function
        min_transactions: Minimum number of transactions
        max_transactions: Maximum number of transactions
        
    Returns:
        A list of transactions with low item overlap
    """
    n_transactions = draw(st.integers(min_value=min_transactions, max_value=max_transactions))
    
    # Large item pool to ensure sparsity
    items = draw(item_pool(min_items=50, max_items=100))
    
    transactions = []
    for _ in range(n_transactions):
        # Each transaction uses a small, random subset of items
        transaction_size = draw(st.integers(min_value=1, max_value=5))
        transaction = draw(st.lists(
            st.sampled_from(items),
            min_size=transaction_size,
            max_size=transaction_size,
            unique=True
        ))
        transactions.append(transaction)
    
    return transactions


@st.composite
def noisy_transaction_lists(
    draw: st.DrawFn,
    min_transactions: int = 10,
    max_transactions: int = 50,
    noise_ratio: float = 0.5
) -> List[List[str]]:
    """
    Generate transactions with noisy/random items mixed with frequent patterns.
    
    This creates a dataset where some patterns are frequent but many items are noise.
    
    Args:
        draw: Hypothesis draw function
        min_transactions: Minimum number of transactions
        max_transactions: Maximum number of transactions
        noise_ratio: Approximate ratio of noise items (0.0 to 1.0)
        
    Returns:
        A list of transactions with mixed signal and noise
    """
    n_transactions = draw(st.integers(min_value=min_transactions, max_value=max_transactions))
    
    # Split items into frequent and noise pools
    frequent_items = draw(item_pool(min_items=3, max_items=8))
    noise_items = draw(item_pool(min_items=20, max_items=50))
    
    transactions = []
    for _ in range(n_transactions):
        transaction = []
        
        # Add some frequent items
        n_frequent = draw(st.integers(min_value=1, max_value=len(frequent_items)))
        frequent_sample = draw(st.lists(
            st.sampled_from(frequent_items),
            min_size=n_frequent,
            max_size=n_frequent
        ))
        transaction.extend(frequent_sample)
        
        # Add noise items based on noise_ratio
        if draw(st.floats(min_value=0.0, max_value=1.0)) < noise_ratio:
            n_noise = draw(st.integers(min_value=1, max_value=10))
            noise_sample = draw(st.lists(
                st.sampled_from(noise_items),
                min_size=n_noise,
                max_size=n_noise
            ))
            transaction.extend(noise_sample)
        
        transactions.append(transaction)
    
    return transactions


@st.composite
def variable_length_transaction_lists(
    draw: st.DrawFn,
    min_transactions: int = 10,
    max_transactions: int = 50
) -> List[List[str]]:
    """
    Generate transactions with highly variable lengths.
    
    This tests handling of datasets with inconsistent transaction sizes.
    
    Args:
        draw: Hypothesis draw function
        min_transactions: Minimum number of transactions
        max_transactions: Maximum number of transactions
        
    Returns:
        A list of transactions with varying lengths
    """
    n_transactions = draw(st.integers(min_value=min_transactions, max_value=max_transactions))
    items = draw(item_pool(min_items=5, max_items=30))
    
    transactions = []
    for _ in range(n_transactions):
        # Highly variable transaction sizes
        transaction_size = draw(st.integers(min_value=1, max_value=min(50, len(items))))
        transaction = draw(st.lists(
            st.sampled_from(items),
            min_size=transaction_size,
            max_size=transaction_size
        ))
        transactions.append(transaction)
    
    return transactions


# ============================================================================
# Malformed Input Strategies
# ============================================================================

@st.composite
def transactions_with_duplicates(
    draw: st.DrawFn,
    min_transactions: int = 5,
    max_transactions: int = 20
) -> List[List[str]]:
    """
    Generate transactions that may contain duplicate items within a transaction.
    
    This tests handling of non-unique items within transactions.
    
    Args:
        draw: Hypothesis draw function
        min_transactions: Minimum number of transactions
        max_transactions: Maximum number of transactions
        
    Returns:
        A list of transactions potentially containing duplicate items
    """
    n_transactions = draw(st.integers(min_value=min_transactions, max_value=max_transactions))
    items = draw(item_pool(min_items=3, max_items=10))
    
    transactions = []
    for _ in range(n_transactions):
        transaction_size = draw(st.integers(min_value=1, max_value=20))
        # Allow duplicates by not using unique=True
        transaction = draw(st.lists(
            st.sampled_from(items),
            min_size=transaction_size,
            max_size=transaction_size
        ))
        transactions.append(transaction)
    
    return transactions


@st.composite
def transactions_with_special_chars(
    draw: st.DrawFn,
    min_transactions: int = 5,
    max_transactions: int = 20
) -> List[List[str]]:
    """
    Generate transactions with special characters, unicode, and edge-case strings.
    
    This tests robustness to unusual string inputs.
    
    Args:
        draw: Hypothesis draw function
        min_transactions: Minimum number of transactions
        max_transactions: Maximum number of transactions
        
    Returns:
        A list of transactions with special character items
    """
    n_transactions = draw(st.integers(min_value=min_transactions, max_value=max_transactions))
    
    # Generate items with various special characteristics
    special_items = draw(st.lists(
        st.one_of(
            st.text(min_size=1, max_size=10),  # Any unicode text
            st.from_regex(r"[!@#$%^&*()]+", fullmatch=True),  # Special chars
            st.just(""),  # Empty strings
            st.text(alphabet=" \t\n", min_size=1, max_size=3),  # Whitespace
        ),
        min_size=5,
        max_size=20,
        unique=True
    ))
    
    transactions = []
    for _ in range(n_transactions):
        transaction_size = draw(st.integers(min_value=1, max_value=min(10, len(special_items))))
        transaction = draw(st.lists(
            st.sampled_from(special_items),
            min_size=transaction_size,
            max_size=transaction_size
        ))
        transactions.append(transaction)
    
    return transactions


# ============================================================================
# Temporal/Timestamped Strategies
# ============================================================================

@st.composite
def timestamped_transaction_lists(
    draw: st.DrawFn,
    min_transactions: int = 2,
    max_transactions: int = 30,
    min_time: float = 0.0,
    max_time: float = 1000.0
) -> List[List[Tuple[str, float]]]:
    """
    Generate timestamped transactions for temporal constraint testing.
    
    Each item in a transaction is a tuple of (item, timestamp).
    
    Args:
        draw: Hypothesis draw function
        min_transactions: Minimum number of transactions
        max_transactions: Maximum number of transactions
        min_time: Minimum timestamp value
        max_time: Maximum timestamp value
        
    Returns:
        A list of timestamped transactions
    """
    n_transactions = draw(st.integers(min_value=min_transactions, max_value=max_transactions))
    items = draw(item_pool(min_items=3, max_items=15))
    
    transactions = []
    for _ in range(n_transactions):
        transaction_size = draw(st.integers(min_value=1, max_value=min(10, len(items))))
        
        # Generate timestamps (sorted for this transaction)
        timestamps = sorted([
            draw(st.floats(min_value=min_time, max_value=max_time, allow_nan=False, allow_infinity=False))
            for _ in range(transaction_size)
        ])
        
        # Generate items
        transaction_items = draw(st.lists(
            st.sampled_from(items),
            min_size=transaction_size,
            max_size=transaction_size
        ))
        
        # Combine items with timestamps
        transaction = list(zip(transaction_items, timestamps))
        transactions.append(transaction)
    
    return transactions


@st.composite
def pathological_timestamped_transactions(
    draw: st.DrawFn,
    pathology_type: str = "reversed"
) -> List[List[Tuple[str, float]]]:
    """
    Generate pathological timestamped transactions for edge-case testing.
    
    Args:
        draw: Hypothesis draw function
        pathology_type: Type of pathology to generate:
            - "reversed": Timestamps in reverse order
            - "identical": All timestamps the same
            - "gaps": Large gaps between timestamps
            
    Returns:
        A list of pathological timestamped transactions
    """
    n_transactions = draw(st.integers(min_value=2, max_value=10))
    items = draw(item_pool(min_items=3, max_items=10))
    
    transactions = []
    for _ in range(n_transactions):
        transaction_size = draw(st.integers(min_value=2, max_value=8))
        transaction_items = draw(st.lists(
            st.sampled_from(items),
            min_size=transaction_size,
            max_size=transaction_size
        ))
        
        if pathology_type == "reversed":
            # Timestamps in reverse order
            base_time = draw(st.floats(min_value=100.0, max_value=1000.0))
            timestamps = [base_time - i * 10 for i in range(transaction_size)]
        
        elif pathology_type == "identical":
            # All timestamps the same
            timestamp = draw(st.floats(min_value=0.0, max_value=1000.0))
            timestamps = [timestamp] * transaction_size
        
        else:  # gaps
            # Large gaps between timestamps
            timestamps = [
                draw(st.floats(min_value=i * 1000, max_value=(i + 1) * 1000))
                for i in range(transaction_size)
            ]
        
        transaction = list(zip(transaction_items, timestamps))
        transactions.append(transaction)
    
    return transactions


# ============================================================================
# Support Threshold Strategies
# ============================================================================

def valid_support_thresholds() -> st.SearchStrategy[float]:
    """
    Generate valid support thresholds for GSP testing.
    
    Returns:
        A strategy generating floats in the valid range [0.01, 1.0]
    """
    return st.floats(min_value=0.01, max_value=1.0)


def edge_case_support_thresholds() -> st.SearchStrategy[float]:
    """
    Generate edge-case support thresholds.
    
    Focuses on boundary values that might reveal edge cases.
    
    Returns:
        A strategy generating edge-case support values
    """
    return st.one_of(
        st.just(0.01),  # Very low support
        st.just(0.99),  # Very high support
        st.just(1.0),   # Maximum support
        st.floats(min_value=0.01, max_value=0.1),  # Low range
        st.floats(min_value=0.9, max_value=1.0),   # High range
    )
