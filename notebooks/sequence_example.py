"""
Sequence Abstraction Example for GSP-Py

This interactive notebook demonstrates how to use the Sequence class in GSP-Py
for working with sequential patterns in a more structured way.
"""

import marimo

__generated_with = "0.19.9"
app = marimo.App(width="medium")


@app.cell(hide_code=False)
def _():
    """Import required libraries"""
    from gsppy import GSP, Sequence, sequences_to_dict
    import marimo as mo
    return GSP, Sequence, sequences_to_dict, mo


@app.cell(hide_code=False)
def _(mo):
    """Introduction"""
    mo.md("""
    # GSP-Py: Sequence Abstraction Example
    
    This notebook demonstrates how to use the **Sequence abstraction** in GSP-Py for 
    working with sequential patterns. The Sequence class provides a rich API for 
    pattern manipulation, filtering, and analysis.
    
    ## Sample Data
    
    We'll use a simple transactional dataset representing customer purchases:
    """)
    return


@app.cell(hide_code=False)
def _(GSP, mo):
    """Define sample data and create GSP instance"""
    transactions = [
        ["Bread", "Milk"],
        ["Bread", "Diaper", "Beer", "Eggs"],
        ["Milk", "Diaper", "Beer", "Coke"],
        ["Bread", "Milk", "Diaper", "Beer"],
        ["Bread", "Milk", "Diaper", "Coke"],
    ]
    
    mo.md(f"""
    **Transactions:**
    ```python
    {transactions}
    ```
    
    Total transactions: {len(transactions)}
    """)
    
    # Initialize GSP
    gsp = GSP(transactions)
    
    return gsp, transactions


@app.cell(hide_code=False)
def _(mo):
    """Example 1 Header"""
    mo.md("""
    ## Example 1: Traditional Dict-based Output
    
    This is the backward-compatible way to get results as dictionaries.
    """)
    return


@app.cell(hide_code=False)
def _(gsp, mo):
    """Example 1: Traditional output"""
    result_dict = gsp.search(min_support=0.3, return_sequences=False)
    
    _output_lines_1 = [f"Found {len(result_dict)} levels of patterns\n"]
    
    for _level1, _patterns in enumerate(result_dict, start=1):
        _output_lines_1.append(f"\n**Level {_level1}** ({len(_patterns)} patterns):")
        for _pattern, _support in sorted(_patterns.items(), key=lambda x: x[1], reverse=True):
            _output_lines_1.append(f"  - Pattern: `{str(_pattern):30}` Support: {_support}")
    
    mo.md("\n".join(_output_lines_1))
    return result_dict,


@app.cell(hide_code=False)
def _(mo):
    """Example 2 Header"""
    mo.md("""
    ## Example 2: Using Sequence Objects
    
    The new Sequence abstraction provides a richer interface for working with patterns.
    """)
    return


@app.cell(hide_code=False)
def _(gsp, mo):
    """Example 2: Sequence objects"""
    result_seq = gsp.search(min_support=0.3, return_sequences=True)
    
    _output_lines_2 = [f"Found {len(result_seq)} levels of patterns\n"]
    
    for _level2, _sequences in enumerate(result_seq, start=1):
        _output_lines_2.append(f"\n**Level {_level2}** ({len(_sequences)} patterns):")
        _sorted_sequences = sorted(_sequences, key=lambda s: s.support, reverse=True)
        for _seq2 in _sorted_sequences:
            _output_lines_2.append(f"  - {_seq2}")
    
    mo.md("\n".join(_output_lines_2))
    return result_seq,


@app.cell(hide_code=False)
def _(mo):
    """Example 3 Header"""
    mo.md("""
    ## Example 3: Accessing Sequence Properties
    
    Sequence objects expose many useful properties for analysis.
    """)
    return


@app.cell(hide_code=False)
def _(result_seq, mo):
    """Example 3: Sequence properties"""
    _result3 = None
    if len(result_seq) > 1 and result_seq[1]:
        level_2_sequences = result_seq[1]
        top_sequence = max(level_2_sequences, key=lambda s: s.support)
        
        _result3 = mo.md(f"""
        **Top 2-sequence pattern:**
        
        - Items: `{top_sequence.items}`
        - Support: `{top_sequence.support}`
        - Length: `{top_sequence.length}`
        - First item: `{top_sequence.first_item}`
        - Last item: `{top_sequence.last_item}`
        - As tuple: `{top_sequence.as_tuple()}`
        """)
    else:
        _result3 = mo.md("No 2-sequence patterns found.")
    _result3
    return level_2_sequences, top_sequence


@app.cell(hide_code=False)
def _(mo):
    """Example 4 Header"""
    mo.md("""
    ## Example 4: Filtering and Analyzing Sequences
    
    You can filter patterns by content or support values.
    """)
    return


