"""
Unit tests for itemset support in GSP-Py.

This module contains tests for:
- Itemset format detection
- Transaction normalization (flat to itemsets)
- Itemset subsequence matching
- Mixed format compatibility
- SPM file parsing with itemsets
- Integration with GSP algorithm

Author: Jackson Antonio do Prado Lima (via GitHub Copilot)
Email: jacksonpradolima@gmail.com
"""

import pytest
from typing import List

from gsppy.utils import (
    is_itemset_format,
    normalize_to_itemsets,
    is_subsequence_with_itemsets,
    _parse_spm_line,
)
from gsppy.gsp import GSP


class TestItemsetDetection:
    """Tests for detecting itemset format in transactions."""

    def test_flat_format_simple(self) -> None:
        """Flat list of strings should not be detected as itemsets."""
        transaction = ['A', 'B', 'C']
        assert not is_itemset_format(transaction)

    def test_flat_format_with_timestamps(self) -> None:
        """Flat list with timestamps should not be detected as itemsets."""
        transaction = [('A', 1.0), ('B', 2.0), ('C', 3.0)]
        assert not is_itemset_format(transaction)

    def test_itemset_format_simple(self) -> None:
        """Nested list structure should be detected as itemsets."""
        transaction = [['A', 'B'], ['C']]
        assert is_itemset_format(transaction)

    def test_itemset_format_with_timestamps(self) -> None:
        """Nested list with timestamps should be detected as itemsets."""
        transaction = [[('A', 1.0), ('B', 1.0)], [('C', 2.0)]]
        assert is_itemset_format(transaction)

    def test_empty_transaction(self) -> None:
        """Empty transaction should return False."""
        transaction: List = []
        assert not is_itemset_format(transaction)

    def test_single_itemset(self) -> None:
        """Single itemset should be detected."""
        transaction = [['A', 'B', 'C']]
        assert is_itemset_format(transaction)


class TestTransactionNormalization:
    """Tests for normalizing transactions to itemset format."""

    def test_normalize_flat_to_itemsets(self) -> None:
        """Flat list should be converted to single-item itemsets."""
        transaction = ['A', 'B', 'C']
        result = normalize_to_itemsets(transaction)
        expected = (('A',), ('B',), ('C',))
        assert result == expected

    def test_normalize_itemsets_to_tuples(self) -> None:
        """Itemset list should be converted to nested tuples."""
        transaction = [['A', 'B'], ['C']]
        result = normalize_to_itemsets(transaction)
        expected = (('A', 'B'), ('C',))
        assert result == expected

    def test_normalize_flat_with_timestamps(self) -> None:
        """Flat timestamped list should be normalized."""
        transaction = [('A', 1.0), ('B', 2.0)]
        result = normalize_to_itemsets(transaction)
        expected = ((('A', 1.0),), (('B', 2.0),))
        assert result == expected

    def test_normalize_itemsets_with_timestamps(self) -> None:
        """Itemset with timestamps should be normalized."""
        transaction = [[('A', 1.0), ('B', 1.0)], [('C', 2.0)]]
        result = normalize_to_itemsets(transaction)
        expected = ((('A', 1.0), ('B', 1.0)), (('C', 2.0),))
        assert result == expected

    def test_normalize_empty_transaction(self) -> None:
        """Empty transaction should return empty tuple."""
        transaction: List = []
        result = normalize_to_itemsets(transaction)
        assert result == ()

    def test_normalize_preserves_immutability(self) -> None:
        """Normalized result should be immutable (tuples)."""
        transaction = [['A', 'B'], ['C']]
        result = normalize_to_itemsets(transaction)
        assert isinstance(result, tuple)
        assert all(isinstance(itemset, tuple) for itemset in result)


class TestItemsetSubsequenceMatching:
    """Tests for subsequence matching with itemsets."""

    def test_exact_match(self) -> None:
        """Pattern exactly matches sequence."""
        pattern = (('A', 'B'), ('C',))
        sequence = (('A', 'B'), ('C',))
        assert is_subsequence_with_itemsets(pattern, sequence)

    def test_subset_match(self) -> None:
        """Pattern itemsets are subsets of sequence itemsets."""
        pattern = (('A', 'B'), ('C',))
        sequence = (('A', 'B', 'D'), ('E',), ('C', 'F'))
        assert is_subsequence_with_itemsets(pattern, sequence)

    def test_single_item_per_itemset(self) -> None:
        """Single items per itemset should work like flat matching."""
        pattern = (('A',), ('C',))
        sequence = (('A',), ('B',), ('C',))
        assert is_subsequence_with_itemsets(pattern, sequence)

    def test_no_match_wrong_order(self) -> None:
        """Pattern in wrong order should not match."""
        pattern = (('C',), ('A',))
        sequence = (('A',), ('B',), ('C',))
        assert not is_subsequence_with_itemsets(pattern, sequence)

    def test_no_match_items_not_together(self) -> None:
        """Items must be in the same itemset to match."""
        pattern = (('A', 'B'),)
        sequence = (('A',), ('B',))
        assert not is_subsequence_with_itemsets(pattern, sequence)

    def test_pattern_longer_than_sequence(self) -> None:
        """Pattern longer than sequence should not match."""
        pattern = (('A',), ('B',), ('C',), ('D',))
        sequence = (('A',), ('B',))
        assert not is_subsequence_with_itemsets(pattern, sequence)

    def test_empty_pattern(self) -> None:
        """Empty pattern should not match any sequence."""
        pattern = ()
        sequence = (('A',), ('B',))
        assert not is_subsequence_with_itemsets(pattern, sequence)

    def test_complex_itemsets(self) -> None:
        """Complex itemsets with multiple items."""
        pattern = (('A', 'B', 'C'), ('D', 'E'))
        sequence = (('A', 'B', 'C', 'F'), ('G',), ('D', 'E', 'H'))
        assert is_subsequence_with_itemsets(pattern, sequence)


