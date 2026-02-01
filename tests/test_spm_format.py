"""
Test suite for SPM/GSP format loader and token mapping utilities.

This module tests the following functionalities:
1. SPM/GSP format parsing with -1 (end of element) and -2 (end of sequence) delimiters
2. Token mapping between strings and integers
3. Edge case handling: empty lines, trailing delimiters, malformed input
4. CLI integration with --format spm option
"""

import os
import tempfile
from typing import Generator, cast

import pytest

from gsppy.cli import read_transactions_from_spm as cli_read_spm
from gsppy.utils import TokenMapper, read_transactions_from_spm


class TestTokenMapper:
    """Test suite for TokenMapper class."""

    def test_add_token(self):
        """Test adding tokens to the mapper."""
        mapper = TokenMapper()
        id_a = mapper.add_token("A")
        id_b = mapper.add_token("B")

        assert id_a == 0
        assert id_b == 1
        assert mapper.to_int("A") == 0
        assert mapper.to_int("B") == 1

    def test_duplicate_token(self):
        """Test that adding duplicate tokens returns the same ID."""
        mapper = TokenMapper()
        id_a1 = mapper.add_token("A")
        id_a2 = mapper.add_token("A")

        assert id_a1 == id_a2
        assert len(mapper.get_str_to_int()) == 1

    def test_to_str(self):
        """Test converting integer IDs back to strings."""
        mapper = TokenMapper()
        mapper.add_token("A")
        mapper.add_token("B")
        mapper.add_token("C")

        assert mapper.to_str(0) == "A"
        assert mapper.to_str(1) == "B"
        assert mapper.to_str(2) == "C"

    def test_to_int_missing(self):
        """Test that accessing non-existent token raises KeyError."""
        mapper = TokenMapper()
        mapper.add_token("A")

        with pytest.raises(KeyError):
            mapper.to_int("B")

    def test_to_str_missing(self):
        """Test that accessing non-existent ID raises KeyError."""
        mapper = TokenMapper()
        mapper.add_token("A")

        with pytest.raises(KeyError):
            mapper.to_str(99)

    def test_get_mappings(self):
        """Test getting copies of mappings."""
        mapper = TokenMapper()
        mapper.add_token("A")
        mapper.add_token("B")

        str_to_int = mapper.get_str_to_int()
        int_to_str = mapper.get_int_to_str()

        assert str_to_int == {"A": 0, "B": 1}
        assert int_to_str == {0: "A", 1: "B"}

        # Verify these are copies
        str_to_int["C"] = 2
        assert "C" not in mapper.get_str_to_int()


class TestSPMFormatBasic:
    """Test basic SPM format parsing."""

    @pytest.fixture
    def simple_spm_file(self) -> Generator[str, None, None]:
        """Fixture to create a simple SPM format file."""
        with tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".txt") as f:
            f.write("1 2 -1 3 -1 -2\n")
            f.write("4 -1 5 6 -1 -2\n")
            f.write("1 -1 2 3 -1 -2\n")
            temp_file_name = f.name
        yield temp_file_name
        os.unlink(temp_file_name)

    def test_basic_parsing(self, simple_spm_file: str):
        """Test basic SPM format parsing."""
        transactions = read_transactions_from_spm(simple_spm_file)

        assert len(transactions) == 3
        assert transactions[0] == ["1", "2", "3"]
        assert transactions[1] == ["4", "5", "6"]
        assert transactions[2] == ["1", "2", "3"]

    def test_basic_parsing_with_mappings(self, simple_spm_file: str):
        """Test SPM parsing with token mappings."""
        result = cast(tuple, read_transactions_from_spm(simple_spm_file, return_mappings=True))
        transactions, str_to_int, int_to_str = result

        assert len(transactions) == 3
        assert len(str_to_int) == 6  # Unique tokens: 1, 2, 3, 4, 5, 6
        assert len(int_to_str) == 6

        # Verify mapping consistency
        for token, token_id in str_to_int.items():
            assert int_to_str[token_id] == token


