"""Token mapping utilities for GSP-Py.

This module provides utilities for bidirectional mapping between string tokens
and integer IDs, useful for compatibility and workflow integration in sequential
pattern mining.
"""

from typing import Dict


class TokenMapper:
    """
    Utility class for mapping between string tokens and integer IDs.
    
    Provides bidirectional mapping between string tokens and internal integer representations,
    useful for compatibility and workflow integration.
    
    Attributes:
        str_to_int (Dict[str, int]): Map from string tokens to integer IDs
        int_to_str (Dict[int, str]): Map from integer IDs to string tokens
    
    Examples:
        >>> mapper = TokenMapper()
        >>> mapper.add_token("A")
        0
        >>> mapper.add_token("B")
        1
        >>> mapper.to_int("A")
        0
        >>> mapper.to_str(1)
        'B'
        >>> mapper.get_str_to_int()
        {'A': 0, 'B': 1}
    """
    
    def __init__(self) -> None:
        """Initialize empty token mappings."""
        self.str_to_int: Dict[str, int] = {}
        self.int_to_str: Dict[int, str] = {}
        self._next_id = 0
    
    def add_token(self, token: str) -> int:
        """
        Add a token to the mapping, returning its integer ID.
        
        If the token already exists, returns its existing ID.
        
        Parameters:
            token: String token to add
            
        Returns:
            int: Integer ID for the token
        """
        if token in self.str_to_int:
            return self.str_to_int[token]
        
        token_id = self._next_id
        self.str_to_int[token] = token_id
        self.int_to_str[token_id] = token
        self._next_id += 1
        return token_id
    
    def to_int(self, token: str) -> int:
        """
        Get the integer ID for a string token.
        
        Parameters:
            token: String token to lookup
            
        Returns:
            int: Integer ID for the token
            
        Raises:
            KeyError: If token not found in mapping
        """
        return self.str_to_int[token]
    
    def to_str(self, token_id: int) -> str:
        """
        Get the string token for an integer ID.
        
        Parameters:
            token_id: Integer ID to lookup
            
        Returns:
            str: String token for the ID
            
        Raises:
            KeyError: If ID not found in mapping
        """
        return self.int_to_str[token_id]
    
    def get_str_to_int(self) -> Dict[str, int]:
        """Get a copy of the string-to-int mapping."""
        return self.str_to_int.copy()
    
    def get_int_to_str(self) -> Dict[int, str]:
        """Get a copy of the int-to-string mapping."""
        return self.int_to_str.copy()
