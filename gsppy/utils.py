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
4. Loading SPM/GSP format files with delimiter-based parsing.

Main functionalities:
- `split_into_batches`: Splits a list of items into smaller batches based on a specified batch size.
- `is_subsequence_in_list`: Determines if a subsequence exists within another sequence in order,
  using caching to improve performance.
- `generate_candidates_from_previous`: Generates candidate patterns by joining previously
  identified frequent patterns.
- `read_transactions_from_spm`: Loads transactions from SPM/GSP delimiter format files.

These utilities are designed to support sequence processing tasks and can be
adapted to various domains, such as data mining, recommendation systems, and sequence analysis.
"""

from typing import Dict, List, Tuple, Union, Optional, Sequence, Generator, cast
from functools import lru_cache
from itertools import product

from gsppy.token_mapper import TokenMapper


def has_timestamps(
    sequence: Union[
        Tuple[Union[str, Tuple[str, Union[int, float]]], ...], List[Union[str, Tuple[str, Union[int, float]]]]
    ],
) -> bool:
    """
    Check if a sequence contains timestamped data (item-timestamp pairs).

    Parameters:
        sequence: A sequence that may contain timestamped data

    Returns:
        bool: True if the sequence contains timestamped data, False otherwise

    Examples:
        >>> has_timestamps((("A", 1), ("B", 2)))
        True
        >>> has_timestamps(("A", "B", "C"))
        False
    """
    if not sequence or len(sequence) == 0:
        return False

    first_item = sequence[0]

    # Check if first item is a tuple or list with 2 elements where second is numeric
    if isinstance(first_item, (tuple, list)) and len(first_item) == 2:
        try:
            # Try to interpret second element as a number
            float(first_item[1])
            return True
        except (TypeError, ValueError):
            return False

    return False


def is_itemset_format(transaction: Union[List, Tuple]) -> bool:
    """
    Check if a transaction is in itemset format (nested lists/tuples).
    
    Itemset format: Each element is itself a list/tuple of items that occur together.
    Example: [['A', 'B'], ['C']] or [[('A', 1.0), ('B', 1.0)], [('C', 2.0)]]
    
    Flat format: Simple list of items.
    Example: ['A', 'B', 'C'] or [('A', 1.0), ('B', 2.0), ('C', 3.0)]
    
    Parameters:
        transaction: A transaction to check
        
    Returns:
        bool: True if transaction is in itemset format, False if flat format
        
    Examples:
        >>> is_itemset_format([['A', 'B'], ['C']])
        True
        >>> is_itemset_format(['A', 'B', 'C'])
        False
        >>> is_itemset_format([[('A', 1.0), ('B', 1.0)], [('C', 2.0)]])
        True
        >>> is_itemset_format([('A', 1.0), ('B', 2.0)])
        False
    """
    if not transaction:
        return False
    
    # Check if first element is a list or tuple (but not a timestamp tuple)
    first_item = transaction[0]
    
    # If it's a tuple with 2 elements where second is numeric, it's a timestamp, not an itemset
    if isinstance(first_item, (tuple, list)):
        if len(first_item) == 2:
            try:
                float(first_item[1])
                # This is a timestamp tuple like ('A', 1.0)
                return False
            except (TypeError, ValueError, IndexError):
                # Not a timestamp, could be an itemset
                pass
        # It's a list/tuple, so this is itemset format
        return True
    
    return False


def normalize_to_itemsets(
    transaction: Union[List[str], List[Tuple[str, float]], List[List[str]], List[List[Tuple[str, float]]]]
) -> Union[Tuple[Tuple[str, ...], ...], Tuple[Tuple[Tuple[str, float], ...], ...]]:
    """
    Normalize a transaction to itemset format.
    
    Converts flat sequences to itemset format where each item becomes its own itemset.
    Already itemset-formatted data is converted to tuples for immutability.
    
    Flat input: ['A', 'B', 'C'] -> (('A',), ('B',), ('C',))
    Itemset input: [['A', 'B'], ['C']] -> (('A', 'B'), ('C',))
    Timestamped flat: [('A', 1.0), ('B', 2.0)] -> ((('A', 1.0),), (('B', 2.0),))
    Timestamped itemset: [[('A', 1.0), ('B', 1.0)], [('C', 2.0)]] -> ((('A', 1.0), ('B', 1.0)), (('C', 2.0),))
    
    Parameters:
        transaction: Input transaction in any supported format
        
    Returns:
        Tuple of tuples representing itemsets
        
    Examples:
        >>> normalize_to_itemsets(['A', 'B', 'C'])
        (('A',), ('B',), ('C',))
        >>> normalize_to_itemsets([['A', 'B'], ['C']])
        (('A', 'B'), ('C',))
        >>> normalize_to_itemsets([('A', 1.0), ('B', 2.0)])
        ((('A', 1.0),), (('B', 2.0),))
    """
    if not transaction:
        return ()
    
    if is_itemset_format(transaction):
        # Already in itemset format, just convert to tuples
        return tuple(tuple(itemset) for itemset in transaction)
    else:
        # Flat format - each item becomes its own itemset
        return tuple((item,) for item in transaction)


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
        >>> is_subsequence_in_list(("a", "c"), ("a", "b", "c"))
        True
        >>> is_subsequence_in_list(("a", "c"), ("c", "a"))
        False
        >>> is_subsequence_in_list(("a", "b"), ("a", "b", "c"))
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


@lru_cache(maxsize=None)
def is_subsequence_with_itemsets(
    pattern: Tuple[Tuple[str, ...], ...],
    sequence: Tuple[Tuple[str, ...], ...]
) -> bool:
    """
    Check if a pattern (sequence of itemsets) matches a sequence (sequence of itemsets).
    
    An itemset pattern matches a sequence itemset if all items in the pattern itemset
    are present in the sequence itemset (subset matching).
    
    The pattern must match in order across the sequence, but itemsets need not be contiguous.
    
    Parameters:
        pattern: Pattern as tuple of itemsets, e.g. (('A', 'B'), ('C',))
        sequence: Sequence as tuple of itemsets, e.g. (('A', 'B', 'D'), ('E',), ('C', 'F'))
        
    Returns:
        bool: True if pattern matches sequence with itemset semantics, False otherwise.
              Returns False for empty patterns.
        
    Examples:
        >>> # Pattern (A,B) then C matches sequence with (A,B,D) then (E) then (C,F)
        >>> is_subsequence_with_itemsets((('A', 'B'), ('C',)), (('A', 'B', 'D'), ('E',), ('C', 'F')))
        True
        >>> # Pattern (A,B) then C does NOT match sequence with (A) then (B) then (C)
        >>> is_subsequence_with_itemsets((('A', 'B'), ('C',)), (('A',), ('B',), ('C',)))
        False
        >>> # Single item per itemset behaves like flat matching
        >>> is_subsequence_with_itemsets((('A',), ('C',)), (('A',), ('B',), ('C',)))
        True
    """
    if not pattern:
        return False
    
    len_pattern = len(pattern)
    len_sequence = len(sequence)
    
    if len_pattern > len_sequence:
        return False
    
    # Two-pointer approach for itemset matching
    pattern_idx = 0
    for seq_idx in range(len_sequence):
        # Check if current pattern itemset is a subset of current sequence itemset
        pattern_itemset = set(pattern[pattern_idx])
        sequence_itemset = set(sequence[seq_idx])
        
        if pattern_itemset.issubset(sequence_itemset):
            pattern_idx += 1
            if pattern_idx == len_pattern:
                return True
    
    return False


@lru_cache(maxsize=None)
@lru_cache(maxsize=None)
def is_subsequence_with_itemsets_and_timestamps(
    pattern: Tuple[Tuple[str, ...], ...],
    sequence: Tuple[Tuple[Tuple[str, float], ...], ...],
    mingap: Optional[float] = None,
    maxgap: Optional[float] = None,
    maxspan: Optional[float] = None,
) -> bool:
    """
    Check if a pattern matches a timestamped itemset sequence with temporal constraints.
    
    This extends itemset matching to support timestamps and temporal constraints.
    Each itemset element contains (item, timestamp) tuples.
    
    Parameters:
        pattern: Pattern as tuple of itemsets (items only, no timestamps)
        sequence: Timestamped sequence as tuple of itemsets with (item, timestamp) tuples
        mingap: Minimum time gap between consecutive pattern elements
        maxgap: Maximum time gap between consecutive pattern elements
        maxspan: Maximum time span from first to last pattern element
        
    Returns:
        bool: True if pattern matches with itemset and temporal constraints, False otherwise.
              Returns False for empty patterns.
        
    Examples:
        >>> pattern = (('A',), ('C',))
        >>> sequence = (((('A', 1.0),)), ((('B', 2.0),)), ((('C', 3.0),)))
        >>> is_subsequence_with_itemsets_and_timestamps(pattern, sequence, mingap=0.5, maxgap=2.0)
        True
    """
    if not pattern:
        return False
    
    len_pattern = len(pattern)
    len_sequence = len(sequence)
    
    if len_pattern > len_sequence:
        return False
    
    # Try to find a match starting from each position
    for start_idx in range(len_sequence - len_pattern + 1):
        if _try_match_with_temporal_constraints(pattern, sequence, start_idx, mingap, maxgap, maxspan):
            return True
    
    return False


def _try_match_with_temporal_constraints(
    pattern: Tuple[Tuple[str, ...], ...],
    sequence: Tuple[Tuple[Tuple[str, float], ...], ...],
    start_idx: int,
    mingap: Optional[float],
    maxgap: Optional[float],
    maxspan: Optional[float],
) -> bool:
    """
    Try to match pattern starting from a specific position with temporal constraints.
    
    Returns:
        bool: True if match is found with constraints satisfied, False otherwise
    """
    pattern_idx = 0
    matched_positions: List[int] = []
    len_pattern = len(pattern)
    len_sequence = len(sequence)
    
    for seq_idx in range(start_idx, len_sequence):
        if pattern_idx >= len_pattern:
            break
            
        # Extract items from timestamped sequence itemset
        pattern_itemset = set(pattern[pattern_idx])
        sequence_items = {item for item, _ in sequence[seq_idx]}
        
        if pattern_itemset.issubset(sequence_items):
            matched_positions.append(seq_idx)
            pattern_idx += 1
    
    # Check if we matched all pattern elements
    if pattern_idx != len_pattern:
        return False
        
    # Validate temporal constraints
    if len(matched_positions) < 2:
        return True  # Single item - no temporal constraints to check
    
    # Get timestamps for matched positions
    matched_timestamps = [
        min(ts for _, ts in sequence[pos])
        for pos in matched_positions
    ]
    
    return _validate_temporal_constraints(matched_timestamps, mingap, maxgap, maxspan)


def _validate_temporal_constraints(
    timestamps: List[float],
    mingap: Optional[float],
    maxgap: Optional[float],
    maxspan: Optional[float],
) -> bool:
    """
    Validate temporal constraints for a sequence of timestamps.
    
    Returns:
        bool: True if all constraints are satisfied, False otherwise
    """
    # Check mingap and maxgap constraints
    for i in range(len(timestamps) - 1):
        gap = timestamps[i + 1] - timestamps[i]
        
        if mingap is not None and gap < mingap:
            return False
        if maxgap is not None and gap > maxgap:
            return False
    
    # Check maxspan constraint
    if maxspan is not None:
        span = timestamps[-1] - timestamps[0]
        if span > maxspan:
            return False
    
    return True


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
        >>> is_subsequence_in_list_with_time_constraints(("A", "C"), ("A", "B", "C"))
        True

        >>> # With timestamps and maxgap constraint
        >>> seq = (("A", 1), ("B", 3), ("C", 10))
        >>> is_subsequence_in_list_with_time_constraints(("A", "C"), seq, maxgap=5)
        False  # Gap between A and C is 9, exceeds maxgap=5

        >>> # With timestamps and mingap constraint
        >>> seq = (("A", 1), ("B", 2), ("C", 3))
        >>> is_subsequence_in_list_with_time_constraints(("A", "C"), seq, mingap=3)
        False  # Gap between A and C is 2, less than mingap=3

        >>> # With timestamps and maxspan constraint
        >>> seq = (("A", 1), ("B", 5), ("C", 12))
        >>> is_subsequence_in_list_with_time_constraints(("A", "C"), seq, maxspan=10)
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
        return is_subsequence_in_list(subsequence, sequence)

    # Extract items and timestamps from sequence
    seq_items, seq_times = _extract_items_and_timestamps(sequence, has_timestamps_flag)

    # Try to find a match starting from each position
    return _find_temporal_match(subsequence, seq_items, seq_times, mingap, maxgap, maxspan)


def _extract_items_and_timestamps(
    sequence: Union[Tuple[str, ...], Tuple[Tuple[str, float], ...]],
    has_timestamps_flag: bool,
) -> Tuple[Tuple[str, ...], Optional[Tuple[float, ...]]]:
    """
    Extract items and timestamps from a sequence.

    Args:
        sequence: The sequence to extract from
        has_timestamps_flag: Whether the sequence has timestamps

    Returns:
        Tuple of (items, timestamps) where timestamps is None if not present
    """
    if has_timestamps_flag:
        # For timestamped sequences, extract items and timestamps separately
        timestamped_seq = cast(Tuple[Tuple[str, float], ...], sequence)
        seq_items = tuple(item for item, _ in timestamped_seq)
        seq_times = tuple(time for _, time in timestamped_seq)
        return seq_items, seq_times
    else:
        # For non-timestamped sequences, return items directly with None for timestamps
        simple_seq = cast(Tuple[str, ...], sequence)
        return simple_seq, None


def _find_temporal_match(
    subsequence: Tuple[str, ...],
    seq_items: Tuple[str, ...],
    seq_times: Optional[Tuple[float, ...]],
    mingap: Optional[float],
    maxgap: Optional[float],
    maxspan: Optional[float],
) -> bool:
    """
    Find if subsequence matches with temporal constraints.

    Args:
        subsequence: Pattern to search for
        seq_items: Items in the sequence
        seq_times: Timestamps (None if not present)
        mingap: Minimum gap constraint
        maxgap: Maximum gap constraint
        maxspan: Maximum span constraint

    Returns:
        True if match found, False otherwise
    """
    len_sub = len(subsequence)
    len_seq = len(seq_items)

    # Try starting from each position
    for start_idx in range(len_seq - len_sub + 1):
        if _try_match_from_position(start_idx, subsequence, seq_items, seq_times, mingap, maxgap, maxspan):
            return True

    return False


def _try_match_from_position(
    start_idx: int,
    subsequence: Tuple[str, ...],
    seq_items: Tuple[str, ...],
    seq_times: Optional[Tuple[float, ...]],
    mingap: Optional[float],
    maxgap: Optional[float],
    maxspan: Optional[float],
) -> bool:
    """
    Try to match subsequence starting from a given position.

    Args:
        start_idx: Starting position in sequence
        subsequence: Pattern to match
        seq_items: Items in sequence
        seq_times: Timestamps (None if not present)
        mingap: Minimum gap constraint
        maxgap: Maximum gap constraint
        maxspan: Maximum span constraint

    Returns:
        True if match found, False otherwise
    """
    sub_idx = 0
    matched_indices: List[int] = []
    len_sub = len(subsequence)
    len_seq = len(seq_items)

    for seq_idx in range(start_idx, len_seq):
        if seq_items[seq_idx] == subsequence[sub_idx]:
            # Check temporal constraints if we have timestamps and have previous matches
            if (
                seq_times is not None
                and matched_indices
                and not _check_temporal_constraints(seq_idx, matched_indices, seq_times, mingap, maxgap)
            ):
                # Skip this occurrence and continue searching for a valid one
                continue

            matched_indices.append(seq_idx)
            sub_idx += 1

            # If we've matched the entire subsequence, check maxspan
            if sub_idx == len_sub:
                return _check_maxspan(matched_indices, seq_times, maxspan)

    return False


def _check_temporal_constraints(
    seq_idx: int,
    matched_indices: List[int],
    seq_times: Tuple[float, ...],
    mingap: Optional[float],
    maxgap: Optional[float],
) -> bool:
    """
    Check if temporal constraints are satisfied for a new match.

    Args:
        seq_idx: Current sequence index
        matched_indices: Previously matched indices
        seq_times: Timestamps
        mingap: Minimum gap constraint
        maxgap: Maximum gap constraint

    Returns:
        True if constraints satisfied, False otherwise
    """
    prev_idx = matched_indices[-1]
    time_gap = seq_times[seq_idx] - seq_times[prev_idx]

    # Check mingap constraint
    if mingap is not None and time_gap < mingap:
        return False

    # Check maxgap constraint
    if maxgap is not None and time_gap > maxgap:
        return False

    return True


def _check_maxspan(
    matched_indices: List[int],
    seq_times: Optional[Tuple[float, ...]],
    maxspan: Optional[float],
) -> bool:
    """
    Check if maxspan constraint is satisfied.

    Args:
        matched_indices: Matched sequence indices
        seq_times: Timestamps (None if not present)
        maxspan: Maximum span constraint

    Returns:
        True if constraint satisfied or not applicable, False otherwise
    """
    if seq_times is not None and maxspan is not None:
        first_idx = matched_indices[0]
        last_idx = matched_indices[-1]
        span = seq_times[last_idx] - seq_times[first_idx]
        if span > maxspan:
            return False

    return True


def generate_candidates_from_previous(prev_patterns: Dict[Tuple[str, ...], int]) -> List[Tuple[str, ...]]:
    """
    Generate joined candidates from the previous level's frequent patterns.

    Parameters:
        prev_patterns (Dict[Tuple, int]): A dictionary of frequent patterns from the previous level.

    Returns:
        List[Tuple]: Candidate patterns for the next level.
    """
    keys: List[Tuple[str, ...]] = list(prev_patterns.keys())
    return [
        pattern1 + (pattern2[-1],)
        for pattern1, pattern2 in product(keys, repeat=2)
        if pattern1[1:] == pattern2[:-1] and not (len(pattern1) == 1 and pattern1 == pattern2)
    ]


def _parse_spm_line(line: str, mapper: Optional[TokenMapper], preserve_itemsets: bool = True) -> Union[List[str], List[List[str]]]:
    """
    Parse a single line from an SPM format file.
    
    Parameters:
        line: Line to parse
        mapper: Optional TokenMapper to track tokens
        preserve_itemsets: If True, preserve itemset structure; if False, flatten to single list
        
    Returns:
        Union[List[str], List[List[str]]]: Parsed sequence as itemsets or flat list
        
    Examples:
        >>> _parse_spm_line("1 2 -1 3 -1 -2", None, preserve_itemsets=True)
        [['1', '2'], ['3']]
        >>> _parse_spm_line("1 2 -1 3 -1 -2", None, preserve_itemsets=False)
        ['1', '2', '3']
    """
    tokens = line.split()
    sequence: List[List[str]] = []
    current_element: List[str] = []
    
    for token in tokens:
        if token == "-2":
            # End of sequence
            if current_element:
                sequence.append(current_element[:])
            break
        elif token == "-1":
            # End of element
            if current_element:
                sequence.append(current_element[:])
                current_element = []
        else:
            # Regular item
            current_element.append(token)
            if mapper:
                mapper.add_token(token)
    
    # Add any remaining items if -2 was missing
    if current_element:
        sequence.append(current_element)
    
    # Return based on preserve_itemsets flag
    if preserve_itemsets:
        return sequence
    else:
        # Flatten for backward compatibility
        return [item for itemset in sequence for item in itemset]


def read_transactions_from_spm(
    path: str, return_mappings: bool = False, preserve_itemsets: bool = False
) -> Union[List[List[str]], List[List[List[str]]], Tuple[Union[List[List[str]], List[List[List[str]]]], Dict[str, int], Dict[int, str]]]:
    """
    Read transactions from an SPM/GSP format file.

    The SPM/GSP format uses delimiters:
    - `-1`: End of element (item set)
    - `-2`: End of sequence (transaction)

    Each line represents one sequence/transaction. Items are space-separated integers
    (or strings), with -1 marking the end of an element and -2 marking the end of a sequence.

    Format examples:
        Simple sequence: `1 2 -1 3 -1 -2` represents [[1, 2], [3]]
        Multiple items: `A -1 B C -1 -2` represents [[A], [B, C]]

    Parameters:
        path: Path to the SPM format file
        return_mappings: If True, return token mappings (str→int, int→str) along with dataset
        preserve_itemsets: If True, preserve itemset structure; if False, flatten sequences (default: False for backward compatibility)

    Returns:
        If return_mappings is False:
            List[List[str]] or List[List[List[str]]]: Parsed dataset (flat or itemset format)
        If return_mappings is True:
            Tuple containing:
                - Dataset (flat or itemset format)
                - Dict[str, int]: String to integer mapping
                - Dict[int, str]: Integer to string mapping

    Raises:
        ValueError: If file cannot be read or contains invalid format
        FileNotFoundError: If file does not exist

    Examples:
        >>> # File content: "1 2 -1 3 -1 -2"
        >>> # Default: flatten for backward compatibility
        >>> transactions = read_transactions_from_spm("data.txt")
        >>> print(transactions)
        [['1', '2', '3']]
        
        >>> # Preserve itemsets
        >>> transactions = read_transactions_from_spm("data.txt", preserve_itemsets=True)
        >>> print(transactions)
        [[['1', '2'], ['3']]]

        >>> # With mappings
        >>> transactions, str_to_int, int_to_str = read_transactions_from_spm("data.txt", return_mappings=True)

    Notes:
        - Empty lines are skipped
        - Extra or trailing delimiters are handled gracefully
        - When preserve_itemsets=False (default), elements within a sequence are flattened into a single list for backward compatibility
        - When preserve_itemsets=True, the itemset structure is preserved
        - All tokens are returned as strings for consistency
    """
    try:
        transactions: List[Union[List[str], List[List[str]]]] = []
        mapper = TokenMapper() if return_mappings else None

        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                
                # Skip empty lines
                if not line:
                    continue
                
                sequence = _parse_spm_line(line, mapper, preserve_itemsets=preserve_itemsets)
                
                # Add non-empty sequences
                if sequence:
                    transactions.append(sequence)

        if return_mappings and mapper:
            return transactions, mapper.get_str_to_int(), mapper.get_int_to_str()
        return transactions

    except FileNotFoundError as e:
        raise FileNotFoundError(f"SPM file '{path}' does not exist.") from e
    except Exception as e:
        raise ValueError(f"Error reading SPM format file '{path}': {e}") from e