class TestSPMFormatEdgeCases:
    """Test edge cases in SPM format parsing."""

    @pytest.fixture
    def empty_lines_file(self) -> Generator[str, None, None]:
        """Fixture with empty lines."""
        with tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".txt") as f:
            f.write("1 2 -1 -2\n")
            f.write("\n")
            f.write("3 4 -1 -2\n")
            f.write("   \n")
            f.write("5 -1 -2\n")
            temp_file_name = f.name
        yield temp_file_name
        os.unlink(temp_file_name)

    def test_empty_lines(self, empty_lines_file: str):
        """Test that empty lines are skipped."""
        transactions = read_transactions_from_spm(empty_lines_file)

        assert len(transactions) == 3
        assert transactions[0] == ["1", "2"]
        assert transactions[1] == ["3", "4"]
        assert transactions[2] == ["5"]

    @pytest.fixture
    def missing_end_delimiter_file(self) -> Generator[str, None, None]:
        """Fixture with missing -2 delimiter."""
        with tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".txt") as f:
            f.write("1 2 -1 3 -1\n")  # Missing -2
            f.write("4 5 -1 -2\n")
            temp_file_name = f.name
        yield temp_file_name
        os.unlink(temp_file_name)

    def test_missing_end_delimiter(self, missing_end_delimiter_file: str):
        """Test handling of missing -2 delimiter."""
        transactions = read_transactions_from_spm(missing_end_delimiter_file)

        assert len(transactions) == 2
        assert transactions[0] == ["1", "2", "3"]  # Should still parse
        assert transactions[1] == ["4", "5"]

    @pytest.fixture
    def extra_delimiters_file(self) -> Generator[str, None, None]:
        """Fixture with extra delimiters."""
        with tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".txt") as f:
            f.write("1 -1 -1 2 -1 -2\n")  # Extra -1
            f.write("3 -1 -2 -2\n")  # Extra -2
            temp_file_name = f.name
        yield temp_file_name
        os.unlink(temp_file_name)

    def test_extra_delimiters(self, extra_delimiters_file: str):
        """Test handling of extra delimiters."""
        transactions = read_transactions_from_spm(extra_delimiters_file)

        assert len(transactions) == 2
        assert transactions[0] == ["1", "2"]
        assert transactions[1] == ["3"]

    @pytest.fixture
    def string_tokens_file(self) -> Generator[str, None, None]:
        """Fixture with string tokens instead of integers."""
        with tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".txt") as f:
            f.write("A B -1 C -1 -2\n")
            f.write("D -1 E F -1 -2\n")
            temp_file_name = f.name
        yield temp_file_name
        os.unlink(temp_file_name)

    def test_string_tokens(self, string_tokens_file: str):
        """Test parsing string tokens."""
        transactions = read_transactions_from_spm(string_tokens_file)

        assert len(transactions) == 2
        assert transactions[0] == ["A", "B", "C"]
        assert transactions[1] == ["D", "E", "F"]

    @pytest.fixture
    def mixed_length_elements_file(self) -> Generator[str, None, None]:
        """Fixture with varied element lengths."""
        with tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".txt") as f:
            f.write("1 -1 -2\n")  # Single item
            f.write("2 3 4 -1 -2\n")  # Three items
            f.write("5 6 -1 7 8 9 10 -1 -2\n")  # Mixed: 2 items, then 4 items
            temp_file_name = f.name
        yield temp_file_name
        os.unlink(temp_file_name)

    def test_mixed_length_elements(self, mixed_length_elements_file: str):
        """Test parsing sequences with varied element lengths."""
        transactions = read_transactions_from_spm(mixed_length_elements_file)

        assert len(transactions) == 3
        assert transactions[0] == ["1"]
        assert transactions[1] == ["2", "3", "4"]
        assert transactions[2] == ["5", "6", "7", "8", "9", "10"]


class TestSPMFormatErrors:
    """Test error handling in SPM format parsing."""

    def test_nonexistent_file(self):
        """Test that reading non-existent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="does not exist"):
            read_transactions_from_spm("/nonexistent/file.txt")

    @pytest.fixture
    def empty_file(self) -> Generator[str, None, None]:
        """Fixture with empty file."""
        with tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".txt") as f:
            temp_file_name = f.name
        yield temp_file_name
        os.unlink(temp_file_name)

    def test_empty_file(self, empty_file: str):
        """Test parsing empty file returns empty list."""
        transactions = read_transactions_from_spm(empty_file)
        assert transactions == []


class TestSPMFormatComplex:
    """Test complex SPM format scenarios."""

    @pytest.fixture
    def complex_spm_file(self) -> Generator[str, None, None]:
        """Fixture with a more complex SPM dataset."""
        with tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".txt") as f:
            # Customer purchase sequences
            f.write("1 2 -1 3 -1 1 4 -1 5 -1 -2\n")
            f.write("1 -1 3 4 -1 2 -1 -2\n")
            f.write("1 -1 2 3 -1 1 5 -1 -2\n")
            f.write("4 5 -1 1 -1 -2\n")
            temp_file_name = f.name
        yield temp_file_name
        os.unlink(temp_file_name)

    def test_complex_parsing(self, complex_spm_file: str):
        """Test parsing complex SPM file."""
        transactions = cast(list, read_transactions_from_spm(complex_spm_file))

        assert len(transactions) == 4
        assert transactions[0] == ["1", "2", "3", "1", "4", "5"]
        assert transactions[1] == ["1", "3", "4", "2"]
        assert transactions[2] == ["1", "2", "3", "1", "5"]
        assert transactions[3] == ["4", "5", "1"]

    def test_complex_with_mappings(self, complex_spm_file: str):
        """Test complex file with mappings."""
        result = cast(tuple, read_transactions_from_spm(complex_spm_file, return_mappings=True))
        transactions, str_to_int, _ = result

        assert len(transactions) == 4
        # Unique tokens: 1, 2, 3, 4, 5
        assert len(str_to_int) == 5
        assert set(str_to_int.keys()) == {"1", "2", "3", "4", "5"}


class TestCLIIntegration:
    """Test CLI integration with SPM format."""

    @pytest.fixture
    def spm_file_for_cli(self) -> Generator[str, None, None]:
        """Fixture for CLI testing."""
        with tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".txt") as f:
            f.write("1 2 -1 3 -1 -2\n")
            f.write("1 -1 2 3 -1 -2\n")
            temp_file_name = f.name
        yield temp_file_name
        os.unlink(temp_file_name)

    def test_cli_read_spm(self, spm_file_for_cli: str):
        """Test CLI SPM reader function."""
        transactions = cli_read_spm(spm_file_for_cli)

        assert len(transactions) == 2
        assert transactions[0] == ["1", "2", "3"]
        assert transactions[1] == ["1", "2", "3"]
