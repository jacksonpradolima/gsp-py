"""
Sequence abstraction for GSP-Py algorithms.

This module provides a Sequence class that encapsulates a pattern's elements,
associated transaction indices or counts, and any extra metadata (such as pattern
support, provenance, or timestamps). This abstraction enhances maintainability,
clarity, and future extensibility of GSP-Py's core logic.

The Sequence class is designed to be:
- Immutable and hashable (can be used as dictionary keys)
- Backward compatible with tuple representations
- Efficient for multiprocessing (pickleable)
- Extensible for future metadata additions

Author: Jackson Antonio do Prado Lima
Email: jacksonpradolima@gmail.com
"""

from __future__ import annotations

from typing import Tuple, Optional, List, Union, Set, Any
from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class Sequence:
    """
    Represents a sequential pattern with associated metadata.

    This class encapsulates a pattern (sequence of items) along with its
    support count, transaction indices, and optional temporal metadata.
    The class is immutable and hashable, allowing it to be used as dictionary
    keys while providing a richer interface than bare tuples.

    Attributes:
        items (Tuple[str, ...]): The pattern elements as an immutable tuple.
        support (int): The support count (number of transactions containing this pattern).
                      Defaults to 0 for candidate sequences not yet evaluated.
        transaction_indices (Optional[Tuple[int, ...]]): Indices of transactions that
                                                         contain this pattern. Optional
                                                         as it may not always be tracked
                                                         to save memory.
        metadata (Optional[dict]): Additional metadata such as timestamps, confidence,
                                   lift, or other pattern-specific information.

    Examples:
        Create a simple sequence:
        >>> seq = Sequence(items=("A", "B", "C"), support=5)
        >>> seq.length
        3
        >>> seq.items
        ('A', 'B', 'C')

        Create from tuple for backward compatibility:
        >>> seq = Sequence.from_tuple(("A", "B"))
        >>> seq.items
        ('A', 'B')

        Use as dictionary key:
        >>> patterns = {seq: 10}
        >>> seq in patterns
        True
    """

    items: Tuple[str, ...]
    support: int = 0
    transaction_indices: Optional[Tuple[int, ...]] = None
    metadata: Optional[dict] = field(default=None, compare=False, hash=False)

    def __post_init__(self) -> None:
        """Validate the sequence after initialization."""
        if not isinstance(self.items, tuple):
            # If items is not a tuple, convert it
            object.__setattr__(self, 'items', tuple(self.items))

        if not self.items:
            raise ValueError("Sequence items cannot be empty")

        if self.support < 0:
            raise ValueError("Support count cannot be negative")

        if self.transaction_indices is not None and not isinstance(self.transaction_indices, tuple):
            object.__setattr__(self, 'transaction_indices', tuple(self.transaction_indices))

    @property
    def length(self) -> int:
        """Return the length of the sequence (number of items)."""
        return len(self.items)

    @property
    def first_item(self) -> str:
        """Return the first item in the sequence."""
        if not self.items:
            raise IndexError("Cannot get first item from empty sequence")
        return self.items[0]

    @property
    def last_item(self) -> str:
        """Return the last item in the sequence."""
        if not self.items:
            raise IndexError("Cannot get last item from empty sequence")
        return self.items[-1]

    def as_tuple(self) -> Tuple[str, ...]:
        """
        Return the pattern as a plain tuple for backward compatibility.

        Returns:
            Tuple[str, ...]: The sequence items as a tuple.
        """
        return self.items

    @classmethod
    def from_tuple(
        cls,
        items: Tuple[str, ...],
        support: int = 0,
        transaction_indices: Optional[Tuple[int, ...]] = None,
        metadata: Optional[dict] = None,
    ) -> Sequence:
        """
        Create a Sequence from a tuple of items.

        This is a convenience method for backward compatibility with code
        that uses plain tuples to represent patterns.

        Parameters:
            items (Tuple[str, ...]): The pattern elements.
            support (int): The support count. Defaults to 0.
            transaction_indices (Optional[Tuple[int, ...]]): Transaction indices.
            metadata (Optional[dict]): Additional metadata.

        Returns:
            Sequence: A new Sequence instance.

        Examples:
            >>> seq = Sequence.from_tuple(("A", "B", "C"), support=5)
            >>> seq.items
            ('A', 'B', 'C')
            >>> seq.support
            5
        """
        return cls(
            items=items,
            support=support,
            transaction_indices=transaction_indices,
            metadata=metadata,
        )

    @classmethod
    def from_item(cls, item: str, support: int = 0) -> Sequence:
        """
        Create a singleton Sequence from a single item.

        Parameters:
            item (str): The single item.
            support (int): The support count. Defaults to 0.

        Returns:
            Sequence: A new Sequence instance containing only the item.

        Examples:
            >>> seq = Sequence.from_item("A", support=10)
            >>> seq.items
            ('A',)
            >>> seq.length
            1
        """
        return cls(items=(item,), support=support)

    def extend(self, item: str, support: int = 0) -> Sequence:
        """
        Create a new Sequence by extending this one with an additional item.

        This is used during candidate generation to create k+1 sequences
        from k sequences.

        Parameters:
            item (str): The item to append.
            support (int): The support count for the new sequence. Defaults to 0.

        Returns:
            Sequence: A new Sequence with the item appended.

        Examples:
            >>> seq = Sequence.from_tuple(("A", "B"))
            >>> new_seq = seq.extend("C")
            >>> new_seq.items
            ('A', 'B', 'C')
        """
        return Sequence(
            items=self.items + (item,),
            support=support,
            transaction_indices=None,  # New sequence, no indices yet
            metadata=self.metadata.copy() if self.metadata else None,
        )

    def with_support(self, support: int, transaction_indices: Optional[Tuple[int, ...]] = None) -> Sequence:
        """
        Create a new Sequence with updated support information.

        This is used after calculating support to update the sequence
        with its actual support count and optionally transaction indices.

        Parameters:
            support (int): The new support count.
            transaction_indices (Optional[Tuple[int, ...]]): Transaction indices.

        Returns:
            Sequence: A new Sequence with updated support information.

        Examples:
            >>> seq = Sequence.from_tuple(("A", "B"))
            >>> supported_seq = seq.with_support(5, (0, 2, 4))
            >>> supported_seq.support
            5
        """
        return Sequence(
            items=self.items,
            support=support,
            transaction_indices=transaction_indices,
            metadata=self.metadata,
        )

    def with_metadata(self, **kwargs: Any) -> Sequence:
        """
        Create a new Sequence with additional or updated metadata.

        Parameters:
            **kwargs: Metadata key-value pairs to add or update.

        Returns:
            Sequence: A new Sequence with updated metadata.

        Examples:
            >>> seq = Sequence.from_tuple(("A", "B"), support=5)
            >>> seq_with_meta = seq.with_metadata(confidence=0.75, lift=1.2)
            >>> seq_with_meta.metadata
            {'confidence': 0.75, 'lift': 1.2}
        """
        new_metadata = (self.metadata or {}).copy()
        new_metadata.update(kwargs)
        return Sequence(
            items=self.items,
            support=self.support,
            transaction_indices=self.transaction_indices,
            metadata=new_metadata,
        )

    def __repr__(self) -> str:
        """Return a string representation of the Sequence."""
        parts = [f"items={self.items}", f"support={self.support}"]
        if self.transaction_indices is not None:
            parts.append(f"transaction_indices={self.transaction_indices}")
        if self.metadata:
            parts.append(f"metadata={self.metadata}")
        return f"Sequence({', '.join(parts)})"

    def __str__(self) -> str:
        """Return a human-readable string representation."""
        return f"{self.items} (support={self.support})"

    def __len__(self) -> int:
        """Return the length of the sequence."""
        return len(self.items)

    def __getitem__(self, index: Union[int, slice]) -> Union[str, Tuple[str, ...]]:
        """
        Access items by index or slice.

        Parameters:
            index: Integer index or slice object.

        Returns:
            str or Tuple[str, ...]: Single item or tuple of items.
        """
        return self.items[index]

    def __iter__(self):
        """Iterate over the items in the sequence."""
        return iter(self.items)

    def __contains__(self, item: str) -> bool:
        """Check if an item is in the sequence."""
        return item in self.items


