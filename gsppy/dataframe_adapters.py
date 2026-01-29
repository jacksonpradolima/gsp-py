"""
DataFrame adapters for GSP-Py.

This module provides utilities to convert Polars and Pandas DataFrames to the format
expected by the GSP algorithm. It enables high-performance workflows by supporting
modern data formats like Arrow and Parquet.

Key Features:
-------------
1. **Polars DataFrame Support**:
   - Convert Polars DataFrames to transaction lists
   - Efficient zero-copy operations where possible
   - Support for timestamped and non-timestamped data

2. **Pandas DataFrame Support**:
   - Convert Pandas DataFrames to transaction lists
   - Compatible with Arrow backend
   - Support for timestamped and non-timestamped data

3. **Schema Validation**:
   - Validate DataFrame structure before conversion
   - Clear error messages for non-compliant schemas
   - Type checking and validation

4. **Flexible Input Formats**:
   - Support for grouped transactions (transaction_id + item columns)
   - Support for sequence columns (list/array of items per row)
   - Support for timestamps (optional)

Example Usage:
--------------
```python
import polars as pl
from gsppy.dataframe_adapters import polars_to_transactions

# Grouped format with transaction_id and item columns
df = pl.DataFrame(
    {
        "transaction_id": [1, 1, 2, 2, 2, 3],
        "item": ["A", "B", "A", "C", "D", "B"],
    }
)
transactions = polars_to_transactions(df, transaction_col="transaction_id", item_col="item")

# Sequence format with list column
df = pl.DataFrame({"sequence": [["A", "B"], ["A", "C", "D"], ["B"]]})
transactions = polars_to_transactions(df, sequence_col="sequence")

# With timestamps
df = pl.DataFrame(
    {
        "transaction_id": [1, 1, 2, 2],
        "item": ["A", "B", "C", "D"],
        "timestamp": [1.0, 2.0, 1.5, 3.0],
    }
)
transactions = polars_to_transactions(df, transaction_col="transaction_id", item_col="item", timestamp_col="timestamp")
```

Author:
-------
- **Developed by:** Jackson Antonio do Prado Lima
- **Email:** jacksonpradolima@gmail.com

License:
--------
This implementation is distributed under the MIT License.
"""

from __future__ import annotations

from typing import Any, List, Tuple, Optional, cast

import pandas as pd
import polars as pl


class DataFrameAdapterError(Exception):
    """Exception raised for errors in DataFrame conversion."""

    pass


def polars_to_transactions(
    df: pl.DataFrame | pl.LazyFrame,
    transaction_col: Optional[str] = None,
    item_col: Optional[str] = None,
    timestamp_col: Optional[str] = None,
    sequence_col: Optional[str] = None,
) -> List[List[str]] | List[List[Tuple[str, float]]]:
    """
    Convert a Polars DataFrame to GSP transaction format.

    This function supports two input formats:
    1. Grouped format: Rows grouped by transaction_id, with separate columns for items and optional timestamps
    2. Sequence format: Each row contains a complete transaction as a list/array

    Parameters:
        df: Polars DataFrame to convert
        transaction_col: Column name for transaction IDs (grouped format)
        item_col: Column name for items (grouped format)
        timestamp_col: Optional column name for timestamps (grouped format)
        sequence_col: Column name containing sequences (sequence format)

    Returns:
        List of transactions, where each transaction is either:
        - A list of items (strings)
        - A list of (item, timestamp) tuples

    Raises:
        DataFrameAdapterError: If the DataFrame schema is invalid or required columns are missing

    Examples:
        >>> import polars as pl
        >>> # Grouped format
        >>> df = pl.DataFrame(
        ...     {
        ...         "txn_id": [1, 1, 2, 2],
        ...         "item": ["A", "B", "C", "D"],
        ...     }
        ... )
        >>> polars_to_transactions(df, transaction_col="txn_id", item_col="item")
        [['A', 'B'], ['C', 'D']]

        >>> # Sequence format
        >>> df = pl.DataFrame({"seq": [["A", "B"], ["C", "D"]]})
        >>> polars_to_transactions(df, sequence_col="seq")
        [['A', 'B'], ['C', 'D']]
    """
    if sequence_col is not None:
        return _polars_sequence_format(df, sequence_col, timestamp_col)
    elif transaction_col is not None and item_col is not None:
        return _polars_grouped_format(df, transaction_col, item_col, timestamp_col)
    else:
        raise DataFrameAdapterError("Must specify either 'sequence_col' or both 'transaction_col' and 'item_col'")


