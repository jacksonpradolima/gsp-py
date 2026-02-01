# GSP-Py Documentation

Welcome to the official documentation for **GSP-Py**, a Python library that implements the Generalized Sequential
Pattern (GSP) algorithm. Use this site to install the library, explore the CLI, and dive into accelerated backends.

## Highlights

- **Sequence mining** with support-based pruning and candidate generation.
- **Sequence abstraction** for typed pattern representation with rich metadata support.
- **Multiple data formats** including JSON, CSV, SPM/GSP, Parquet, and Arrow.
- **Token mapping utilities** for transparent string ↔ integer conversion.
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

### Using Sequence Objects (New in 4.0+)

Get richer pattern representation with typed Sequence objects:

```python
from gsppy import GSP

transactions = [
    ["Bread", "Milk"],
    ["Bread", "Diaper", "Beer", "Eggs"],
    ["Milk", "Diaper", "Beer", "Coke"],
]

# Enable Sequence objects
patterns = GSP(transactions).search(min_support=0.3, return_sequences=True)

for level_patterns in patterns:
    for seq in level_patterns:
        print(f"{seq.items} (support={seq.support}, length={seq.length})")
        if "Milk" in seq:
            enriched = seq.with_metadata(confidence=0.85)
```

### Loading from SPM/GSP Format

```python
from gsppy.utils import read_transactions_from_spm
from gsppy import GSP

# Load classical SPM format with -1/-2 delimiters
transactions = read_transactions_from_spm('data.txt')
patterns = GSP(transactions).search(min_support=0.3)
```

Continue to the [Usage](usage.md) guide for installation details and backend selection tips.
