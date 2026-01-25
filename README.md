[![Docs](https://img.shields.io/badge/Docs-GSP--Py%20Site-3D9970?style=flat-square)](https://jacksonpradolima.github.io/gsp-py/)
[![PyPI License](https://img.shields.io/pypi/l/gsppy.svg?style=flat-square)]()
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.3333987.svg)](https://doi.org/10.5281/zenodo.3333987)

[![PyPI Downloads](https://img.shields.io/pypi/dm/gsppy.svg?style=flat-square)](https://pypi.org/project/gsppy/)
[![PyPI version](https://badge.fury.io/py/gsppy.svg)](https://pypi.org/project/gsppy)
![](https://img.shields.io/badge/python-3.10+-blue.svg)

[![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/jacksonpradolima/gsp-py/badge)](https://securityscorecards.dev/viewer/?uri=github.com/jacksonpradolima/gsp-py)
[![SLSA provenance](https://github.com/jacksonpradolima/gsp-py/actions/workflows/slsa-provenance.yml/badge.svg)](https://github.com/jacksonpradolima/gsp-py/actions/workflows/slsa-provenance.yml)
[![OpenSSF Best Practices](https://www.bestpractices.dev/projects/11684/badge)](https://www.bestpractices.dev/projects/11684)

[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=jacksonpradolima_gsp-py&metric=bugs)](https://sonarcloud.io/summary/new_code?id=jacksonpradolima_gsp-py)
[![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=jacksonpradolima_gsp-py&metric=vulnerabilities)](https://sonarcloud.io/summary/new_code?id=jacksonpradolima_gsp-py)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=jacksonpradolima_gsp-py&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=jacksonpradolima_gsp-py)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=jacksonpradolima_gsp-py&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=jacksonpradolima_gsp-py)
[![codecov](https://codecov.io/github/jacksonpradolima/gsp-py/graph/badge.svg?token=o1P0qXaYtJ)](https://codecov.io/github/jacksonpradolima/gsp-py)

# GSP-Py

**GSP-Py**: A Python-powered library to mine sequential patterns in large datasets, based on the robust **Generalized
Sequence Pattern (GSP)** algorithm. Ideal for market basket analysis, temporal mining, and user journey discovery.

> [!IMPORTANT]
> GSP-Py is compatible with Python 3.10 and later versions!

---

## 📚 Table of Contents

1. [🔍 What is GSP?](#what-is-gsp)
2. [🔧 Requirements](#requirements)
3. [🚀 Installation](#installation)
    - [❖ Clone Repository](#option-1-clone-the-repository)
    - [❖ Install via PyPI](#option-2-install-via-pip)
4. [🛠️ Developer Installation](#developer-installation)
5. [📖 Documentation](#documentation)
6. [💡 Usage](#usage)
    - [✅ Example: Analyzing Sales Data](#example-analyzing-sales-data)
    - [📊 Explanation: Support and Results](#explanation-support-and-results)
    - [⏱️ Temporal Constraints](#temporal-constraints)
7. [⌨️ Typing](#typing)
8. [🌟 Planned Features](#planned-features)
9. [🤝 Contributing](#contributing)
10. [📝 License](#license)
11. [📖 Citation](#citation)

---

## 🔍 What is GSP?

The **Generalized Sequential Pattern (GSP)** algorithm is a sequential pattern mining technique based on **Apriori
principles**. Using support thresholds, GSP identifies frequent sequences of items in transaction datasets.

### Key Features:

- **Ordered (non-contiguous) matching**: Detects patterns where items appear in order but not necessarily adjacent, following standard GSP semantics. For example, the pattern `('A', 'C')` is found in the sequence `['A', 'B', 'C']`.
- **Support-based pruning**: Only retains sequences that meet the minimum support threshold.
- **Candidate generation**: Iteratively generates candidate sequences of increasing length.
- **Temporal constraints**: Support for time-constrained pattern mining with `mingap`, `maxgap`, and `maxspan` parameters to find patterns within specific time windows.
- **General-purpose**: Useful in retail, web analytics, social networks, temporal sequence mining, and more.

For example:

- In a shopping dataset, GSP can identify patterns like "Customers who buy bread and milk often purchase diapers next" - even if other items appear between bread and milk.
- In a website clickstream, GSP might find patterns like "Users visit A, then eventually go to C" - capturing user journeys with intermediate steps.

---

## 🔧 Requirements

You will need Python installed on your system. On most Linux systems, you can install Python with:

```bash
sudo apt install python3
```

For package dependencies of GSP-Py, they will automatically be installed when using `pip`.

---

## 🚀 Installation

GSP-Py can be easily installed from either the **repository** or PyPI.

### Option 1: Clone the Repository

To manually clone the repository and set up the environment:

```bash
git clone https://github.com/jacksonpradolima/gsp-py.git
cd gsp-py
```

Refer to the [Developer Installation](#developer-installation) section and run the setup with uv.

### Option 2: Install via `pip`

Alternatively, install GSP-Py from PyPI with:

```bash
pip install gsppy
```

---

## 🛠️ Developer Installation

This project now uses [uv](https://github.com/astral-sh/uv) for dependency management and virtual environments.

#### 1. Install uv
```bash
curl -Ls https://astral.sh/uv/install.sh | bash
```

Make sure uv is on your PATH (for most Linux setups):
```bash
export PATH="$HOME/.local/bin:$PATH"
```

#### 2. Set up the project environment
Create a local virtual environment and install dependencies from uv.lock (single source of truth):

```bash
uv venv .venv
uv sync --frozen --extra dev  # uses uv.lock
uv pip install -e .
```

#### 3. Optional: Enable Rust acceleration

Rust acceleration is optional and provides faster support counting using a PyO3 extension. Python fallback remains available.

Build the extension locally:
```bash
make rust-build
```

Select backend at runtime (auto tries Rust, then falls back to Python):
```bash
export GSPPY_BACKEND=rust   # or python, or unset for auto
```

Run benchmarks (adjust to your machine):
```bash
make bench-small
make bench-big   # may use significant memory/CPU
# or customize:
GSPPY_BACKEND=auto uv run --python .venv/bin/python --no-project \
  python benchmarks/bench_support.py --n_tx 1000000 --tx_len 8 --vocab 50000 --min_support 0.2 --warmup
```

#### 4. Optional: Enable GPU (CuPy) acceleration

GPU acceleration is experimental and currently optimizes singleton (k=1) support counting using CuPy.
Non-singleton candidates fall back to the Rust/Python backend.

Install the optional extra (choose a CuPy build that matches your CUDA/ROCm setup if needed):

```bash
uv run pip install -e .[gpu]
```

Select the GPU backend at runtime:

```bash
export GSPPY_BACKEND=gpu
```

If a GPU isn't available, an error will be raised when GSPPY_BACKEND=gpu is set. Otherwise, the default "auto" uses CPU.

#### 5. Common development tasks
After the environment is ready, activate it and run tasks with standard tools:

```bash
source .venv/bin/activate
pytest -n auto
ruff check .
pyright
```

If you prefer, you can also prefix commands with uv without activating:

```bash
uv run pytest -n auto
uv run ruff check .
uv run pyright
```

#### 5. Makefile (shortcuts)
You can use the Makefile to automate common tasks:

```bash
make setup               # create .venv with uv and pin Python
make install             # sync deps (from uv.lock) + install project (-e .)
make test                # pytest -n auto
make lint                # ruff check .
make format              # ruff --fix
make typecheck           # pyright + ty
make pre-commit-install  # install the pre-commit hook
make pre-commit-run      # run pre-commit on all files

# Rust-specific shortcuts
make rust-setup          # install rustup toolchain
make rust-build          # build PyO3 extension with maturin
make bench-small         # run small benchmark
make bench-big           # run large benchmark
```

> [!NOTE]
> Tox in this project uses the "tox-uv" plugin. When running `make tox` or `tox`, missing Python interpreters can be provisioned automatically via uv (no need to pre-install all versions). This makes local setup faster.

## 🔏 Release assets and verification

Every GitHub release bundles artifacts to help you validate what you download:

- Built wheels and source distributions produced by the automated publish workflow.
- `sbom.json` (CycloneDX) generated with [Syft](https://github.com/anchore/syft).
- Sigstore-generated `.sig` and `.pem` files for each artifact, created using GitHub OIDC identity.

To verify a downloaded artifact from a release:

```bash
python -m pip install sigstore  # installs the CLI
sigstore verify identity \
  --certificate gsppy-<version>-py3-none-any.whl.pem \
  --signature gsppy-<version>-py3-none-any.whl.sig \
  --cert-identity "https://github.com/jacksonpradolima/gsp-py/.github/workflows/publish.yml@refs/tags/v<version>" \
  --cert-oidc-issuer https://token.actions.githubusercontent.com \
  gsppy-<version>-py3-none-any.whl
```

Replace `<version>` with the numeric package version (for example, `3.1.1`) in the filenames; in `--cert-identity`, this becomes `v<version>` (for example, `v3.1.1`). Adjust the filenames for the sdist (`.tar.gz`) if preferred. The same release page also hosts `sbom.json` for supply-chain inspection.

## 📖 Documentation

- **Live site:** https://jacksonpradolima.github.io/gsp-py/
- **Build locally:**

  ```bash
  uv venv .venv
  uv sync --extra docs
  uv run mkdocs serve
  ```

The docs use MkDocs with the Material theme and mkdocstrings to render the Python API directly from docstrings.

## 💡 Usage

The library is designed to be easy to use and integrate with your own projects. You can use GSP-Py either programmatically (Python API) or directly from the command line (CLI).

---

## 🚦 Using GSP-Py via CLI

GSP-Py provides a command-line interface (CLI) for running the Generalized Sequential Pattern algorithm on transactional data. This allows you to mine frequent sequential patterns from JSON or CSV files without writing any code.

### Installation

First, install GSP-Py (if not already installed):

```bash
pip install gsppy
```

This will make the `gsppy` CLI command available in your environment.

### Preparing Your Data

Your input file should be either:

- **JSON**: A list of transactions, each transaction is a list of items. Example:
  ```json
  [
    ["Bread", "Milk"],
    ["Bread", "Diaper", "Beer", "Eggs"],
    ["Milk", "Diaper", "Beer", "Coke"],
    ["Bread", "Milk", "Diaper", "Beer"],
    ["Bread", "Milk", "Diaper", "Coke"]
  ]
  ```

- **CSV**: Each row is a transaction, items separated by commas. Example:
  ```csv
  Bread,Milk
  Bread,Diaper,Beer,Eggs
  Milk,Diaper,Beer,Coke
  Bread,Milk,Diaper,Beer
  Bread,Milk,Diaper,Coke
  ```

### Running the CLI

Use the following command to run GSPPy on your data:

```bash
gsppy --file path/to/transactions.json --min_support 0.3 --backend auto
```

Or for CSV files:

```bash
gsppy --file path/to/transactions.csv --min_support 0.3 --backend rust
```

#### CLI Options

- `--file`: Path to your input file (JSON or CSV). **Required**.
- `--min_support`: Minimum support threshold as a fraction (e.g., `0.3` for 30%). Default is `0.2`.
- `--backend`: Backend to use for support counting. One of `auto` (default), `python`, `rust`, or `gpu`.
- `--verbose`: Enable detailed logging with timestamps, log levels, and process IDs for debugging and traceability.
- `--mingap`, `--maxgap`, `--maxspan`: Temporal constraints for time-aware pattern mining (requires timestamped transactions).

#### Verbose Mode

For debugging or to track execution in CI/CD pipelines, use the `--verbose` flag:

```bash
gsppy --file transactions.json --min_support 0.3 --verbose
```

This produces structured logging output with timestamps, log levels, and process information:

```
2026-01-25T23:09:50 | INFO     | PID:4179 | gsppy.gsp | Pre-processing transactions...
2026-01-25T23:09:50 | DEBUG    | PID:4179 | gsppy.gsp | Unique candidates: [('Bread',), ('Milk',), ...]
2026-01-25T23:09:50 | INFO     | PID:4179 | gsppy.gsp | Starting GSP algorithm with min_support=0.3...
2026-01-25T23:09:50 | INFO     | PID:4179 | gsppy.gsp | Run 1: 6 candidates filtered to 5.
...
```

For complete logging documentation, see [docs/logging.md](docs/logging.md).

#### Example

Suppose you have a file `transactions.json` as shown above. To find patterns with at least 30% support:

```bash
gsppy --file transactions.json --min_support 0.3
```

Sample output:

```
Pre-processing transactions...
Starting GSP algorithm with min_support=0.3...
Run 1: 6 candidates filtered to 5.
Run 2: 20 candidates filtered to 3.
Run 3: 2 candidates filtered to 2.
Run 4: 1 candidates filtered to 0.
GSP algorithm completed.
Frequent Patterns Found:

1-Sequence Patterns:
Pattern: ('Bread',), Support: 4
Pattern: ('Milk',), Support: 4
Pattern: ('Diaper',), Support: 4
Pattern: ('Beer',), Support: 3
Pattern: ('Coke',), Support: 2

2-Sequence Patterns:
Pattern: ('Bread', 'Milk'), Support: 3
Pattern: ('Milk', 'Diaper'), Support: 3
Pattern: ('Diaper', 'Beer'), Support: 3

3-Sequence Patterns:
Pattern: ('Bread', 'Milk', 'Diaper'), Support: 2
Pattern: ('Milk', 'Diaper', 'Beer'), Support: 2
```

#### Error Handling

- If the file does not exist or is in an unsupported format, a clear error message will be shown.
- The `min_support` value must be between 0.0 and 1.0 (exclusive of 0.0, inclusive of 1.0).

#### Advanced: Verbose Output

To see detailed logs for debugging, add the `--verbose` flag:

```bash
gsppy --file transactions.json --min_support 0.3 --verbose
```

---

The following example shows how to use GSP-Py programmatically in Python:

### Example Input Data

The input to the algorithm is a sequence of transactions, where each transaction contains a sequence of items:

```python
transactions = [
    ['Bread', 'Milk'],
    ['Bread', 'Diaper', 'Beer', 'Eggs'],
    ['Milk', 'Diaper', 'Beer', 'Coke'],
    ['Bread', 'Milk', 'Diaper', 'Beer'],
    ['Bread', 'Milk', 'Diaper', 'Coke']
]
```

### Importing and Initializing the GSP Algorithm

Import the `GSP` class from the `gsppy` package and call the `search` method to find frequent patterns with a support
threshold (e.g., `0.3`):

```python
from gsppy.gsp import GSP

# Example transactions: customer purchases
transactions = [
    ['Bread', 'Milk'],  # Transaction 1
    ['Bread', 'Diaper', 'Beer', 'Eggs'],  # Transaction 2
    ['Milk', 'Diaper', 'Beer', 'Coke'],  # Transaction 3
    ['Bread', 'Milk', 'Diaper', 'Beer'],  # Transaction 4
    ['Bread', 'Milk', 'Diaper', 'Coke']  # Transaction 5
]

# Set minimum support threshold (30%)
min_support = 0.3

# Find frequent patterns
result = GSP(transactions).search(min_support)

# Output the results
print(result)
```

### Verbose Mode for Debugging

Enable detailed logging to track algorithm progress and debug issues:

```python
from gsppy.gsp import GSP

# Enable verbose logging for the entire instance
gsp = GSP(transactions, verbose=True)
result = gsp.search(min_support=0.3)

# Or enable verbose for a specific search only
gsp = GSP(transactions)
result = gsp.search(min_support=0.3, verbose=True)
```

Verbose mode provides:
- Detailed progress information during execution
- Candidate generation and filtering statistics
- Preprocessing and validation details
- Useful for debugging, research, and CI/CD integration

For complete documentation on logging, see [docs/logging.md](docs/logging.md).

### Output

The algorithm will return a list of patterns with their corresponding support.

Sample Output:

```python
[
    {('Bread',): 4, ('Milk',): 4, ('Diaper',): 4, ('Beer',): 3, ('Coke',): 2},
    {('Bread', 'Milk'): 3, ('Bread', 'Diaper'): 3, ('Bread', 'Beer'): 2, ('Milk', 'Diaper'): 3, ('Milk', 'Beer'): 2, ('Milk', 'Coke'): 2, ('Diaper', 'Beer'): 3, ('Diaper', 'Coke'): 2},
    {('Bread', 'Milk', 'Diaper'): 2, ('Bread', 'Diaper', 'Beer'): 2, ('Milk', 'Diaper', 'Beer'): 2, ('Milk', 'Diaper', 'Coke'): 2}
]
```

- The **first dictionary** contains single-item sequences with their frequencies (e.g., `('Bread',): 4` means "Bread"
  appears in 4 transactions).
- The **second dictionary** contains 2-item sequential patterns (e.g., `('Bread', 'Milk'): 3` means the sequence "
  Bread → Milk" appears in 3 transactions). Note that patterns like `('Bread', 'Beer')` are detected even when they don't appear adjacent in transactions - they just need to appear in order.
- The **third dictionary** contains 3-item sequential patterns (e.g., `('Bread', 'Milk', 'Diaper'): 2` means the
  sequence "Bread → Milk → Diaper" appears in 2 transactions).

> [!NOTE]
> The **support** of a sequence is calculated as the fraction of transactions containing the sequence **in order** (not necessarily contiguously), e.g.,
`('Bread', 'Milk')` appears in 3 out of 5 transactions → Support = `3 / 5 = 0.6` (60%).
> This insight helps identify frequently occurring sequential patterns in datasets, such as shopping trends or user
> behavior.

> [!IMPORTANT]
> **Non-contiguous (ordered) matching**: GSP-Py detects patterns where items appear in the specified order but not necessarily adjacent. For example, the pattern `('Bread', 'Beer')` matches the transaction `['Bread', 'Milk', 'Diaper', 'Beer']` because Bread appears before Beer, even though they are not adjacent. This follows the standard GSP algorithm semantics for sequential pattern mining.

### Understanding Non-Contiguous Pattern Matching

GSP-Py follows the standard GSP algorithm semantics by detecting **ordered (non-contiguous)** subsequences. This means:

- ✅ **Order matters**: Items must appear in the specified sequence order
- ✅ **Gaps allowed**: Items don't need to be adjacent
- ❌ **Wrong order rejected**: Items appearing in different order won't match

**Example:**

```python
from gsppy.gsp import GSP

sequences = [
    ['a', 'b', 'c'],  # Contains: (a,b), (a,c), (b,c), (a,b,c)
    ['a', 'c'],       # Contains: (a,c)
    ['b', 'c', 'a'],  # Contains: (b,c), (b,a), (c,a)
    ['a', 'b', 'c', 'd'],  # Contains: (a,b), (a,c), (a,d), (b,c), (b,d), (c,d), etc.
]

gsp = GSP(sequences)
result = gsp.search(min_support=0.5)  # Need at least 2/4 sequences

# Pattern ('a', 'c') is found with support=3 because:
# - It appears in ['a', 'b', 'c'] (with 'b' in between)
# - It appears in ['a', 'c'] (adjacent)
# - It appears in ['a', 'b', 'c', 'd'] (with 'b' in between)
# Total: 3 out of 4 sequences = 75% support ✅
```


> [!TIP]
> For more complex examples, find example scripts in the [`gsppy/tests`](gsppy/tests) folder.

---

## ⏱️ Temporal Constraints

GSP-Py supports **time-constrained sequential pattern mining** with three powerful temporal constraints: `mingap`, `maxgap`, and `maxspan`. These constraints enable domain-specific applications such as medical event mining, retail analytics, and temporal user journey discovery.

### Temporal Constraint Parameters

- **`mingap`**: Minimum time gap required between consecutive items in a pattern
- **`maxgap`**: Maximum time gap allowed between consecutive items in a pattern  
- **`maxspan`**: Maximum time span from the first to the last item in a pattern

### Using Temporal Constraints

To use temporal constraints, your transactions must include timestamps as (item, timestamp) tuples:

```python
from gsppy.gsp import GSP

# Transactions with timestamps (e.g., in seconds, hours, days, etc.)
timestamped_transactions = [
    [("Login", 0), ("Browse", 2), ("AddToCart", 5), ("Purchase", 7)],
    [("Login", 0), ("Browse", 1), ("AddToCart", 15), ("Purchase", 20)],
    [("Login", 0), ("Browse", 3), ("AddToCart", 6), ("Purchase", 8)],
]

# Find patterns where consecutive events occur within 10 time units
gsp = GSP(timestamped_transactions, maxgap=10)
patterns = gsp.search(min_support=0.6)

# The pattern ("Browse", "AddToCart", "Purchase") will:
# - Be found in transaction 1: gaps are 3 and 2 (both ≤ 10) ✅
# - NOT be found in transaction 2: gap between Browse→AddToCart is 14 (exceeds maxgap) ❌
# - Be found in transaction 3: gaps are 3 and 2 (both ≤ 10) ✅
# Result: Support = 2/3 = 67% (above threshold of 60%)
```

### CLI Usage with Temporal Constraints

```bash
# Find patterns with maximum gap of 5 time units
gsppy --file temporal_data.json --min_support 0.3 --maxgap 5

# Find patterns with minimum gap of 2 time units
gsppy --file temporal_data.json --min_support 0.3 --mingap 2

# Find patterns that complete within 10 time units
gsppy --file temporal_data.json --min_support 0.3 --maxspan 10

# Combine multiple constraints
gsppy --file temporal_data.json --min_support 0.3 --mingap 1 --maxgap 5 --maxspan 10
```

### Real-World Examples

#### Medical Event Mining

```python
from gsppy.gsp import GSP

# Medical events with timestamps in days
medical_sequences = [
    [("Symptom", 0), ("Diagnosis", 2), ("Treatment", 5), ("Recovery", 15)],
    [("Symptom", 0), ("Diagnosis", 1), ("Treatment", 20), ("Recovery", 30)],
    [("Symptom", 0), ("Diagnosis", 3), ("Treatment", 6), ("Recovery", 18)],
]

# Find patterns where treatment follows diagnosis within 10 days
gsp = GSP(medical_sequences, maxgap=10)
result = gsp.search(min_support=0.5)

# Pattern ("Diagnosis", "Treatment") found in sequences 1 & 3 only
# (sequence 2 has gap of 19 days, exceeding maxgap)
```

#### Retail Analytics

```python
from gsppy.gsp import GSP

# Customer purchases with timestamps in hours
purchase_sequences = [
    [("Browse", 0), ("AddToCart", 0.5), ("Purchase", 1)],
    [("Browse", 0), ("AddToCart", 1), ("Purchase", 25)],  # Long delay
    [("Browse", 0), ("AddToCart", 0.3), ("Purchase", 0.8)],
]

# Find purchase journeys that complete within 2 hours
gsp = GSP(purchase_sequences, maxspan=2)
result = gsp.search(min_support=0.5)

# Full sequence found in 2 out of 3 transactions
# (sequence 2 has span of 25 hours, exceeding maxspan)
```

#### User Journey Discovery

```python
from gsppy.gsp import GSP

# Website navigation with timestamps in seconds
navigation_sequences = [
    [("Home", 0), ("Search", 5), ("Product", 10), ("Checkout", 15)],
    [("Home", 0), ("Search", 3), ("Product", 8), ("Checkout", 180)],
    [("Home", 0), ("Search", 4), ("Product", 9), ("Checkout", 14)],
]

# Find navigation patterns with:
# - Minimum 2 seconds between steps (mingap)
# - Maximum 20 seconds between steps (maxgap)
# - Complete within 30 seconds total (maxspan)
gsp = GSP(navigation_sequences, mingap=2, maxgap=20, maxspan=30)
result = gsp.search(min_support=0.5)
```

### Important Notes

- Temporal constraints require timestamped transactions (item-timestamp tuples)
- If temporal constraints are specified but transactions don't have timestamps, a warning is logged and constraints are ignored
- When using temporal constraints, the Python backend is automatically used (accelerated backends don't yet support temporal constraints)
- Timestamps can be in any unit (seconds, minutes, hours, days) as long as they're consistent within your dataset

---

## ⌨️ Typing

`gsppy` ships inline type information (PEP 561) via a bundled `py.typed` marker. The public API is re-exported from
`gsppy` directly—import `GSP` for programmatic use or reuse the CLI helpers (`detect_and_read_file`,
`read_transactions_from_json`, `read_transactions_from_csv`, and `setup_logging`) when embedding the tool in
larger applications.

---

## 🌟 Planned Features

We are actively working to improve GSP-Py. Here are some exciting features planned for future releases:

1. **Custom Filters for Candidate Pruning**:
    - Enable users to define their own pruning logic during the mining process.

2. **Support for Preprocessing and Postprocessing**:
    - Add hooks to allow users to transform datasets before mining and customize the output results.

Want to contribute or suggest an
improvement? [Open a discussion or issue!](https://github.com/jacksonpradolima/gsp-py/issues)

---

## 🤝 Contributing

We welcome contributions from the community! If you'd like to help improve GSP-Py, read
our [CONTRIBUTING.md](CONTRIBUTING.md) guide to get started.

Development dependencies (e.g., testing and linting tools) are handled via uv.
To set up and run the main tasks:

```bash
uv venv .venv
uv sync --frozen --extra dev
uv pip install -e .

# Run tasks
uv run pytest -n auto
uv run ruff check .
uv run pyright
```

### Testing & Fuzzing

GSP-Py includes comprehensive test coverage, including property-based fuzzing tests using [Hypothesis](https://hypothesis.readthedocs.io/). These fuzzing tests automatically generate random inputs to verify algorithm invariants and discover edge cases. Run the fuzzing tests with:

```bash
uv run pytest tests/test_gsp_fuzzing.py -v
```

### General Steps:

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/my-feature`.
3. Commit your changes using [Conventional Commits](https://www.conventionalcommits.org/) format: `git commit -m "feat: add my feature"`.
4. Push to your branch: `git push origin feature/my-feature`.
5. Submit a pull request to the main repository!

Looking for ideas? Check out our [Planned Features](#planned-features) section.

### Release Management

GSP-Py uses automated release management with [Conventional Commits](https://www.conventionalcommits.org/). When commits are merged to `main`:
- **Releases are triggered** by: `fix:` (patch), `feat:` (minor), `perf:` (patch), or `BREAKING CHANGE:` (major)
- **No release** for: `docs:`, `style:`, `refactor:`, `test:`, `build:`, `ci:`, `chore:`
- CHANGELOG.md is automatically updated with structured release notes
- Git tags and GitHub releases are created automatically

See [Release Management Guide](docs/RELEASE_MANAGEMENT.md) for details on commit message format and release process.

---

## 📝 License

This project is licensed under the terms of the **MIT License**. For more details, refer to the [LICENSE](LICENSE) file.

---

## 📖 Citation

If GSP-Py contributed to your research or project that led to a publication, we kindly ask that you cite it as follows:

```
@misc{pradolima_gsppy,
  author       = {Prado Lima, Jackson Antonio do},
  title        = {{GSP-Py - Generalized Sequence Pattern algorithm in Python}},
  month        = Dec,
  year         = 2025,
  doi          = {10.5281/zenodo.3333987},
  url          = {https://doi.org/10.5281/zenodo.3333987}
}
```
