# Interactive Examples

GSP-Py provides interactive notebook examples using [marimo](https://marimo.io/) that demonstrate various features and use cases. These notebooks are fully executable and can be run locally.

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
- Medical records example
- Product bundles example

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

## Running Notebooks Locally

To run these notebooks interactively on your machine:

1. **Install GSP-Py with notebook dependencies:**

```bash
pip install 'gsppy[dataframe]'
pip install marimo
```

2. **Clone the repository:**

```bash
git clone https://github.com/jacksonpradolima/gsp-py.git
cd gsp-py
```

3. **Run a notebook:**

```bash
marimo edit notebooks/sequence_example.py
```

This will open the notebook in your browser where you can interact with the code, modify parameters, and see results in real-time.

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
- [Source Code Examples](https://github.com/jacksonpradolima/gsp-py/tree/master/examples)
