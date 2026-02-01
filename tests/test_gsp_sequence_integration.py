"""
Integration tests for GSP algorithm with Sequence abstraction.

This module tests the integration of the Sequence class with the GSP algorithm,
ensuring that:
- The return_sequences parameter works correctly
- Sequence objects contain correct pattern data
- Backward compatibility is maintained
- Edge cases are handled properly

Author: Jackson Antonio do Prado Lima
Email: jacksonpradolima@gmail.com
"""

import pytest
from typing import List

from gsppy import GSP, Sequence


@pytest.fixture
def supermarket_transactions() -> List[List[str]]:
    """
    Fixture to provide a dataset representing supermarket transactions.
    
    Returns:
        list: A list of transactions, where each transaction is a list of items.
    """
    return [
        ["Bread", "Milk"],
        ["Bread", "Diaper", "Beer", "Eggs"],
        ["Milk", "Diaper", "Beer", "Coke"],
        ["Bread", "Milk", "Diaper", "Beer"],
        ["Bread", "Milk", "Diaper", "Coke"],
    ]


class TestGSPSequenceIntegration:
    """Test GSP algorithm with Sequence objects."""

    def test_gsp_returns_sequences_when_requested(self, supermarket_transactions: List[List[str]]) -> None:
        """Test that GSP returns Sequence objects when return_sequences=True."""
        gsp = GSP(supermarket_transactions)
        result = gsp.search(min_support=0.3, return_sequences=True)
        
        # Check that we get a list of lists of Sequence objects
        assert isinstance(result, list)
        assert len(result) > 0
        
        # Check first level patterns
        first_level = result[0]
        assert isinstance(first_level, list)
        assert len(first_level) > 0
        assert all(isinstance(seq, Sequence) for seq in first_level)
        
    def test_gsp_default_returns_dicts(self, supermarket_transactions: List[List[str]]) -> None:
        """Test that GSP returns dict format by default (backward compatibility)."""
        gsp = GSP(supermarket_transactions)
        result = gsp.search(min_support=0.3)
        
        # Check that we get a list of dicts (traditional format)
        assert isinstance(result, list)
        assert len(result) > 0
        
        # Check first level patterns
        first_level = result[0]
        assert isinstance(first_level, dict)
        # Keys should be tuples
        for key in first_level.keys():
            assert isinstance(key, tuple)
            
    def test_sequence_results_match_dict_results(self, supermarket_transactions: List[List[str]]) -> None:
        """Test that Sequence results match traditional dict results."""
        gsp = GSP(supermarket_transactions)
        
        # Get results in both formats
        dict_result = gsp.search(min_support=0.3, return_sequences=False)
        seq_result = gsp.search(min_support=0.3, return_sequences=True)
        
        # Should have same number of levels
        assert len(dict_result) == len(seq_result)
        
        # Check each level
        for level_idx, (dict_level, seq_level) in enumerate(zip(dict_result, seq_result)):
            # Convert sequences back to dict format for comparison
            seq_as_dict = {seq.items: seq.support for seq in seq_level}
            assert dict_level == seq_as_dict, f"Mismatch at level {level_idx}"
            
    def test_sequence_objects_contain_correct_data(self, supermarket_transactions: List[List[str]]) -> None:
        """Test that Sequence objects contain correct pattern and support data."""
        gsp = GSP(supermarket_transactions)
        result = gsp.search(min_support=0.3, return_sequences=True)
        
        # Check first level (1-sequences)
        level_1 = result[0]
        
        # Find the "Bread" pattern
        bread_seq = next((seq for seq in level_1 if seq.items == ("Bread",)), None)
        assert bread_seq is not None, "Bread pattern not found"
        assert bread_seq.support == 4, "Bread should have support 4"
        assert bread_seq.length == 1, "Bread should be length 1"
        
        # Check second level (2-sequences) if it exists
        if len(result) > 1:
            level_2 = result[1]
            # Find a 2-sequence pattern
            bread_milk = next((seq for seq in level_2 if seq.items == ("Bread", "Milk")), None)
            if bread_milk:
                assert bread_milk.support == 3, "Bread->Milk should have support 3"
                assert bread_milk.length == 2, "Bread->Milk should be length 2"
                
    def test_sequence_properties_accessible(self, supermarket_transactions: List[List[str]]) -> None:
        """Test that Sequence properties are accessible and correct."""
        gsp = GSP(supermarket_transactions)
        result = gsp.search(min_support=0.3, return_sequences=True)
        
        # Get a sequence from first level
        seq = result[0][0]
        
        # Test various properties
        assert hasattr(seq, 'items')
        assert hasattr(seq, 'support')
        assert hasattr(seq, 'length')
        assert hasattr(seq, 'as_tuple')
        
        # Test that properties work
        assert isinstance(seq.items, tuple)
        assert isinstance(seq.support, int)
        assert seq.length == len(seq.items)
        assert seq.as_tuple() == seq.items
        
    def test_empty_result_with_sequences(self, supermarket_transactions: List[List[str]]) -> None:
        """Test that empty results work correctly with return_sequences=True."""
        gsp = GSP(supermarket_transactions)
        # Use very high min_support to get no patterns
        result = gsp.search(min_support=0.9, return_sequences=True)
        
        assert isinstance(result, list)
        assert len(result) == 0
        
    def test_sequences_can_be_iterated(self, supermarket_transactions: List[List[str]]) -> None:
        """Test that Sequence objects can be iterated over."""
        gsp = GSP(supermarket_transactions)
        result = gsp.search(min_support=0.3, return_sequences=True)
        
        if len(result) > 1:
            # Get a 2-sequence
            level_2 = result[1]
            if level_2:
                seq = level_2[0]
                # Should be able to iterate
                items = list(seq)
                assert len(items) == seq.length
                assert items == list(seq.items)
                
    def test_sequences_with_low_min_support(self, supermarket_transactions: List[List[str]]) -> None:
        """Test Sequences with low minimum support."""
        gsp = GSP(supermarket_transactions)
        result = gsp.search(min_support=0.2, return_sequences=True)
        
        # Should have multiple levels
        assert len(result) >= 1
        
        # All items should be Sequence objects
        for level in result:
            assert all(isinstance(seq, Sequence) for seq in level)
            # All sequences should have positive support
            assert all(seq.support > 0 for seq in level)
            
    def test_sequences_multiple_searches(self, supermarket_transactions: List[List[str]]) -> None:
        """Test that multiple searches with return_sequences work correctly."""
        gsp = GSP(supermarket_transactions)
        
        # Run multiple searches
        result1 = gsp.search(min_support=0.3, return_sequences=True)
        result3 = gsp.search(min_support=0.3, return_sequences=True)
        
        # result1 and result3 should be equivalent (same parameters)
        assert len(result1) == len(result3)
        for level_idx in range(len(result1)):
            items_1 = {seq.items: seq.support for seq in result1[level_idx]}
            items_3 = {seq.items: seq.support for seq in result3[level_idx]}
            assert items_1 == items_3
        
    def test_sequence_indexing_and_slicing(self, supermarket_transactions: List[List[str]]) -> None:
        """Test that Sequence objects support indexing and slicing."""
        gsp = GSP(supermarket_transactions)
        result = gsp.search(min_support=0.3, return_sequences=True)
        
        if len(result) > 1:
            level_2 = result[1]
            if level_2:
                seq = level_2[0]
                if seq.length >= 2:
                    # Test indexing
                    assert seq[0] == seq.items[0]
                    assert seq[1] == seq.items[1]
                    assert seq[-1] == seq.items[-1]
                    
                    # Test slicing
                    assert seq[0:2] == seq.items[0:2]