def _polars_sequence_format(
    df: pl.DataFrame | pl.LazyFrame,
    sequence_col: str,
    timestamp_col: Optional[str] = None,
) -> List[List[str]] | List[List[Tuple[str, float]]]:
    """
    Convert Polars DataFrame in sequence format.

    Parameters:
        df: Polars DataFrame or pl.LazyFrame
        sequence_col: Column containing sequences
        timestamp_col: Optional column containing timestamps per sequence

    Returns:
        List of transactions
    """
    # Collect pl.LazyFrame if needed
    if isinstance(df, pl.LazyFrame):
        df = df.collect()

    if sequence_col not in df.columns:
        raise DataFrameAdapterError(f"Column '{sequence_col}' not found in DataFrame")

    sequences: List[Any] = df[sequence_col].to_list()

    if timestamp_col is not None:
        if timestamp_col not in df.columns:
            raise DataFrameAdapterError(f"Column '{timestamp_col}' not found in DataFrame")

        timestamps: List[Any] = df[timestamp_col].to_list()

        # Create timestamped transactions
        result: List[List[Tuple[str, float]]] = []
        for seq, times in zip(sequences, timestamps, strict=True):
            if not isinstance(seq, list) or not isinstance(times, list):
                raise DataFrameAdapterError(f"Both '{sequence_col}' and '{timestamp_col}' must contain lists")
            seq_list: List[Any] = cast(List[Any], seq)
            times_list: List[Any] = cast(List[Any], times)
            if len(seq_list) != len(times_list):
                raise DataFrameAdapterError(f"Sequence and timestamp lists must have the same length")
            result.append([(str(item), float(ts)) for item, ts in zip(seq_list, times_list, strict=True)])
        return result
    else:
        # Create non-timestamped transactions
        result_simple: List[List[str]] = []
        for seq in sequences:
            if not isinstance(seq, list):
                raise DataFrameAdapterError(f"Column '{sequence_col}' must contain lists")
            seq_list_simple: List[Any] = cast(List[Any], seq)
            result_simple.append([str(item) for item in seq_list_simple])
        return result_simple


def _polars_grouped_format(
    df: pl.DataFrame | pl.LazyFrame,
    transaction_col: str,
    item_col: str,
    timestamp_col: Optional[str] = None,
) -> List[List[str]] | List[List[Tuple[str, float]]]:
    """
    Convert Polars DataFrame in grouped format.

    Parameters:
        df: Polars DataFrame or pl.LazyFrame
        transaction_col: Column containing transaction IDs
        item_col: Column containing items
        timestamp_col: Optional column containing timestamps

    Returns:
        List of transactions
    """
    # Collect pl.LazyFrame if needed
    if isinstance(df, pl.LazyFrame):
        df = df.collect()

    # Validate required columns exist
    if transaction_col not in df.columns:
        raise DataFrameAdapterError(f"Column '{transaction_col}' not found in DataFrame")
    if item_col not in df.columns:
        raise DataFrameAdapterError(f"Column '{item_col}' not found in DataFrame")

    # Sort by transaction and optionally timestamp
    sort_cols = [transaction_col]
    if timestamp_col is not None:
        if timestamp_col not in df.columns:
            raise DataFrameAdapterError(f"Column '{timestamp_col}' not found in DataFrame")
        sort_cols.append(timestamp_col)

    df_sorted = df.sort(sort_cols)

    # Group by transaction
    if timestamp_col is not None:
        # Create timestamped transactions
        grouped = df_sorted.group_by(transaction_col, maintain_order=True).agg(
            [
                pl.col(item_col).alias("items"),
                pl.col(timestamp_col).alias("timestamps"),
            ]
        )

        result: List[List[Tuple[str, float]]] = []
        for row in grouped.iter_rows(named=True):
            items = row["items"]
            timestamps = row["timestamps"]
            result.append([(str(item), float(ts)) for item, ts in zip(items, timestamps, strict=False)])
        return result
    else:
        # Create non-timestamped transactions
        grouped = df_sorted.group_by(transaction_col, maintain_order=True).agg(pl.col(item_col).alias("items"))

        result_simple: List[List[str]] = []
        for row in grouped.iter_rows(named=True):
            items = row["items"]
            result_simple.append([str(item) for item in items])
        return result_simple


