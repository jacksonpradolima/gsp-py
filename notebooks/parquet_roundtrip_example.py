import marimo

__generated_with = "0.19.11"
app = marimo.App()


@app.cell
def _():
    """
    Example: Round-trip Parquet Workflow with GSP-Py

    This script demonstrates a complete workflow for using Parquet files with GSP-Py:
    1. Load transactions from CSV
    2. Convert to Parquet format
    3. Run GSP mining on Parquet data
    4. Export results to Parquet
    5. Handle edge cases and errors

    Requirements:
        pip install 'gsppy[dataframe]'
    """

    import os
    import tempfile

    import polars as pl

    from gsppy import GSP
    from gsppy.cli import (
        write_patterns_to_arrow,
        write_patterns_to_parquet,
        read_transactions_from_parquet,
    )

    print("=" * 80)
    print("GSP-Py Parquet Round-trip Workflow Examples")
    print("=" * 80)

    # ============================================================================
    # Example 1: CSV → Parquet → Mining → Parquet Export
    # ============================================================================
    print("\n1. Complete Round-trip: CSV → Parquet → Mining → Parquet")
    print("-" * 80)

    # Step 1: Create sample CSV data
    csv_data = """transaction_id,item,timestamp
    1,Bread,1.0
    1,Milk,2.0
    2,Milk,1.0
    2,Diaper,2.0
    3,Bread,1.0
    3,Diaper,2.0
    3,Beer,3.0"""

    # Step 2: Convert CSV to Parquet using Polars
    print("\nStep 1: Converting CSV to Parquet...")
    df_from_csv = pl.read_csv(csv_data.encode(), has_header=True)
    print(f"Loaded {len(df_from_csv)} rows from CSV")
    print(df_from_csv)

    # Save to Parquet
    input_parquet = os.path.join(tempfile.gettempdir(), "transactions.parquet")
    df_from_csv.write_parquet(input_parquet)
    print(f"\n✓ Saved to Parquet: {input_parquet}")

    # Step 3: Load from Parquet and run GSP mining
    print("\nStep 2: Loading from Parquet and mining patterns...")
    transactions = read_transactions_from_parquet(
        input_parquet,
        transaction_col="transaction_id",
        item_col="item",
        timestamp_col="timestamp"
    )
    print(f"Loaded {len(transactions)} transactions")

    gsp = GSP(transactions)
    patterns = gsp.search(min_support=0.5)
    print(f"\n✓ Found {sum(len(level) for level in patterns)} patterns")

    # Display patterns
    for level_idx, level_patterns in enumerate(patterns, start=1):
        print(f"\n{level_idx}-Sequence Patterns:")
        for pattern, support in level_patterns.items():
            print(f"  {pattern}: {support}")

    # Step 4: Export results to Parquet
    output_parquet = os.path.join(tempfile.gettempdir(), "gsp_results.parquet")
    write_patterns_to_parquet(patterns, output_parquet)
    print(f"\n✓ Exported results to: {output_parquet}")

    # Verify exported results
    results_df = pl.read_parquet(output_parquet)
    print("\nExported Results Preview:")
    print(results_df.head())

    # ============================================================================
    # Example 2: Working with Sequence Format (Pre-aggregated)
    # ============================================================================
    print("\n" + "=" * 80)
    print("2. Sequence Format Workflow")
    print("-" * 80)

    # Create data with sequences already grouped
    sequences_df = pl.DataFrame({
        "customer_id": [1, 2, 3, 4],
        "purchase_sequence": [
            ["Login", "Browse", "AddToCart", "Purchase"],
            ["Login", "Browse", "Purchase"],
            ["Browse", "AddToCart", "Purchase"],
            ["Login", "AddToCart", "Purchase"],
        ]
    })

    print("\nInput DataFrame (Sequence Format):")
    print(sequences_df)

    # Save to Parquet
    sequence_parquet = os.path.join(tempfile.gettempdir(), "sequences.parquet")
    sequences_df.write_parquet(sequence_parquet)

    # Load and mine
    transactions = read_transactions_from_parquet(
        sequence_parquet,
        sequence_col="purchase_sequence"
    )

    gsp = GSP(transactions)
    patterns = gsp.search(min_support=0.5)

    print("\nFrequent Patterns (min_support=0.5):")
    for level_idx, level_patterns in enumerate(patterns, start=1):
        print(f"\n{level_idx}-Sequence Patterns:")
        for pattern, support in level_patterns.items():
            print(f"  {pattern}: {support}")

    # Export to Arrow format for variety
    output_arrow = os.path.join(tempfile.gettempdir(), "sequence_results.arrow")
    write_patterns_to_arrow(patterns, output_arrow)
    print(f"\n✓ Exported to Arrow format: {output_arrow}")

    # ============================================================================
    # Example 3: Edge Cases and Error Handling
    # ============================================================================
    print("\n" + "=" * 80)
    print("3. Edge Cases and Error Handling")
    print("-" * 80)

    # Edge Case 1: Empty transactions
    print("\nEdge Case 1: Handling empty sequences...")
    empty_df = pl.DataFrame({
        "transaction_id": [],
        "item": []
    })
    empty_parquet = os.path.join(tempfile.gettempdir(), "empty.parquet")
    empty_df.write_parquet(empty_parquet)

    try:
        transactions = read_transactions_from_parquet(
            empty_parquet,
            transaction_col="transaction_id",
            item_col="item"
        )
        print(f"✓ Loaded {len(transactions)} transactions (empty is valid)")
    except Exception as e:
        print(f"✗ Error: {e}")

    # Edge Case 2: Missing columns
    print("\nEdge Case 2: Missing required columns...")
    wrong_cols_df = pl.DataFrame({
        "txn": [1, 2, 3],
        "product": ["A", "B", "C"]
    })
    wrong_parquet = os.path.join(tempfile.gettempdir(), "wrong_cols.parquet")
    wrong_cols_df.write_parquet(wrong_parquet)

    try:
        read_transactions_from_parquet(
            wrong_parquet,
            transaction_col="transaction_id",  # This column doesn't exist
            item_col="item"  # This column doesn't exist
        )
        print("✓ Loaded successfully")
    except ValueError as e:
        print(f"✓ Caught expected error: {str(e)[:80]}...")

    # Edge Case 3: Mixed data types
    print("\nEdge Case 3: Mixed data types (integers as items)...")
    mixed_df = pl.DataFrame({
        "transaction_id": [1, 1, 2, 2],
        "item": [100, 200, 100, 300],  # Integer items
    })
    mixed_parquet = os.path.join(tempfile.gettempdir(), "mixed_types.parquet")
    mixed_df.write_parquet(mixed_parquet)

    try:
        transactions = read_transactions_from_parquet(
            mixed_parquet,
            transaction_col="transaction_id",
            item_col="item"
        )
        print(f"✓ Loaded {len(transactions)} transactions with integer items")
        print(f"  First transaction: {transactions[0]}")
    except Exception as e:
        print(f"✗ Error: {e}")

    # Edge Case 4: Large dataset simulation
    print("\nEdge Case 4: Large dataset handling...")
    n_transactions = 10000
    large_txn_ids = []
    large_items = []

    for i in range(n_transactions):
        for j in range(3):  # 3 items per transaction
            large_txn_ids.append(i)
            large_items.append(f"Item_{j % 10}")

    large_df = pl.DataFrame({
        "transaction_id": large_txn_ids,
        "item": large_items
    })

    large_parquet = os.path.join(tempfile.gettempdir(), "large.parquet")
    large_df.write_parquet(large_parquet)
    file_size_mb = os.path.getsize(large_parquet) / (1024 * 1024)
    print(f"✓ Created Parquet file: {file_size_mb:.2f} MB")

    transactions = read_transactions_from_parquet(
        large_parquet,
        transaction_col="transaction_id",
        item_col="item"
    )
    print(f"✓ Loaded {len(transactions)} transactions efficiently")

    # Run mining on large dataset
    gsp = GSP(transactions)
    patterns = gsp.search(min_support=0.1)
    print(f"✓ Mined {sum(len(level) for level in patterns)} patterns from large dataset")

    # ============================================================================
    # Example 4: Schema Evolution and Type Handling
    # ============================================================================
    print("\n" + "=" * 80)
    print("4. Schema Variations and Type Conversions")
    print("-" * 80)

    # Different column types
    print("\nHandling different timestamp formats...")

    # Float timestamps
    float_ts_df = pl.DataFrame({
        "txn_id": [1, 1, 1],
        "item": ["A", "B", "C"],
        "ts": [1.5, 2.5, 3.5]  # Float timestamps
    })

    # Integer timestamps
    int_ts_df = pl.DataFrame({
        "txn_id": [1, 1, 1],
        "item": ["A", "B", "C"],
        "ts": [1, 2, 3]  # Integer timestamps
    })

    for name, df in [("float", float_ts_df), ("integer", int_ts_df)]:
        temp_path = os.path.join(tempfile.gettempdir(), f"{name}_ts.parquet")
        df.write_parquet(temp_path)
    
        transactions = read_transactions_from_parquet(
            temp_path,
            transaction_col="txn_id",
            item_col="item",
            timestamp_col="ts"
        )
        print(f"✓ Handled {name} timestamps: {transactions[0][0]}")

    # ============================================================================
    # Cleanup
    # ============================================================================
    print("\n" + "=" * 80)
    print("Cleanup: Removing temporary files...")
    print("-" * 80)

    temp_files = [
        input_parquet, output_parquet, sequence_parquet, output_arrow,
        empty_parquet, wrong_parquet, mixed_parquet, large_parquet,
        os.path.join(tempfile.gettempdir(), "float_ts.parquet"),
        os.path.join(tempfile.gettempdir(), "integer_ts.parquet"),
    ]

    for temp_file in temp_files:
        if os.path.exists(temp_file):
            os.unlink(temp_file)
            print(f"✓ Removed: {temp_file}")

    print("\n" + "=" * 80)
    print("Examples completed successfully!")
    print("=" * 80)

    print("""
    Key Takeaways:
    1. Parquet format provides efficient storage for large transaction datasets
    2. GSP-Py seamlessly works with both grouped and sequence formats
    3. Round-trip workflows (CSV→Parquet→Mining→Export) are fully supported
    4. Edge cases like empty data, wrong columns, and mixed types are handled gracefully
    5. Large datasets benefit from Parquet's columnar storage and compression
    6. Results can be exported to multiple formats (Parquet, Arrow, CSV, JSON)
    """)
    return


if __name__ == "__main__":
    app.run()
