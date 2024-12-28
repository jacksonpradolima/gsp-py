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
    ['Bread', 'Milk'],
    ['Bread', 'Diaper', 'Beer', 'Eggs'],
    ['Milk', 'Diaper', 'Beer', 'Coke'],
    ['Bread', 'Milk', 'Diaper', 'Beer'],
    ['Bread', 'Milk', 'Diaper', 'Coke']
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
import logging
import multiprocessing as mp
from typing import Any, Dict, List, Tuple
from itertools import chain
from collections import Counter

from gsppy.utils import split_into_batches, is_subsequence_in_list, generate_candidates_from_previous

logger = logging.getLogger(__name__)


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

    def __init__(self, raw_transactions: List[List[str]]):
        """
        Initialize the GSP algorithm with raw transactional data.

        Parameters:
            raw_transactions (List[List]): Input transaction dataset where each transaction
                                           is a list of items (e.g., [['A', 'B'], ['B', 'C', 'D']]).

        Attributes Initialized:
            - Processes the input raw transaction dataset.
            - Computes unique singleton candidates (`unique_candidates`).
            - Extracts the maximum transaction size (`max_size`) from the dataset for limiting
              the search space.

        Raises:
            ValueError: If the input transaction dataset is empty, contains
                        fewer than two transactions, or is not properly formatted.
        """
        self.freq_patterns: List[Dict[Tuple[str, ...], int]] = []
        self._pre_processing(raw_transactions)

    def _pre_processing(self, raw_transactions: List[List[str]]) -> None:
        """
        Validate and preprocess the input transactional dataset.

        This method ensures that the dataset is formatted correctly and converts the transactions
        into tuples while counting unique singleton candidates for initial support computation steps.

        Parameters:
            raw_transactions (List[List]): Input transactional data.

        Attributes Set:
            - `transactions`: The preprocessed transactions converted to tuples.
            - `unique_candidates`: A list of unique singleton candidates derived from the dataset.
            - `max_size`: The length of the largest transaction in the data.

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
        self.max_size = max(len(item) for item in raw_transactions)
        self.transactions: List[Tuple[str, ...]] = [tuple(transaction) for transaction in raw_transactions]
        counts: Counter[str] = Counter(chain.from_iterable(raw_transactions))
        self.unique_candidates: list[tuple[str, Any]] = [(item,) for item in counts.keys()]
        logger.debug("Unique candidates: %s", self.unique_candidates)

    @staticmethod
    def _worker_batch(
        batch: List[Tuple[str, ...]],
        transactions: List[Tuple[str, ...]],
        min_support: int
    ) -> List[Tuple[Tuple[str, ...], int]]:
        """
        Evaluate a batch of candidate sequences to compute their support.

        This method iterates over the candidates in the given batch and checks their frequency
        of appearance across all transactions. Candidates meeting the user-defined minimum
        support threshold are returned.

        Parameters:
            batch (List[Tuple]): A batch of candidate sequences, where each sequence is represented as a tuple.
            transactions (List[Tuple]): Preprocessed transactions as tuples.
            min_support (int): Absolute minimum support count required for a candidate to be considered frequent.

        Returns:
            List[Tuple[Tuple, int]]: A list of tuples where each tuple contains:
                                     - A candidate sequence.
                                     - The candidate's support count.
        """
        results: List[Tuple[Tuple[str, ...], int]] = []
        for item in batch:
            frequency = sum(1 for t in transactions if is_subsequence_in_list(item, t))
            if frequency >= min_support:
                results.append((item, frequency))
        return results

    def _support(
        self,
        items: List[Tuple[str, ...]], min_support: float = 0, batch_size: int = 100
    ) -> Dict[Tuple[str, ...], int]:
        """
        Calculate support counts for candidate sequences, using parallel processing.

        To improve efficiency, candidate sequences are processed in parallel batches using the
        `multiprocessing` module. Each sequence is checked against transactions, and its support
        count is calculated.

        Parameters:
            items (List[Tuple]): Candidate sequences to evaluate.
            min_support (float): Absolute minimum support count required for a sequence to be considered frequent.
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
                [(batch, self.transactions, min_support) for batch in batches]
            )

        # Flatten the list of results and convert to a dictionary
        return {item: freq for batch in batch_results for item, freq in batch}

    def _print_status(self, run: int, candidates: List[Tuple[str, ...]]) -> None:
        """
        Log progress information for the current GSP iteration.

        This method logs the number of candidate sequences generated and filtered during the
        current run of the GSP algorithm.

        Parameters:
            run (int): Current k-sequence generation level (e.g., 1 for 1-item sequences).
            candidates (List[Tuple]): Candidate sequences generated at this level.
        """
        logger.info("Run %d: %d candidates filtered to %d.",
                    run, len(candidates), len(self.freq_patterns[run - 1]))

    def search(self, min_support: float = 0.2) -> List[Dict[Tuple[str, ...], int]]:
        """
        Execute the Generalized Sequential Pattern (GSP) mining algorithm.

        This method facilitates the discovery of frequent sequential patterns
        in the input transaction dataset. Patterns are extracted iteratively at each k-sequence level,
        starting from singleton sequences, until no further frequent patterns can be found.

        Parameters:
            min_support (float): Minimum support threshold as a fraction of total transactions.
                                     For example, `0.3` means that a sequence is frequent if it
                                     appears in at least 30% of all transactions.

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
        """
        if not 0.0 < min_support <= 1.0:
            raise ValueError("Minimum support must be in the range (0.0, 1.0]")

        min_support = len(self.transactions) * min_support

        logger.info("Starting GSP algorithm with min_support=%.2f...", min_support)

        # the set of frequent 1-sequence: all singleton sequences
        # (k-itemsets/k-sequence = 1) - Initially, every item in DB is a
        # candidate
        candidates = self.unique_candidates

        # scan transactions to collect support count for each candidate
        # sequence & filter
        self.freq_patterns.append(self._support(candidates, min_support))

        # (k-itemsets/k-sequence = 1)
        k_items = 1

        self._print_status(k_items, candidates)

        # repeat until no frequent sequence or no candidate can be found
        while self.freq_patterns[k_items - 1] and k_items + 1 <= self.max_size:
            k_items += 1

            # Generate candidate sets Ck (set of candidate k-sequences) -
            # generate new candidates from the last "best" candidates filtered
            # by minimum support
            candidates = generate_candidates_from_previous(self.freq_patterns[k_items - 2])

            # candidate pruning - eliminates candidates who are not potentially
            # frequent (using support as threshold)
            self.freq_patterns.append(self._support(candidates, min_support))

            self._print_status(k_items, candidates)
        logger.info("GSP algorithm completed.")
        return self.freq_patterns[:-1]
