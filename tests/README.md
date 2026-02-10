# GSP-Py Test Suite

This directory contains comprehensive tests for the GSP-Py library, including unit tests, integration tests, and property-based fuzzing tests.

## 📋 Test Structure

### Core Algorithm Tests
- **`test_gsp.py`** - Unit tests for core GSP algorithm functionality
- **`test_sequence.py`** - Tests for sequence handling and validation
- **`test_itemsets.py`** - Tests for itemset operations
- **`test_pruning.py`** - Tests for candidate pruning logic

### Property-Based Fuzzing Tests
- **`test_gsp_fuzzing.py`** - Standard property-based tests validating algorithm invariants
- **`test_gsp_edge_cases.py`** - Extended edge-case tests (extreme sizes, sparse data, malformed inputs)
- **`test_cli_fuzzing.py`** - CLI interface fuzzing tests

### Integration Tests
- **`test_gsp_sequence_integration.py`** - Integration tests for sequence mining workflows
- **`test_dataframe.py`** - DataFrame input support tests (Polars, Pandas)
- **`test_temporal_constraints.py`** - Temporal constraint tests (mingap, maxgap, maxspan)

### CLI Tests
- **`test_cli.py`** - CLI interface tests
- **`test_cli_hooks.py`** - CLI hook system tests
- **`test_hooks.py`** - Hook mechanism tests

### Utilities
- **`test_utils.py`** - Utility function tests
- **`test_spm_format.py`** - SPM format parser tests

### Supporting Modules
- **`hypothesis_strategies.py`** - Reusable Hypothesis strategies for property-based testing
- **`run_fuzzing_tests.py`** - Script for running fuzzing test suites

## 🚀 Running Tests

### Run All Tests
```bash
# Using pytest directly (excludes slow integration tests)
pytest

# Using make
make test

# In parallel
pytest -n auto
```

### Run Specific Test Suites
```bash
# Core algorithm tests
pytest tests/test_gsp.py

# All fast fuzzing tests (excludes integration tests)
pytest tests/test_gsp_fuzzing.py tests/test_gsp_edge_cases.py tests/test_cli_fuzzing.py

# CLI tests
pytest tests/test_cli.py tests/test_cli_fuzzing.py

# DataFrame tests
pytest tests/test_dataframe.py

# Integration tests only (slow, 15+ minutes)
pytest -m integration

# All tests including integration
pytest -m "integration or not integration"
```

### Run Property-Based Fuzzing Tests

**Using the fuzzing test runner:**
```bash
# Run all fuzzing test suites (fast tests only)
python tests/run_fuzzing_tests.py

# Run specific suite
python tests/run_fuzzing_tests.py --suite edge

# Reproducible test with seed
python tests/run_fuzzing_tests.py --seed 42

# Run with coverage
python tests/run_fuzzing_tests.py --coverage
```

**Using pytest directly:**
```bash
# Standard fuzzing tests (11 tests)
pytest tests/test_gsp_fuzzing.py -v

# Extended edge-case tests (21 tests, excludes integration)
pytest tests/test_gsp_edge_cases.py -v

# CLI fuzzing tests (15+ tests)
pytest tests/test_cli_fuzzing.py -v

# Reproduce specific failure
pytest tests/test_gsp_fuzzing.py --hypothesis-seed=12345
```

### Run with Coverage
```bash
# Generate coverage report
pytest --cov=gsppy --cov-report=html --cov-report=term

# Using make
make coverage
```

## 🧪 Property-Based Testing (Fuzzing)