class TestSequenceWithVerboseMode:
    """Test Sequence integration with verbose mode."""

    def test_sequences_with_verbose_true(self, supermarket_transactions: List[List[str]], caplog: pytest.LogCaptureFixture) -> None:
        """Test that verbose mode works with return_sequences=True."""
        import logging
        with caplog.at_level(logging.INFO, logger='gsppy.gsp'):
            gsp = GSP(supermarket_transactions, verbose=True)
            result = gsp.search(min_support=0.3, return_sequences=True)
            
            # Should get Sequence objects
            assert len(result) > 0
            assert all(isinstance(seq, Sequence) for seq in result[0])
            
            # Should have verbose logs
            info_messages = [record.message for record in caplog.records if record.levelno == logging.INFO]
            assert len(info_messages) > 0
            
    def test_sequences_with_verbose_override(self, supermarket_transactions: List[List[str]], caplog: pytest.LogCaptureFixture) -> None:
        """Test verbose override with return_sequences."""
        import logging
        caplog.clear()
        with caplog.at_level(logging.INFO, logger='gsppy.gsp'):
            gsp = GSP(supermarket_transactions, verbose=False)
            result = gsp.search(min_support=0.3, verbose=True, return_sequences=True)
            
            # Should get Sequence objects
            assert len(result) > 0
            assert all(isinstance(seq, Sequence) for seq in result[0])
            
            # Should have verbose logs despite verbose=False in init
            info_messages = [record.message for record in caplog.records if record.levelno == logging.INFO]
            assert len(info_messages) > 0


