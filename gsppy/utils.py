"""
This module provides utility functions for working with sequences and generating candidate patterns.
It is designed to facilitate operations such as batching, identifying subsequences,
and generating candidate patterns from previously frequent patterns.

The key functionalities include:
1. Splitting a list of items into smaller batches for easier processing.
2. Checking for the existence of a contiguous subsequence within a sequence,
   with caching to optimize repeated comparisons.
3. Generating candidate patterns from a dictionary of frequent patterns
   to support pattern generation tasks in algorithms like sequence mining.

Main functionalities:
- `split_into_batches`: Splits a list of items into smaller batches based on a specified batch size.
- `is_subsequence_in_list`: Determines if a subsequence exists within another sequence,
  using caching to improve performance.
- `generate_candidates_from_previous`: Generates candidate patterns by joining previously
  identified frequent patterns.

These utilities are designed to support sequence processing tasks and can be
adapted to various domains, such as data mining, recommendation systems, and sequence analysis.
"""
from functools import lru_cache
from itertools import product
from typing import List, Tuple, Generator, Dict


def split_into_batches(items: List[Tuple], batch_size: int) -> Generator[List[Tuple], None, None]:
    """
    Split the list of items into smaller batches.

    Parameters:
        items (List[Tuple]): The list of candidate items.
        batch_size (int): The maximum size of each batch.

    Returns:
        List[List[Tuple]]: A list of batches, where each batch contains a subset of candidate items.
    """
    for i in range(0, len(items), batch_size):
        yield items[i:i + batch_size]


# Cache the results of the slice comparison function to avoid redundant calculations
@lru_cache(maxsize=None)
def is_subsequence_in_list(subsequence: Tuple, sequence: Tuple) -> bool:
    """
    Check if a subsequence exists within a sequence as a contiguous subsequence.

    Parameters:
        subsequence: Tuple (tuple): The sequence to search for.
        sequence (tuple): The sequence to search within.

    Returns:
        bool: True if the subsequence is found, False otherwise.
    """
    # Handle the case where the subsequence is empty - it should not exist in any sequence
    if not subsequence:
        return False

    len_sub, len_seq = len(subsequence), len(sequence)

    # Return False if the sequence is longer than the list
    if len_sub > len_seq:
        return False

    # Use any to check if any slice matches the sequence
    return any(sequence[i:i + len_sub] == subsequence for i in range(len_seq - len_sub + 1))


def generate_candidates_from_previous(prev_patterns: Dict[Tuple, int]) -> List[Tuple]:
    """
    Generate joined candidates from the previous level's frequent patterns.

    Parameters:
        prev_patterns (Dict[Tuple, int]): Frequent patterns at the previous level.

    Returns:
        List[Tuple]: Candidate patterns for the next level.
    """
    keys = list(prev_patterns.keys())
    return [
        pattern1 + (pattern2[-1],)
        for pattern1, pattern2 in product(keys, repeat=2)
        if pattern1[1:] == pattern2[:-1] and not (len(pattern1) == 1 and pattern1 == pattern2)
    ]
