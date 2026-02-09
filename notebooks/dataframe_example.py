"""
DataFrame Example for GSP-Py

This interactive notebook demonstrates how to use GSP-Py with Polars and Pandas DataFrames
for high-performance sequential pattern mining.
"""

import marimo

__generated_with = "0.19.9"
app = marimo.App(width="medium")


@app.cell(hide_code=False)
def _():
    """Import required libraries"""
    import pandas as pd
    import polars as pl
    from gsppy import GSP
    import marimo as mo
    return GSP, mo, pd, pl


@app.cell(hide_code=False)
def _(mo):
    """Introduction"""
    mo.md("""
    # GSP-Py: DataFrame Integration Example
    
    This notebook demonstrates how to use GSP-Py with **Polars** and **Pandas** DataFrames
    for high-performance sequential pattern mining.
    
    ## Requirements
    
    To use DataFrame features, install with:
    ```bash
    pip install 'gsppy[dataframe]'
    ```
    """)
    return


@app.cell(hide_code=False)
def _(mo):
    """Example 1 Header"""
    mo.md("""
    ## Example 1: Polars DataFrame (Grouped Format)
    
    Using Polars with transaction_id and item columns.
    """)
    return


@app.cell(hide_code=False)
def _(GSP, mo, pl):
    """Polars DataFrame example"""
    df_polars = pl.DataFrame(
        {
            "transaction_id": [1, 1, 2, 2, 2, 3, 3, 4, 4],
            "item": ["Bread", "Milk", "Bread", "Diaper", "Beer", "Milk", "Coke", "Bread", "Beer"],
        }
    )
    
    gsp_polars = GSP(df_polars, transaction_col="transaction_id", item_col="item")
    patterns_polars = gsp_polars.search(min_support=0.5)
    
    _output_polars = [f"**Input DataFrame:**\n```\n{df_polars}\n```\n"]
    _output_polars.append("\n**Frequent Patterns (min_support=0.5):**\n")
    
    for _lvl, _freq_patterns in enumerate(patterns_polars, start=1):
        _output_polars.append(f"\n**{_lvl}-Sequence Patterns:**")
        for _ptn, _sup in _freq_patterns.items():
            _output_polars.append(f"  - `{_ptn}`: {_sup}")
    
    mo.md("\n".join(_output_polars))
    return df_polars, gsp_polars, patterns_polars


@app.cell(hide_code=False)
def _(mo):
    """Example 2 Header"""
    mo.md("""
    ## Example 2: Pandas DataFrame (Sequence Format)
    
    Using Pandas with sequences stored directly in a column.
    """)
    return


@app.cell(hide_code=False)
def _(GSP, mo, pd):
    """Pandas DataFrame example"""
    df_pandas = pd.DataFrame(
        {
            "transaction": [
                ["Login", "Browse", "AddToCart", "Purchase"],
                ["Login", "Browse", "Purchase"],
                ["Browse", "AddToCart", "Purchase"],
                ["Login", "AddToCart", "Purchase"],
            ]
        }
    )
    
    gsp_pandas = GSP(df_pandas, sequence_col="transaction")
    patterns_pandas = gsp_pandas.search(min_support=0.5)
    
    _output_pandas = [f"**Input DataFrame:**\n```\n{df_pandas}\n```\n"]
    _output_pandas.append("\n**Frequent Patterns (min_support=0.5):**\n")
    
    for _lvl_p, _freq_patterns_p in enumerate(patterns_pandas, start=1):
        _output_pandas.append(f"\n**{_lvl_p}-Sequence Patterns:**")
        for _ptn_p, _sup_p in _freq_patterns_p.items():
            _output_pandas.append(f"  - `{_ptn_p}`: {_sup_p}")
    
    mo.md("\n".join(_output_pandas))
    return df_pandas, gsp_pandas, patterns_pandas


@app.cell(hide_code=False)
def _(mo):
    """Example 3 Header"""
    mo.md("""
    ## Example 3: Temporal Mining with Timestamps
    
    Using timestamps to find patterns within specific time windows.
    """)
    return


@app.cell(hide_code=False)
def _(GSP, mo, pl):
    """Temporal mining example"""
    df_temporal = pl.DataFrame(
        {
            "transaction_id": [1, 1, 1, 2, 2, 2, 3, 3, 3],
            "item": ["A", "B", "C", "A", "B", "C", "A", "B", "C"],
            "timestamp": [1, 2, 5, 1, 3, 15, 1, 2, 4],  # Note: Transaction 2 has large gap
        }
    )
    
    # Find patterns where consecutive items occur within 5 time units
    gsp_temporal = GSP(
        df_temporal,
        transaction_col="transaction_id",
        item_col="item",
        timestamp_col="timestamp",
        maxgap=5
    )
    patterns_temporal = gsp_temporal.search(min_support=0.5)
    
    _output_temporal = [f"**Input DataFrame with Timestamps:**\n```\n{df_temporal}\n```\n"]
    _output_temporal.append("\n**Frequent Patterns with maxgap=5 (min_support=0.5):**\n")
    _output_temporal.append("\n*Note: Pattern ('A', 'B', 'C') is found only in transactions 1 and 3*")
    _output_temporal.append("*because transaction 2 has a gap > 5 between B and C*\n")
    
    for _lvl_t, _freq_patterns_t in enumerate(patterns_temporal, start=1):
        _output_temporal.append(f"\n**{_lvl_t}-Sequence Patterns:**")
        for _ptn_t, _sup_t in _freq_patterns_t.items():
            _output_temporal.append(f"  - `{_ptn_t}`: {_sup_t}")
    
    mo.md("\n".join(_output_temporal))
    return df_temporal, gsp_temporal, patterns_temporal


@app.cell(hide_code=False)
def _(mo):
    """Conclusion"""
    mo.md("""
    ## Key Advantages of DataFrame Integration
    
    Using DataFrames with GSP-Py provides several benefits:
    
    ### Performance
    - **Zero-copy conversion**: Efficient data handling with Polars/Pandas
    - **Optimized operations**: Leverages DataFrame optimizations
    
    ### Flexibility
    - **Multiple formats**: Support for grouped and sequence formats
    - **Temporal constraints**: Easy integration with timestamp columns
    - **Data preprocessing**: Use DataFrame operations before pattern mining
    
    ### Interoperability
    - **Parquet support**: Read/write to Parquet files
    - **Arrow format**: Efficient data exchange between tools
    - **Integration**: Works seamlessly with your data pipeline
    
    ### Example Use Cases
    
    1. **E-commerce**: Analyze customer purchase sequences from database
    2. **Web analytics**: Mine user clickstream patterns from logs
    3. **Healthcare**: Discover treatment sequences from medical records
    4. **Manufacturing**: Find equipment failure patterns from sensor data
    """)
    return


if __name__ == "__main__":
    app.run()
