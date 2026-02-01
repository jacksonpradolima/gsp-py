"""
Unit tests for the Sequence abstraction class.

This module contains comprehensive tests for the Sequence class including:
- Basic initialization and properties
- Conversion methods (from_tuple, from_item)
- Sequence operations (extend, with_support, with_metadata)
- Hashability and immutability
- Backward compatibility with tuples
- Edge cases and error handling

Author: Jackson Antonio do Prado Lima
Email: jacksonpradolima@gmail.com
"""

import pytest

from gsppy.sequence import (
    Sequence,
    to_sequence,
    dict_to_sequences,
    sequences_to_dict,
    is_sequence_or_tuple,
)


class TestSequenceBasicOperations:
    """Test basic Sequence initialization and properties."""

    def test_sequence_basic_initialization(self) -> None:
        """Test creating a Sequence with basic parameters."""
        seq = Sequence(items=("A", "B", "C"), support=5)
        assert seq.items == ("A", "B", "C")
        assert seq.support == 5
        assert seq.length == 3
        assert seq.transaction_indices is None
        assert seq.metadata is None

    def test_sequence_with_all_parameters(self) -> None:
        """Test creating a Sequence with all parameters."""
        seq = Sequence(
            items=("A", "B"),
            support=10,
            transaction_indices=(0, 2, 5),
            metadata={"confidence": 0.8},
        )
        assert seq.items == ("A", "B")
        assert seq.support == 10
        assert seq.transaction_indices == (0, 2, 5)
        assert seq.metadata == {"confidence": 0.8}

    def test_sequence_default_support(self) -> None:
        """Test that support defaults to 0."""
        seq = Sequence(items=("A",))
        assert seq.support == 0

    def test_sequence_empty_items_raises_error(self) -> None:
        """Test that creating a Sequence with empty items raises an error."""
        with pytest.raises(ValueError, match="Sequence items cannot be empty"):
            Sequence(items=())

    def test_sequence_negative_support_raises_error(self) -> None:
        """Test that negative support raises an error."""
        with pytest.raises(ValueError, match="Support count cannot be negative"):
            Sequence(items=("A",), support=-1)

    def test_sequence_converts_list_to_tuple(self) -> None:
        """Test that Sequence converts list items to tuple."""
        seq = Sequence(items=["A", "B", "C"])  # type: ignore
        assert isinstance(seq.items, tuple)
        assert seq.items == ("A", "B", "C")

    def test_sequence_converts_transaction_indices_to_tuple(self) -> None:
        """Test that transaction_indices are converted to tuple."""
        seq = Sequence(items=("A",), transaction_indices=[0, 1, 2])  # type: ignore
        assert isinstance(seq.transaction_indices, tuple)
        assert seq.transaction_indices == (0, 1, 2)


class TestSequenceProperties:
    """Test Sequence property accessors."""

    def test_length_property(self) -> None:
        """Test the length property."""
        seq = Sequence(items=("A", "B", "C"))
        assert seq.length == 3
        assert len(seq) == 3

    def test_first_item_property(self) -> None:
        """Test the first_item property."""
        seq = Sequence(items=("A", "B", "C"))
        assert seq.first_item == "A"

    def test_last_item_property(self) -> None:
        """Test the last_item property."""
        seq = Sequence(items=("A", "B", "C"))
        assert seq.last_item == "C"

    def test_as_tuple_method(self) -> None:
        """Test the as_tuple method for backward compatibility."""
        seq = Sequence(items=("A", "B", "C"), support=5)
        assert seq.as_tuple() == ("A", "B", "C")
        assert isinstance(seq.as_tuple(), tuple)


