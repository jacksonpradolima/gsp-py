"""
Unit tests for DataFrame input support in GSP-Py.

This module tests the DataFrame adapters for both Polars and Pandas DataFrames,
including various input formats, edge cases, and error handling.

Author: Jackson Antonio do Prado Lima
Email: jacksonpradolima@gmail.com
"""

import pandas as pd
import polars as pl
import pytest

from gsppy.gsp import GSP


class TestPolarsDataFrame:
    """Tests for Polars DataFrame input."""

    def test_polars_grouped_format_simple(self):
        """Test Polars DataFrame with grouped format (transaction_id + item)."""
        df = pl.DataFrame(
            {
                "transaction_id": [1, 1, 2, 2, 2, 3, 3],
                "item": ["A", "B", "A", "C", "D", "B", "D"],
            }
        )

        gsp = GSP(df, transaction_col="transaction_id", item_col="item")
        result = gsp.search(min_support=0.5)

        # Check that we got patterns
        assert len(result) > 0
        # Check that singleton patterns include common items
        assert any("A" in pattern for pattern in result[0].keys())
        assert any("B" in pattern for pattern in result[0].keys())

    def test_polars_grouped_format_with_timestamps(self):
        """Test Polars DataFrame with timestamps in grouped format."""
        df = pl.DataFrame(
            {
                "transaction_id": [1, 1, 2, 2, 2],
                "item": ["A", "B", "A", "C", "D"],
                "timestamp": [1.0, 2.0, 1.0, 3.0, 4.0],
            }
        )

        gsp = GSP(df, transaction_col="transaction_id", item_col="item", timestamp_col="timestamp", maxgap=5.0)
        result = gsp.search(min_support=0.5)

        # Check that we got patterns
        assert len(result) > 0

    def test_polars_sequence_format(self):
        """Test Polars DataFrame with sequence format (list column)."""
        df = pl.DataFrame({"sequence": [["A", "B"], ["A", "C", "D"], ["B", "D"]]})

        gsp = GSP(df, sequence_col="sequence")
        result = gsp.search(min_support=0.5)

        # Check that we got patterns
        assert len(result) > 0
        # Check singleton patterns
        assert ("A",) in result[0] or ("B",) in result[0] or ("D",) in result[0]

    def test_polars_sequence_format_with_timestamps(self):
        """Test Polars DataFrame with sequences and timestamps."""
        df = pl.DataFrame(
            {
                "sequence": [["A", "B"], ["A", "C"]],
                "timestamps": [[1.0, 2.0], [1.0, 3.0]],
            }
        )

        gsp = GSP(df, sequence_col="sequence", timestamp_col="timestamps")
        result = gsp.search(min_support=0.5)

        # Check that we got patterns
        assert len(result) > 0

    def test_polars_missing_column_error(self):
        """Test error handling for missing columns."""
        df = pl.DataFrame(
            {
                "transaction_id": [1, 1, 2],
                "item": ["A", "B", "C"],
            }
        )

        # Try to use non-existent timestamp column
        with pytest.raises(ValueError, match="not found"):
            GSP(df, transaction_col="transaction_id", item_col="item", timestamp_col="nonexistent")

    def test_polars_invalid_format_error(self):
        """Test error handling for invalid format specification."""
        df = pl.DataFrame({"data": [["A", "B"], ["C", "D"]]})

        # Must specify either sequence_col or both transaction_col and item_col
        with pytest.raises(ValueError, match="Must specify"):
            GSP(df)


class TestPandasDataFrame:
    """Tests for Pandas DataFrame input."""

    def test_pandas_grouped_format_simple(self):
        """Test Pandas DataFrame with grouped format (transaction_id + item)."""
        df = pd.DataFrame(
            {
                "transaction_id": [1, 1, 2, 2, 2, 3, 3],
                "item": ["A", "B", "A", "C", "D", "B", "D"],
            }
        )

        gsp = GSP(df, transaction_col="transaction_id", item_col="item")
        result = gsp.search(min_support=0.5)

        # Check that we got patterns
        assert len(result) > 0
        # Check that singleton patterns include common items
        assert any("A" in pattern for pattern in result[0].keys())
        assert any("B" in pattern for pattern in result[0].keys())

    def test_pandas_grouped_format_with_timestamps(self):
        """Test Pandas DataFrame with timestamps in grouped format."""
        df = pd.DataFrame(
            {
                "transaction_id": [1, 1, 2, 2, 2],
                "item": ["A", "B", "A", "C", "D"],
                "timestamp": [1.0, 2.0, 1.0, 3.0, 4.0],
            }
        )

        gsp = GSP(df, transaction_col="transaction_id", item_col="item", timestamp_col="timestamp", maxgap=5.0)
        result = gsp.search(min_support=0.5)

        # Check that we got patterns
        assert len(result) > 0

    def test_pandas_sequence_format(self):
        """Test Pandas DataFrame with sequence format (list column)."""
        df = pd.DataFrame({"sequence": [["A", "B"], ["A", "C", "D"], ["B", "D"]]})

        gsp = GSP(df, sequence_col="sequence")
        result = gsp.search(min_support=0.5)

        # Check that we got patterns
        assert len(result) > 0
        # Check singleton patterns
        assert ("A",) in result[0] or ("B",) in result[0] or ("D",) in result[0]

    def test_pandas_sequence_format_with_timestamps(self):
        """Test Pandas DataFrame with sequences and timestamps."""
        df = pd.DataFrame(
            {
                "sequence": [["A", "B"], ["A", "C"]],
                "timestamps": [[1.0, 2.0], [1.0, 3.0]],
            }
        )

        gsp = GSP(df, sequence_col="sequence", timestamp_col="timestamps")
        result = gsp.search(min_support=0.5)

        # Check that we got patterns
        assert len(result) > 0

    def test_pandas_missing_column_error(self):
        """Test error handling for missing columns."""
        df = pd.DataFrame(
            {
                "transaction_id": [1, 1, 2],
                "item": ["A", "B", "C"],
            }
        )

        # Try to use non-existent timestamp column
        with pytest.raises(ValueError, match="not found"):
            GSP(df, transaction_col="transaction_id", item_col="item", timestamp_col="nonexistent")