class TestSequenceEdgeCases:
    """Test edge cases with Sequence integration."""

    def test_single_item_sequences(self) -> None:
        """Test patterns with only 1-item sequences."""
        transactions = [["A", "B"], ["A"], ["B", "A"]]
        gsp = GSP(transactions)
        result = gsp.search(min_support=0.5, return_sequences=True)
        
        # Should have 1-sequences and possibly 2-sequences
        assert len(result) >= 1
        assert len(result[0]) >= 1  # At least one 1-sequence pattern
        
        # Find sequence "A" - appears in all 3 transactions
        seq_a = next((s for s in result[0] if s.items == ("A",)), None)
        assert seq_a is not None
        assert seq_a.support == 3
        assert seq_a.length == 1
        
        # Find sequence "B" - appears in 2 transactions
        seq_b = next((s for s in result[0] if s.items == ("B",)), None)
        assert seq_b is not None
        assert seq_b.support == 2  # Only in transactions 0 and 2
        assert seq_b.length == 1
        
    def test_sequences_with_many_levels(self) -> None:
        """Test patterns with multiple k-sequence levels."""
        transactions = [
            ["A", "B", "C", "D"],
            ["A", "B", "C", "D"],
            ["A", "B", "C", "D"],
        ]
        gsp = GSP(transactions)
        result = gsp.search(min_support=0.5, return_sequences=True)
        
        # Should have multiple levels
        assert len(result) >= 2
        
        # Check that pattern lengths increase with levels
        for level_idx, level in enumerate(result):
            expected_length = level_idx + 1
            for seq in level:
                assert seq.length == expected_length
                
    def test_sequences_all_equal_support(self) -> None:
        """Test when all patterns have the same support."""
        transactions = [
            ["A", "B"],
            ["A", "B"],
            ["A", "B"],
        ]
        gsp = GSP(transactions)
        result = gsp.search(min_support=0.5, return_sequences=True)
        
        # All patterns should have support = 3
        for level in result:
            for seq in level:
                assert seq.support == 3


class TestSequenceBackwardCompatibility:
    """Test backward compatibility of Sequence integration."""

    def test_old_code_still_works(self, supermarket_transactions: List[List[str]]) -> None:
        """Test that existing code without return_sequences still works."""
        gsp = GSP(supermarket_transactions)
        # Old style call without return_sequences parameter
        result = gsp.search(min_support=0.3)
        
        # Should get dict format
        assert isinstance(result, list)
        assert isinstance(result[0], dict)
        
        # Expected patterns should still be there
        expected_level_1 = {("Bread",), ("Milk",), ("Diaper",), ("Beer",)}
        result_level_1 = set(result[0].keys())
        assert expected_level_1.issubset(result_level_1)
        
    def test_mixing_return_types_across_searches(self, supermarket_transactions: List[List[str]]) -> None:
        """Test that different return types can be used in different searches."""
        gsp = GSP(supermarket_transactions)
        
        # First search with sequences
        result_seq = gsp.search(min_support=0.3, return_sequences=True)
        assert all(isinstance(seq, Sequence) for seq in result_seq[0])
        
        # Second search with dicts
        result_dict = gsp.search(min_support=0.3, return_sequences=False)
        assert isinstance(result_dict[0], dict)
        
        # Third search with sequences again
        result_seq2 = gsp.search(min_support=0.3, return_sequences=True)
        assert all(isinstance(seq, Sequence) for seq in result_seq2[0])
        
    def test_as_tuple_provides_backward_compatibility(self, supermarket_transactions: List[List[str]]) -> None:
        """Test that Sequence.as_tuple() provides backward compatibility."""
        gsp = GSP(supermarket_transactions)
        result = gsp.search(min_support=0.3, return_sequences=True)
        
        # Convert back to dict format using as_tuple()
        for level in result:
            # Should be able to create dict from sequences
            pattern_dict = {seq.as_tuple(): seq.support for seq in level}
            assert isinstance(pattern_dict, dict)
            # Keys should be tuples
            for key in pattern_dict.keys():
                assert isinstance(key, tuple)
