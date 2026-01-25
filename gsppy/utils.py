"""
This module provides utility functions for working with sequences and generating candidate patterns.
It is designed to facilitate operations such as batching, identifying subsequences,
and generating candidate patterns from previously frequent patterns.

The key functionalities include:
1. Splitting a list of items into smaller batches for easier processing.
2. Checking for the existence of an ordered (non-contiguous) subsequence within a sequence,
   with caching to optimize repeated comparisons.
3. Generating candidate patterns from a dictionary of frequent patterns
   to support pattern generation tasks in algorithms like sequence mining.

Main functionalities:
- `split_into_batches`: Splits a list of items into smaller batches based on a specified batch size.
- `is_subsequence_in_list`: Determines if a subsequence exists within another sequence in order,
  using caching to improve performance.
- `generate_candidates_from_previous`: Generates candidate patterns by joining previously
  identified frequent patterns.

These utilities are designed to support sequence processing tasks and can be
adapted to various domains, such as data mining, recommendation systems, and sequence analysis.
"""

from typing import Dict, List, Tuple, Sequence, Generator, Optional, Union
from functools import lru_cache
from itertools import product


def has_timestamps(sequence: Union[Tuple, List]) -> bool:
    """
    Check if a sequence contains timestamped data (item-timestamp pairs).
    
    Parameters:
        sequence: A sequence that may contain timestamped data
        
    Returns:
        bool: True if the sequence contains timestamped data, False otherwise
        
    Examples:
        >>> has_timestamps((('A', 1), ('B', 2)))
        True
        >>> has_timestamps(('A', 'B', 'C'))
        False
    """
    if not sequence or len(sequence) == 0:
        return False
    
    first_item = sequence[0]
    
    # Check if first item is a tuple with 2 elements where second is numeric
    if isinstance(first_item, tuple) and len(first_item) == 2:
        try:
            # Try to interpret second element as a number
            float(first_item[1])
            return True
        except (TypeError, ValueError):
            return False
    
    return False


def split_into_batches(
    items: Sequence[Tuple[str, ...]], batch_size: int
) -> Generator[Sequence[Tuple[str, ...]], None, None]:
    """
    Split the list of items into smaller batches.

    Parameters:
        items (Sequence[Tuple]): A sequence of items to be batched.
        batch_size (int): The maximum size of each batch.

    Returns:
        Generator[Sequence[Tuple], None, None]: A generator yielding batches of items.
    """
    for i in range(0, len(items), batch_size):
        yield items[i : i + batch_size]


@lru_cache(maxsize=None)
def is_subsequence_in_list(subsequence: Tuple[str, ...], sequence: Tuple[str, ...]) -> bool:
    """
    Check if a subsequence exists within a sequence as an ordered (non-contiguous) subsequence.

    This function implements the standard GSP semantics where items in the subsequence
    must appear in the same order in the sequence, but not necessarily contiguously.

    Parameters:
        subsequence: (tuple): The sequence to search for.
        sequence (tuple): The sequence to search within.

    Returns:
        bool: True if the subsequence is found, False otherwise.

    Examples:
        >>> is_subsequence_in_list(('a', 'c'), ('a', 'b', 'c'))
        True
        >>> is_subsequence_in_list(('a', 'c'), ('c', 'a'))
        False
        >>> is_subsequence_in_list(('a', 'b'), ('a', 'b', 'c'))
        True
    """
    # Handle the case where the subsequence is empty - it should not exist in any sequence
    if not subsequence:
        return False

    len_sub, len_seq = len(subsequence), len(sequence)

    # Return False if the subsequence is longer than the sequence
    if len_sub > len_seq:
        return False

    # Use two-pointer approach to check if subsequence exists in order
    sub_idx = 0
    for seq_idx in range(len_seq):
        if sequence[seq_idx] == subsequence[sub_idx]:
            sub_idx += 1
            if sub_idx == len_sub:
                return True
    return False