@app.cell(hide_code=False)
def _(result_seq, mo):
    """Example 4: Filtering sequences"""
    # Find all patterns containing "Milk"
    milk_patterns = []
    for _level4 in result_seq:
        for _seq4 in _level4:
            if "Milk" in _seq4:
                milk_patterns.append(_seq4)
    
    _output_lines_4 = [f"Found {len(milk_patterns)} patterns containing 'Milk':\n"]
    for _seq4a in milk_patterns:
        _output_lines_4.append(f"  - {_seq4a}")
    
    # Find patterns with high support (>= 3)
    high_support_patterns = []
    for _level4b in result_seq:
        for _seq4b in _level4b:
            if _seq4b.support >= 3:
                high_support_patterns.append(_seq4b)
    
    _output_lines_4.append(f"\n\nFound {len(high_support_patterns)} patterns with support >= 3:\n")
    for _seq4c in sorted(high_support_patterns, key=lambda s: s.support, reverse=True):
        _output_lines_4.append(f"  - {_seq4c}")
    
    mo.md("\n".join(_output_lines_4))
    return high_support_patterns, milk_patterns


@app.cell(hide_code=False)
def _(mo):
    """Example 5 Header"""
    mo.md("""
    ## Example 5: Creating Custom Sequence Objects
    
    You can create and manipulate Sequence objects programmatically.
    """)
    return


@app.cell(hide_code=False)
def _(Sequence, mo):
    """Example 7: Custom sequences"""
    # Create a new Sequence from items
    custom_seq = Sequence.from_tuple(("Custom", "Pattern"), support=10)
    
    # Extend a sequence with a new item
    extended_seq = custom_seq.extend("Extended")
    
    # Add metadata to a sequence
    seq_with_metadata = custom_seq.with_metadata(
        confidence=0.85,
        lift=1.5,
        note="Important pattern"
    )
    
    metadata_str = str(seq_with_metadata.metadata) if seq_with_metadata.metadata else "None"
    
    mo.md(f"""
    **Created custom sequence:** `{custom_seq}`
    
    **Extended sequence:** `{extended_seq}`
    
    **Sequence with metadata:** `{seq_with_metadata}`
    - Metadata: `{metadata_str}`
    """)
    return custom_seq, extended_seq, seq_with_metadata


@app.cell(hide_code=False)
def _(mo):
    """Example 6 Header"""
    mo.md("""
    ## Example 6: Pattern Analysis Statistics
    
    Compute aggregate statistics across all discovered patterns.
    """)
    return


@app.cell(hide_code=False)
def _(result_seq, mo):
    """Example 8: Pattern statistics"""
    all_sequences = [_seq8 for _level8 in result_seq for _seq8 in _level8]
    
    _result8 = None
    if all_sequences:
        total_patterns = len(all_sequences)
        avg_support = sum(_s.support for _s in all_sequences) / total_patterns
        max_support = max(_s.support for _s in all_sequences)
        min_support = min(_s.support for _s in all_sequences)
        avg_length = sum(_s.length for _s in all_sequences) / total_patterns
        
        # Group by length
        patterns_by_length = {}
        for _seq8b in all_sequences:
            _length = _seq8b.length
            if _length not in patterns_by_length:
                patterns_by_length[_length] = []
            patterns_by_length[_length].append(_seq8b)
        
        length_stats = "\n".join([
            f"  - Length {_len}: {len(patterns_by_length[_len])} patterns"
            for _len in sorted(patterns_by_length.keys())
        ])
        
        _result8 = mo.md(f"""
        **Overall Statistics:**
        
        - Total patterns found: `{total_patterns}`
        - Average support: `{avg_support:.2f}`
        - Max support: `{max_support}`
        - Min support: `{min_support}`
        - Average pattern length: `{avg_length:.2f}`
        
        **Patterns grouped by length:**
        
        {length_stats}
        """)
    else:
        _result8 = mo.md("No patterns found.")
    _result8
    return all_sequences, avg_length, avg_support, max_support, min_support, patterns_by_length, total_patterns


@app.cell(hide_code=False)
def _(mo):
    """Conclusion"""
    mo.md("""
    ## Conclusion
    
    The Sequence abstraction in GSP-Py provides a powerful and intuitive way to work with 
    sequential patterns. Key benefits include:
    
    - **Rich API**: Access properties like `items`, `support`, `length`, etc.
    - **Filtering**: Use Python's `in` operator to check for item membership
    - **Extensibility**: Create custom sequences and add metadata
    - **Statistics**: Easily compute aggregate statistics
    - **Compatibility**: Convert between Sequence objects and traditional dict format
    
    For more examples, check out the other notebooks in this documentation!
    """)
    return


if __name__ == "__main__":
    app.run()
