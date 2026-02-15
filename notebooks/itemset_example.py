import marimo

__generated_with = "0.19.11"
app = marimo.App()


@app.cell
def _():
    """
    Example demonstrating itemset support in GSP-Py.

    This example shows how to use GSP-Py with itemsets, where multiple items
    can occur together at the same time step in a sequence.

    Key concepts:
    1. Flat sequences: ['A', 'B', 'C'] - each item at separate time steps
    2. Itemset sequences: [['A', 'B'], ['C']] - A and B occur together, then C

    Author: Jackson Antonio do Prado Lima
    Email: jacksonpradolima@gmail.com
    """

    from gsppy import GSP

    def example_flat_vs_itemset():
        """
        Demonstrate the difference between flat and itemset representations.
        """
        print("=" * 80)
        print("EXAMPLE 1: Flat vs Itemset Sequences")
        print("=" * 80)
    
        # Flat sequences - each item happens at a separate time step
        print("\n1a. Flat sequences (traditional format):")
        flat_transactions = [
            ['A', 'B', 'C'],  # A, then B, then C
            ['A', 'C'],        # A, then C
            ['A', 'B', 'C'],  # A, then B, then C
        ]
        print(f"   Transactions: {flat_transactions}")
    
        gsp_flat = GSP(flat_transactions)
        patterns_flat = gsp_flat.search(min_support=0.66)
    
        print("   Frequent patterns (min_support=0.66):")
        for i, level_patterns in enumerate(patterns_flat, start=1):
            print(f"      {i}-sequences: {level_patterns}")
    
        # Itemset sequences - items in same list occur together
        print("\n1b. Itemset sequences:")
        itemset_transactions = [
            [['A', 'B'], ['C']],  # A and B together, then C
            [['A'], ['C']],        # A, then C
            [['A', 'B'], ['C']],  # A and B together, then C
        ]
        print(f"   Transactions: {itemset_transactions}")
    
        gsp_itemset = GSP(itemset_transactions)
        patterns_itemset = gsp_itemset.search(min_support=0.66)
    
        print("   Frequent patterns (min_support=0.66):")
        for i, level_patterns in enumerate(patterns_itemset, start=1):
            print(f"      {i}-sequences: {level_patterns}")


    def example_market_basket():
        """
        Real-world example: Market basket analysis with itemsets.
    
        Customers can buy multiple items in a single transaction, then return
        to buy more items in subsequent transactions.
        """
        print("\n" + "=" * 80)
        print("EXAMPLE 2: Market Basket Analysis with Itemsets")
        print("=" * 80)
    
        # Each customer's purchase history
        # Nested lists represent items bought together (same shopping trip)
        transactions = [
            # Customer 1: Bought bread & milk together, then came back for eggs
            [['Bread', 'Milk'], ['Eggs']],
        
            # Customer 2: Bought bread, milk & butter together
            [['Bread', 'Milk', 'Butter']],
        
            # Customer 3: Bought bread & milk together, then eggs later
            [['Bread', 'Milk'], ['Eggs']],
        
            # Customer 4: Bought bread & milk together, then eggs & butter together
            [['Bread', 'Milk'], ['Eggs', 'Butter']],
        ]
    
        print("\nCustomer transaction history:")
        for i, tx in enumerate(transactions, start=1):
            print(f"   Customer {i}: {tx}")
    
        gsp = GSP(transactions)
        patterns = gsp.search(min_support=0.5)
    
        print("\nFrequent patterns (min_support=0.5, i.e., 2+ customers):")
        for i, level_patterns in enumerate(patterns, start=1):
            print(f"\n   {i}-sequences:")
            for pattern, support in level_patterns.items():
                print(f"      {pattern} - appears in {support} customer histories")
    
        # Insights
        print("\n📊 Insights:")
        print("   - Customers who buy Bread and Milk often return to buy Eggs later")
        print("   - This is different from 'Bread, then Milk, then Eggs' pattern")
        print("   - Itemsets capture co-occurrence (items bought together)")


    def example_clickstream():
        """
        Example: Web analytics with itemsets.
    
        Users can view multiple pages in parallel (multiple tabs) before
        moving to the next set of pages.
        """
        print("\n" + "=" * 80)
        print("EXAMPLE 3: Web Clickstream with Parallel Page Views")
        print("=" * 80)
    
        # User sessions with parallel page views
        sessions = [
            # User 1: Opened Home & Products in tabs, then viewed Checkout
            [['Home', 'Products'], ['Checkout']],
        
            # User 2: Home and Products together, then Cart, then Checkout
            [['Home', 'Products'], ['Cart'], ['Checkout']],
        
            # User 3: Home page, then Products & Cart together, then Checkout
            [['Home'], ['Products', 'Cart'], ['Checkout']],
        
            # User 4: Home & Products together, then Checkout
            [['Home', 'Products'], ['Checkout']],
        ]
    
        print("\nUser sessions (parallel page views):")
        for i, session in enumerate(sessions, start=1):
            print(f"   User {i}: {session}")
    
        gsp = GSP(sessions)
        patterns = gsp.search(min_support=0.5)
    
        print("\nFrequent navigation patterns (min_support=0.5):")
        for i, level_patterns in enumerate(patterns, start=1):
            if level_patterns:
                print(f"\n   {i}-sequences:")
                for pattern, support in level_patterns.items():
                    print(f"      {pattern} - in {support} sessions")


    def example_spm_format():
        """
        Example: Reading itemsets from SPM format files.
    
        SPM format uses delimiters:
        - `-1` marks end of itemset
        - `-2` marks end of sequence
        """
        print("\n" + "=" * 80)
        print("EXAMPLE 4: Reading Itemsets from SPM Format")
        print("=" * 80)
    
        import tempfile
        import os
        from gsppy.utils import read_transactions_from_spm
    
        # Create a temporary SPM file with itemsets
        spm_content = """1 2 -1 3 -1 -2
    1 -1 3 4 -1 -2
    1 2 -1 3 -1 -2"""
    
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(spm_content)
            temp_path = f.name
    
        try:
            print(f"\nSPM file content:\n{spm_content}")
        
            # Read with itemsets flattened (backward compatible)
            print("\nReading with itemsets flattened (preserve_itemsets=False):")
            flat_txs = read_transactions_from_spm(temp_path, preserve_itemsets=False)
            for i, tx in enumerate(flat_txs, start=1):
                print(f"   Transaction {i}: {tx}")
        
            # Read with itemsets preserved
            print("\nReading with itemsets preserved (preserve_itemsets=True):")
            itemset_txs = read_transactions_from_spm(temp_path, preserve_itemsets=True)
            for i, tx in enumerate(itemset_txs, start=1):
                print(f"   Transaction {i}: {tx}")
            
            # Use in GSP
            print("\nRunning GSP on itemset data:")
            gsp = GSP(itemset_txs)
            patterns = gsp.search(min_support=0.66)
            print(f"   Frequent patterns: {patterns}")
        
        finally:
            os.unlink(temp_path)


    if __name__ == '__main__':
        # Run all examples
        example_flat_vs_itemset()
        example_market_basket()
        example_clickstream()
        example_spm_format()
    
        print("\n" + "=" * 80)
        print("Summary:")
        print("=" * 80)
        print("✓ Itemsets capture co-occurrence of items at the same time step")
        print("✓ Flat sequences are automatically normalized to itemsets internally")
        print("✓ Both formats work seamlessly with GSP-Py")
        print("✓ Use itemsets when temporal co-occurrence matters in your domain")
        print("=" * 80)
    return


if __name__ == "__main__":
    app.run()
