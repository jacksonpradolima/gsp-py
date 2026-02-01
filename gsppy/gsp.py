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

from __future__ import annotations

import math
import logging
import multiprocessing as mp
from typing import TYPE_CHECKING, Dict, List, Tuple, Union, Literal, Optional, cast, overload
from itertools import chain
from collections import Counter

from gsppy.utils import (
    has_timestamps,
    split_into_batches,
    is_subsequence_in_list,
    generate_candidates_from_previous,
    is_subsequence_in_list_with_time_constraints,
    is_itemset_format,
    normalize_to_itemsets,
    is_subsequence_with_itemsets,
    is_subsequence_with_itemsets_and_timestamps,
)
from gsppy.pruning import PruningStrategy, create_default_pruning_strategy
from gsppy.sequence import Sequence, dict_to_sequences
from gsppy.accelerate import support_counts as support_counts_accel

if TYPE_CHECKING:
    import pandas as pd
    import polars as pl

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
        raw_transactions: Union[
            List[List[str]],
            List[List[Tuple[str, float]]],
            "pl.DataFrame",
            "pl.LazyFrame",
            "pd.DataFrame",
        ],
        mingap: Optional[float] = None,
        maxgap: Optional[float] = None,
        maxspan: Optional[float] = None,
        verbose: bool = False,
        pruning_strategy: Optional[PruningStrategy] = None,
        transaction_col: Optional[str] = None,
        item_col: Optional[str] = None,
        timestamp_col: Optional[str] = None,
        sequence_col: Optional[str] = None,
    ):
        """
        Initialize the GSP algorithm with raw transactional data.

        Parameters:
            raw_transactions (Union[List[List[str]], List[List[Tuple[str, float]]], DataFrame]):
                Input transaction dataset. Accepts:
                - A list of transactions where each transaction is a list of items (e.g., [['A', 'B'], ['B', 'C', 'D']])
                - A list of transactions with timestamps (e.g., [[('A', 1.0), ('B', 2.0)]])
                - A Polars or Pandas DataFrame (requires 'gsppy[dataframe]' installation)

                When using DataFrames, you must specify either:
                - `sequence_col`: Column containing complete sequences (list format)
                - `transaction_col` and `item_col`: Columns for grouped format

            mingap (Optional[float]): Minimum time gap required between consecutive items in patterns.
            maxgap (Optional[float]): Maximum time gap allowed between consecutive items in patterns.
            maxspan (Optional[float]): Maximum time span from first to last item in patterns.
            verbose (bool): Enable verbose logging output with detailed progress information.
                           Default is False (minimal output).
            pruning_strategy (Optional[PruningStrategy]): Custom pruning strategy for candidate filtering.
                                                          If None, a default strategy is created based on
                                                          temporal constraints.
            transaction_col (Optional[str]): DataFrame only - column name for transaction IDs (grouped format).
            item_col (Optional[str]): DataFrame only - column name for items (grouped format).
            timestamp_col (Optional[str]): DataFrame only - column name for timestamps.
            sequence_col (Optional[str]): DataFrame only - column name containing sequences (sequence format).

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

        Examples:
            Basic usage with lists:

            ```python
            from gsppy.gsp import GSP

            transactions = [["A", "B"], ["B", "C", "D"]]
            gsp = GSP(transactions)
            patterns = gsp.search(min_support=0.5)
            ```

            Using Polars DataFrame (grouped format):

            ```python
            import polars as pl
            from gsppy.gsp import GSP

            df = pl.DataFrame(
                {
                    "transaction_id": [1, 1, 2, 2, 2],
                    "item": ["A", "B", "A", "C", "D"],
                }
            )
            gsp = GSP(df, transaction_col="transaction_id", item_col="item")
            patterns = gsp.search(min_support=0.5)
            ```

            Using Pandas DataFrame (sequence format):

            ```python
            import pandas as pd
            from gsppy.gsp import GSP

            df = pd.DataFrame({"sequence": [["A", "B"], ["A", "C", "D"]]})
            gsp = GSP(df, sequence_col="sequence")
            patterns = gsp.search(min_support=0.5)
            ```
        """
        self.freq_patterns: List[Dict[Tuple[str, ...], int]] = []
        self.mingap = mingap
        self.maxgap = maxgap
        self.maxspan = maxspan
        self.verbose = verbose
        self.pruning_strategy: PruningStrategy
        self._configure_logging()
        self._validate_temporal_constraints()

        # Convert DataFrame to transaction list if necessary
        transactions_to_process = self._convert_input_data(
            raw_transactions, transaction_col, item_col, timestamp_col, sequence_col
        )

        self._pre_processing(transactions_to_process)
        # Initialize default pruning strategy if none provided
        if pruning_strategy is None:
            self.pruning_strategy = create_default_pruning_strategy(
                mingap=self.mingap, maxgap=self.maxgap, maxspan=self.maxspan
            )
            logger.debug("Using default pruning strategy: %s", self.pruning_strategy.get_description())
        else:
            self.pruning_strategy = pruning_strategy

    def _convert_input_data(
        self,
        raw_transactions: Union[
            List[List[str]],
            List[List[Tuple[str, float]]],
            "pl.DataFrame",
            "pl.LazyFrame",
            "pd.DataFrame",
        ],
        transaction_col: Optional[str],
        item_col: Optional[str],
        timestamp_col: Optional[str],
        sequence_col: Optional[str],
    ) -> Union[List[List[str]], List[List[Tuple[str, float]]]]:
        """
        Convert input data to the expected transaction list format.

        This method handles both traditional list inputs and DataFrame inputs
        (Polars or Pandas). DataFrames are converted using the dataframe_adapters module.

        Parameters:
            raw_transactions: Input data (list or DataFrame)
            transaction_col: Column name for transaction IDs (DataFrame grouped format)
            item_col: Column name for items (DataFrame grouped format)
            timestamp_col: Column name for timestamps (DataFrame)
            sequence_col: Column name for sequences (DataFrame sequence format)

        Returns:
            Transaction list in the expected format

        Raises:
            ValueError: If DataFrame parameters are specified for non-DataFrame input
                       or if DataFrame conversion fails
        """
        # Check if any DataFrame-specific parameters are provided
        df_params_provided = any([transaction_col, item_col, timestamp_col, sequence_col])

        # If it's a list, validate that no DataFrame parameters were provided
        if isinstance(raw_transactions, list):
            if df_params_provided:
                raise ValueError(
                    "DataFrame parameters (transaction_col, item_col, timestamp_col, sequence_col) "
                    "cannot be used with list input"
                )
            return cast(Union[List[List[str]], List[List[Tuple[str, float]]]], raw_transactions)  # pyright: ignore[reportUnnecessaryCast]

        # Otherwise, try to convert as DataFrame
        from gsppy.dataframe_adapters import DataFrameAdapterError, dataframe_to_transactions

        try:
            logger.debug("Converting DataFrame input to transaction list")
            transactions = dataframe_to_transactions(
                raw_transactions,
                transaction_col=transaction_col,
                item_col=item_col,
                timestamp_col=timestamp_col,
                sequence_col=sequence_col,
            )
            logger.debug("Successfully converted DataFrame with %d transactions", len(transactions))
            return transactions
        except DataFrameAdapterError as e:
            msg = f"Failed to convert DataFrame input: {e}"
            logger.error(msg)
            raise ValueError(msg) from e
        except ImportError as e:
            msg = (
                "DataFrame input detected but dataframe_adapters module failed to import. "
                "Install DataFrame support with: pip install 'gsppy[dataframe]'"
            )
            logger.error(msg)
            raise ValueError(msg) from e

    def _configure_logging(self) -> None:
        """
        Configure logging for the GSP instance based on verbosity setting.

        When verbose is True, sets the module logger to DEBUG level for detailed output.
        When verbose is False, sets the module logger to WARNING level for minimal output.

        This method intentionally avoids modifying the root logger to prevent
        unexpected global logging side effects, especially in multiprocessing
        environments.
        """
        if self.verbose:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.WARNING)

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
        if self.mingap is not None and self.maxgap is not None and self.mingap > self.maxgap:
            raise ValueError("mingap cannot be greater than maxgap")

    def _pre_processing(self, raw_transactions: Union[List[List[str]], List[List[Tuple[str, float]]], List[List[List[str]]], List[List[List[Tuple[str, float]]]]]) -> None:
        """
        Validate and preprocess the input transactional dataset.

        This method ensures that the dataset is formatted correctly and converts the transactions
        into tuples while counting unique singleton candidates for initial support computation steps.
        It handles:
        - Simple flat transactions (items only): ['A', 'B', 'C']
        - Timestamped flat transactions: [('A', 1.0), ('B', 2.0)]
        - Itemset transactions: [['A', 'B'], ['C']]
        - Timestamped itemset transactions: [[('A', 1.0), ('B', 1.0)], [('C', 2.0)]]

        Parameters:
            raw_transactions: Input transactional data in any supported format

        Attributes Set:
            - `transactions`: The preprocessed transactions converted to tuples (itemset format internally)
            - `unique_candidates`: A list of unique singleton candidates derived from the dataset
            - `max_size`: The length of the largest transaction in the data (number of itemsets)
            - `has_timestamps`: Boolean indicating if transactions include timestamps
            - `has_itemsets`: Boolean indicating if transactions use itemset format

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

        # Detect if transactions have itemsets and/or timestamps by checking non-empty transactions
        self.has_timestamps = False
        self.has_itemsets = False
        
        for tx in raw_transactions:
            if tx:  # Check non-empty transactions
                # Check for itemset format first
                self.has_itemsets = is_itemset_format(tx)
                
                if self.has_itemsets:
                    # For itemset format, check if items within itemsets have timestamps
                    first_itemset = tx[0]
                    if first_itemset and isinstance(first_itemset, (list, tuple)):
                        first_item = first_itemset[0]
                        if isinstance(first_item, (tuple, list)) and len(first_item) == 2:
                            try:
                                float(first_item[1])
                                self.has_timestamps = True
                                logger.debug("Detected timestamped itemset transactions")
                            except (TypeError, ValueError):
                                pass
                        if not self.has_timestamps:
                            logger.debug("Detected itemset transactions (no timestamps)")
                else:
                    # Flat format - check for timestamps
                    tx_sequence = cast(List[Union[str, Tuple[str, float]]], tx)
                    self.has_timestamps = has_timestamps(tx_sequence)
                    if self.has_timestamps:
                        logger.debug("Detected timestamped flat transactions")
                    else:
                        logger.debug("Detected flat transactions (no timestamps)")
                break

        # Validate temporal constraints are only used with timestamps
        if (self.mingap is not None or self.maxgap is not None or self.maxspan is not None) and not self.has_timestamps:
            logger.warning(
                "Temporal constraints specified but transactions do not have timestamps. Constraints will be ignored."
            )
            # Clear temporal constraints since they cannot be applied
            self.mingap = None
            self.maxgap = None
            self.maxspan = None

        # Normalize all transactions to itemset format for internal processing
        normalized_transactions = []
        all_items_list = []
        
        for tx in raw_transactions:
            normalized_tx = normalize_to_itemsets(tx)
            normalized_transactions.append(normalized_tx)
            
            # Extract items for counting (handling both timestamped and non-timestamped)
            if self.has_timestamps:
                # Extract items from timestamped itemsets
                for itemset in normalized_tx:
                    for item_tuple in itemset:
                        if isinstance(item_tuple, tuple) and len(item_tuple) == 2:
                            all_items_list.append(item_tuple[0])
            else:
                # Extract items from non-timestamped itemsets
                for itemset in normalized_tx:
                    for item in itemset:
                        all_items_list.append(item)
        
        self.transactions = normalized_transactions
        self.max_size = max(len(tx) for tx in normalized_transactions)
        
        # Count unique items for singleton candidates
        counts: Counter[str] = Counter(all_items_list)

        # Start with singleton candidates (1-sequences)
        self.unique_candidates: List[Tuple[str, ...]] = [(item,) for item in counts.keys()]
        logger.debug("Unique candidates: %s", self.unique_candidates)

    @staticmethod
    def _worker_batch(
        batch: List[Tuple[str, ...]],
        transactions: List[Union[Tuple[str, ...], Tuple[Tuple[str, float], ...], Tuple[Tuple[str, ...], ...], Tuple[Tuple[Tuple[str, float], ...], ...]]],
        min_support: int,
        mingap: Optional[float] = None,
        maxgap: Optional[float] = None,
        maxspan: Optional[float] = None,
        use_itemset_matching: bool = True,
    ) -> List[Tuple[Tuple[str, ...], int]]:
        """
        Evaluate a batch of candidate sequences to compute their support.

        This method iterates over the candidates in the given batch and checks their frequency
        of appearance across all transactions. Candidates meeting the user-defined minimum
        support threshold are returned. Supports temporal constraints when timestamps are present
        and itemset matching when itemsets are present.

        Parameters:
            batch: A batch of candidate sequences (flat patterns as tuples)
            transactions: Preprocessed transactions (always in itemset format internally)
            min_support: Absolute minimum support count required for a candidate to be considered frequent
            mingap: Minimum time gap between consecutive items
            maxgap: Maximum time gap between consecutive items
            maxspan: Maximum time span from first to last item
            use_itemset_matching: Whether to use itemset matching (always True for normalized transactions)

        Returns:
            List of tuples containing (candidate sequence, support count) for frequent patterns
        """
        results: List[Tuple[Tuple[str, ...], int]] = []
        has_temporal = mingap is not None or maxgap is not None or maxspan is not None

        # Detect if transactions have timestamps
        first_non_empty_tx = next((t for t in transactions if t), None)
        
        # Check if timestamps are present in the itemset format
        has_timestamps_flag = False
        if first_non_empty_tx and len(first_non_empty_tx) > 0:
            first_itemset = first_non_empty_tx[0]
            if first_itemset and len(first_itemset) > 0:
                first_item = first_itemset[0]
                if isinstance(first_item, tuple) and len(first_item) == 2:
                    try:
                        float(first_item[1])
                        has_timestamps_flag = True
                    except (TypeError, ValueError):
                        pass

        for item in batch:
            # Convert flat pattern to itemset pattern (each item in its own itemset)
            pattern_as_itemsets = tuple((elem,) for elem in item)
            
            if has_timestamps_flag:
                # Use timestamped matching (with or without temporal constraints)
                frequency = sum(
                    1
                    for t in transactions
                    if is_subsequence_with_itemsets_and_timestamps(
                        pattern_as_itemsets, t, mingap=mingap, maxgap=maxgap, maxspan=maxspan
                    )
                )
            else:
                # Itemset without timestamps (standard case)
                frequency = sum(
                    1 for t in transactions if is_subsequence_with_itemsets(pattern_as_itemsets, t)
                )

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
                [(batch, self.transactions, min_support, self.mingap, self.maxgap, self.maxspan, True) for batch in batches],
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
        
        Since transactions are always normalized to itemset format internally, we always use
        the Python implementation which supports itemset matching.

        Note: Accelerated backends are not used because transactions are internally normalized
        to itemset format for consistency.
        """
        # Always use Python implementation since we normalize to itemsets internally
        return self._support_python(items, min_support, batch_size)

    def _apply_pruning(
        self, freq_patterns: Dict[Tuple[str, ...], int], min_support_count: int
    ) -> Dict[Tuple[str, ...], int]:
        """
        Apply the configured pruning strategy to filter frequent patterns.

        This method uses the pruning strategy to post-process patterns that have
        already met the minimum support threshold. Additional pruning can be applied
        based on other criteria such as temporal feasibility or frequency thresholds.

        Parameters:
            freq_patterns (Dict[Tuple[str, ...], int]): Dictionary of patterns and their support counts.
            min_support_count (int): Absolute minimum support count threshold.

        Returns:
            Dict[Tuple[str, ...], int]: Filtered patterns after applying pruning strategy.
        """
        if not freq_patterns:
            return freq_patterns

        pruned_patterns: Dict[Tuple[str, ...], int] = {}
        context = {"min_support_count": min_support_count}

        for candidate, support_count in freq_patterns.items():
            if not self.pruning_strategy.should_prune(candidate, support_count, len(self.transactions), context):
                pruned_patterns[candidate] = support_count

        num_pruned = len(freq_patterns) - len(pruned_patterns)
        if num_pruned > 0:
            logger.debug("Pruning strategy filtered out %d additional candidates", num_pruned)

        return pruned_patterns

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

    @overload
    def search(
        self,
        min_support: float = 0.2,
        max_k: Optional[int] = None,
        backend: Optional[str] = None,
        verbose: Optional[bool] = None,
        *,
        return_sequences: Literal[False] = False,
    ) -> List[Dict[Tuple[str, ...], int]]: ...

    @overload
    def search(
        self,
        min_support: float = 0.2,
        max_k: Optional[int] = None,
        backend: Optional[str] = None,
        verbose: Optional[bool] = None,
        *,
        return_sequences: Literal[True],
    ) -> List[List[Sequence]]: ...

    def search(
        self,
        min_support: float = 0.2,
        max_k: Optional[int] = None,
        backend: Optional[str] = None,
        verbose: Optional[bool] = None,
        *,
        return_sequences: bool = False,
    ) -> Union[List[Dict[Tuple[str, ...], int]], List[List[Sequence]]]:
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
            verbose (Optional[bool]): Override instance verbosity setting for this search.
                                     If None, uses the instance's verbose setting.
            return_sequences (bool): If True, returns patterns as Sequence objects instead of
                                    Dict[Tuple[str, ...], int]. Defaults to False for backward
                                    compatibility. When True, returns List[List[Sequence]] where
                                    each Sequence contains items, support count, and can be extended
                                    with additional metadata.

        Returns:
            Union[List[Dict[Tuple[str, ...], int]], List[List[Sequence]]]:
                If return_sequences is False (default):
                    A list of dictionaries containing frequent patterns at each k-sequence level,
                    with patterns as keys and their support counts as values.
                If return_sequences is True:
                    A list of lists containing Sequence objects at each k-sequence level,
                    where each Sequence encapsulates the pattern items and support count.

        Raises:
            ValueError: If the minimum support threshold is not in the range `(0.0, 1.0]`.

        Logs:
            - Information about the algorithm's start, intermediate progress (candidates filtered),
              and completion.
            - Status updates for each iteration until the algorithm terminates.

        Examples:
            Basic usage without temporal constraints (default tuple-based):

            ```python
            from gsppy.gsp import GSP

            transactions = [
                ["Bread", "Milk"],
                ["Bread", "Diaper", "Beer", "Eggs"],
                ["Milk", "Diaper", "Beer", "Coke"],
            ]

            gsp = GSP(transactions)
            patterns = gsp.search(min_support=0.3)
            # Returns: [{('Bread',): 4, ('Milk',): 4, ...}, {('Bread', 'Milk'): 3, ...}, ...]
            ```

            Using Sequence objects for richer pattern representation:

            ```python
            from gsppy.gsp import GSP

            transactions = [
                ["Bread", "Milk"],
                ["Bread", "Diaper", "Beer", "Eggs"],
                ["Milk", "Diaper", "Beer", "Coke"],
            ]

            gsp = GSP(transactions)
            patterns = gsp.search(min_support=0.3, return_sequences=True)
            # Returns: [[Sequence(('Bread',), support=4), Sequence(('Milk',), support=4), ...], ...]

            # Access pattern details
            for level_patterns in patterns:
                for seq in level_patterns:
                    print(f"Pattern: {seq.items}, Support: {seq.support}")
            ```

            Usage with temporal constraints (requires timestamped transactions):

            ```python
            from gsppy.gsp import GSP

            # Transactions with timestamps (item, timestamp) pairs
            # where timestamps can be in any unit (seconds, minutes, hours, days, etc.)
            timestamped_transactions = [
                [("A", 1), ("B", 3), ("C", 5)],  # timestamps: 1, 3, 5
                [("A", 2), ("B", 10), ("C", 12)],  # timestamps: 2, 10, 12
                [("A", 1), ("C", 4)],  # timestamps: 1, 4
            ]

            # Find patterns with maxgap of 5 time units between consecutive items
            gsp = GSP(timestamped_transactions, maxgap=5)
            patterns = gsp.search(min_support=0.5)
            # Pattern ("A", "B", "C") won't be found in transaction 2
            # because gap between A and B is 8 (exceeds maxgap=5)
            ```
        """
        # Override verbosity if specified for this search
        original_verbose = self.verbose
        if verbose is not None:
            self.verbose = verbose
            self._configure_logging()

        if not 0.0 < min_support <= 1.0:
            raise ValueError("Minimum support must be in the range (0.0, 1.0]")

        logger.info(f"Starting GSP algorithm with min_support={min_support}...")
        if self.mingap is not None or self.maxgap is not None or self.maxspan is not None:
            logger.info(
                f"Using temporal constraints: mingap={self.mingap}, maxgap={self.maxgap}, maxspan={self.maxspan}"
            )

        # Clear freq_patterns for this search (allow reusing the GSP instance)
        self.freq_patterns = []

        # Convert fractional support to absolute count (ceil to preserve threshold semantics)
        abs_min_support = int(math.ceil(len(self.transactions) * float(min_support)))

        # the set of frequent 1-sequence: all singleton sequences
        # (k-itemsets/k-sequence = 1) - Initially, every item in DB is a
        # candidate
        candidates = self.unique_candidates

        # scan transactions to collect support count for each candidate
        # sequence & filter
        freq_1 = self._support(candidates, abs_min_support, backend=backend)
        # Apply pruning strategy for additional filtering
        freq_1 = self._apply_pruning(freq_1, abs_min_support)
        self.freq_patterns.append(freq_1)

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
            freq_k = self._support(candidates, abs_min_support, backend=backend)
            # Apply pruning strategy for additional filtering
            freq_k = self._apply_pruning(freq_k, abs_min_support)
            self.freq_patterns.append(freq_k)

            self._print_status(k_items, candidates)
        logger.info("GSP algorithm completed.")

        # Restore original verbosity if it was overridden
        if verbose is not None:
            self.verbose = original_verbose
            self._configure_logging()

        # Return results in the requested format
        result = self.freq_patterns[:-1]
        if return_sequences:
            # Convert Dict[Tuple[str, ...], int] to List[Sequence] for each level
            return [dict_to_sequences(level_patterns) for level_patterns in result]
        return result
