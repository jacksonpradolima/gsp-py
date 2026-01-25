"""
===============================================
Generalized Sequential Pattern (GSP) Algorithm
===============================================

This module provides an implementation of the GSP (Generalized Sequential Pattern) algorithm,
a widely used sequence mining algorithm designed to discover frequent sequential patterns
in transactional datasets. It allows users to analyze sequential data and extract patterns
based on a user-defined minimum support threshold.

Key Features:
-------------
1. **Efficient Support Count Calculation**:
    - Parallel processing using `multiprocessing` to efficiently calculate support for candidate sequences.
    - Support batching to improve scalability on large datasets.

2. **Candidate Generation**:
    - Supports iterative candidate generation for k-sequences (k-itemsets).
    - Prunes non-frequent candidates to enhance performance during pattern discovery.

3. **Flexible Input Handling**:
    - Processes raw transactional datasets in the form of lists of lists.
    - Handles datasets with variable-length transactions.

4. **User Control & Parameters**:
    - Accepts a user-specified `min_support` as a fraction of total transactions.
    - Supports tuning, such as batch processing size, to optimize performance.

5. **Detailed Log Output**:
    - Configurable logging to track progress, intermediate results, and issues during execution.

Example Usage:
--------------
```python
# Define the transactional dataset
transactions = [
    ["Bread", "Milk"],
    ["Bread", "Diaper", "Beer", "Eggs"],
    ["Milk", "Diaper", "Beer", "Coke"],
    ["Bread", "Milk", "Diaper", "Beer"],
    ["Bread", "Milk", "Diaper", "Coke"],
]

# Initialize GSP with the transactional dataset
gsp = GSP(transactions)

# Run the GSP algorithm with a specified minimum support
patterns = gsp.search(min_support=0.3)

# Output discovered patterns
for level, freq_patterns in enumerate(patterns, start=1):
    print(f"\n{level}-Sequence Frequent Patterns:")
    for pattern, support in freq_patterns.items():
        print(f"Pattern: {pattern}, Support: {support}")
```

Main Components:
-----------------
- **Class GSP**:
    - `__init__`: Initializes the algorithm with raw transactional data.
    - `_pre_processing`: Validates and preprocesses the input transactions for compatibility.
    - `_worker_batch`: Processes candidate batches to calculate support counts.
    - `_support`: Computes the support of candidate sequences, using parallel processing for efficiency.
    - `_print_status`: Logs current algorithm progress and candidate filtering.
    - `search`: Executes the GSP algorithm to discover frequent patterns at all k-sequence levels.

Typical Applications:
----------------------
- Market Basket Analysis (e.g., discovering frequent purchase patterns).
- Analyzing user behavior sequences in web or app usage.
- Sequential pattern discovery in event or log data.
- Pattern mining in bioinformatics or time-series data.

Author:
-------
- **Developed by:** Jackson Antonio do Prado Lima
- **Email:** jacksonpradolima@gmail.com

License:
--------
This implementation is distributed under the MIT License.

Version:
--------
- Current Version: 2.0
"""

import math
import logging
import multiprocessing as mp
from typing import Dict, List, Tuple, Optional, Union
from itertools import chain
from collections import Counter

from gsppy.utils import (
    split_into_batches,
    is_subsequence_in_list,
    is_subsequence_in_list_with_time_constraints,
    generate_candidates_from_previous,
    has_timestamps,
)
from gsppy.accelerate import support_counts as support_counts_accel

logger: logging.Logger = logging.getLogger(__name__)