# Utility functions for working with Sequences and tuples


def sequences_to_dict(sequences: List[Sequence]) -> dict[Tuple[str, ...], int]:
    """
    Convert a list of Sequence objects to a dictionary mapping tuples to support counts.

    This function provides backward compatibility with code expecting the
    traditional Dict[Tuple[str, ...], int] format.

    Parameters:
        sequences (List[Sequence]): List of Sequence objects.

    Returns:
        dict[Tuple[str, ...], int]: Dictionary mapping pattern tuples to support counts.

    Examples:
        >>> seqs = [Sequence(("A",), 5), Sequence(("B",), 3)]
        >>> sequences_to_dict(seqs)
        {('A',): 5, ('B',): 3}
    """
    return {seq.items: seq.support for seq in sequences}


def dict_to_sequences(pattern_dict: dict[Tuple[str, ...], int]) -> List[Sequence]:
    """
    Convert a dictionary of patterns to a list of Sequence objects.

    This function converts the traditional Dict[Tuple[str, ...], int] format
    to Sequence objects.

    Parameters:
        pattern_dict (dict[Tuple[str, ...], int]): Dictionary mapping tuples to support.

    Returns:
        List[Sequence]: List of Sequence objects.

    Examples:
        >>> patterns = {('A',): 5, ('B',): 3}
        >>> seqs = dict_to_sequences(patterns)
        >>> len(seqs)
        2
    """
    return [Sequence.from_tuple(items, support=support) for items, support in pattern_dict.items()]


def is_sequence_or_tuple(obj: Any) -> bool:
    """
    Check if an object is a Sequence instance or a tuple.

    Parameters:
        obj: Object to check.

    Returns:
        bool: True if obj is a Sequence or tuple, False otherwise.
    """
    return isinstance(obj, (Sequence, tuple))


def to_sequence(obj: Union[Sequence, Tuple[str, ...], str], support: int = 0) -> Sequence:
    """
    Convert various input types to a Sequence object.

    Parameters:
        obj: Input object (Sequence, tuple, or string).
        support: Support count to use if creating a new Sequence.

    Returns:
        Sequence: A Sequence object.

    Examples:
        >>> to_sequence(("A", "B"), support=5)
        Sequence(items=('A', 'B'), support=5)
        >>> seq = Sequence(("X",), 3)
        >>> to_sequence(seq)
        Sequence(items=('X',), support=3)
    """
    if isinstance(obj, Sequence):
        return obj
    elif isinstance(obj, tuple):
        return Sequence.from_tuple(obj, support=support)
    elif isinstance(obj, str):
        return Sequence.from_item(obj, support=support)
    else:
        raise TypeError(f"Cannot convert {type(obj)} to Sequence")