class TestDataFrameCompatibility:
    """Tests for DataFrame compatibility and edge cases."""

    def test_list_input_with_dataframe_params_error(self):
        """Test that DataFrame parameters cannot be used with list input."""
        transactions = [["A", "B"], ["C", "D"]]

        with pytest.raises(ValueError, match="DataFrame parameters"):
            GSP(transactions, transaction_col="txn")

    def test_list_input_still_works(self):
        """Test that traditional list input still works."""
        transactions = [["A", "B"], ["A", "C"], ["B", "C"]]

        gsp = GSP(transactions)
        result = gsp.search(min_support=0.5)

        # Check that we got patterns
        assert len(result) > 0


class TestDataFrameInteroperability:
    """Tests comparing Polars and Pandas results."""

    def test_polars_pandas_same_results(self):
        """Test that Polars and Pandas produce the same patterns."""
        # Create same data in both formats
        data = {
            "transaction_id": [1, 1, 2, 2, 2, 3, 3],
            "item": ["A", "B", "A", "C", "D", "B", "D"],
        }

        df_polars = pl.DataFrame(data)
        df_pandas = pd.DataFrame(data)

        gsp_polars = GSP(df_polars, transaction_col="transaction_id", item_col="item")
        gsp_pandas = GSP(df_pandas, transaction_col="transaction_id", item_col="item")

        result_polars = gsp_polars.search(min_support=0.5)
        result_pandas = gsp_pandas.search(min_support=0.5)

        # Check same number of levels
        assert len(result_polars) == len(result_pandas)

        # Check same patterns at each level
        for level_polars, level_pandas in zip(result_polars, result_pandas, strict=False):
            assert set(level_polars.keys()) == set(level_pandas.keys())


class TestPolarsAdvancedFeatures:
    """Tests for advanced Polars-specific features."""

    def test_polars_large_dataset(self):
        """Test Polars with a larger dataset."""
        # Create a larger dataset
        n_transactions = 100
        transaction_ids: list[int] = []
        items: list[str] = []

        for txn_id in range(1, n_transactions + 1):
            # Each transaction has 2-5 items
            n_items = (txn_id % 4) + 2
            for _ in range(n_items):
                transaction_ids.append(txn_id)
                items.append(chr(65 + (txn_id % 10)))  # A-J

        df = pl.DataFrame(
            {
                "transaction_id": transaction_ids,
                "item": items,
            }
        )

        gsp = GSP(df, transaction_col="transaction_id", item_col="item")
        result = gsp.search(min_support=0.1)

        # Check that we got patterns
        assert len(result) > 0

    def test_polars_sorted_by_timestamp(self):
        """Test that timestamps are properly sorted."""
        df = pl.DataFrame(
            {
                "transaction_id": [1, 1, 1, 2, 2],
                "item": ["A", "B", "C", "A", "C"],
                "timestamp": [3.0, 1.0, 2.0, 1.0, 2.0],  # First transaction out of order
            }
        )

        gsp = GSP(df, transaction_col="transaction_id", item_col="item", timestamp_col="timestamp")
        result = gsp.search(min_support=0.5)

        # Should work correctly even with unsorted timestamps
        assert len(result) > 0

    def test_polars_lazyframe_grouped_format(self):
        """Test Polars LazyFrame with grouped format."""
        df = pl.DataFrame(
            {
                "transaction_id": [1, 1, 2, 2, 2],
                "item": ["A", "B", "A", "C", "D"],
            }
        ).lazy()  # Convert to LazyFrame

        gsp = GSP(df, transaction_col="transaction_id", item_col="item")
        result = gsp.search(min_support=0.5)

        # Check that LazyFrame works correctly
        assert len(result) > 0
        assert ("A",) in result[0]

    def test_polars_lazyframe_sequence_format(self):
        """Test Polars LazyFrame with sequence format."""
        df = pl.DataFrame({"sequence": [["A", "B"], ["A", "C", "D"], ["B", "D"]]}).lazy()  # Convert to LazyFrame

        gsp = GSP(df, sequence_col="sequence")
        result = gsp.search(min_support=0.5)

        # Check that LazyFrame works correctly
        assert len(result) > 0


class TestPandasAdvancedFeatures:
    """Tests for advanced Pandas-specific features."""

    def test_pandas_with_index(self):
        """Test Pandas DataFrame with custom index."""
        df = pd.DataFrame(
            {
                "transaction_id": [1, 1, 2, 2],
                "item": ["A", "B", "C", "D"],
            },
            index=[10, 20, 30, 40],
        )

        gsp = GSP(df, transaction_col="transaction_id", item_col="item")
        result = gsp.search(min_support=0.5)

        # Should work correctly regardless of index
        assert len(result) > 0

    def test_pandas_dtypes_conversion(self):
        """Test that various dtypes are handled correctly."""
        df = pd.DataFrame(
            {
                "transaction_id": [1, 1, 2, 2],
                "item": ["A", "B", "C", "D"],
                "timestamp": [1, 2, 3, 4],  # Integer timestamps
            }
        )

        gsp = GSP(df, transaction_col="transaction_id", item_col="item", timestamp_col="timestamp")
        result = gsp.search(min_support=0.5)

        # Should work with integer timestamps
        assert len(result) > 0
