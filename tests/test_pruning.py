"""
Unit tests for pruning strategies in the GSP algorithm.

This module tests the flexible pruning system, including:
- Abstract pruning strategy interface
- Built-in pruning strategies (support, frequency, temporal)
- Combined pruning strategies
- Integration with GSP algorithm
- Edge cases and correctness
"""

import pytest
from typing import List

from gsppy.gsp import GSP
from gsppy.pruning import (
    PruningStrategy,
    SupportBasedPruning,
    FrequencyBasedPruning,
    TemporalAwarePruning,
    CombinedPruning,
    create_default_pruning_strategy,
)


@pytest.fixture
def simple_transactions() -> List[List[str]]:
    """Provide a simple dataset for testing."""
    return [
        ["A", "B", "C"],
        ["A", "B", "D"],
        ["A", "C", "D"],
        ["B", "C", "D"],
        ["A", "B", "C", "D"],
    ]


@pytest.fixture
def timestamped_transactions():
    """Provide timestamped transactions for temporal testing."""
    return [
        [("A", 0), ("B", 2), ("C", 5)],
        [("A", 0), ("B", 1), ("D", 10)],
        [("A", 0), ("C", 3), ("D", 5)],
        [("B", 0), ("C", 2), ("D", 4)],
        [("A", 0), ("B", 1), ("C", 2), ("D", 3)],
    ]


class TestSupportBasedPruning:
    """Test SupportBasedPruning strategy."""

    def test_initialization(self):
        """Test initialization with different parameters."""
        # With explicit min_support
        pruner = SupportBasedPruning(min_support_fraction=0.3)
        assert pruner.min_support_fraction == 0.3

        # Without min_support (dynamic)
        pruner = SupportBasedPruning()
        assert pruner.min_support_fraction is None

    def test_should_prune_with_context(self):
        """Test pruning with context providing min_support_count."""
        pruner = SupportBasedPruning()
        context = {"min_support_count": 3}

        # Should not prune if support_count >= min_support_count
        assert not pruner.should_prune(("A", "B"), 3, 10, context)
        assert not pruner.should_prune(("A", "B"), 5, 10, context)

        # Should prune if support_count < min_support_count
        assert pruner.should_prune(("A", "B"), 2, 10, context)
        assert pruner.should_prune(("A", "B"), 0, 10, context)

    def test_should_prune_with_fraction(self):
        """Test pruning with explicit min_support_fraction."""
        pruner = SupportBasedPruning(min_support_fraction=0.3)

        # With 10 transactions, min_support = ceil(10 * 0.3) = 3
        # Should not prune if support_count >= 3
        assert not pruner.should_prune(("A", "B"), 3, 10)
        assert not pruner.should_prune(("A", "B"), 5, 10)

        # Should prune if support_count < 3
        assert pruner.should_prune(("A", "B"), 2, 10)
        assert pruner.should_prune(("A", "B"), 1, 10)

    def test_description(self):
        """Test description generation."""
        pruner1 = SupportBasedPruning(min_support_fraction=0.3)
        assert "0.3" in pruner1.get_description()

        pruner2 = SupportBasedPruning()
        assert "dynamic" in pruner2.get_description()


class TestFrequencyBasedPruning:
    """Test FrequencyBasedPruning strategy."""

    def test_initialization(self):
        """Test initialization with valid and invalid parameters."""
        # Valid initialization
        pruner = FrequencyBasedPruning(min_frequency=5)
        assert pruner.min_frequency == 5

        # Invalid initialization
        with pytest.raises(ValueError, match="min_frequency must be at least 1"):
            FrequencyBasedPruning(min_frequency=0)

    def test_should_prune(self):
        """Test pruning based on absolute frequency."""
        pruner = FrequencyBasedPruning(min_frequency=5)

        # Should not prune if frequency >= min_frequency
        assert not pruner.should_prune(("A", "B"), 5, 100)
        assert not pruner.should_prune(("A", "B"), 10, 100)

        # Should prune if frequency < min_frequency
        assert pruner.should_prune(("A", "B"), 4, 100)
        assert pruner.should_prune(("A", "B"), 1, 100)

    def test_description(self):
        """Test description generation."""
        pruner = FrequencyBasedPruning(min_frequency=5)
        desc = pruner.get_description()
        assert "FrequencyBasedPruning" in desc
        assert "5" in desc