class GSP:
    """
    Generalized Sequential Pattern (GSP) Algorithm.

    The GSP algorithm is used to find frequent sequential patterns in transactional datasets
    based on a user-defined minimum support threshold. This implementation is optimized
    for efficiency with candidate generation, batch processing, and multiprocessing.

    Attributes:
        freq_patterns (List[Dict[Tuple, int]]): Stores discovered frequent sequential patterns
                                                at each k-sequence level as dictionaries
                                                mapping patterns to their support counts.
        transactions (List[Tuple]): Preprocessed dataset where each transaction is represented
                                    as a tuple of items.
        unique_candidates (List[Tuple]): List of initial singleton candidates (1-item sequences).
        max_size (int): Length of the longest transaction in the dataset, used to set the maximum
                        k-sequence for pattern generation.
    """

    def __init__(
        self,
        raw_transactions: Union[List[List[str]], List[List[Tuple[str, float]]]],
        mingap: Optional[float] = None,
        maxgap: Optional[float] = None,
        maxspan: Optional[float] = None,
    ):
        """
        Initialize the GSP algorithm with raw transactional data.

        Parameters:
            raw_transactions (Union[List[List[str]], List[List[Tuple[str, float]]]]): 
                Input transaction dataset where each transaction is either:
                - A list of items (e.g., [['A', 'B'], ['B', 'C', 'D']])
                - A list of (item, timestamp) tuples (e.g., [[('A', 1.0), ('B', 2.0)]])
            mingap (Optional[float]): Minimum time gap required between consecutive items in patterns.
            maxgap (Optional[float]): Maximum time gap allowed between consecutive items in patterns.
            maxspan (Optional[float]): Maximum time span from first to last item in patterns.

        Attributes Initialized:
            - Processes the input raw transaction dataset.
            - Computes unique singleton candidates (`unique_candidates`).
            - Extracts the maximum transaction size (`max_size`) from the dataset for limiting
              the search space.
            - Stores temporal constraints for use during pattern mining.

        Raises:
            ValueError: If the input transaction dataset is empty, contains
                        fewer than two transactions, or is not properly formatted.
                        Also raised if temporal constraints are invalid.
        """
        self.freq_patterns: List[Dict[Tuple[str, ...], int]] = []
        self.mingap = mingap
        self.maxgap = maxgap
        self.maxspan = maxspan
        self._validate_temporal_constraints()
        self._pre_processing(raw_transactions)

    def _validate_temporal_constraints(self) -> None:
        """
        Validate temporal constraint parameters.

        Raises:
            ValueError: If any temporal constraint is negative or if mingap > maxgap.
        """
        if self.mingap is not None and self.mingap < 0:
            raise ValueError("mingap must be non-negative")
        if self.maxgap is not None and self.maxgap < 0:
            raise ValueError("maxgap must be non-negative")
        if self.maxspan is not None and self.maxspan < 0:
            raise ValueError("maxspan must be non-negative")
        if (
            self.mingap is not None
            and self.maxgap is not None
            and self.mingap > self.maxgap
        ):
            raise ValueError("mingap cannot be greater than maxgap")

    def _pre_processing(
        self, raw_transactions: Union[List[List[str]], List[List[Tuple[str, float]]]]
    ) -> None:
        """
        Validate and preprocess the input transactional dataset.

        This method ensures that the dataset is formatted correctly and converts the transactions
        into tuples while counting unique singleton candidates for initial support computation steps.
        It handles both simple transactions (items only) and timestamped transactions.

        Parameters:
            raw_transactions (Union[List[List[str]], List[List[Tuple[str, float]]]]): 
                Input transactional data (with or without timestamps).

        Attributes Set:
            - `transactions`: The preprocessed transactions converted to tuples.
            - `unique_candidates`: A list of unique singleton candidates derived from the dataset.
            - `max_size`: The length of the largest transaction in the data.
            - `has_timestamps`: Boolean indicating if transactions include timestamps.

        Raises:
            ValueError: If the dataset is empty, improperly formatted, or contains fewer than 2 transactions.

        Logs:
            - Error messages if the input data is invalid.
            - Debug information about the unique candidates after preprocessing.
        """
        if not raw_transactions:
            msg = "Input transactions are empty. GSP requires at least one transaction."
            logger.error(msg)
            raise ValueError(msg)

        if len(raw_transactions) == 1:
            msg = "GSP requires multiple transactions to find meaningful patterns."
            logger.error(msg)
            raise ValueError(msg)

        logger.info("Pre-processing transactions...")
        
        # Detect if transactions have timestamps by checking non-empty transactions
        self.has_timestamps = False
        for tx in raw_transactions:
            if tx:  # Check non-empty transactions
                self.has_timestamps = has_timestamps(tx)
                if self.has_timestamps:
                    logger.debug("Detected timestamped transactions")
                break

        # Validate temporal constraints are only used with timestamps
        if (self.mingap is not None or self.maxgap is not None or self.maxspan is not None) and not self.has_timestamps:
            logger.warning(
                "Temporal constraints specified but transactions do not have timestamps. "
                "Constraints will be ignored."
            )

        self.max_size: int = max(len(item) for item in raw_transactions)
        
        if self.has_timestamps:
            # For timestamped transactions, convert to tuples and extract items for counting
            self.transactions: List[Union[Tuple[str, ...], Tuple[Tuple[str, float], ...]]] = [
                tuple(transaction) for transaction in raw_transactions  # type: ignore
            ]
            # Extract just the items for counting unique candidates
            all_items = chain.from_iterable([[item for item, _ in tx] for tx in raw_transactions])  # type: ignore
            counts: Counter[str] = Counter(all_items)
        else:
            # For non-timestamped transactions, process as before
            self.transactions: List[Union[Tuple[str, ...], Tuple[Tuple[str, float], ...]]] = [
                tuple(transaction) for transaction in raw_transactions  # type: ignore
            ]
            counts: Counter[str] = Counter(chain.from_iterable(raw_transactions))  # type: ignore

        # Start with singleton candidates (1-sequences)
        self.unique_candidates: List[Tuple[str, ...]] = [(item,) for item in counts.keys()]
        logger.debug("Unique candidates: %s", self.unique_candidates)

    @staticmethod
    def _worker_batch(
        batch: List[Tuple[str, ...]],
        transactions: List[Union[Tuple[str, ...], Tuple[Tuple[str, float], ...]]],
        min_support: int,
        mingap: Optional[float] = None,
        maxgap: Optional[float] = None,
        maxspan: Optional[float] = None,
    ) -> List[Tuple[Tuple[str, ...], int]]:
        """
        Evaluate a batch of candidate sequences to compute their support.

        This method iterates over the candidates in the given batch and checks their frequency
        of appearance across all transactions. Candidates meeting the user-defined minimum
        support threshold are returned. Supports temporal constraints when timestamps are present.

        Parameters:
            batch (List[Tuple]): A batch of candidate sequences, where each sequence is represented as a tuple.
            transactions (List[Union[Tuple[str, ...], Tuple[Tuple[str, float], ...]]]): 
                Preprocessed transactions as tuples (with or without timestamps).
            min_support (int): Absolute minimum support count required for a candidate to be considered frequent.
            mingap (Optional[float]): Minimum time gap between consecutive items.
            maxgap (Optional[float]): Maximum time gap between consecutive items.
            maxspan (Optional[float]): Maximum time span from first to last item.

        Returns:
            List[Tuple[Tuple, int]]: A list of tuples where each tuple contains:
                                     - A candidate sequence.
                                     - The candidate's support count.
        """
        results: List[Tuple[Tuple[str, ...], int]] = []
        has_temporal = mingap is not None or maxgap is not None or maxspan is not None
        
        # Detect if transactions have timestamps using the helper function
        has_timestamps_flag = transactions and has_timestamps(transactions[0])
        
        for item in batch:
            if has_timestamps_flag or has_temporal:
                # Use temporal-aware checking for timestamped transactions
                frequency = sum(
                    1
                    for t in transactions
                    if is_subsequence_in_list_with_time_constraints(
                        item, t, mingap=mingap, maxgap=maxgap, maxspan=maxspan
                    )
                )
            else:
                # Use standard non-temporal checking for simple transactions
                frequency = sum(1 for t in transactions if is_subsequence_in_list(item, t))  # type: ignore
            
            if frequency >= min_support:
                results.append((item, frequency))
        return results

    def _support_python(
        self, items: List[Tuple[str, ...]], min_support: int = 0, batch_size: int = 100
    ) -> Dict[Tuple[str, ...], int]:
        """
        Calculate support counts for candidate sequences using Python multiprocessing.

        Parameters:
            items (List[Tuple]): Candidate sequences to evaluate.
            min_support (int): Absolute minimum support count required for a sequence to be considered frequent.
            batch_size (int): Maximum number of candidates to process per batch.

        Returns:
            Dict[Tuple, int]: A dictionary containing frequent sequences as keys
                              and their support counts as values.
        """
        # Split candidates into batches
        batches = list(split_into_batches(items, batch_size))

        # Use multiprocessing pool to calculate frequency in parallel, batch-wise
        with mp.Pool(processes=mp.cpu_count()) as pool:
            batch_results = pool.starmap(
                self._worker_batch,  # Process a batch at a time
                [
                    (batch, self.transactions, min_support, self.mingap, self.maxgap, self.maxspan)
                    for batch in batches
                ],
            )

        # Flatten the list of results and convert to a dictionary
        return {item: freq for batch in batch_results for item, freq in batch}

    def _support(
        self,
        items: List[Tuple[str, ...]],
        min_support: int = 0,
        batch_size: int = 100,
        backend: Optional[str] = None,
    ) -> Dict[Tuple[str, ...], int]:
        """
        Calculate support counts for candidate sequences using the fastest available backend.
        This will try the Rust extension if available (and configured), otherwise fall back to
        the Python multiprocessing implementation.
        
        Note: When temporal constraints are active or transactions have timestamps,
        the Python implementation is always used as the accelerated backends do not yet
        support temporal constraints or timestamped transactions.
        """
        # Use Python implementation when temporal constraints are active or timestamps present
        has_temporal = self.mingap is not None or self.maxgap is not None or self.maxspan is not None
        if has_temporal or self.has_timestamps:
            return self._support_python(items, min_support, batch_size)
        
        try:
            return support_counts_accel(self.transactions, items, min_support, batch_size, backend=backend)
        except Exception:
            # Fallback to Python implementation on any acceleration failure
            return self._support_python(items, min_support, batch_size)

    def _print_status(self, run: int, candidates: List[Tuple[str, ...]]) -> None:
        """
        Log progress information for the current GSP iteration.

        This method logs the number of candidate sequences generated and filtered during the
        current run of the GSP algorithm.

        Parameters:
            run (int): Current k-sequence generation level (e.g., 1 for 1-item sequences).
            candidates (List[Tuple]): Candidate sequences generated at this level.
        """
        logger.info("Run %d: %d candidates filtered to %d.", run, len(candidates), len(self.freq_patterns[run - 1]))

    def search(
        self,
        min_support: float = 0.2,
        max_k: Optional[int] = None,
        backend: Optional[str] = None,
    ) -> List[Dict[Tuple[str, ...], int]]:
        """
        Execute the Generalized Sequential Pattern (GSP) mining algorithm.

        This method facilitates the discovery of frequent sequential patterns
        in the input transaction dataset. Patterns are extracted iteratively at each k-sequence level,
        starting from singleton sequences, until no further frequent patterns can be found.
        
        When temporal constraints (mingap, maxgap, maxspan) are specified during initialization,
        the algorithm enforces these constraints during pattern matching, allowing for time-aware
        sequential pattern mining.

        Parameters:
            min_support (float): Minimum support threshold as a fraction of total transactions.
                                     For example, `0.3` means that a sequence is frequent if it
                                     appears in at least 30% of all transactions.
            max_k (Optional[int]): Maximum length of patterns to mine. If None, mines up to max transaction length.
            backend (Optional[str]): Backend to use for support counting ('auto', 'python', 'rust', 'gpu').
                                    Note: temporal constraints always use Python backend.

        Returns:
            List[Dict[Tuple[str, ...], int]]: A list of dictionaries containing frequent patterns
                                              at each k-sequence level, with patterns as keys
                                              and their support counts as values.

        Raises:
            ValueError: If the minimum support threshold is not in the range `(0.0, 1.0]`.

        Logs:
            - Information about the algorithm's start, intermediate progress (candidates filtered),
              and completion.
            - Status updates for each iteration until the algorithm terminates.

        Examples:
            Basic usage without temporal constraints:

            ```python
            from gsppy.gsp import GSP

            transactions = [
                ["Bread", "Milk"],
                ["Bread", "Diaper", "Beer", "Eggs"],
                ["Milk", "Diaper", "Beer", "Coke"],
            ]

            gsp = GSP(transactions)
            patterns = gsp.search(min_support=0.3)
            ```
            
            Usage with temporal constraints (requires timestamped transactions):

            ```python
            from gsppy.gsp import GSP

            # Transactions with timestamps
            timestamped_transactions = [
                [("A", 1), ("B", 3), ("C", 5)],
                [("A", 2), ("B", 10), ("C", 12)],
                [("A", 1), ("C", 4)],
            ]

            # Find patterns with maxgap of 5 time units between consecutive items
            gsp = GSP(timestamped_transactions, maxgap=5)
            patterns = gsp.search(min_support=0.5)
            # Pattern ("A", "B", "C") won't be found in transaction 2 
            # because gap between B and C is only 2, but A to B is 8 (exceeds maxgap)
            ```
        """
        if not 0.0 < min_support <= 1.0:
            raise ValueError("Minimum support must be in the range (0.0, 1.0]")

        logger.info(f"Starting GSP algorithm with min_support={min_support}...")
        if self.mingap is not None or self.maxgap is not None or self.maxspan is not None:
            logger.info(
                f"Using temporal constraints: mingap={self.mingap}, maxgap={self.maxgap}, maxspan={self.maxspan}"
            )

        # Convert fractional support to absolute count (ceil to preserve threshold semantics)
        abs_min_support = int(math.ceil(len(self.transactions) * float(min_support)))

        # the set of frequent 1-sequence: all singleton sequences
        # (k-itemsets/k-sequence = 1) - Initially, every item in DB is a
        # candidate
        candidates = self.unique_candidates

        # scan transactions to collect support count for each candidate
        # sequence & filter
        self.freq_patterns.append(self._support(candidates, abs_min_support, backend=backend))

        # (k-itemsets/k-sequence = 1)
        k_items = 1

        self._print_status(k_items, candidates)

        # repeat until no frequent sequence or no candidate can be found
        # If max_k is provided, stop generating candidates beyond that length
        while (
            self.freq_patterns[k_items - 1] and k_items + 1 <= self.max_size and (max_k is None or k_items + 1 <= max_k)
        ):
            k_items += 1

            # Generate candidate sets Ck (set of candidate k-sequences) -
            # generate new candidates from the last "best" candidates filtered
            # by minimum support
            candidates = generate_candidates_from_previous(self.freq_patterns[k_items - 2])

            # candidate pruning - eliminates candidates who are not potentially
            # frequent (using support as threshold)
            self.freq_patterns.append(self._support(candidates, abs_min_support, backend=backend))

            self._print_status(k_items, candidates)
        logger.info("GSP algorithm completed.")
        return self.freq_patterns[:-1]