def is_subsequence_in_list_with_time_constraints(
    subsequence: Tuple[str, ...],
    sequence: Union[Tuple[str, ...], Tuple[Tuple[str, float], ...]],
    mingap: Optional[float] = None,
    maxgap: Optional[float] = None,
    maxspan: Optional[float] = None,
) -> bool:
    """
    Check if a subsequence exists within a sequence with optional temporal constraints.

    This function extends the standard subsequence check to support temporal constraints
    for time-constrained sequential pattern mining. It handles both simple sequences
    (items only) and timestamped sequences (item-timestamp pairs).

    Temporal Constraints:
        - mingap: Minimum time gap required between consecutive items in the pattern.
        - maxgap: Maximum time gap allowed between consecutive items in the pattern.
        - maxspan: Maximum time span from the first to last item in the pattern.

    Parameters:
        subsequence (Tuple[str, ...]): The pattern to search for (items only, no timestamps).
        sequence (Union[Tuple[str, ...], Tuple[Tuple[str, float], ...]]): 
            The sequence to search within. Can be:
            - Simple: Tuple of items (e.g., ('A', 'B', 'C'))
            - Timestamped: Tuple of (item, timestamp) pairs (e.g., (('A', 1.0), ('B', 3.0)))
        mingap (Optional[float]): Minimum time between consecutive pattern elements.
        maxgap (Optional[float]): Maximum time between consecutive pattern elements.
        maxspan (Optional[float]): Maximum time from first to last pattern element.

    Returns:
        bool: True if the subsequence is found respecting temporal constraints, False otherwise.

    Examples:
        >>> # Without timestamps (backward compatible)
        >>> is_subsequence_in_list_with_time_constraints(('A', 'C'), ('A', 'B', 'C'))
        True
        
        >>> # With timestamps and maxgap constraint
        >>> seq = (('A', 1), ('B', 3), ('C', 10))
        >>> is_subsequence_in_list_with_time_constraints(('A', 'C'), seq, maxgap=5)
        False  # Gap between A and C is 9, exceeds maxgap=5
        
        >>> # With timestamps and mingap constraint
        >>> seq = (('A', 1), ('B', 2), ('C', 3))
        >>> is_subsequence_in_list_with_time_constraints(('A', 'C'), seq, mingap=3)
        False  # Gap between A and C is 2, less than mingap=3
        
        >>> # With timestamps and maxspan constraint
        >>> seq = (('A', 1), ('B', 5), ('C', 12))
        >>> is_subsequence_in_list_with_time_constraints(('A', 'C'), seq, maxspan=10)
        False  # Span from A to C is 11, exceeds maxspan=10
    """
    # Handle empty subsequence
    if not subsequence:
        return False

    # Return False if the subsequence is longer than the sequence
    if len(subsequence) > len(sequence):
        return False

    # Determine if sequence has timestamps
    has_timestamps_flag = has_timestamps(sequence)
    
    # If no temporal constraints and no timestamps, use the optimized cached version
    if not has_timestamps_flag and mingap is None and maxgap is None and maxspan is None:
        return is_subsequence_in_list(subsequence, sequence)  # type: ignore

    # Extract items and timestamps from sequence
    if has_timestamps_flag:
        seq_items = tuple(item for item, _ in sequence)  # type: ignore
        seq_times = tuple(time for _, time in sequence)  # type: ignore
    else:
        seq_items = sequence  # type: ignore
        seq_times = None

    len_sub = len(subsequence)
    len_seq = len(seq_items)
    
    # Use two-pointer approach with temporal constraint checking
    # For maxgap violations, we need to try starting from each position
    for start_idx in range(len_seq - len_sub + 1):
        sub_idx = 0
        matched_indices = []
        
        for seq_idx in range(start_idx, len_seq):
            if seq_items[seq_idx] == subsequence[sub_idx]:
                # Check temporal constraints if we have timestamps
                if seq_times is not None and len(matched_indices) > 0:
                    prev_idx = matched_indices[-1]
                    time_gap = seq_times[seq_idx] - seq_times[prev_idx]
                    
                    # Check mingap constraint
                    if mingap is not None and time_gap < mingap:
                        continue
                    
                    # Check maxgap constraint
                    if maxgap is not None and time_gap > maxgap:
                        # This match chain is broken, try next starting position
                        break
                
                matched_indices.append(seq_idx)
                sub_idx += 1
                
                # If we've matched the entire subsequence, check maxspan
                if sub_idx == len_sub:
                    if seq_times is not None and maxspan is not None:
                        first_idx = matched_indices[0]
                        last_idx = matched_indices[-1]
                        span = seq_times[last_idx] - seq_times[first_idx]
                        if span > maxspan:
                            # This match violates maxspan, try next starting position
                            break
                    return True
    
    return False


def generate_candidates_from_previous(prev_patterns: Dict[Tuple[str, ...], int]) -> List[Tuple[str, ...]]:
    """
    Generate joined candidates from the previous level's frequent patterns.

    Parameters:
        prev_patterns (Dict[Tuple, int]): A dictionary of frequent patterns from the previous level.

    Returns:
        List[Tuple]: Candidate patterns for the next level.
    """
    keys = list(prev_patterns.keys())
    return [
        pattern1 + (pattern2[-1],)
        for pattern1, pattern2 in product(keys, repeat=2)
        if pattern1[1:] == pattern2[:-1] and not (len(pattern1) == 1 and pattern1 == pattern2)
    ]
