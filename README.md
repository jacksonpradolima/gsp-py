[![PyPI License](https://img.shields.io/pypi/l/gsppy.svg?style=flat-square)]()
![](https://img.shields.io/badge/python-3.10+-blue.svg)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.3333987.svg)](https://doi.org/10.5281/zenodo.3333987)

[![PyPI Downloads](https://img.shields.io/pypi/dm/gsppy.svg?style=flat-square)](https://pypi.org/project/gsppy/)
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
5. [💡 Usage](#usage)
    - [✅ Example: Analyzing Sales Data](#example-analyzing-sales-data)
    - [📊 Explanation: Support and Results](#explanation-support-and-results)
6. [🌟 Planned Features](#planned-features)
7. [🤝 Contributing](#contributing)
8. [📝 License](#license)
9. [📖 Citation](#citation)

---

## 🔍 What is GSP?

The **Generalized Sequential Pattern (GSP)** algorithm is a sequential pattern mining technique based on **Apriori
principles**. Using support thresholds, GSP identifies frequent sequences of items in transaction datasets.

### Key Features:

- **Ordered (non-contiguous) matching**: Detects patterns where items appear in order but not necessarily adjacent, following standard GSP semantics. For example, the pattern `('A', 'C')` is found in the sequence `['A', 'B', 'C']`.
- **Support-based pruning**: Only retains sequences that meet the minimum support threshold.
- **Candidate generation**: Iteratively generates candidate sequences of increasing length.
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
make typecheck           # pyright (and mypy if configured)
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
- `--verbose`: (Optional) Enable detailed output for debugging.

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

## 🌟 Planned Features

We are actively working to improve GSP-Py. Here are some exciting features planned for future releases:

1. **Custom Filters for Candidate Pruning**:
    - Enable users to define their own pruning logic during the mining process.

2. **Support for Preprocessing and Postprocessing**:
    - Add hooks to allow users to transform datasets before mining and customize the output results.

3. **Support for Time-Constrained Pattern Mining**:
    - Extend GSP-Py to handle temporal datasets by allowing users to define time constraints (e.g., maximum time gaps
      between events, time windows) during the sequence mining process.
    - Enable candidate pruning and support calculations based on these temporal constraints.

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

### General Steps:

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/my-feature`.
3. Commit your changes: `git commit -m "Add my feature."`
4. Push to your branch: `git push origin feature/my-feature`.
5. Submit a pull request to the main repository!

Looking for ideas? Check out our [Planned Features](#planned-features) section.

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
