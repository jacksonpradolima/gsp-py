# Interactive Examples

GSP-Py provides interactive notebook examples using [marimo](https://marimo.io/) that demonstrate various features and use cases. These notebooks are fully executable and can be run locally or viewed as static HTML.

## Available Notebooks

### 1. Sequence Abstraction Example

Learn how to use the Sequence class for working with sequential patterns in a structured way.

**Topics covered:**
- Traditional dict-based output
- Sequence objects and their properties
- Filtering and analyzing sequences
- Creating custom sequence objects
- Pattern analysis and statistics

[View Notebook](sequence_example.html){ .md-button .md-button--primary }

### 2. Itemset Support Example

Understand how to work with itemsets where multiple items can occur together at the same time step.

**Topics covered:**
- Flat vs. itemset sequences
- Market basket analysis with itemsets
- E-commerce click streams with concurrent actions
- When and how to use itemsets

[View Notebook](itemset_example.html){ .md-button .md-button--primary }

### 3. DataFrame Integration Example

Learn how to use GSP-Py with Polars and Pandas DataFrames for efficient pattern mining.

**Topics covered:**
- Polars DataFrame with grouped format
- Pandas DataFrame with sequence format
- Temporal mining with timestamps
- Performance benefits of DataFrame integration

[View Notebook](dataframe_example.html){ .md-button .md-button--primary }

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
