"""
Example: Using GSP-Py with DataFrames

This script demonstrates how to use GSP-Py with Polars and Pandas DataFrames
for high-performance sequential pattern mining.

Requirements:
    pip install 'gsppy[dataframe]'
"""

import tempfile
import polars as pl
import pandas as pd
from gsppy import GSP

print("=" * 70)
print("GSP-Py DataFrame Examples")
print("=" * 70)

# Example 1: Polars DataFrame with Grouped Format
print("\n1. Polars DataFrame (Grouped Format)")
print("-" * 70)

df_polars = pl.DataFrame({
    "transaction_id": [1, 1, 2, 2, 2, 3, 3, 4, 4],
    "item": ["Bread", "Milk", "Bread", "Diaper", "Beer", "Milk", "Coke", "Bread", "Beer"],
})

print("Input DataFrame:")
print(df_polars)

gsp_polars = GSP(df_polars, transaction_col="transaction_id", item_col="item")
patterns_polars = gsp_polars.search(min_support=0.5)

print("\nFrequent Patterns (min_support=0.5):")
for level, freq_patterns in enumerate(patterns_polars, start=1):
    print(f"\n{level}-Sequence Patterns:")
    for pattern, support in freq_patterns.items():
        print(f"  {pattern}: {support}")

# Example 2: Pandas DataFrame with Sequence Format
print("\n" + "=" * 70)
print("2. Pandas DataFrame (Sequence Format)")
print("-" * 70)

df_pandas = pd.DataFrame({
    "transaction": [
        ["Login", "Browse", "AddToCart", "Purchase"],
        ["Login", "Browse", "Purchase"],
        ["Browse", "AddToCart", "Purchase"],
        ["Login", "AddToCart", "Purchase"],
    ]
})

print("Input DataFrame:")
print(df_pandas)

gsp_pandas = GSP(df_pandas, sequence_col="transaction")
patterns_pandas = gsp_pandas.search(min_support=0.5)

print("\nFrequent Patterns (min_support=0.5):")
for level, freq_patterns in enumerate(patterns_pandas, start=1):
    print(f"\n{level}-Sequence Patterns:")
    for pattern, support in freq_patterns.items():
        print(f"  {pattern}: {support}")

# Example 3: Polars DataFrame with Timestamps
print("\n" + "=" * 70)
print("3. Polars DataFrame with Timestamps (Temporal Mining)")
print("-" * 70)

df_temporal = pl.DataFrame({
    "transaction_id": [1, 1, 1, 2, 2, 2, 3, 3, 3],
    "item": ["A", "B", "C", "A", "B", "C", "A", "B", "C"],
    "timestamp": [1, 2, 5, 1, 3, 15, 1, 2, 4],  # Note: Transaction 2 has large gap
})

print("Input DataFrame:")
print(df_temporal)

# Find patterns where consecutive items occur within 5 time units
gsp_temporal = GSP(
    df_temporal,
    transaction_col="transaction_id",
    item_col="item",
    timestamp_col="timestamp",
    maxgap=5
)
patterns_temporal = gsp_temporal.search(min_support=0.5)

print("\nFrequent Patterns with maxgap=5 (min_support=0.5):")
print("Note: Pattern ('A', 'B', 'C') is found only in transactions 1 and 3")
print("      because transaction 2 has a gap > 5 between B and C")
for level, freq_patterns in enumerate(patterns_temporal, start=1):
    print(f"\n{level}-Sequence Patterns:")
    for pattern, support in freq_patterns.items():
        print(f"  {pattern}: {support}")

# Example 4: Reading from Parquet file
print("\n" + "=" * 70)
print("4. Reading from Parquet File")
print("-" * 70)

# Save DataFrame to Parquet using secure temporary directory
import os
parquet_file = os.path.join(tempfile.gettempdir(), "example_transactions.parquet")
df_polars.write_parquet(parquet_file)
print(f"Saved DataFrame to {parquet_file}")

# Read back and process
df_from_parquet = pl.read_parquet(parquet_file)
gsp_parquet = GSP(df_from_parquet, transaction_col="transaction_id", item_col="item")
patterns_parquet = gsp_parquet.search(min_support=0.5)

print(f"Successfully loaded from Parquet and found {len(patterns_parquet[0])} 1-sequence patterns")

# Example 5: Performance comparison
print("\n" + "=" * 70)
print("5. Performance Comparison: DataFrame vs List")
print("-" * 70)

import time

# Create a larger dataset
n_transactions = 1000
transaction_ids = []
items = []

for txn_id in range(1, n_transactions + 1):
    n_items = (txn_id % 5) + 2  # 2-6 items per transaction
    for i in range(n_items):
        transaction_ids.append(txn_id)
        items.append(chr(65 + (i % 10)))  # A-J

df_large = pl.DataFrame({
    "transaction_id": transaction_ids,
    "item": items,
})

# Method 1: Direct DataFrame input
start = time.time()
gsp_df = GSP(df_large, transaction_col="transaction_id", item_col="item")
_ = gsp_df.search(min_support=0.1)
time_df = time.time() - start

# Method 2: Convert to list first (traditional approach)
from gsppy.dataframe_adapters import polars_to_transactions
transactions_list = polars_to_transactions(df_large, transaction_col="transaction_id", item_col="item")

start = time.time()
gsp_list = GSP(transactions_list)
_ = gsp_list.search(min_support=0.1)
time_list = time.time() - start

print(f"Dataset: {n_transactions} transactions")
print(f"DataFrame method: {time_df:.4f} seconds")
print(f"List method:      {time_list:.4f} seconds")
print(f"Difference:       {abs(time_df - time_list):.4f} seconds")
print("\nNote: Performance is similar because conversion is fast and")
print("      the GSP algorithm dominates runtime for pattern mining.")

print("\n" + "=" * 70)
print("Examples completed!")
print("=" * 70)
