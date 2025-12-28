# GSP-Py Documentation

Welcome to the official documentation for **GSP-Py**, a Python library that implements the Generalized Sequential
Pattern (GSP) algorithm. Use this site to install the library, explore the CLI, and dive into accelerated backends.

## Highlights

- **Sequence mining** with support-based pruning and candidate generation.
- **Optional acceleration** via Rust and GPU backends.
- **Developer-friendly tools** including typed APIs and optional benchmarks.

## Quickstart

Install the package from PyPI and run a simple search:

```bash
pip install gsppy
```

```python
from gsppy.gsp import GSP

transactions = [
    ["Bread", "Milk"],
    ["Bread", "Diaper", "Beer", "Eggs"],
    ["Milk", "Diaper", "Beer", "Coke"],
]

patterns = GSP(transactions).search(min_support=0.3)
for level, freq_patterns in enumerate(patterns, start=1):
    print(f"Level {level}: {freq_patterns}")
```

Continue to the [Usage](usage.md) guide for installation details and backend selection tips.