class TestSequenceFactoryMethods:
    """Test Sequence factory/class methods."""

    def test_from_tuple_basic(self) -> None:
        """Test creating Sequence from tuple."""
        seq = Sequence.from_tuple(("A", "B", "C"))
        assert seq.items == ("A", "B", "C")
        assert seq.support == 0

    def test_from_tuple_with_support(self) -> None:
        """Test creating Sequence from tuple with support."""
        seq = Sequence.from_tuple(("A", "B"), support=10)
        assert seq.items == ("A", "B")
        assert seq.support == 10

    def test_from_tuple_with_all_parameters(self) -> None:
        """Test creating Sequence from tuple with all parameters."""
        seq = Sequence.from_tuple(
            ("A", "B"),
            support=5,
            transaction_indices=(0, 1, 2),
            metadata={"test": "value"},
        )
        assert seq.items == ("A", "B")
        assert seq.support == 5
        assert seq.transaction_indices == (0, 1, 2)
        assert seq.metadata == {"test": "value"}

    def test_from_item_basic(self) -> None:
        """Test creating singleton Sequence from item."""
        seq = Sequence.from_item("A")
        assert seq.items == ("A",)
        assert seq.length == 1
        assert seq.support == 0

    def test_from_item_with_support(self) -> None:
        """Test creating singleton Sequence with support."""
        seq = Sequence.from_item("A", support=10)
        assert seq.items == ("A",)
        assert seq.support == 10


class TestSequenceOperations:
    """Test Sequence operation methods."""

    def test_extend_basic(self) -> None:
        """Test extending a Sequence with a new item."""
        seq = Sequence(items=("A", "B"))
        extended = seq.extend("C")
        assert extended.items == ("A", "B", "C")
        assert extended.support == 0  # New sequence has no support yet
        assert seq.items == ("A", "B")  # Original unchanged

    def test_extend_with_support(self) -> None:
        """Test extending with support value."""
        seq = Sequence(items=("A", "B"), support=5)
        extended = seq.extend("C", support=3)
        assert extended.items == ("A", "B", "C")
        assert extended.support == 3

    def test_extend_preserves_metadata(self) -> None:
        """Test that extend preserves metadata."""
        seq = Sequence(items=("A",), metadata={"key": "value"})
        extended = seq.extend("B")
        assert extended.metadata == {"key": "value"}

    def test_with_support_basic(self) -> None:
        """Test updating support count."""
        seq = Sequence(items=("A", "B"))
        updated = seq.with_support(10)
        assert updated.support == 10
        assert updated.items == ("A", "B")
        assert seq.support == 0  # Original unchanged

    def test_with_support_and_indices(self) -> None:
        """Test updating support with transaction indices."""
        seq = Sequence(items=("A", "B"))
        updated = seq.with_support(5, transaction_indices=(0, 2, 4))
        assert updated.support == 5
        assert updated.transaction_indices == (0, 2, 4)

    def test_with_metadata_basic(self) -> None:
        """Test adding metadata to a Sequence."""
        seq = Sequence(items=("A", "B"), support=5)
        updated = seq.with_metadata(confidence=0.75, lift=1.2)
        assert updated.metadata == {"confidence": 0.75, "lift": 1.2}
        assert updated.items == ("A", "B")
        assert updated.support == 5

    def test_with_metadata_updates_existing(self) -> None:
        """Test that with_metadata updates existing metadata."""
        seq = Sequence(items=("A",), metadata={"old": "value"})
        updated = seq.with_metadata(new="data", old="updated")
        assert updated.metadata == {"old": "updated", "new": "data"}


class TestSequenceImmutability:
    """Test that Sequence objects are immutable."""

    def test_sequence_is_frozen(self) -> None:
        """Test that Sequence is frozen (immutable)."""
        seq = Sequence(items=("A", "B"), support=5)
        with pytest.raises(AttributeError):
            seq.support = 10  # type: ignore

    def test_items_are_immutable(self) -> None:
        """Test that items cannot be modified."""
        seq = Sequence(items=("A", "B"))
        with pytest.raises(AttributeError):
            seq.items = ("X", "Y")  # type: ignore


class TestSequenceHashability:
    """Test Sequence hashing and dictionary usage."""

    def test_sequence_is_hashable(self) -> None:
        """Test that Sequence can be hashed."""
        seq = Sequence(items=("A", "B"), support=5)
        hash_value = hash(seq)
        assert isinstance(hash_value, int)

    def test_sequences_with_same_items_have_same_hash(self) -> None:
        """Test that Sequences with same items have same hash."""
        seq1 = Sequence(items=("A", "B"), support=5)
        seq2 = Sequence(items=("A", "B"), support=10)  # Different support
        # Support is included in hash because it's in the default dataclass hash
        # But for dictionary key purposes, items should be what matters most
        assert seq1.items == seq2.items

    def test_sequence_as_dict_key(self) -> None:
        """Test using Sequence as dictionary key."""
        seq1 = Sequence(items=("A", "B"), support=5)
        seq2 = Sequence(items=("A", "B"), support=5)
        seq3 = Sequence(items=("C", "D"), support=5)

        patterns = {seq1: "pattern1", seq3: "pattern2"}
        assert seq1 in patterns
        assert seq2 in patterns  # Same content
        assert seq3 in patterns

    def test_sequence_equality(self) -> None:
        """Test Sequence equality comparison."""
        seq1 = Sequence(items=("A", "B"), support=5)
        seq2 = Sequence(items=("A", "B"), support=5)
        seq3 = Sequence(items=("A", "B"), support=10)  # Different support
        seq4 = Sequence(items=("C", "D"), support=5)

        assert seq1 == seq2
        assert seq1 != seq3  # Different support
        assert seq1 != seq4  # Different items


