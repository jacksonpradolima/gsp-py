"""
Flexible candidate pruning strategies for the GSP algorithm.

This module provides a pluggable pruning system that allows different strategies
for filtering candidate sequences during pattern mining. The pruning strategies
can significantly impact performance and pattern discovery based on dataset
characteristics and mining requirements.

Key Features:
-------------
1. **Abstract Pruning Strategy Interface**:
    - Defines a common interface for all pruning strategies.
    - Allows custom pruning logic to be easily integrated.

2. **Built-in Pruning Strategies**:
    - **SupportBasedPruning**: Standard GSP pruning based on minimum support threshold.
    - **FrequencyBasedPruning**: Prunes candidates with low absolute frequency.
    - **TemporalAwarePruning**: Prunes candidates that violate temporal constraints.
    - **CombinedPruning**: Combines multiple pruning strategies.

3. **Performance Optimization**:
    - Early termination of candidate generation when patterns cannot be extended.
    - Reduces memory footprint by eliminating non-promising candidates early.

Example Usage:
--------------
```python
from gsppy.gsp import GSP
from gsppy.pruning import SupportBasedPruning, FrequencyBasedPruning, CombinedPruning

# Use default support-based pruning
gsp = GSP(transactions)
patterns = gsp.search(min_support=0.3)

# Use frequency-based pruning with a minimum frequency threshold
pruner = FrequencyBasedPruning(min_frequency=5)
gsp = GSP(transactions, pruning_strategy=pruner)
patterns = gsp.search(min_support=0.3)

# Combine multiple pruning strategies
combined = CombinedPruning([
    SupportBasedPruning(),
    FrequencyBasedPruning(min_frequency=3)
])
gsp = GSP(transactions, pruning_strategy=combined)
patterns = gsp.search(min_support=0.3)
```

Author:
-------
- **Developed by:** Jackson Antonio do Prado Lima
- **Email:** jacksonpradolima@gmail.com

License:
--------
This implementation is distributed under the MIT License.
"""

import math
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Optional


class PruningStrategy(ABC):
    """
    Abstract base class for candidate pruning strategies.

    A pruning strategy determines which candidate sequences should be
    filtered out during the GSP algorithm's candidate generation phase.
    Custom pruning strategies can be implemented by subclassing this class
    and implementing the `should_prune` method.
    """

    @abstractmethod
    def should_prune(
        self,
        candidate: Tuple[str, ...],
        support_count: int,
        total_transactions: int,
        context: Optional[Dict] = None,
    ) -> bool:
        """
        Determine whether a candidate sequence should be pruned.

        Parameters:
            candidate (Tuple[str, ...]): The candidate sequence to evaluate.
            support_count (int): The support count of the candidate in the dataset.
            total_transactions (int): Total number of transactions in the dataset.
            context (Optional[Dict]): Additional context information for pruning decisions.
                                     May include temporal constraints, pattern length, etc.

        Returns:
            bool: True if the candidate should be pruned (filtered out), False otherwise.
        """
        pass

    def get_description(self) -> str:
        """
        Get a human-readable description of the pruning strategy.

        Returns:
            str: Description of the pruning strategy.
        """
        return self.__class__.__name__


