# GSP-Py Interactive Notebooks

This directory contains interactive [marimo](https://marimo.io/) notebooks demonstrating various features of GSP-Py.

## Available Notebooks

### 1. `sequence_example.py`
Demonstrates the Sequence abstraction in GSP-Py:
- Traditional dict-based output vs. Sequence objects
- Accessing sequence properties
- Filtering and analyzing sequences
- Creating custom sequence objects
- Pattern analysis and statistics

### 2. `itemset_example.py`
Shows how to use itemsets where multiple items occur together:
- Flat vs. itemset sequences
- Market basket analysis with itemsets
- E-commerce click streams with concurrent actions

### 3. `dataframe_example.py`
Integration with Polars and Pandas DataFrames:
- Polars DataFrame with grouped format
- Pandas DataFrame with sequence format
- Temporal mining with timestamps

## Running Notebooks Locally

### Prerequisites

Install marimo and GSP-Py with dataframe support:

```bash
pip install marimo 'gsppy[dataframe]'
```

### Running a Notebook

To run a notebook interactively:

```bash
marimo edit sequence_example.py
```

This opens the notebook in your browser where you can:
- Modify code and see results update reactively
- Experiment with different parameters
- Save your changes

### Running as a Script

You can also run notebooks as regular Python scripts:

```bash
python sequence_example.py
```

Or using marimo's run command for a read-only app:

```bash
marimo run sequence_example.py
```

## Notebook Structure

Marimo notebooks are:
- **Pure Python files**: Easy to version control and review
- **Reactive**: Changes propagate automatically through dependent cells
- **Reproducible**: Execute deterministically every time
- **Shareable**: Can be exported to HTML, PDF, or run as web apps

Each notebook is structured with `@app.cell` decorators that define reactive cells. Variables defined in one cell are automatically available to dependent cells.

## Exporting Notebooks

To export a notebook to HTML for documentation:

```bash
marimo export html sequence_example.py -o sequence_example.html
```

To export to Markdown:

```bash
marimo export md sequence_example.py -o sequence_example.md
```

## Contributing

When adding new notebooks:

1. Create the notebook in this directory
2. Test it with `marimo check your_notebook.py`
3. Export to HTML: `marimo export html your_notebook.py -o ../docs/your_notebook.html --force`
4. Add a link in `docs/examples.md`
5. Update `mkdocs.yml` if adding a new documentation page
6. Commit both the `.py` notebook and the `.html` export

**Important:** When modifying existing notebooks, remember to regenerate the HTML export:

```bash
# After modifying a notebook
marimo export html your_notebook.py -o ../docs/your_notebook.html --force
git add notebooks/your_notebook.py docs/your_notebook.html
```

This ensures the documentation stays in sync with the notebook source.

## More Resources

- [Marimo Documentation](https://docs.marimo.io/)
- [GSP-Py Documentation](https://jacksonpradolima.github.io/gsp-py/)
- [GSP-Py API Reference](https://jacksonpradolima.github.io/gsp-py/api.html)
