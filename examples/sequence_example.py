"""
Example: Using the Sequence abstraction in GSP-Py.

This example demonstrates how to use the Sequence class to work with
sequential patterns in a more structured and maintainable way. The Sequence
class encapsulates pattern items, support counts, and provides a rich API
for pattern manipulation.

Author: Jackson Antonio do Prado Lima
Email: jacksonpradolima@gmail.com
"""

from gsppy import GSP, Sequence


def main():
    """Demonstrate Sequence abstraction usage."""
    
    # Define sample transactional data
    transactions = [
        ["Bread", "Milk"],
        ["Bread", "Diaper", "Beer", "Eggs"],
        ["Milk", "Diaper", "Beer", "Coke"],
        ["Bread", "Milk", "Diaper", "Beer"],
        ["Bread", "Milk", "Diaper", "Coke"],
    ]
    
    print("=" * 70)
    print("GSP-Py: Sequence Abstraction Example")
    print("=" * 70)
    print()
    
    # Initialize GSP
    gsp = GSP(transactions)
    
    # ========================================================================
    # Example 1: Traditional Dict-based Output (Backward Compatible)
    # ========================================================================
    print("Example 1: Traditional Dict-based Output")
    print("-" * 70)
    
    result_dict = gsp.search(min_support=0.3, return_sequences=False)
    
    print(f"Found {len(result_dict)} levels of patterns\n")
    
    for level, patterns in enumerate(result_dict, start=1):
        print(f"Level {level} ({len(patterns)} patterns):")
        for pattern, support in sorted(patterns.items(), key=lambda x: x[1], reverse=True):
            print(f"  Pattern: {str(pattern):30} Support: {support}")
        print()
    
    # ========================================================================
    # Example 2: Sequence Objects (New Feature)
    # ========================================================================
    print("\nExample 2: Using Sequence Objects")
    print("-" * 70)
    
    result_seq = gsp.search(min_support=0.3, return_sequences=True)
    
    print(f"Found {len(result_seq)} levels of patterns\n")
    
    for level, sequences in enumerate(result_seq, start=1):
        print(f"Level {level} ({len(sequences)} patterns):")
        # Sort by support (descending)
        sorted_sequences = sorted(sequences, key=lambda s: s.support, reverse=True)
        for seq in sorted_sequences:
            print(f"  {seq}")  # Uses __str__ method
        print()
    
    # ========================================================================
    # Example 3: Working with Sequence Properties
    # ========================================================================
    print("\nExample 3: Accessing Sequence Properties")
    print("-" * 70)
    
    # Get the most frequent 2-sequences if available
    if len(result_seq) > 1 and result_seq[1]:
        level_2_sequences = result_seq[1]
        top_sequence = max(level_2_sequences, key=lambda s: s.support)
        
        print(f"Top 2-sequence pattern:")
        print(f"  Items:        {top_sequence.items}")
        print(f"  Support:      {top_sequence.support}")
        print(f"  Length:       {top_sequence.length}")
        print(f"  First item:   {top_sequence.first_item}")
        print(f"  Last item:    {top_sequence.last_item}")
        print(f"  As tuple:     {top_sequence.as_tuple()}")
        print()
    
    # ========================================================================
    # Example 4: Filtering and Analyzing Sequences
    # ========================================================================
    print("\nExample 4: Filtering and Analyzing Sequences")
    print("-" * 70)
    
    # Find all patterns containing "Milk"
    milk_patterns = []
    for level in result_seq:
        for seq in level:
            if "Milk" in seq:  # Uses __contains__ method
                milk_patterns.append(seq)
    
    print(f"Found {len(milk_patterns)} patterns containing 'Milk':")
    for seq in milk_patterns:
        print(f"  {seq}")
    print()
    
    # Find patterns with high support (>= 3)
    high_support_patterns = []
    for level in result_seq:
        for seq in level:
            if seq.support >= 3:
                high_support_patterns.append(seq)
    
    print(f"\nFound {len(high_support_patterns)} patterns with support >= 3:")
    for seq in sorted(high_support_patterns, key=lambda s: s.support, reverse=True):
        print(f"  {seq}")
    print()
    
    # ========================================================================
    # Example 5: Converting Between Formats
    # ========================================================================
    print("\nExample 5: Converting Between Formats")
    print("-" * 70)
    
    # Convert Sequence objects back to dict format for compatibility
    from gsppy import sequences_to_dict
    
    if result_seq:
        level_1_dict = sequences_to_dict(result_seq[0])
        print("Level 1 patterns as dictionary:")
        for pattern, support in sorted(level_1_dict.items(), key=lambda x: x[1], reverse=True):
            print(f"  {pattern}: {support}")
    print()
    
    # ========================================================================
    # Example 6: Iterating Over Sequence Items
    # ========================================================================
    print("\nExample 6: Iterating Over Sequence Items")
    print("-" * 70)
    
    if len(result_seq) > 1 and result_seq[1]:
        sample_seq = result_seq[1][0]
        print(f"Iterating over items in pattern {sample_seq.items}:")
        for idx, item in enumerate(sample_seq):
            print(f"  Position {idx}: {item}")
        print()
        
        # Accessing by index
        print("Accessing items by index:")
        print(f"  First item:  {sample_seq[0]}")
        print(f"  Last item:   {sample_seq[-1]}")
        if sample_seq.length >= 2:
            print(f"  Slice [0:2]: {sample_seq[0:2]}")
        print()
    
    # ========================================================================
    # Example 7: Creating Custom Sequence Objects
    # ========================================================================
    print("\nExample 7: Creating Custom Sequence Objects")
    print("-" * 70)
    
    # Create a new Sequence from items
    custom_seq = Sequence.from_tuple(("Custom", "Pattern"), support=10)
    print(f"Created custom sequence: {custom_seq}")
    
    # Extend a sequence with a new item
    extended_seq = custom_seq.extend("Extended")
    print(f"Extended sequence: {extended_seq}")
    
    # Add metadata to a sequence
    seq_with_metadata = custom_seq.with_metadata(
        confidence=0.85,
        lift=1.5,
        note="Important pattern"
    )
    print(f"Sequence with metadata: {seq_with_metadata}")
    if seq_with_metadata.metadata:
        print(f"  Metadata: {seq_with_metadata.metadata}")
    print()
    
    # ========================================================================
    # Example 8: Using Sequences in Data Analysis
    # ========================================================================
    print("\nExample 8: Pattern Analysis Statistics")
    print("-" * 70)
    
    all_sequences = [seq for level in result_seq for seq in level]
    
    if all_sequences:
        total_patterns = len(all_sequences)
        avg_support = sum(seq.support for seq in all_sequences) / total_patterns
        max_support = max(seq.support for seq in all_sequences)
        min_support = min(seq.support for seq in all_sequences)
        avg_length = sum(seq.length for seq in all_sequences) / total_patterns
        
        print(f"Total patterns found:    {total_patterns}")
        print(f"Average support:         {avg_support:.2f}")
        print(f"Max support:             {max_support}")
        print(f"Min support:             {min_support}")
        print(f"Average pattern length:  {avg_length:.2f}")
        print()
        
        # Group by length
        patterns_by_length = {}
        for seq in all_sequences:
            length = seq.length
            if length not in patterns_by_length:
                patterns_by_length[length] = []
            patterns_by_length[length].append(seq)
        
        print("Patterns grouped by length:")
        for length in sorted(patterns_by_length.keys()):
            count = len(patterns_by_length[length])
            print(f"  Length {length}: {count} patterns")
    
    print()
    print("=" * 70)
    print("Example completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