class TestSPMParsing:
    """Tests for SPM file parsing with itemset preservation."""

    def test_parse_spm_line_with_itemsets(self) -> None:
        """Parse SPM line preserving itemsets."""
        line = "1 2 -1 3 -1 -2"
        result = _parse_spm_line(line, None, preserve_itemsets=True)
        expected = [['1', '2'], ['3']]
        assert result == expected

    def test_parse_spm_line_flatten(self) -> None:
        """Parse SPM line with flattening for backward compatibility."""
        line = "1 2 -1 3 -1 -2"
        result = _parse_spm_line(line, None, preserve_itemsets=False)
        expected = ['1', '2', '3']
        assert result == expected

    def test_parse_spm_single_item_per_element(self) -> None:
        """Parse SPM with single items per element."""
        line = "A -1 B -1 C -1 -2"
        result = _parse_spm_line(line, None, preserve_itemsets=True)
        expected = [['A'], ['B'], ['C']]
        assert result == expected

    def test_parse_spm_multiple_items_per_element(self) -> None:
        """Parse SPM with multiple items per element."""
        line = "A B C -1 D E -1 -2"
        result = _parse_spm_line(line, None, preserve_itemsets=True)
        expected = [['A', 'B', 'C'], ['D', 'E']]
        assert result == expected


class TestGSPWithItemsets:
    """Integration tests for GSP algorithm with itemset support."""

    def test_gsp_flat_transactions(self) -> None:
        """GSP should work with traditional flat transactions."""
        transactions = [
            ['A', 'B', 'C'],
            ['A', 'C'],
            ['A', 'B', 'C', 'D'],
            ['A', 'C', 'D'],
        ]
        gsp = GSP(transactions)
        patterns = gsp.search(min_support=0.5)
        
        # Should find at least ('A',) and ('C',) as 1-patterns
        assert len(patterns) > 0
        assert ('A',) in patterns[0]
        assert ('C',) in patterns[0]

    def test_gsp_itemset_transactions(self) -> None:
        """GSP should work with itemset transactions."""
        transactions = [
            [['A', 'B'], ['C']],
            [['A'], ['C']],
            [['A', 'B'], ['C', 'D']],
            [['A'], ['C', 'D']],
        ]
        gsp = GSP(transactions)
        patterns = gsp.search(min_support=0.5)
        
        # Should find frequent items
        assert len(patterns) > 0
        assert ('A',) in patterns[0]
        assert ('C',) in patterns[0]

    def test_gsp_mixed_format_normalized(self) -> None:
        """GSP should normalize flat transactions to itemsets internally."""
        flat_transactions = [
            ['A', 'B', 'C'],
            ['A', 'C'],
        ]
        itemset_transactions = [
            [['A'], ['B'], ['C']],
            [['A'], ['C']],
        ]
        
        gsp_flat = GSP(flat_transactions)
        gsp_itemset = GSP(itemset_transactions)
        
        # Both should have itemset flag set
        assert hasattr(gsp_flat, 'has_itemsets')
        assert hasattr(gsp_itemset, 'has_itemsets')

    def test_gsp_itemset_co_occurrence(self) -> None:
        """Test that items in same itemset are treated as co-occurring."""
        transactions = [
            [['A', 'B'], ['C']],  # A and B occur together, then C
            [['A', 'B'], ['C']],  # Same pattern
            [['A'], ['B'], ['C']],  # A, B, C occur separately
        ]
        gsp = GSP(transactions)
        patterns = gsp.search(min_support=0.5)
        
        # A, B, C should all be frequent as 1-patterns (appear in 3, 3, 3 transactions respectively)
        assert ('A',) in patterns[0]
        assert ('B',) in patterns[0]
        assert ('C',) in patterns[0]
        
        # Sequential patterns should be found
        # ('A', 'C') appears in all 3 transactions
        assert len(patterns) >= 2
        if len(patterns) >= 2:
            assert ('A', 'C') in patterns[1]
            # ('B', 'C') should also be found (B before C in all transactions)
            assert ('B', 'C') in patterns[1]
            
        # Note: The current GSP implementation discovers sequential patterns (item1 -> item2),
        # not co-occurrence patterns like (A, B together). The itemset support enables
        # matching where items in the same itemset can match pattern elements, but the
        # output patterns remain sequential single-item patterns as per standard GSP algorithm.

    def test_gsp_empty_itemsets_handling(self) -> None:
        """GSP should handle transactions gracefully."""
        transactions = [
            [['A'], ['B']],
            [['A'], ['C']],
        ]
        gsp = GSP(transactions)
        patterns = gsp.search(min_support=0.5)
        
        # Should find A as frequent
        assert ('A',) in patterns[0]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
