# Pruning Strategies

GSP-Py provides a flexible pruning system that allows you to customize how candidate sequences are filtered during pattern mining. This document describes the pruning strategies in detail, their use cases, and performance characteristics.

## Overview

Candidate pruning is a critical optimization in the GSP algorithm. By filtering out non-promising candidates early, we can:

- **Reduce computation time** by avoiding support calculation for unlikely patterns
- **Decrease memory usage** by storing fewer candidates
- **Focus on relevant patterns** based on domain-specific criteria

## Architecture

The pruning system is built around an abstract `PruningStrategy` interface:

```python
class PruningStrategy(ABC):
    @abstractmethod
    def should_prune(
        self,
        candidate: Tuple[str, ...],
        support_count: int,
        total_transactions: int,
        context: Optional[Dict] = None,
    ) -> bool:
        """Return True to prune (filter out) the candidate, False to keep it."""
        pass
```

This design allows:
- Easy implementation of custom strategies
- Composition of multiple strategies
- Runtime strategy selection
- Backward compatibility (default strategy maintains original behavior)

## Built-in Strategies

### 1. SupportBasedPruning

**Description**: The classic GSP pruning based on minimum support threshold.

**Parameters**:
- `min_support_fraction` (Optional[float]): Minimum support as a fraction (0.0, 1.0]

**Behavior**:
- Prunes candidates with support count below the minimum support threshold
- If no fraction is specified, uses the value from `search()` parameters
- This is the default strategy used when none is specified

**Example**:
```python
from gsppy.gsp import GSP
from gsppy.pruning import SupportBasedPruning

pruner = SupportBasedPruning(min_support_fraction=0.3)
gsp = GSP(transactions, pruning_strategy=pruner)
result = gsp.search(min_support=0.3)
```

**Use Cases**:
- General-purpose sequential pattern mining
- When you want standard GSP behavior
- Baseline for comparing other strategies

**Performance**: Moderate pruning, baseline performance

---

### 2. FrequencyBasedPruning

**Description**: Prunes candidates based on absolute frequency (minimum occurrences).

**Parameters**:
- `min_frequency` (int): Minimum number of occurrences required (must be >= 1)

**Behavior**:
- Prunes candidates that appear fewer than `min_frequency` times
- Independent of dataset size (unlike support-based)
- Useful when you need patterns to occur a minimum absolute number of times

**Example**:
```python
from gsppy.pruning import FrequencyBasedPruning

# Require patterns to appear at least 10 times
pruner = FrequencyBasedPruning(min_frequency=10)
gsp = GSP(transactions, pruning_strategy=pruner)
result = gsp.search(min_support=0.1)
```

**Use Cases**:
- Large datasets where you want patterns with significant absolute frequency
- When relative support is less important than occurrence count
- Filtering rare patterns regardless of dataset size

**Performance**: High pruning for large datasets, faster execution

**Tradeoffs**:
- May miss patterns with low absolute frequency but high relative support in small datasets
- More aggressive than support-based for large datasets

---

### 3. TemporalAwarePruning

**Description**: Optimizes pruning for time-constrained pattern mining by pre-filtering infeasible patterns.

**Parameters**:
- `mingap` (Optional[float]): Minimum time gap between consecutive items
- `maxgap` (Optional[float]): Maximum time gap between consecutive items
- `maxspan` (Optional[float]): Maximum time span from first to last item
- `min_support_fraction` (Optional[float]): Additional support threshold

**Behavior**:
- Prunes based on support threshold (if specified)
- Pre-filters patterns that cannot satisfy temporal constraints
- Example: Pattern of length 5 with mingap=2 needs minimum span of 8
  - If maxspan=7, the pattern is infeasible and pruned immediately

**Example**:
```python
from gsppy.pruning import TemporalAwarePruning

pruner = TemporalAwarePruning(
    mingap=1,
    maxgap=5,
    maxspan=10,
    min_support_fraction=0.3
)
gsp = GSP(
    timestamped_transactions,
    mingap=1,
    maxgap=5,
    maxspan=10,
    pruning_strategy=pruner
)
result = gsp.search(min_support=0.3)
```

**Use Cases**:
- Time-constrained sequential pattern mining
- Medical event sequences with time windows
- User behavior analysis with session timeouts
- Any scenario with temporal constraints

**Performance**: High pruning for temporal data, significant speedup

**Tradeoffs**:
- Only beneficial when temporal constraints are active
- Requires timestamped transactions
- Pre-filtering is based on theoretical feasibility (may prune some edge cases)

---

### 4. CombinedPruning

**Description**: Combines multiple pruning strategies using logical AND.

**Parameters**:
- `strategies` (List[PruningStrategy]): List of strategies to combine

**Behavior**:
- Prunes if ANY constituent strategy recommends pruning
- Allows aggressive filtering with multiple criteria
- Strategies are evaluated in order (short-circuit evaluation)

**Example**:
```python
from gsppy.pruning import (
    CombinedPruning,
    SupportBasedPruning,
    FrequencyBasedPruning
)

strategies = [
    SupportBasedPruning(min_support_fraction=0.3),
    FrequencyBasedPruning(min_frequency=5)
]
pruner = CombinedPruning(strategies)
gsp = GSP(transactions, pruning_strategy=pruner)
result = gsp.search(min_support=0.3)
```

**Use Cases**:
- When you need patterns to satisfy multiple criteria
- Selective pattern discovery with strict requirements
- Combining domain-specific constraints

**Performance**: Very high pruning, fastest execution

**Tradeoffs**:
- Most aggressive filtering
- May miss edge cases where patterns barely meet one criterion
- Results in fewer patterns overall

---

## Custom Pruning Strategies