def pandas_to_transactions(
    df: pd.DataFrame,
    transaction_col: Optional[str] = None,
    item_col: Optional[str] = None,
    timestamp_col: Optional[str] = None,
    sequence_col: Optional[str] = None,
) -> List[List[str]] | List[List[Tuple[str, float]]]:
    """
    Convert a Pandas DataFrame to GSP transaction format.

    This function supports two input formats:
    1. Grouped format: Rows grouped by transaction_id, with separate columns for items and optional timestamps
    2. Sequence format: Each row contains a complete transaction as a list/array

    Parameters:
        df: Pandas DataFrame to convert
        transaction_col: Column name for transaction IDs (grouped format)
        item_col: Column name for items (grouped format)
        timestamp_col: Optional column name for timestamps (grouped format)
        sequence_col: Column name containing sequences (sequence format)

    Returns:
        List of transactions, where each transaction is either:
        - A list of items (strings)
        - A list of (item, timestamp) tuples

    Raises:
        DataFrameAdapterError: If the DataFrame schema is invalid or required columns are missing

    Examples:
        >>> import pandas as pd
        >>> # Grouped format
        >>> df = pd.DataFrame(
        ...     {
        ...         "txn_id": [1, 1, 2, 2],
        ...         "item": ["A", "B", "C", "D"],
        ...     }
        ... )
        >>> pandas_to_transactions(df, transaction_col="txn_id", item_col="item")
        [['A', 'B'], ['C', 'D']]

        >>> # Sequence format
        >>> df = pd.DataFrame({"seq": [["A", "B"], ["C", "D"]]})
        >>> pandas_to_transactions(df, sequence_col="seq")
        [['A', 'B'], ['C', 'D']]
    """
    if sequence_col is not None:
        return _pandas_sequence_format(df, sequence_col, timestamp_col)
    elif transaction_col is not None and item_col is not None:
        return _pandas_grouped_format(df, transaction_col, item_col, timestamp_col)
    else:
        raise DataFrameAdapterError("Must specify either 'sequence_col' or both 'transaction_col' and 'item_col'")


def _pandas_sequence_format(
    df: pd.DataFrame,
    sequence_col: str,
    timestamp_col: Optional[str] = None,
) -> List[List[str]] | List[List[Tuple[str, float]]]:
    """
    Convert Pandas DataFrame in sequence format.

    Parameters:
        df: Pandas DataFrame
        sequence_col: Column containing sequences
        timestamp_col: Optional column containing timestamps per sequence

    Returns:
        List of transactions
    """
    if sequence_col not in df.columns:
        raise DataFrameAdapterError(f"Column '{sequence_col}' not found in DataFrame")

    sequences: List[Any] = df[sequence_col].tolist()

    if timestamp_col is not None:
        if timestamp_col not in df.columns:
            raise DataFrameAdapterError(f"Column '{timestamp_col}' not found in DataFrame")

        timestamps: List[Any] = df[timestamp_col].tolist()

        # Create timestamped transactions
        result: List[List[Tuple[str, float]]] = []
        for seq, times in zip(sequences, timestamps, strict=True):
            if not isinstance(seq, list) or not isinstance(times, list):
                raise DataFrameAdapterError(f"Both '{sequence_col}' and '{timestamp_col}' must contain lists")
            seq_list: List[Any] = cast(List[Any], seq)
            times_list: List[Any] = cast(List[Any], times)
            if len(seq_list) != len(times_list):
                raise DataFrameAdapterError(f"Sequence and timestamp lists must have the same length")
            result.append([(str(item), float(ts)) for item, ts in zip(seq_list, times_list, strict=True)])
        return result
    else:
        # Create non-timestamped transactions
        result_simple: List[List[str]] = []
        for seq in sequences:
            if not isinstance(seq, list):
                raise DataFrameAdapterError(f"Column '{sequence_col}' must contain lists")
            result_simple.append([str(item) for item in seq])  # pyright: ignore[reportUnknownArgumentType,reportUnknownVariableType]
        return result_simple