GSP-Py uses [Hypothesis](https://hypothesis.readthedocs.io/) for property-based testing, which automatically generates test cases to discover edge cases.

### What Properties Do We Test?

**Core Invariants:**
- ✅ Support monotonicity: Lower thresholds yield ≥ patterns
- ✅ Pattern structure: Level k contains k-length sequences
- ✅ Support compliance: All patterns meet minimum support
- ✅ Determinism: Same input → same output
- ✅ No duplicates: Patterns appear once per level

**Edge Cases:**
- ✅ Extreme transaction sizes (1-100+ items per transaction)
- ✅ Large datasets (100-500 transactions)
- ✅ Sparse patterns (low overlap)
- ✅ Noisy data (signal + random noise)
- ✅ Variable-length transactions
- ✅ Malformed inputs (duplicates, special characters, unicode)
- ✅ Temporal edge cases (identical timestamps, large gaps)
- ✅ Boundary support values (0.01, 0.99, 1.0)

**Robustness:**
- ✅ CLI argument validation
- ✅ File format handling (JSON, CSV)
- ✅ Error message quality
- ✅ Graceful degradation

### Using Hypothesis Strategies

The `hypothesis_strategies.py` module provides reusable strategies:

```python
from hypothesis import given
from tests.hypothesis_strategies import (
    transaction_lists,              # Standard transaction data
    extreme_transaction_lists,      # Extreme sizes
    sparse_transaction_lists,       # Sparse patterns
    noisy_transaction_lists,        # Noisy data
    timestamped_transaction_lists,  # Temporal data
)

@given(transactions=transaction_lists())
def test_my_property(transactions):
    gsp = GSP(transactions)
    result = gsp.search(min_support=0.2)
    # Assert property here
```

See [CONTRIBUTING.md](../CONTRIBUTING.md#property-based-testing-with-hypothesis) for detailed guidance on writing property-based tests.

## 📊 Test Coverage

To generate a coverage report:

```bash
# Generate HTML report
pytest --cov=gsppy --cov-report=html

# Open in browser
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

## 🐛 Debugging Failed Tests

### Hypothesis Test Failures

When a property-based test fails, Hypothesis provides:
1. The failing input
2. A simplified (shrunk) version
3. The random seed

**Reproduce the failure:**
```bash
pytest tests/test_gsp_fuzzing.py::test_name --hypothesis-seed=12345
```

**Debug with verbose output:**
```bash
pytest tests/test_gsp_fuzzing.py::test_name -vv --tb=long
```

### Regular Test Failures

**Run with full traceback:**
```bash
pytest tests/test_gsp.py::test_name -vv --tb=long
```

**Drop into debugger on failure:**
```bash
pytest tests/test_gsp.py::test_name --pdb
```

## 🔧 Test Configuration

Test configuration is in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--tb=short -v"
xfail_strict = true
filterwarnings = ["error"]
```

Test settings for Hypothesis are configured in each test file using the `@settings` decorator.

## 📝 Writing New Tests

### Standard Unit Tests

```python
import pytest
from gsppy.gsp import GSP

def test_my_feature():
    """Test description."""
    transactions = [['A', 'B'], ['A', 'C']]
    gsp = GSP(transactions)
    result = gsp.search(min_support=0.5)
    
    assert len(result) > 0
    # More assertions...
```

### Property-Based Tests

```python
from hypothesis import given, settings, HealthCheck
from tests.hypothesis_strategies import transaction_lists

@given(transactions=transaction_lists())
@settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.too_slow])
def test_my_property(transactions):
    """
    Property: Description of what invariant this validates.
    
    Explain the property and why it matters.
    """
    gsp = GSP(transactions)
    result = gsp.search(min_support=0.2)
    
    # Assert the property
    assert some_invariant_holds(result)
```

See [CONTRIBUTING.md](../CONTRIBUTING.md#property-based-testing-with-hypothesis) for comprehensive guidance.

## 🤝 Contributing Tests

We welcome test contributions! When adding tests:

1. **Choose the right test type:**
   - Unit test for specific functionality
   - Property-based test for invariants
   - Integration test for workflows

2. **Use descriptive names:**
   - `test_gsp_handles_empty_input` ✅
   - `test_1` ❌

3. **Document the test:**
   - What is being tested?
   - What property/behavior is validated?
   - Why does it matter?

4. **Reuse strategies:**
   - Use existing strategies from `hypothesis_strategies.py`
   - Compose strategies for complex scenarios
   - Add new strategies if needed

5. **Keep tests focused:**
   - One property per test
   - Clear assertions
   - Minimal setup

For more information, see [CONTRIBUTING.md](../CONTRIBUTING.md).

## 📚 Additional Resources

- [Hypothesis Documentation](https://hypothesis.readthedocs.io/)
- [pytest Documentation](https://docs.pytest.org/)
- [GSP-Py Contributing Guide](../CONTRIBUTING.md)
- [GSP-Py README](../README.md)

---

**Questions or issues?** Open an issue on [GitHub](https://github.com/jacksonpradolima/gsp-py/issues).