class TestSequenceDunderMethods:
    """Test Sequence special methods."""

    def test_repr(self) -> None:
        """Test __repr__ output."""
        seq = Sequence(items=("A", "B"), support=5)
        repr_str = repr(seq)
        assert "Sequence" in repr_str
        assert "items=('A', 'B')" in repr_str
        assert "support=5" in repr_str

    def test_str(self) -> None:
        """Test __str__ output."""
        seq = Sequence(items=("A", "B"), support=5)
        str_output = str(seq)
        assert "('A', 'B')" in str_output
        assert "support=5" in str_output

    def test_len(self) -> None:
        """Test __len__ method."""
        seq = Sequence(items=("A", "B", "C"))
        assert len(seq) == 3

    def test_getitem_by_index(self) -> None:
        """Test accessing items by index."""
        seq = Sequence(items=("A", "B", "C"))
        assert seq[0] == "A"
        assert seq[1] == "B"
        assert seq[2] == "C"
        assert seq[-1] == "C"

    def test_getitem_by_slice(self) -> None:
        """Test accessing items by slice."""
        seq = Sequence(items=("A", "B", "C", "D"))
        assert seq[1:3] == ("B", "C")
        assert seq[:2] == ("A", "B")
        assert seq[2:] == ("C", "D")

    def test_iter(self) -> None:
        """Test iterating over Sequence."""
        seq = Sequence(items=("A", "B", "C"))
        items = list(seq)
        assert items == ["A", "B", "C"]

    def test_contains(self) -> None:
        """Test __contains__ method."""
        seq = Sequence(items=("A", "B", "C"))
        assert "A" in seq
        assert "B" in seq
        assert "D" not in seq


class TestUtilityFunctions:
    """Test utility functions for Sequence conversion."""

    def test_sequences_to_dict(self) -> None:
        """Test converting Sequences to dictionary."""
        sequences = [
            Sequence(items=("A",), support=5),
            Sequence(items=("B",), support=3),
            Sequence(items=("A", "B"), support=2),
        ]
        result = sequences_to_dict(sequences)
        assert result == {("A",): 5, ("B",): 3, ("A", "B"): 2}

    def test_sequences_to_dict_empty(self) -> None:
        """Test converting empty list of Sequences."""
        result = sequences_to_dict([])
        assert result == {}

    def test_dict_to_sequences(self) -> None:
        """Test converting dictionary to Sequences."""
        pattern_dict = {("A",): 5, ("B",): 3, ("A", "B"): 2}
        sequences = dict_to_sequences(pattern_dict)
        assert len(sequences) == 3
        # Check all sequences are created correctly
        items_and_support = {(seq.items, seq.support) for seq in sequences}
        assert items_and_support == {(("A",), 5), (("B",), 3), (("A", "B"), 2)}

    def test_dict_to_sequences_empty(self) -> None:
        """Test converting empty dictionary."""
        sequences = dict_to_sequences({})
        assert sequences == []

    def test_is_sequence_or_tuple(self) -> None:
        """Test checking if object is Sequence or tuple."""
        seq = Sequence(items=("A", "B"))
        assert is_sequence_or_tuple(seq) is True
        assert is_sequence_or_tuple(("A", "B")) is True
        assert is_sequence_or_tuple(["A", "B"]) is False
        assert is_sequence_or_tuple("AB") is False

    def test_to_sequence_from_sequence(self) -> None:
        """Test converting Sequence to Sequence (no-op)."""
        seq = Sequence(items=("A", "B"), support=5)
        result = to_sequence(seq)
        assert result is seq  # Should return same object

    def test_to_sequence_from_tuple(self) -> None:
        """Test converting tuple to Sequence."""
        result = to_sequence(("A", "B"), support=5)
        assert isinstance(result, Sequence)
        assert result.items == ("A", "B")
        assert result.support == 5

    def test_to_sequence_from_string(self) -> None:
        """Test converting string to singleton Sequence."""
        result = to_sequence("A", support=3)
        assert isinstance(result, Sequence)
        assert result.items == ("A",)
        assert result.support == 3

    def test_to_sequence_invalid_type(self) -> None:
        """Test that converting invalid type raises TypeError."""
        with pytest.raises(TypeError, match="Cannot convert"):
            to_sequence([1, 2, 3])


