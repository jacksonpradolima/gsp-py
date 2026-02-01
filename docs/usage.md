# Usage

This guide walks through installation, dependency management with **uv**, and running the GSP algorithm with various data formats.

## Installation

The recommended way to install GSP-Py is from PyPI:

```bash
pip install gsppy
```

For DataFrame support (Parquet/Arrow with Polars/Pandas):

```bash
pip install 'gsppy[dataframe]'
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

### Basic Usage

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

### Loading from Different Formats

#### JSON and CSV Files

```python
from gsppy import detect_and_read_file

# Auto-detect format from file extension
transactions = detect_and_read_file("data.json")
# or
transactions = detect_and_read_file("data.csv")

model = GSP(transactions)
frequent = model.search(min_support=0.5)
```

#### SPM/GSP Format Files

The SPM/GSP format uses delimiters to mark sequence boundaries:
- `-1`: End of element (itemset)
- `-2`: End of sequence (transaction)

```python
from gsppy.utils import read_transactions_from_spm
from gsppy import GSP

# Load SPM format file
transactions = read_transactions_from_spm('data.txt')

# Run GSP algorithm
gsp = GSP(transactions)
result = gsp.search(min_support=0.3)
```

**Example SPM format:**
```text
1 2 -1 3 -1 -2
4 -1 5 6 -1 -2
```

This represents:
- Transaction 1: `['1', '2', '3']`
- Transaction 2: `['4', '5', '6']`

#### With Token Mappings

For workflows requiring conversion between string tokens and integer IDs:

```python
from gsppy.utils import read_transactions_from_spm
from gsppy import TokenMapper

# Load with mappings
transactions, str_to_int, int_to_str = read_transactions_from_spm(
    'data.txt', 
    return_mappings=True
)

# Use mappings for conversion
token_id = str_to_int['A']  # Get integer ID for token 'A'
token_str = int_to_str[0]   # Get string token for ID 0

# Or use TokenMapper directly
mapper = TokenMapper()
id_a = mapper.add_token("A")  # Returns 0
id_b = mapper.add_token("B")  # Returns 1
```

#### Parquet and Arrow Files

Requires the DataFrame extra (`pip install 'gsppy[dataframe]'`):

```python
from gsppy.cli import read_transactions_from_parquet, read_transactions_from_arrow

# Parquet with transaction-item structure
transactions = read_transactions_from_parquet(
    'data.parquet',
    transaction_col='txn_id',
    item_col='product'
)

# Arrow with sequence column
transactions = read_transactions_from_arrow(
    'sequences.arrow',
    sequence_col='items'
)

model = GSP(transactions)
frequent = model.search(min_support=0.5)
```

## Using Sequence Objects

GSP-Py 4.0+ introduces a **Sequence abstraction** that provides a richer, more maintainable way to work with sequential patterns. The Sequence class encapsulates pattern items, support counts, and optional metadata.

### Traditional Dict-based Output (Default)

By default, GSP returns patterns as dictionaries mapping tuples to support counts:

```python
from gsppy import GSP

transactions = [
    ["Bread", "Milk"],
    ["Bread", "Diaper", "Beer", "Eggs"],
    ["Milk", "Diaper", "Beer", "Coke"],
]

gsp = GSP(transactions)
result = gsp.search(min_support=0.3)

# Returns: [{('Bread',): 4, ('Milk',): 4, ...}, ...]
for level_patterns in result:
    for pattern, support in level_patterns.items():
        print(f"Pattern: {pattern}, Support: {support}")
```

### Sequence Objects (New Feature)

Enable the new Sequence objects by setting `return_sequences=True`:

```python
from gsppy import GSP

transactions = [
    ["Bread", "Milk"],
    ["Bread", "Diaper", "Beer", "Eggs"],
    ["Milk", "Diaper", "Beer", "Coke"],
]

gsp = GSP(transactions)
result = gsp.search(min_support=0.3, return_sequences=True)

# Returns: [[Sequence(('Bread',), support=4), ...], ...]
for level_patterns in result:
    for seq in level_patterns:
        print(f"Pattern: {seq.items}")
        print(f"Support: {seq.support}")
        print(f"Length: {seq.length}")
        
        # Rich API
        if "Milk" in seq:
            print("Contains Milk!")
```

### Sequence Properties and Methods

The Sequence class provides a rich API:

```python
from gsppy import Sequence

# Create sequences
seq = Sequence.from_tuple(("A", "B", "C"), support=5)

# Access properties
print(seq.items)        # ('A', 'B', 'C')
print(seq.support)      # 5
print(seq.length)       # 3
print(seq.first_item)   # 'A'
print(seq.last_item)    # 'C'

# Operations
extended = seq.extend("D")  # Sequence(('A', 'B', 'C', 'D'))
updated = seq.with_support(10)
enriched = seq.with_metadata(confidence=0.85, lift=1.5)

# Check membership
if "B" in seq:
    print("Sequence contains B")

# Iterate over items
for item in seq:
    print(item)

# Convert to tuple for compatibility
tuple_form = seq.as_tuple()  # ('A', 'B', 'C')
```

### Converting Between Formats

Use utility functions to convert between Sequence objects and dict format:

```python
from gsppy import sequences_to_dict, dict_to_sequences

# Get results as Sequences
result = gsp.search(min_support=0.3, return_sequences=True)

# Convert to dict format for compatibility
dict_format = sequences_to_dict(result[0])
# {('Bread',): 4, ('Milk',): 4, ...}

# Convert back to Sequences
sequences = dict_to_sequences(dict_format)
# [Sequence(('Bread',), support=4), ...]
```

For a complete example demonstrating all Sequence features, see `examples/sequence_example.py` in the repository.

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
