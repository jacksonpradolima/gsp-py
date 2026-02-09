"""
Itemset Example for GSP-Py

This interactive notebook demonstrates how to use GSP-Py with itemsets,
where multiple items can occur together at the same time step in a sequence.
"""

import marimo

__generated_with = "0.19.9"
app = marimo.App(width="medium")


@app.cell(hide_code=False)
def _():
    """Import required libraries"""
    from gsppy import GSP
    import marimo as mo
    return GSP, mo


@app.cell(hide_code=False)
def _(mo):
    """Introduction"""
    mo.md("""
    # GSP-Py: Itemset Support Example
    
    This notebook demonstrates how to use **itemsets** in GSP-Py, where multiple items
    can occur together at the same time step in a sequence.
    
    ## Key Concepts
    
    1. **Flat sequences**: `['A', 'B', 'C']` - each item at separate time steps
    2. **Itemset sequences**: `[['A', 'B'], ['C']]` - A and B occur together, then C
    """)
    return


@app.cell(hide_code=False)
def _(mo):
    """Example 1 Header"""
    mo.md("""
    ## Example 1: Flat vs Itemset Sequences
    
    Let's compare how flat and itemset sequences differ in their representation and results.
    """)
    return


@app.cell(hide_code=False)
def _(GSP, mo):
    """Flat sequences example"""
    flat_transactions = [
        ['A', 'B', 'C'],  # A, then B, then C
        ['A', 'C'],        # A, then C
        ['A', 'B', 'C'],  # A, then B, then C
    ]
    
    gsp_flat = GSP(flat_transactions)
    patterns_flat = gsp_flat.search(min_support=0.66)
    
    _output_flat = [f"**Flat transactions:** `{flat_transactions}`\n"]
    _output_flat.append("\n**Frequent patterns (min_support=0.66):**\n")
    for _i, _level_patterns in enumerate(patterns_flat, start=1):
        _output_flat.append(f"\n{_i}-sequences: `{_level_patterns}`")
    
    mo.md("\n".join(_output_flat))
    return flat_transactions, gsp_flat, patterns_flat


@app.cell(hide_code=False)
def _(GSP, mo):
    """Itemset sequences example"""
    itemset_transactions = [
        [['A', 'B'], ['C']],  # A and B together, then C
        [['A'], ['C']],        # A, then C
        [['A', 'B'], ['C']],  # A and B together, then C
    ]
    
    gsp_itemset = GSP(itemset_transactions)
    patterns_itemset = gsp_itemset.search(min_support=0.66)
    
    _output_itemset = [f"**Itemset transactions:** `{itemset_transactions}`\n"]
    _output_itemset.append("\n**Frequent patterns (min_support=0.66):**\n")
    for _i, _level_patterns in enumerate(patterns_itemset, start=1):
        _output_itemset.append(f"\n{_i}-sequences: `{_level_patterns}`")
    
    mo.md("\n".join(_output_itemset))
    return gsp_itemset, itemset_transactions, patterns_itemset


@app.cell(hide_code=False)
def _(mo):
    """Example 2 Header"""
    mo.md("""
    ## Example 2: Market Basket Analysis with Itemsets
    
    A real-world example: Market basket analysis where customers can buy multiple items
    in a single transaction, then return to buy more items in subsequent transactions.
    """)
    return


@app.cell(hide_code=False)
def _(GSP, mo):
    """Market basket example"""
    # Each customer's purchase history
    # Nested lists represent items bought together (same shopping trip)
    market_transactions = [
        # Customer 1: Bought bread & milk together, then came back for eggs
        [['Bread', 'Milk'], ['Eggs']],
        
        # Customer 2: Bought bread, milk & butter together
        [['Bread', 'Milk', 'Butter']],
        
        # Customer 3: Bought bread & milk together, then eggs later
        [['Bread', 'Milk'], ['Eggs']],
        
        # Customer 4: Bought bread & milk, then butter
        [['Bread', 'Milk'], ['Butter']],
        
        # Customer 5: Bought bread alone, then milk & eggs together
        [['Bread'], ['Milk', 'Eggs']],
    ]
    
    gsp_market = GSP(market_transactions)
    patterns_market = gsp_market.search(min_support=0.4)
    
    _output_market = ["**Customer purchase histories:**\n"]
    for _idx, _txn in enumerate(market_transactions, start=1):
        _output_market.append(f"- Customer {_idx}: `{_txn}`")
    
    _output_market.append(f"\n\n**Frequent patterns (min_support=0.4):**\n")
    for _level_idx, _level_patterns in enumerate(patterns_market, start=1):
        _output_market.append(f"\n**Level {_level_idx}** ({len(_level_patterns)} patterns):")
        for _pattern, _support in sorted(_level_patterns.items(), key=lambda x: x[1], reverse=True):
            _output_market.append(f"  - Pattern: `{_pattern}` | Support: {_support}")
    
    mo.md("\n".join(_output_market))
    return gsp_market, market_transactions, patterns_market