You can create custom strategies by implementing the `PruningStrategy` interface:

### Example: Length-Based Pruning

```python
from gsppy.pruning import PruningStrategy
from typing import Dict, Optional, Tuple

class LengthBasedPruning(PruningStrategy):
    """Prune patterns that are too short or too long."""
    
    def __init__(self, min_length: int = 1, max_length: int = 10):
        self.min_length = min_length
        self.max_length = max_length
    
    def should_prune(
        self,
        candidate: Tuple[str, ...],
        support_count: int,
        total_transactions: int,
        context: Optional[Dict] = None,
    ) -> bool:
        length = len(candidate)
        return length < self.min_length or length > self.max_length
    
    def get_description(self) -> str:
        return f"LengthBasedPruning(min={self.min_length}, max={self.max_length})"

# Use the custom strategy
pruner = LengthBasedPruning(min_length=2, max_length=5)
gsp = GSP(transactions, pruning_strategy=pruner)
result = gsp.search(min_support=0.2)
```

### Example: Domain-Specific Pruning

```python
class DomainSpecificPruning(PruningStrategy):
    """Prune patterns based on domain rules."""
    
    def __init__(self, forbidden_items: set, required_prefix: str = None):
        self.forbidden_items = forbidden_items
        self.required_prefix = required_prefix
    
    def should_prune(
        self,
        candidate: Tuple[str, ...],
        support_count: int,
        total_transactions: int,
        context: Optional[Dict] = None,
    ) -> bool:
        # Prune if contains forbidden items
        if any(item in self.forbidden_items for item in candidate):
            return True
        
        # Prune if doesn't have required prefix
        if self.required_prefix and not candidate[0].startswith(self.required_prefix):
            return True
        
        return False

# Example usage
pruner = DomainSpecificPruning(
    forbidden_items={'error', 'invalid'},
    required_prefix='user_'
)
```

## Performance Characteristics

### Computational Complexity

| Strategy | Time Complexity | Space Complexity | Notes |
|----------|----------------|------------------|-------|
| SupportBased | O(1) per candidate | O(1) | Simple comparison |
| FrequencyBased | O(1) per candidate | O(1) | Simple comparison |
| TemporalAware | O(1) per candidate | O(1) | Simple arithmetic |
| Combined | O(k) per candidate | O(k) | k = number of strategies |

### Empirical Performance

Based on benchmarks with synthetic data (1000 transactions, 100 items vocabulary):

| Strategy | Avg. Time (s) | Speedup | Patterns Found | Pruning Rate |
|----------|--------------|---------|----------------|--------------|
| Default (Support) | 0.125 | 1.0x | 50 | Baseline |
| Explicit Support | 0.031 | 4.0x | 50 | Same |
| Frequency (min=5) | 0.032 | 3.9x | 45 | 10% more |
| Combined | 0.030 | 4.2x | 42 | 16% more |

*Note: Results vary based on dataset characteristics, support threshold, and mining parameters.*

## Best Practices

### Choosing a Strategy

1. **Start with SupportBasedPruning** - It's the standard approach and provides a good baseline
2. **Use FrequencyBasedPruning** - For large datasets where absolute frequency matters
3. **Use TemporalAwarePruning** - When mining timestamped data with temporal constraints
4. **Use CombinedPruning** - When you need multiple filtering criteria

### Configuration Tips

1. **Support Threshold**:
   - Lower values (0.1-0.3): More patterns, slower
   - Higher values (0.5-0.8): Fewer patterns, faster

2. **Frequency Threshold**:
   - Set based on dataset size: `min_frequency = int(n_transactions * min_support)`
   - Adjust based on domain requirements

3. **Temporal Constraints**:
   - Align with business rules (e.g., session timeout = 30 minutes)
   - Test different values to find optimal tradeoff

4. **Combined Strategies**:
   - Order matters: put cheaper checks first
   - Don't over-constrain: may result in no patterns

### Testing and Validation

Always validate pruning strategies on your specific dataset:

```python
# Test with different strategies
strategies = [
    ("default", None),
    ("frequency_5", FrequencyBasedPruning(min_frequency=5)),
    ("frequency_10", FrequencyBasedPruning(min_frequency=10)),
]

for name, strategy in strategies:
    gsp = GSP(transactions, pruning_strategy=strategy)
    start = time.time()
    result = gsp.search(min_support=0.2)
    elapsed = time.time() - start
    print(f"{name}: {elapsed:.3f}s, {sum(len(r) for r in result)} patterns")
```

## Benchmarking

Use the provided benchmarking script to evaluate strategies:

```bash
# Compare all strategies
python benchmarks/bench_pruning.py --strategy all --n_tx 1000 --vocab 100

# Benchmark with your parameters
python benchmarks/bench_pruning.py \
    --n_tx 5000 \
    --vocab 200 \
    --min_support 0.2 \
    --strategy all \
    --rounds 3
```

## Troubleshooting

### No Patterns Found

If pruning is too aggressive and no patterns are found:
1. Lower the support threshold
2. Reduce frequency requirements
3. Relax temporal constraints
4. Use a single strategy instead of combined

### Slow Performance

If mining is slower than expected:
1. Increase minimum support
2. Use more aggressive pruning (Combined or Frequency-based)
3. Add temporal constraints if applicable
4. Limit max pattern length with `max_k` parameter

### Unexpected Results

If results differ from expectations:
1. Verify pruning strategy configuration
2. Check that temporal constraints match your requirements
3. Compare with default strategy to identify differences
4. Enable verbose mode to see pruning statistics

## API Reference

For complete API documentation, see:
- [gsppy.pruning module documentation](api.md#gsppy.pruning)
- [GSP class documentation](api.md#gsppy.gsp.GSP)
