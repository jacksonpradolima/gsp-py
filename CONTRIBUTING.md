# Contributing to GSP-Py

Thank you for considering contributing to **GSP-Py**, a Python implementation of the Generalized Sequential Pattern algorithm! Contributions, whether they're reporting bugs, suggesting improvements, or submitting code, are greatly appreciated. Please review this document to understand how you can contribute effectively.

---

## How Can You Contribute?

Here are some ways to contribute to the project:
1. **Report Bugs**: If you encounter any issues, please let us know by submitting a bug report.
2. **Suggest Enhancements**: Suggest new features or improvements.
3. **Fix Bugs or Add Features**: Help fix issues or implement features based on the project's roadmap or your own ideas.
4. **Improve Documentation**: Correct typos, add usage examples, or expand explanations in the documentation.
5. **Write Tests**: Testing is an essential component to ensure a reliable library.

---

## Workflow for Contributors

If you'd like to contribute code or documentation, please follow these steps:

### **1. Fork the Repository**
- Visit the [GSP-Py repository](https://github.com/jacksonpradolima/gsp-py) and click "Fork."

### **2. Clone the Fork**
Clone the forked repository to your local machine:
```bash
git clone https://github.com/<your-username>/gsp-py.git
cd gsp-py
```

### **3. Create a New Branch**
Create a new branch for your work:
```bash
git checkout -b feature/my-feature
```
Use a descriptive branch name, such as `fix/issue-123` or `feature/custom-filter-support`.

### **4. Make Changes**
- Edit and test your code locally.
- Ensure any new features include unit tests.

### **5. Run Tests**
Before submitting your changes, ensure the code passes all tests:
```bash
pytest
```

If you're adding a new feature, include tests for it in the `tests/` directory.

### **6. Push Changes**
Push your changes to your forked repository:
```bash
git add .
git commit -m "Add a brief but descriptive commit message"
git push origin feature/my-feature
```

### **7. Submit a Pull Request (PR)**
- Navigate to the main repository's GitHub page and select **Pull Requests**.
- Click **New Pull Request** and provide details about your changes, including:
  - A clear summary of your contribution.
  - Any relevant references (e.g., a related issue or feature request).
- Be sure to reference the associated issue (if applicable) in your PR description (e.g., "Closes #12").

---

## Coding Standards and Guidelines

To maintain consistency and code quality, please follow these coding guidelines:

1. **Formatting**:
   - Follow [PEP 8](https://peps.python.org/pep-0008/) for Python code style conventions.
   - Use tools like `pylint` or `flake8` to ensure your code is formatted correctly:
     ```bash
     pylint path/to/file.py
     ```

2. **Commit Messages**:
   - Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification.
   - Use the format: `<type>(<scope>): <description>`
   - Common types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`
   - Examples:
     - `feat(cli): add export format option`
     - `fix: correct off-by-one error in pattern matching`
     - `docs: update installation instructions`
   - For breaking changes, add `!` after type/scope or include `BREAKING CHANGE:` in the footer
   - See [Release Management Guide](docs/RELEASE_MANAGEMENT.md) for details

3. **Tests**:
   - Write tests for new features or bug fixes.
   - Use `pytest` as the testing framework.
   - Place tests in the `tests/` directory using descriptive test names.
   - Consider property-based tests for robust validation (see Property-Based Testing section below).

4. **Documentation**:
   - Update documentation (`README.md`, `CHANGELOG.md`, comments in code) related to your changes.
   - If a new feature is added, provide usage examples and explanation.

---

## Getting Started with the Codebase

To get familiar with the existing code, follow these steps:

1. **Setup Environment**:
    This project uses [uv](https://github.com/astral-sh/uv) for managing dependencies and the virtual environment. Follow these instructions to set it up:

    - Install uv (if not already installed):
       ```bash
       curl -Ls https://astral.sh/uv/install.sh | bash
       ```

       Make sure uv's binary directory is added to your `PATH`:
       ```bash
       export PATH="$HOME/.local/bin:$PATH"
       ```

    - Create the virtual environment and install dependencies from uv.lock:
       ```bash
       uv venv .venv
       uv sync --frozen --extra dev
       uv pip install -e .
       ```

       This will create a local `.venv` and install project dependencies.

2. **Run Tests**:
   Use uv to run tests and verify the baseline state:
   ```bash
   uv run pytest -n auto
   ```

   This will execute tests in parallel using pytest-xdist if available.

   Note: This project integrates the "tox-uv" plugin. When running `tox` locally (or `make tox`), missing Python interpreters can be provisioned automatically via uv, so you don't need to have all versions installed ahead of time.

4. **Optional: Rust Acceleration**

Some hot loops can be accelerated with Rust via PyO3. This is entirely optional: the library will fall back to pure Python if the extension is not present.

- Install Rust and build the extension:
   ```bash
   make rust-build
   ```

- Choose backend at runtime (defaults to auto):
   ```bash
   export GSPPY_BACKEND=rust   # or python, or unset for auto
   ```

- Run a benchmark (small):
   ```bash
   make bench-small
   ```

- Run a larger benchmark (adjust to your machine):
   ```bash
   make bench-big
   # or customize:
   GSPPY_BACKEND=auto uv run --python .venv/bin/python --no-project \
      python benchmarks/bench_support.py --n_tx 1000000 --tx_len 8 --vocab 50000 --min_support 0.2 --warmup
   ```

3. **Explore the Code**:
   The main entry point for the GSP algorithm is in the `gsppy` module. The libraries for support counting, candidate generation, and additional utility functions are also within this module.

---

### Notes:
- No need to manage a global virtualenv manually; uv will create and manage `.venv` as desired.
- If you’re unfamiliar with uv, refer to its [documentation](https://github.com/astral-sh/uv).

### Makefile and pre-commit
- Useful Makefile targets:
   - `make setup`, `make install`, `make test`, `make lint`, `make format`, `make typecheck`
   - `make pre-commit-install` to install the pre-commit hook
   - `make pre-commit-run` to run on all files
- To set up pre-commit manually: `uv run pre-commit install`

---

## Property-Based Testing with Hypothesis

GSP-Py uses [Hypothesis](https://hypothesis.readthedocs.io/) for property-based testing (fuzzing), which automatically generates test cases to discover edge cases and ensure robustness.

### What is Property-Based Testing?

Rather than writing individual test cases with specific inputs, property-based testing defines **properties** (invariants) that should hold for all inputs. Hypothesis then generates hundreds of random test cases to verify these properties.

### Running Fuzzing Tests

All property-based tests use the `@given` decorator from Hypothesis:

```bash
# Run all fuzzing tests
pytest tests/test_gsp_fuzzing.py tests/test_gsp_edge_cases.py tests/test_cli_fuzzing.py -v

# Run specific fuzzing test
pytest tests/test_gsp_edge_cases.py::test_gsp_handles_large_transactions -v

# Run with a fixed Hypothesis seed for reproducible fuzzing
pytest tests/test_gsp_fuzzing.py --hypothesis-seed=42
```

### Using Modular Hypothesis Strategies

GSP-Py provides reusable strategies in `tests/hypothesis_strategies.py` that you can compose for new tests:

```python
from hypothesis import given
from tests.hypothesis_strategies import (
    transaction_lists,           # Standard transaction data
    extreme_transaction_lists,   # Extreme sizes (large/many/minimal)
    sparse_transaction_lists,    # Low pattern overlap
    noisy_transaction_lists,     # Mixed signal and noise
    timestamped_transaction_lists, # Temporal data
    valid_support_thresholds,    # Valid support values
)

@given(transactions=transaction_lists())
def test_my_property(transactions):
    gsp = GSP(transactions)
    result = gsp.search(min_support=0.2)
    # Assert your property here
    assert isinstance(result, list)
```

### Available Strategies

**Basic Strategies:**
- `transaction_lists()` - Standard transaction data (2-50 transactions)
- `item_pool()` - Generate unique items for transactions
- `item_strings()` - Generate individual item strings

**Edge Case Strategies:**
- `extreme_transaction_lists(size_type="large")` - Few transactions with many items
- `extreme_transaction_lists(size_type="many")` - Many transactions (100-500)
- `extreme_transaction_lists(size_type="minimal")` - Minimal valid input (2 transactions)
- `sparse_transaction_lists()` - Low pattern overlap/sparse patterns
- `noisy_transaction_lists()` - High noise ratio with some signal
- `variable_length_transaction_lists()` - Highly variable transaction sizes

**Malformed Input Strategies:**
- `transactions_with_duplicates()` - Duplicate items within transactions
- `transactions_with_special_chars()` - Unicode, special chars, whitespace

**Temporal Strategies:**
- `timestamped_transaction_lists()` - Transactions with timestamps
- `pathological_timestamped_transactions()` - Edge cases (reversed, identical, large gaps)

**Support Threshold Strategies:**
- `valid_support_thresholds()` - Valid range (0.01-1.0)
- `edge_case_support_thresholds()` - Boundary values

### Writing New Property-Based Tests

1. **Identify the property/invariant** you want to test (e.g., "support counts should never exceed total transactions")

2. **Choose or create appropriate strategies** from `tests/hypothesis_strategies.py`

3. **Write the test using `@given`**:

```python
from hypothesis import given, settings, HealthCheck
from tests.hypothesis_strategies import transaction_lists

@given(transactions=transaction_lists())
@settings(max_examples=5, deadline=None, suppress_health_check=[HealthCheck.too_slow])
def test_gsp_my_property(transactions):
    """
    Property: Describe what invariant this test validates.
    
    Explain what the test is checking and why it matters.
    """
    gsp = GSP(transactions)
    result = gsp.search(min_support=0.2)
    
    # Assert your property
    for level_patterns in result:
        for pattern, support in level_patterns.items():
            assert support <= len(transactions), "Support cannot exceed transaction count"
```

4. **Configure test settings** as needed:
   - `max_examples`: Number of random test cases to generate (use small values like 3-10 for fast tests)
   - `deadline`: Maximum time per test case (use `None` for slow operations)
   - `suppress_health_check`: Disable specific health checks like `HealthCheck.too_slow`

**Note:** Keep `max_examples` low (3-10) to ensure tests run quickly. The fuzzing suite should complete in under a minute.

### Creating Custom Strategies

To create a new reusable strategy in `tests/hypothesis_strategies.py`:

```python
from hypothesis import strategies as st

@st.composite
def my_custom_strategy(draw: st.DrawFn, **kwargs) -> MyType:
    """
    Generate custom test data.
    
    Args:
        draw: Hypothesis draw function
        **kwargs: Custom parameters
        
    Returns:
        Generated test data
    """
    # Use draw() to generate random values
    n = draw(st.integers(min_value=1, max_value=10))
    items = draw(st.lists(st.text(), min_size=n, max_size=n))
    return items
```

### Best Practices for Property-Based Testing

1. **Test properties, not specific outputs**: Focus on invariants that should always hold
   - ✅ "All patterns should meet minimum support threshold"
   - ❌ "Transaction X should produce patterns Y"

2. **Use appropriate strategies**: Match the strategy to what you're testing
   - Testing edge cases? Use `extreme_transaction_lists()`
   - Testing noise resistance? Use `noisy_transaction_lists()`

3. **Handle expected failures gracefully**: Use `assume()` to skip invalid inputs or `pytest.raises()` for expected errors

4. **Keep tests focused**: Each test should validate one clear property

5. **Document properties clearly**: Explain what invariant is being tested in the docstring

6. **Compose strategies**: Combine existing strategies rather than creating everything from scratch

### Example: Testing a New Feature

If you're adding a new feature (e.g., new pruning strategies), create tests that:

1. **Validate basic functionality** with standard strategies
2. **Test edge cases** with extreme strategies
3. **Verify invariants** (e.g., parameters don't violate constraints)
4. **Check integration** with existing features

```python
@given(
    transactions=transaction_lists(),
)
@settings(max_examples=5, deadline=None)
def test_gsp_patterns_property(transactions):
    """Property: Returned pattern supports should stay within valid bounds."""
    gsp = GSP(transactions)
    result = gsp.search(min_support=0.2)
    
    # Verify support calculations are within expected bounds
    max_possible_support = len(transactions)
    for level_patterns in result:
        for pattern, support in level_patterns.items():
            assert 0 <= support <= max_possible_support
```

### Debugging Failed Property-Based Tests

When a property-based test fails, Hypothesis provides:
- The **specific input** that caused the failure
- A **simplified version** of that input (shrinking)
- The **random seed** to reproduce the failure

To reproduce a failure:
```bash
pytest tests/test_gsp_edge_cases.py::test_name --hypothesis-seed=12345
```

For more information, see the [Hypothesis documentation](https://hypothesis.readthedocs.io/).

---

## Running Fuzzing Tests in CI

The project's CI configuration automatically runs fuzzing tests. The tests use settings configured in each test file via the `@settings` decorator.

To run all tests (including fuzzing tests) locally:
```bash
pytest tests/
```

## Reporting Issues

To report a bug or suggest an enhancement, open an issue on GitHub:

1. **Go to the [Issues](https://github.com/jacksonpradolima/gsp-py/issues) page**.
2. Select **New Issue** and choose the appropriate issue template:
   - Bug report
   - Feature request
3. Include as much detail as possible:
   - Steps to reproduce (for bugs).
   - Clear description of the feature or enhancement (for feature requests).

---

## Feedback

We welcome all suggestions or feedback for improving this project! You can reach out by opening an issue or submitting a pull request.

Let’s build a great tool together! 😊

---

## Code of Conduct

Please note that this project adheres to the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/). By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainer.

---

Thank you for contributing! 🙌
