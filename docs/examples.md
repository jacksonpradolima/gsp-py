# Interactive Examples with Marimo

GSP-Py provides interactive notebook examples using [marimo](https://marimo.io/) that demonstrate various features and use cases. Marimo notebooks are reactive Python notebooks that provide an interactive environment for exploring GSP-Py functionality.

## What is Marimo?

[Marimo](https://marimo.io/) is a reactive Python notebook that runs as a pure Python program. Unlike traditional notebooks:
- **Reactive**: Changes propagate automatically through dependent cells
- **Reproducible**: Runs deterministically every time
- **Git-friendly**: Stored as pure Python files (`.py`), not JSON
- **Interactive**: Edit code and see results update in real-time
- **Shareable**: Can be exported to HTML, PDF, or run as web apps

## Available Notebooks

### 1. Sequence Abstraction Example

Learn how to use the Sequence class for working with sequential patterns in a structured way.

**Topics covered:**
- Traditional dict-based output vs. Sequence objects
- Accessing sequence properties (items, support, length)
- Filtering and analyzing sequences
- Creating custom sequence objects
- Pattern analysis and statistics

**Notebook:** [`notebooks/sequence_example.py`](https://github.com/jacksonpradolima/gsp-py/tree/master/notebooks/sequence_example.py)

### 2. Itemset Support Example

Understand how to work with itemsets where multiple items can occur together at the same time step.

**Topics covered:**
- Flat vs. itemset sequences
- Market basket analysis with itemsets
- Web clickstream with parallel page views
- Reading itemsets from SPM format

**Notebook:** [`notebooks/itemset_example.py`](https://github.com/jacksonpradolima/gsp-py/tree/master/notebooks/itemset_example.py)

### 3. DataFrame Integration Example

Learn how to use GSP-Py with Polars and Pandas DataFrames for efficient pattern mining.

**Topics covered:**
- Polars DataFrame with grouped format
- Pandas DataFrame with sequence format
- Temporal mining with timestamps
- Reading from Parquet files
- Performance comparison

**Notebook:** [`notebooks/dataframe_examples.py`](https://github.com/jacksonpradolima/gsp-py/tree/master/notebooks/dataframe_examples.py)

### 4. Hooks Example

Explore how to use preprocessing, postprocessing, and candidate filtering hooks.

**Topics covered:**
- Custom preprocessing hooks
- Candidate filtering strategies
- Postprocessing transformations
- Practical examples with hooks

**Notebook:** [`notebooks/hooks_example.py`](https://github.com/jacksonpradolima/gsp-py/tree/master/notebooks/hooks_example.py)

### 5. Custom Hooks

Advanced custom hooks for preprocessing, postprocessing, and candidate filtering.

**Topics covered:**
- Normalization and filtering hooks
- Length and support constraint filters
- Pattern transformation and enrichment
- Metadata addition and top-k filtering

**Notebook:** [`notebooks/custom_hooks.py`](https://github.com/jacksonpradolima/gsp-py/tree/master/notebooks/custom_hooks.py)

### 6. Parquet Round-trip Example

Complete workflow for using Parquet files with GSP-Py.

**Topics covered:**
- Loading transactions from CSV
- Converting to Parquet format
- Running GSP mining on Parquet data
- Exporting results to Parquet
- Handling edge cases and errors

**Notebook:** [`notebooks/parquet_roundtrip_example.py`](https://github.com/jacksonpradolima/gsp-py/tree/master/notebooks/parquet_roundtrip_example.py)

## Setup and Installation

Before running the notebooks, you need to install marimo and GSP-Py:

```bash
# Install GSP-Py with dataframe support (recommended)
pip install 'gsppy[dataframe]'

# Install marimo
pip install marimo
```

## Running Notebooks Locally

To run these notebooks interactively on your machine:

1. **Clone the repository:**

```bash
git clone https://github.com/jacksonpradolima/gsp-py.git
cd gsp-py
```

2. **Run a notebook in interactive mode:**

```bash
marimo edit notebooks/sequence_example.py
```

This opens the notebook in your browser where you can:
- Modify code and see results update automatically
- Experiment with different parameters
- Add new cells and explore the library
- Save your changes back to the `.py` file

3. **Run a notebook as a script:**

```bash
python notebooks/sequence_example.py
```

Or use marimo to run it as a read-only app:

```bash
marimo run notebooks/sequence_example.py
```

## Working with Marimo Notebooks

### Interactive Editing

When you run `marimo edit`, you get a reactive development environment:

1. **Edit any cell** - Changes propagate automatically to dependent cells
2. **Add new cells** - Use the + button or keyboard shortcuts
3. **Reorder cells** - Drag and drop to reorganize
4. **View outputs** - Rich display of DataFrames, plots, and results

### Keyboard Shortcuts

- `Cmd/Ctrl + Enter`: Run current cell
- `Shift + Enter`: Run cell and select next
- `Cmd/Ctrl + S`: Save notebook

### Cell Dependencies

Marimo automatically tracks dependencies between cells:
- If you change a variable, all cells using it update
- No need to manually re-run cells in order
- Prevents stale outputs and hidden state bugs

## Creating Your Own Notebooks

You can create your own marimo notebooks for GSP-Py:

```bash
# Create a new notebook
marimo new my_notebook.py

# Edit an existing notebook
marimo edit my_notebook.py
```

Marimo notebooks are:
- **Reactive**: Changes propagate automatically
- **Reproducible**: Run deterministically every time
- **Git-friendly**: Stored as pure Python files
- **Shareable**: Export to HTML, PDF, or run as apps

## Additional Resources

- [Marimo Documentation](https://docs.marimo.io/)
- [GSP-Py API Reference](api.md)
- [GSP-Py Usage Guide](usage.md)
- [Notebooks Source Code](https://github.com/jacksonpradolima/gsp-py/tree/master/notebooks)