def _pandas_grouped_format(
    df: pd.DataFrame,
    transaction_col: str,
    item_col: str,
    timestamp_col: Optional[str] = None,
) -> List[List[str]] | List[List[Tuple[str, float]]]:
    """
    Convert Pandas DataFrame in grouped format.

    Parameters:
        df: Pandas DataFrame
        transaction_col: Column containing transaction IDs
        item_col: Column containing items
        timestamp_col: Optional column containing timestamps

    Returns:
        List of transactions
    """
    # Validate required columns exist
    if transaction_col not in df.columns:
        raise DataFrameAdapterError(f"Column '{transaction_col}' not found in DataFrame")
    if item_col not in df.columns:
        raise DataFrameAdapterError(f"Column '{item_col}' not found in DataFrame")

    # Sort by transaction and optionally timestamp
    sort_cols = [transaction_col]
    if timestamp_col is not None:
        if timestamp_col not in df.columns:
            raise DataFrameAdapterError(f"Column '{timestamp_col}' not found in DataFrame")
        sort_cols.append(timestamp_col)

    df_sorted = df.sort_values(by=sort_cols)

    # Group by transaction
    if timestamp_col is not None:
        # Create timestamped transactions
        grouped = df_sorted.groupby(transaction_col, sort=False)
        result: List[List[Tuple[str, float]]] = []
        for _, group in grouped:
            items: List[Any] = group[item_col].tolist()
            timestamps_list: List[Any] = group[timestamp_col].tolist()
            result.append([(str(item), float(ts)) for item, ts in zip(items, timestamps_list, strict=True)])
        return result
    else:
        # Create non-timestamped transactions
        grouped = df_sorted.groupby(transaction_col, sort=False)
        result_simple: List[List[str]] = []
        for _, group in grouped:
            items_list: List[Any] = group[item_col].tolist()
            result_simple.append([str(item) for item in items_list])
        return result_simple


def detect_dataframe_type(data: Any) -> Optional[str]:
    """
    Detect the type of DataFrame (Polars or Pandas).

    Parameters:
        data: Data to check

    Returns:
        'polars' if Polars DataFrame, 'pandas' if Pandas DataFrame, None otherwise
    """
    if isinstance(data, (pl.DataFrame, pl.LazyFrame)):
        return "polars"

    if isinstance(data, pd.DataFrame):
        return "pandas"

    return None


def dataframe_to_transactions(
    df: pl.DataFrame | pl.LazyFrame | pd.DataFrame,
    transaction_col: Optional[str] = None,
    item_col: Optional[str] = None,
    timestamp_col: Optional[str] = None,
    sequence_col: Optional[str] = None,
) -> List[List[str]] | List[List[Tuple[str, float]]]:
    """
    Convert any supported DataFrame to GSP transaction format.

    Automatically detects whether the input is a Polars or Pandas DataFrame
    and uses the appropriate conversion function.

    Parameters:
        df: DataFrame to convert (Polars or Pandas)
        transaction_col: Column name for transaction IDs (grouped format)
        item_col: Column name for items (grouped format)
        timestamp_col: Optional column name for timestamps (grouped format)
        sequence_col: Column name containing sequences (sequence format)

    Returns:
        List of transactions

    Raises:
        DataFrameAdapterError: If the input is not a recognized DataFrame type
    """
    df_type = detect_dataframe_type(df)

    if df_type == "polars":
        return polars_to_transactions(df, transaction_col, item_col, timestamp_col, sequence_col)  # type: ignore
    elif df_type == "pandas":
        return pandas_to_transactions(df, transaction_col, item_col, timestamp_col, sequence_col)  # type: ignore
    else:
        raise DataFrameAdapterError(
            "Input must be a Polars or Pandas DataFrame. "
            "Install required libraries with: pip install 'gsppy[dataframe]'"
        )
