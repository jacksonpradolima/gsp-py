"""
This module contains unit tests for the CLI-related functionality of the `gsppy` package
and the Generalized Sequential Pattern (GSP) mining algorithm. The tests ensure correctness,
robustness, and error handling for both file handling and the GSP algorithm implementation.

The tests include:
1. Validating file input handling for both JSON and CSV formats.
2. Ensuring proper error handling for invalid or malformed files (JSON, CSV) and unsupported formats.
3. Testing exceptions for non-existent files.
4. Verifying the behavior of the GSP algorithm when given valid inputs and configurations.
5. Checking for appropriate error handling when invalid parameters (e.g., `min_support`) are provided to the GSP algorithm.

Key components tested:
- `detect_and_read_file`: A method to detect the file type (JSON/CSV) and read transactions from it.
- `GSP.search`: Validates the sequential pattern mining functionality for valid and invalid `min_support` parameters.

Fixtures are used to create temporary files (valid/invalid JSON and CSV) for reliable testing without affecting the file system.
Pytest is utilized for parametrized testing to improve coverage and reduce redundancy in test cases.
"""
import json
import os
import tempfile

import pytest

from gsppy.cli import detect_and_read_file
from gsppy.gsp import GSP


@pytest.fixture
def valid_json_file():
    """Fixture to create a valid JSON file."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w") as temp_file:
        json.dump([["Bread", "Milk"], ["Milk", "Diaper"], ["Bread", "Diaper", "Beer"]], temp_file)
        temp_file_name = temp_file.name
    yield temp_file_name
    os.unlink(temp_file_name)


@pytest.fixture
def valid_csv_file():
    """Fixture to create a valid CSV file."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_file:
        temp_file.write(b"Bread,Milk\nMilk,Diaper\nBread,Diaper,Beer\n")
        temp_file_name = temp_file.name
    yield temp_file_name
    os.unlink(temp_file_name)


@pytest.fixture
def invalid_json_file():
    """Fixture to create an invalid JSON file."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp_file:
        temp_file.write(b"{invalid_json: true")  # Malformed JSON
        temp_file_name = temp_file.name
    yield temp_file_name
    os.unlink(temp_file_name)


@pytest.fixture
def invalid_csv_file():
    """Fixture to create an invalid CSV file."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_file:
        temp_file.write(b",,\nBread,,Milk\n")  # Broken format
        temp_file_name = temp_file.name
    yield temp_file_name
    os.unlink(temp_file_name)


@pytest.fixture
def unsupported_file():
    """Fixture to create an unsupported file."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as temp_file:
        temp_file.write(b"This is a plain text file.")
        temp_file_name = temp_file.name
    yield temp_file_name
    os.unlink(temp_file_name)


def test_valid_json_file(valid_json_file):
    """Test if a valid JSON file is correctly read."""
    transactions = detect_and_read_file(valid_json_file)
    assert transactions == [["Bread", "Milk"], ["Milk", "Diaper"], ["Bread", "Diaper", "Beer"]]


def test_valid_csv_file(valid_csv_file):
    """Test if a valid CSV file is correctly read."""
    transactions = detect_and_read_file(valid_csv_file)
    assert transactions == [["Bread", "Milk"], ["Milk", "Diaper"], ["Bread", "Diaper", "Beer"]]


def test_invalid_json_file(invalid_json_file):
    """Test if an invalid JSON file raises an error."""
    with pytest.raises(ValueError, match="Error reading transaction data from JSON file"):
        detect_and_read_file(invalid_json_file)


def test_invalid_csv_file(invalid_csv_file):
    """Test if an invalid CSV file raises an error."""
    with pytest.raises(ValueError, match="Error reading transaction data from CSV file"):
        detect_and_read_file(invalid_csv_file)


def test_unsupported_file_format(unsupported_file):
    """Test if an unsupported file format raises an error."""
    with pytest.raises(ValueError, match="Unsupported file format"):
        detect_and_read_file(unsupported_file)


def test_non_existent_file():
    """Test if a non-existent file raises an error."""
    with pytest.raises(ValueError, match="File 'non_existent_file.json' does not exist."):
        detect_and_read_file("non_existent_file.json")


@pytest.mark.parametrize("min_support", [-0.1, 1.1])
def test_invalid_min_support_gsp(min_support):
    """Test if invalid min_support values raise an error."""
    transactions = [["Bread", "Milk"], ["Milk", "Diaper"], ["Bread", "Diaper", "Beer"]]
    gsp = GSP(transactions)
    with pytest.raises(ValueError):
        gsp.search(min_support=min_support)


@pytest.mark.parametrize("min_support", [0.5])
def test_valid_min_support_gsp(min_support):
    """Test if valid min_support values work with the GSP algorithm."""
    transactions = [["Bread", "Milk"], ["Milk", "Diaper"], ["Bread", "Diaper", "Beer"]]
    gsp = GSP(transactions)
    patterns = gsp.search(min_support=min_support)
    assert len(patterns) > 0  # Ensure at least some patterns are found
    assert patterns[0]  # Ensure frequent patterns are not empty