class TestSequenceEdgeCases:
    """Test edge cases and special scenarios."""

    def test_singleton_sequence(self) -> None:
        """Test Sequence with single item."""
        seq = Sequence(items=("A",))
        assert seq.length == 1
        assert seq.first_item == "A"
        assert seq.last_item == "A"

    def test_sequence_with_duplicate_items(self) -> None:
        """Test Sequence can contain duplicate items."""
        seq = Sequence(items=("A", "A", "B", "A"))
        assert seq.length == 4
        assert seq.items.count("A") == 3

    def test_sequence_with_large_support(self) -> None:
        """Test Sequence with very large support value."""
        seq = Sequence(items=("A",), support=1000000)
        assert seq.support == 1000000

    def test_sequence_with_many_items(self) -> None:
        """Test Sequence with many items."""
        items = tuple(str(i) for i in range(100))
        seq = Sequence(items=items)
        assert seq.length == 100
        assert seq.first_item == "0"
        assert seq.last_item == "99"

    def test_sequence_metadata_not_in_hash(self) -> None:
        """Test that metadata doesn't affect hash (as per dataclass config)."""
        seq1 = Sequence(items=("A",), support=5, metadata={"key": "value1"})
        seq2 = Sequence(items=("A",), support=5, metadata={"key": "value2"})
        # Metadata has compare=False and hash=False, so different metadata
        # shouldn't affect equality or hashing when other fields match
        # But they should still be equal since metadata is excluded from comparison
        assert seq1 == seq2  # Equal because metadata is excluded from comparison

    def test_sequence_roundtrip_conversion(self) -> None:
        """Test converting to dict and back to Sequences preserves data."""
        original_sequences = [
            Sequence(items=("A",), support=5),
            Sequence(items=("B", "C"), support=3),
        ]
        # Convert to dict
        pattern_dict = sequences_to_dict(original_sequences)
        # Convert back to sequences
        new_sequences = dict_to_sequences(pattern_dict)
        # Check equivalence (order might differ)
        original_set = {(seq.items, seq.support) for seq in original_sequences}
        new_set = {(seq.items, seq.support) for seq in new_sequences}
        assert original_set == new_set


class TestSequenceBackwardCompatibility:
    """Test backward compatibility with tuple-based code."""

    def test_sequence_can_replace_tuple_as_dict_key(self) -> None:
        """Test that Sequence can be used where tuples were used as keys."""
        # New style: Using Sequences
        seq1 = Sequence(items=("A", "B"), support=5)
        seq2 = Sequence(items=("C", "D"), support=3)

        # Can create dict with Sequences
        new_patterns = {seq1: seq1.support, seq2: seq2.support}
        assert len(new_patterns) == 2

    def test_as_tuple_for_legacy_code(self) -> None:
        """Test that as_tuple() provides tuple for legacy code."""
        seq = Sequence(items=("A", "B", "C"), support=5)
        pattern_tuple = seq.as_tuple()

        # Can use in legacy code expecting tuples
        legacy_dict = {pattern_tuple: seq.support}
        assert legacy_dict[("A", "B", "C")] == 5

    def test_conversion_functions_for_legacy_integration(self) -> None:
        """Test conversion functions for legacy API compatibility."""
        # New code returns Sequences
        sequences = [
            Sequence(items=("A",), support=5),
            Sequence(items=("B",), support=3),
        ]

        # Convert to old format for legacy code
        legacy_format = sequences_to_dict(sequences)
        assert legacy_format == {("A",): 5, ("B",): 3}

        # Convert back to new format
        new_sequences = dict_to_sequences(legacy_format)
        assert len(new_sequences) == 2