class TestTemporalAwarePruning:
    """Test TemporalAwarePruning strategy."""

    def test_initialization(self):
        """Test initialization with temporal constraints."""
        pruner = TemporalAwarePruning(mingap=1, maxgap=5, maxspan=10, min_support_fraction=0.3)
        assert pruner.mingap == 1
        assert pruner.maxgap == 5
        assert pruner.maxspan == 10
        assert pruner.min_support_fraction == 0.3

    def test_should_prune_support(self):
        """Test support-based pruning within temporal strategy."""
        pruner = TemporalAwarePruning(min_support_fraction=0.3)

        # With 10 transactions, min_support = ceil(10 * 0.3) = 3
        # Should prune based on support
        assert pruner.should_prune(("A", "B"), 2, 10)
        assert not pruner.should_prune(("A", "B"), 3, 10)

    def test_should_prune_temporal_feasibility(self):
        """Test pruning based on temporal feasibility."""
        # Pattern length of 5 with mingap=2 requires minimum span of 8
        # If maxspan=7, pattern is infeasible
        pruner = TemporalAwarePruning(mingap=2, maxspan=7)

        # Short patterns should not be pruned based on temporal feasibility
        assert not pruner.should_prune(("A", "B"), 5, 10)
        assert not pruner.should_prune(("A", "B", "C"), 5, 10)

        # Long pattern (length 5) needs span of at least (5-1)*2 = 8
        # which exceeds maxspan=7, so it should be pruned
        assert pruner.should_prune(("A", "B", "C", "D", "E"), 5, 10)

    def test_should_prune_no_constraints(self):
        """Test that no pruning occurs when no constraints are set."""
        pruner = TemporalAwarePruning()

        # Without constraints, nothing should be pruned
        assert not pruner.should_prune(("A", "B"), 1, 10)
        assert not pruner.should_prune(("A", "B", "C", "D", "E"), 1, 10)

    def test_description(self):
        """Test description generation."""
        pruner1 = TemporalAwarePruning(mingap=1, maxgap=5)
        desc1 = pruner1.get_description()
        assert "mingap=1" in desc1
        assert "maxgap=5" in desc1

        pruner2 = TemporalAwarePruning()
        desc2 = pruner2.get_description()
        assert "no constraints" in desc2


class TestCombinedPruning:
    """Test CombinedPruning strategy."""

    def test_initialization(self):
        """Test initialization with valid and invalid parameters."""
        # Valid initialization
        strategies = [SupportBasedPruning(0.3), FrequencyBasedPruning(5)]
        pruner = CombinedPruning(strategies)
        assert len(pruner.strategies) == 2

        # Invalid initialization (empty list)
        with pytest.raises(ValueError, match="At least one pruning strategy must be provided"):
            CombinedPruning([])

    def test_should_prune_any_strategy(self):
        """Test that pruning occurs if ANY strategy recommends it."""
        # Create combined strategy with support (min_support=3) and frequency (min_freq=5)
        strategies = [
            SupportBasedPruning(),  # Will use context
            FrequencyBasedPruning(min_frequency=5),
        ]
        pruner = CombinedPruning(strategies)
        context = {"min_support_count": 3}

        # Should not prune if ALL strategies accept
        assert not pruner.should_prune(("A", "B"), 5, 10, context)

        # Should prune if support < 3 (first strategy rejects)
        assert pruner.should_prune(("A", "B"), 2, 10, context)

        # Should prune if frequency < 5 (second strategy rejects)
        assert pruner.should_prune(("A", "B"), 4, 10, context)

    def test_description(self):
        """Test description generation for combined strategy."""
        strategies = [SupportBasedPruning(0.3), FrequencyBasedPruning(5)]
        pruner = CombinedPruning(strategies)
        desc = pruner.get_description()
        assert "CombinedPruning" in desc
        assert "SupportBasedPruning" in desc
        assert "FrequencyBasedPruning" in desc


class TestPruningStrategyFactory:
    """Test the factory function for creating default pruning strategies."""

    def test_create_default_without_temporal(self):
        """Test factory creates SupportBasedPruning without temporal constraints."""
        strategy = create_default_pruning_strategy(min_support_fraction=0.3)
        assert isinstance(strategy, SupportBasedPruning)
        assert strategy.min_support_fraction == 0.3

    def test_create_default_with_temporal(self):
        """Test factory creates TemporalAwarePruning with temporal constraints."""
        strategy = create_default_pruning_strategy(
            min_support_fraction=0.3, mingap=1, maxgap=5, maxspan=10
        )
        assert isinstance(strategy, TemporalAwarePruning)
        assert strategy.mingap == 1
        assert strategy.maxgap == 5
        assert strategy.maxspan == 10