class SupportBasedPruning(PruningStrategy):
    """
    Standard GSP pruning based on minimum support threshold.

    This is the default pruning strategy used in the classic GSP algorithm.
    Candidates are pruned if their support count is below the minimum support
    threshold.

    Parameters:
        min_support_fraction (Optional[float]): Minimum support as a fraction (0.0, 1.0].
                                                If None, uses the value from search parameters.
    """

    def __init__(self, min_support_fraction: Optional[float] = None):
        """
        Initialize support-based pruning strategy.

        Parameters:
            min_support_fraction (Optional[float]): Minimum support threshold.
                                                   If None, uses the value from search.
        """
        self.min_support_fraction = min_support_fraction

    def should_prune(
        self,
        candidate: Tuple[str, ...],
        support_count: int,
        total_transactions: int,
        context: Optional[Dict] = None,
    ) -> bool:
        """
        Prune candidates below the minimum support threshold.

        Parameters:
            candidate: The candidate sequence.
            support_count: Support count of the candidate.
            total_transactions: Total number of transactions.
            context: Optional context with 'min_support_count' key.

        Returns:
            bool: True if support_count < min_support_count, False otherwise.
        """
        # Use min_support_count from context if provided, otherwise calculate from fraction
        if context and "min_support_count" in context:
            min_support_count = context["min_support_count"]
        elif self.min_support_fraction is not None:
            min_support_count = int(math.ceil(total_transactions * self.min_support_fraction))
        else:
            # If no threshold specified, don't prune
            return False

        return support_count < min_support_count

    def get_description(self) -> str:
        """Get description of this pruning strategy."""
        if self.min_support_fraction is not None:
            return f"SupportBasedPruning(min_support={self.min_support_fraction})"
        return "SupportBasedPruning(dynamic)"


class FrequencyBasedPruning(PruningStrategy):
    """
    Prunes candidates based on absolute frequency threshold.

    This strategy prunes candidates that appear fewer times than a specified
    minimum frequency, regardless of the dataset size. Useful for datasets
    where you want to ensure patterns appear a minimum number of times.

    Parameters:
        min_frequency (int): Minimum absolute frequency threshold.
    """

    def __init__(self, min_frequency: int):
        """
        Initialize frequency-based pruning strategy.

        Parameters:
            min_frequency (int): Minimum number of occurrences required.
        """
        if min_frequency < 1:
            raise ValueError("min_frequency must be at least 1")
        self.min_frequency = min_frequency

    def should_prune(
        self,
        candidate: Tuple[str, ...],
        support_count: int,
        total_transactions: int,
        context: Optional[Dict] = None,
    ) -> bool:
        """
        Prune candidates with frequency below the minimum threshold.

        Parameters:
            candidate: The candidate sequence.
            support_count: Support count (frequency) of the candidate.
            total_transactions: Total number of transactions (unused).
            context: Optional context (unused).

        Returns:
            bool: True if support_count < min_frequency, False otherwise.
        """
        return support_count < self.min_frequency

    def get_description(self) -> str:
        """Get description of this pruning strategy."""
        return f"FrequencyBasedPruning(min_frequency={self.min_frequency})"


class TemporalAwarePruning(PruningStrategy):
    """
    Prunes candidates based on temporal constraint feasibility.

    This strategy can pre-filter candidates that are unlikely to satisfy
    temporal constraints (mingap, maxgap, maxspan) based on pattern structure
    and candidate length.

    Parameters:
        mingap (Optional[float]): Minimum time gap between consecutive items.
        maxgap (Optional[float]): Maximum time gap between consecutive items.
        maxspan (Optional[float]): Maximum time span from first to last item.
        min_support_fraction (Optional[float]): Additional support threshold.
    """

    def __init__(
        self,
        mingap: Optional[float] = None,
        maxgap: Optional[float] = None,
        maxspan: Optional[float] = None,
        min_support_fraction: Optional[float] = None,
    ):
        """
        Initialize temporal-aware pruning strategy.

        Parameters:
            mingap: Minimum time gap constraint.
            maxgap: Maximum time gap constraint.
            maxspan: Maximum time span constraint.
            min_support_fraction: Additional support threshold.
        """
        self.mingap = mingap
        self.maxgap = maxgap
        self.maxspan = maxspan
        self.min_support_fraction = min_support_fraction

    def should_prune(
        self,
        candidate: Tuple[str, ...],
        support_count: int,
        total_transactions: int,
        context: Optional[Dict] = None,
    ) -> bool:
        """
        Prune candidates based on temporal feasibility and support.

        This method performs two checks:
        1. Support-based pruning (if min_support is specified)
        2. Temporal feasibility check (pattern length vs constraints)

        Parameters:
            candidate: The candidate sequence.
            support_count: Support count of the candidate.
            total_transactions: Total number of transactions.
            context: Optional context with 'min_support_count' key.

        Returns:
            bool: True if candidate should be pruned, False otherwise.
        """
        # First check support threshold if specified
        if self.min_support_fraction is not None:
            min_support_count = int(math.ceil(total_transactions * self.min_support_fraction))
            if support_count < min_support_count:
                return True
        elif context and "min_support_count" in context:
            if support_count < context["min_support_count"]:
                return True

        # Check temporal feasibility
        # If we have maxspan and mingap, check if pattern length is feasible
        if self.maxspan is not None and self.mingap is not None and len(candidate) > 1:
            # Minimum possible span for this pattern length
            min_possible_span = (len(candidate) - 1) * self.mingap
            if min_possible_span > self.maxspan:
                # Pattern is too long to fit within maxspan given mingap
                return True

        return False

    def get_description(self) -> str:
        """Get description of this pruning strategy."""
        parts = []
        if self.mingap is not None:
            parts.append(f"mingap={self.mingap}")
        if self.maxgap is not None:
            parts.append(f"maxgap={self.maxgap}")
        if self.maxspan is not None:
            parts.append(f"maxspan={self.maxspan}")
        if self.min_support_fraction is not None:
            parts.append(f"min_support={self.min_support_fraction}")
        params = ", ".join(parts) if parts else "no constraints"
        return f"TemporalAwarePruning({params})"


