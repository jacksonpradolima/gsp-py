# Usage

This guide walks through installation, dependency management with **uv**, and running the GSP algorithm.

## Installation

The recommended way to install GSP-Py is from PyPI:

```bash
pip install gsppy
```

Alternatively, clone the repository and install in editable mode:

```bash
git clone https://github.com/jacksonpradolima/gsp-py.git
cd gsp-py
uv venv .venv
uv sync --frozen
uv pip install -e .
```

## Running a search

```python
from gsppy.gsp import GSP

transactions = [
    ["A", "B", "C"],
    ["A", "C"],
    ["A", "B"],
]

model = GSP(transactions)
frequent = model.search(min_support=0.5)
print(frequent)
```

The `min_support` argument expects a fraction in the range `(0.0, 1.0]` and defaults to `0.2`.

## Verbose Mode

Enable detailed logging to track algorithm progress and debug issues:

```python
# Enable verbose logging for the entire instance
gsp = GSP(transactions, verbose=True)
patterns = gsp.search(min_support=0.5)

# Or enable verbose for a specific search
gsp = GSP(transactions)
patterns = gsp.search(min_support=0.5, verbose=True)
```

For more details on logging, output formatting, and traceability, see the [Logging Guide](logging.md).

## Backend selection

GSP-Py can accelerate support counting with optional backends:

- **auto (default):** tries the Rust extension, falling back to Python.
- **python:** uses the pure-Python implementation.
- **rust:** requires the Rust extension to be installed.
- **gpu:** experimental CuPy backend for singleton counting.

Set the backend via keyword argument or environment variable:

```bash
GSPPY_BACKEND=rust gsppy --file transactions.json
```

## CLI helper

Install the CLI entrypoint with the package:

```bash
pip install gsppy
```

Run `gsppy --help` to see available options, or read the [CLI page](cli.md) for examples.