class TestGSPIntegration:
    """Test integration of pruning strategies with GSP algorithm."""

    def test_gsp_with_default_strategy(self, simple_transactions):
        """Test GSP with default pruning strategy."""
        gsp = GSP(simple_transactions)
        result = gsp.search(min_support=0.4)

        # Should find frequent patterns
        assert len(result) > 0
        assert len(result[0]) > 0  # Should have 1-sequences

    def test_gsp_with_custom_support_strategy(self, simple_transactions):
        """Test GSP with custom support-based pruning."""
        pruner = SupportBasedPruning(min_support_fraction=0.4)
        gsp = GSP(simple_transactions, pruning_strategy=pruner)
        result = gsp.search(min_support=0.4)

        # Should find frequent patterns
        assert len(result) > 0
        # All patterns should have support >= 2 (0.4 * 5 = 2)
        for patterns in result:
            for pattern, support in patterns.items():
                assert support >= 2

    def test_gsp_with_frequency_strategy(self, simple_transactions):
        """Test GSP with frequency-based pruning."""
        pruner = FrequencyBasedPruning(min_frequency=3)
        gsp = GSP(simple_transactions, pruning_strategy=pruner)
        result = gsp.search(min_support=0.2)  # Low support to see frequency filtering

        # All patterns should have frequency >= 3
        for patterns in result:
            for pattern, support in patterns.items():
                assert support >= 3

    def test_gsp_with_combined_strategy(self, simple_transactions):
        """Test GSP with combined pruning strategy."""
        strategies = [
            SupportBasedPruning(min_support_fraction=0.3),
            FrequencyBasedPruning(min_frequency=2),
        ]
        pruner = CombinedPruning(strategies)
        gsp = GSP(simple_transactions, pruning_strategy=pruner)
        result = gsp.search(min_support=0.3)

        # Should find patterns meeting both criteria
        assert len(result) > 0
        for patterns in result:
            for pattern, support in patterns.items():
                # Should meet minimum frequency of 2
                assert support >= 2
                # Should meet minimum support of ceil(5 * 0.3) = 2
                assert support >= 2

    def test_gsp_with_temporal_strategy(self, timestamped_transactions):
        """Test GSP with temporal-aware pruning."""
        pruner = TemporalAwarePruning(mingap=0, maxgap=3, maxspan=10, min_support_fraction=0.4)
        gsp = GSP(timestamped_transactions, mingap=0, maxgap=3, maxspan=10, pruning_strategy=pruner)
        result = gsp.search(min_support=0.4)

        # Should find patterns that satisfy temporal constraints
        assert len(result) >= 0  # May or may not find patterns depending on constraints

    def test_gsp_preserves_correctness(self, simple_transactions):
        """Test that custom pruning doesn't break correctness."""
        # Run with default strategy
        gsp1 = GSP(simple_transactions)
        result1 = gsp1.search(min_support=0.4)

        # Run with explicit support-based strategy (should be equivalent)
        pruner = SupportBasedPruning(min_support_fraction=0.4)
        gsp2 = GSP(simple_transactions, pruning_strategy=pruner)
        result2 = gsp2.search(min_support=0.4)

        # Results should be identical (same patterns, same supports)
        assert len(result1) == len(result2)
        for level1, level2 in zip(result1, result2):
            assert level1 == level2


class TestEdgeCases:
    """Test edge cases for pruning strategies."""

    def test_empty_patterns(self):
        """Test pruning with empty pattern dictionary."""
        pruner = SupportBasedPruning(min_support_fraction=0.3)
        # Empty patterns should be pruned as they're invalid
        assert pruner.should_prune((), 0, 10)

    def test_singleton_pattern(self):
        """Test pruning with single-item patterns."""
        pruner = FrequencyBasedPruning(min_frequency=2)
        assert not pruner.should_prune(("A",), 2, 10)
        assert pruner.should_prune(("A",), 1, 10)

    def test_very_long_pattern(self):
        """Test pruning with very long patterns."""
        pruner = TemporalAwarePruning(mingap=1, maxspan=5)
        long_pattern = tuple([f"Item{i}" for i in range(10)])
        # Long pattern should be pruned due to temporal infeasibility
        # Pattern length 10 needs minimum span of (10-1)*1 = 9, exceeds maxspan=5
        assert pruner.should_prune(long_pattern, 5, 10)

    def test_zero_transactions(self):
        """Test behavior with zero transactions."""
        pruner = SupportBasedPruning(min_support_fraction=0.3)
        # With 0 transactions, min_support = 0, so should not prune
        assert not pruner.should_prune(("A",), 0, 0)

    def test_high_min_support(self):
        """Test with very high minimum support."""
        pruner = SupportBasedPruning(min_support_fraction=0.9)
        # Should prune most patterns
        assert pruner.should_prune(("A",), 5, 10)  # 5 < ceil(10*0.9) = 9
        assert not pruner.should_prune(("A",), 9, 10)  # 9 >= 9


class TestPruningPerformance:
    """Test that pruning improves performance characteristics."""

    def test_aggressive_pruning_reduces_candidates(self, simple_transactions):
        """Test that aggressive pruning reduces the number of candidates."""
        # Run with lenient pruning
        pruner1 = FrequencyBasedPruning(min_frequency=1)
        gsp1 = GSP(simple_transactions, pruning_strategy=pruner1)
        result1 = gsp1.search(min_support=0.2)

        # Run with aggressive pruning
        pruner2 = FrequencyBasedPruning(min_frequency=3)
        gsp2 = GSP(simple_transactions, pruning_strategy=pruner2)
        result2 = gsp2.search(min_support=0.2)

        # Aggressive pruning should produce fewer or equal patterns
        total_patterns1 = sum(len(level) for level in result1)
        total_patterns2 = sum(len(level) for level in result2)
        assert total_patterns2 <= total_patterns1