class CombinedPruning(PruningStrategy):
    """
    Combines multiple pruning strategies using logical AND.

    A candidate is pruned if ANY of the constituent strategies determines
    it should be pruned. This allows combining different pruning criteria
    for more aggressive filtering.

    Parameters:
        strategies (List[PruningStrategy]): List of pruning strategies to combine.
    """

    def __init__(self, strategies: List[PruningStrategy]):
        """
        Initialize combined pruning strategy.

        Parameters:
            strategies: List of pruning strategies to apply.
        """
        if not strategies:
            raise ValueError("At least one pruning strategy must be provided")
        self.strategies = strategies

    def should_prune(
        self,
        candidate: Tuple[str, ...],
        support_count: int,
        total_transactions: int,
        context: Optional[Dict] = None,
    ) -> bool:
        """
        Prune candidate if ANY strategy recommends pruning.

        Parameters:
            candidate: The candidate sequence.
            support_count: Support count of the candidate.
            total_transactions: Total number of transactions.
            context: Optional context for pruning decisions.

        Returns:
            bool: True if any strategy recommends pruning, False otherwise.
        """
        for strategy in self.strategies:
            if strategy.should_prune(candidate, support_count, total_transactions, context):
                return True
        return False

    def get_description(self) -> str:
        """Get description of this combined pruning strategy."""
        strategy_descs = [s.get_description() for s in self.strategies]
        return f"CombinedPruning([{', '.join(strategy_descs)}])"


def create_default_pruning_strategy(
    min_support_fraction: Optional[float] = None,
    mingap: Optional[float] = None,
    maxgap: Optional[float] = None,
    maxspan: Optional[float] = None,
) -> PruningStrategy:
    """
    Create an appropriate default pruning strategy based on parameters.

    This factory function selects the best pruning strategy based on the
    provided parameters:
    - If temporal constraints are specified, uses TemporalAwarePruning
    - Otherwise, uses standard SupportBasedPruning

    Parameters:
        min_support_fraction: Minimum support threshold.
        mingap: Minimum time gap constraint.
        maxgap: Maximum time gap constraint.
        maxspan: Maximum time span constraint.

    Returns:
        PruningStrategy: An appropriate pruning strategy instance.
    """
    has_temporal = mingap is not None or maxgap is not None or maxspan is not None

    if has_temporal:
        return TemporalAwarePruning(
            mingap=mingap, maxgap=maxgap, maxspan=maxspan, min_support_fraction=min_support_fraction
        )
    else:
        return SupportBasedPruning(min_support_fraction=min_support_fraction)