@app.cell(hide_code=False)
def _(mo):
    """Example 3 Header"""
    mo.md("""
    ## Example 3: E-commerce Click Streams with Concurrent Actions
    
    Tracking user behavior where multiple actions can happen simultaneously
    (e.g., adding multiple items to cart at once).
    """)
    return


@app.cell(hide_code=False)
def _(GSP, mo):
    """E-commerce example"""
    clickstream_transactions = [
        # User 1: Viewed homepage, added multiple items to cart together, then purchased
        [['HomePage'], ['AddToCart_ProductA', 'AddToCart_ProductB'], ['Purchase']],
        
        # User 2: Viewed homepage, searched, added one item, purchased
        [['HomePage'], ['Search'], ['AddToCart_ProductA'], ['Purchase']],
        
        # User 3: Viewed homepage, added multiple items, purchased
        [['HomePage'], ['AddToCart_ProductA', 'AddToCart_ProductB'], ['Purchase']],
        
        # User 4: Viewed homepage, viewed multiple products, added to cart, purchased
        [['HomePage'], ['ViewProduct_A', 'ViewProduct_B'], ['AddToCart_ProductA'], ['Purchase']],
        
        # User 5: Viewed homepage, added to cart, purchased
        [['HomePage'], ['AddToCart_ProductA'], ['Purchase']],
    ]
    
    gsp_clickstream = GSP(clickstream_transactions)
    patterns_clickstream = gsp_clickstream.search(min_support=0.6)
    
    _output_clickstream = ["**User clickstream data:**\n"]
    for _usr_idx, _stream in enumerate(clickstream_transactions, start=1):
        _output_clickstream.append(f"- User {_usr_idx}: `{_stream}`")
    
    _output_clickstream.append(f"\n\n**Frequent patterns (min_support=0.6):**\n")
    _output_clickstream.append("These patterns show common user journeys through the site.\n")
    
    for _lvl_idx, _lvl_patterns in enumerate(patterns_clickstream, start=1):
        _output_clickstream.append(f"\n**Level {_lvl_idx}** ({len(_lvl_patterns)} patterns):")
        for _ptrn, _sup in sorted(_lvl_patterns.items(), key=lambda x: x[1], reverse=True):
            _output_clickstream.append(f"  - `{_ptrn}` | Support: {_sup}")
    
    mo.md("\n".join(_output_clickstream))
    return clickstream_transactions, gsp_clickstream, patterns_clickstream


@app.cell(hide_code=False)
def _(mo):
    """Conclusion"""
    mo.md("""
    ## Key Takeaways
    
    Using itemsets in GSP-Py allows you to:
    
    1. **Model simultaneous events**: Capture items that occur together at the same time
    2. **More accurate patterns**: Distinguish between items bought together vs. sequentially
    3. **Richer analysis**: Find patterns like "customers who buy A and B together often return to buy C"
    
    ### When to Use Itemsets
    
    - **Market basket analysis**: Multiple items purchased in single transaction
    - **Web analytics**: Multiple clicks/actions happening simultaneously
    - **Medical records**: Multiple symptoms or treatments occurring at the same time
    - **Manufacturing**: Multiple parts installed together in assembly process
    
    ### Syntax Reminder
    
    - Flat: `[['A', 'B', 'C']]` - each item is separate
    - Itemset: `[[['A', 'B'], ['C']]]` - A and B together, then C
    """)
    return


if __name__ == "__main__":
    app.run()
