"""
This module contains unit tests for the CLI-related functionality of the `gsppy` package
and the Generalized Sequential Pattern (GSP) mining algorithm. The tests ensure correctness,
robustness, and error handling for both file handling and the GSP algorithm implementation.

The tests include:
1. Validating file input handling for both JSON and CSV formats.
2. Ensuring proper error handling for invalid or malformed files (JSON, CSV) and unsupported formats.
3. Testing exceptions for non-existent files.
4. Verifying the behavior of the GSP algorithm when given valid inputs and configurations.
5. Checking for appropriate error handling when invalid parameters (e.g., `min_support`)
   are provided to the GSP algorithm.

Key components tested:
- `detect_and_read_file`: A method to detect the file type (JSON/CSV) and read transactions from it.
- `GSP.search`: Validates the sequential pattern mining functionality for valid and invalid `min_support` parameters.

Fixtures are used to create temporary files (valid/invalid JSON and CSV) for reliable testing
without affecting the file system.
Pytest is utilized for parametrized testing to improve coverage and reduce redundancy in test cases.
"""
import json
import os
import runpy
import sys
import tempfile
from unittest.mock import patch

import pytest

from gsppy.cli import detect_and_read_file, main
from gsppy.gsp import GSP


def test_invalid_json_structure():
    """
    Test if a JSON file with an invalid structure raises an error.
    """
    # Create an invalid JSON structure that does not adhere to the expected format
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w") as temp_file:
        temp_file.write(json.dumps({"invalid": "data"}))
        temp_file_name = temp_file.name

    # Attempt to read the invalid JSON file
    with pytest.raises(ValueError, match="File should contain a JSON array of transaction lists."):
        detect_and_read_file(temp_file_name)

    # Cleanup
    os.unlink(temp_file_name)


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


def test_main_invalid_json_file(monkeypatch, capfd):
    """
    Test `main()` with a JSON file that has an invalid structure.
    """
    # Create an invalid JSON file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w") as temp_file:
        temp_file.write(json.dumps({"invalid": "data"}))
        temp_file_name = temp_file.name

    # Mock CLI arguments
    monkeypatch.setattr(
        'sys.argv', ['main', '--file', temp_file_name, '--min_support', '0.2']
    )

    main()

    # Capture output
    captured = capfd.readouterr()
    assert "File should contain a JSON array of transaction lists." in captured.out

    # Cleanup
    os.unlink(temp_file_name)


def test_main_non_existent_file(monkeypatch, capfd):
    """
    Test `main()` with a file that does not exist.
    """
    # Mock CLI arguments
    monkeypatch.setattr(
        'sys.argv', ['main', '--file', 'non_existent.json', '--min_support', '0.2']
    )

    main()

    # Capture output
    captured = capfd.readouterr()
    assert "File 'non_existent.json' does not exist." in captured.out


def test_main_valid_json_file(monkeypatch, capfd):
    """
    Test `main()` with a valid JSON file.
    """
    # Create a valid JSON file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w") as temp_file:
        json.dump([["Bread", "Milk"], ["Milk", "Diaper"], ["Bread", "Diaper", "Beer"]], temp_file)
        temp_file_name = temp_file.name

    # Mock CLI arguments
    monkeypatch.setattr(
        'sys.argv', ['main', '--file', temp_file_name, '--min_support', '0.2']
    )

    main()

    # Capture output
    captured = capfd.readouterr()
    assert "Frequent Patterns Found:" in captured.out

    # Cleanup
    os.unlink(temp_file_name)


def test_main_invalid_min_support(monkeypatch, capfd):
    """
    Test `main()` with an invalid `min_support` value.
    """
    # Create a valid JSON file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w") as temp_file:
        json.dump([["Bread", "Milk"], ["Milk", "Diaper"], ["Bread", "Diaper", "Beer"]], temp_file)
        temp_file_name = temp_file.name

    # Mock CLI arguments
    monkeypatch.setattr(
        'sys.argv', ['main', '--file', temp_file_name, '--min_support', '-1.0']  # Invalid min_support
    )

    main()

    # Capture output
    captured = capfd.readouterr()
    assert "Error: min_support must be in the range (0.0, 1.0]." in captured.out

    # Cleanup
    os.unlink(temp_file_name)


def test_main_entry_point(monkeypatch, capfd):
    """
    Test the script entry point (`if __name__ == '__main__': main()`).
    """
    # Create a valid JSON file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w") as temp_file:
        json.dump([["Bread", "Milk"], ["Milk", "Diaper"], ["Bread", "Diaper", "Beer"]], temp_file)
        temp_file_name = temp_file.name

    # Mock CLI arguments - Simulating script call
    monkeypatch.setattr(
        'sys.argv', ['gsppy.cli', '--file', temp_file_name, '--min_support', '0.2']
    )

    # Remove the module from sys.modules before running it
    if 'gsppy.cli' in sys.modules:
        del sys.modules['gsppy.cli']

    # Use `runpy` to execute the script as if it were run from the command line
    runpy.run_module('gsppy.cli', run_name='__main__')

    # Capture the output
    captured = capfd.readouterr()
    assert "Frequent Patterns Found:" in captured.out

    # Cleanup
    os.unlink(temp_file_name)


def test_main_edge_case_min_support(monkeypatch, capfd):
    """
    Test `main()` with edge-case values for `min_support` (valid and invalid).
    """
    # Create a valid JSON
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w") as temp_file:
        json.dump([["Bread", "Milk"], ["Milk", "Diaper"], ["Bread", "Diaper", "Beer"]], temp_file)
        temp_file_name = temp_file.name

    # Case 1: `min_support` = 1.0 (Valid Edge Case)
    monkeypatch.setattr(
        'sys.argv', ['main', '--file', temp_file_name, '--min_support', '1.0']
    )
    main()
    captured = capfd.readouterr()
    assert "Frequent Patterns Found:" in captured.out

    # Case 2: `min_support` = -1.0 (Invalid Edge Case)
    monkeypatch.setattr(
        'sys.argv', ['main', '--file', temp_file_name, '--min_support', '-1.0']
    )
    main()
    captured = capfd.readouterr()
    assert "Error: min_support must be in the range (0.0, 1.0]." in captured.out

    # Cleanup
    os.unlink(temp_file_name)


def test_main_gsp_exception(monkeypatch, capfd):
    """
    Test `main()` when the GSP algorithm raises an exception.
    """
    # Step 1: Create a valid JSON file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w") as temp_file:
        json.dump([["Bread", "Milk"], ["Milk", "Diaper"], ["Bread", "Diaper", "Beer"]], temp_file)
        temp_file_name = temp_file.name

    # Step 2: Mock CLI arguments
    monkeypatch.setattr(
        'sys.argv', ['main', '--file', temp_file_name, '--min_support', '0.2']
    )

    # Step 3: Mock GSP.search to raise an exception
    with patch('gsppy.gsp.GSP.search', side_effect=Exception("Simulated GSP failure")):
        main()

    # Step 4: Capture output and assert the error message
    captured = capfd.readouterr()
    assert "Error executing GSP algorithm: Simulated GSP failure" in captured.out

    # Step 5: Cleanup
    os.unlink(temp_file_name)
