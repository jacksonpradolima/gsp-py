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
import os
import json
import logging
import tempfile
import subprocess
from typing import Any, Generator
from unittest.mock import patch

import pytest
from pytest import MonkeyPatch

from gsppy.cli import main, detect_and_read_file
from gsppy.gsp import GSP


@pytest.fixture
def valid_json_file() -> Generator[Any, Any, Any]:
    """Fixture to create a valid JSON file."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w") as temp_file:
        json.dump([["Bread", "Milk"], ["Milk", "Diaper"], ["Bread", "Diaper", "Beer"]], temp_file)
        temp_file_name = temp_file.name
    yield temp_file_name
    os.unlink(temp_file_name)


@pytest.fixture
def valid_csv_file() -> Generator[Any, Any, Any]:
    """Fixture to create a valid CSV file."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_file:
        temp_file.write(b"Bread,Milk\nMilk,Diaper\nBread,Diaper,Beer\n")
        temp_file_name = temp_file.name
    yield temp_file_name
    os.unlink(temp_file_name)


@pytest.fixture
def invalid_json_file() -> Generator[Any, Any, Any]:
    """Fixture to create an invalid JSON file."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp_file:
        temp_file.write(b"{invalid_json: true")  # Malformed JSON
        temp_file_name = temp_file.name
    yield temp_file_name
    os.unlink(temp_file_name)


@pytest.fixture
def invalid_csv_file() -> Generator[Any, Any, Any]:
    """Fixture to create an invalid CSV file."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_file:
        temp_file.write(b",,\nBread,,Milk\n")  # Broken format
        temp_file_name = temp_file.name
    yield temp_file_name
    os.unlink(temp_file_name)


@pytest.fixture
def unsupported_file() -> Generator[Any, Any, Any]:
    """Fixture to create an unsupported file."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as temp_file:
        temp_file.write(b"This is a plain text file.")
        temp_file_name = temp_file.name
    yield temp_file_name
    os.unlink(temp_file_name)


def test_valid_json_file(valid_json_file: Generator[Any, Any, Any]):
    """Test if a valid JSON file is correctly read."""
    transactions = detect_and_read_file(str(valid_json_file))
    assert transactions == [["Bread", "Milk"], ["Milk", "Diaper"], ["Bread", "Diaper", "Beer"]]


def test_valid_csv_file(valid_csv_file: Generator[Any, Any, Any]):
    """Test if a valid CSV file is correctly read."""
    transactions = detect_and_read_file(str(valid_csv_file))
    assert transactions == [["Bread", "Milk"], ["Milk", "Diaper"], ["Bread", "Diaper", "Beer"]]


def test_invalid_json_file(invalid_json_file: Generator[Any, Any, Any]):
    """Test if an invalid JSON file raises an error."""
    with pytest.raises(ValueError, match="Error reading transaction data from JSON file"):
        detect_and_read_file(str(invalid_json_file))


def test_invalid_csv_file(invalid_csv_file: Generator[Any, Any, Any]):
    """Test if an invalid CSV file raises an error."""
    with pytest.raises(ValueError, match="Error reading transaction data from CSV file"):
        detect_and_read_file(str(invalid_csv_file))


def test_unsupported_file_format(unsupported_file: Generator[Any, Any, Any]):
    """Test if an unsupported file format raises an error."""
    with pytest.raises(ValueError, match="Unsupported file format"):
        detect_and_read_file(str(unsupported_file))


def test_non_existent_file():
    """Test if a non-existent file raises an error."""
    with pytest.raises(ValueError, match="File 'non_existent_file.json' does not exist."):
        detect_and_read_file("non_existent_file.json")


@pytest.mark.parametrize("min_support", [-0.1, 1.1])
def test_invalid_min_support_gsp(min_support: float):
    """Test if invalid min_support values raise an error."""
    transactions = [["Bread", "Milk"], ["Milk", "Diaper"], ["Bread", "Diaper", "Beer"]]
    gsp = GSP(transactions)
    with pytest.raises(ValueError):
        gsp.search(min_support=min_support)


@pytest.mark.parametrize("min_support", [0.5])
def test_valid_min_support_gsp(min_support: float):
    """Test if valid min_support values work with the GSP algorithm."""
    transactions = [["Bread", "Milk"], ["Milk", "Diaper"], ["Bread", "Diaper", "Beer"]]
    gsp = GSP(transactions)
    patterns = gsp.search(min_support=min_support)
    assert len(patterns) > 0  # Ensure at least some patterns are found
    assert patterns[0]  # Ensure frequent patterns are not empty


def test_main_invalid_json_file(monkeypatch: MonkeyPatch):
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

    # Mock logger.error and test messages directly
    with patch("gsppy.cli.logger.error") as mock_error:
        main()

        # Assert correct error message was logged
        mock_error.assert_called_with(
            "Error executing GSP algorithm: GSP requires multiple transactions to find meaningful patterns."
        )

    # Cleanup
    os.unlink(temp_file_name)


def test_main_non_existent_file(monkeypatch: MonkeyPatch):
    """
    Test `main()` with a file that does not exist.
    """
    # Mock CLI arguments
    monkeypatch.setattr(
        'sys.argv', ['main', '--file', 'non_existent.json', '--min_support', '0.2']
    )

    with patch("gsppy.cli.logger.error") as mock_error:
        main()
        mock_error.assert_called_with("Error: File 'non_existent.json' does not exist.")


def test_main_valid_json_file(monkeypatch: MonkeyPatch):
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

    with patch("gsppy.cli.logger.info") as mock_info:
        main()
        mock_info.assert_any_call("Frequent Patterns Found:")  # Check for expected log message

    # Cleanup
    os.unlink(temp_file_name)


def test_main_invalid_min_support(monkeypatch: MonkeyPatch):
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

    with patch("gsppy.cli.logger.error") as mock_error:
        main()
        mock_error.assert_called_with("Error: min_support must be in the range (0.0, 1.0].")

    # Cleanup
    os.unlink(temp_file_name)


def test_main_entry_point():
    """
    Test the script entry point (`if __name__ == '__main__': main()`).
    """
    # Create a valid JSON file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w") as temp_file:
        json.dump([["Bread", "Milk"], ["Milk", "Diaper"], ["Bread", "Diaper", "Beer"]], temp_file)
        temp_file_name = temp_file.name

    # Get the CLI script path
    cli_script = os.path.abspath(os.path.join(os.path.dirname(__file__), '../gsppy/cli.py'))

    # Set up the environment with the correct PYTHONPATH
    env = os.environ.copy()
    env['PYTHONPATH'] = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))  # Add project root to PYTHONPATH

    # Construct the command to run the script
    cmd = [os.environ.get('PYTHON', 'python'), cli_script, '--file', temp_file_name, '--min_support', '0.2']

    # Run the script using subprocess
    process = subprocess.run(cmd, text=True, capture_output=True, env=env)

    # Assert that the output contains the expected message
    assert process.returncode == 0
    assert "Frequent Patterns Found:" in process.stdout

    # Cleanup
    os.unlink(temp_file_name)


def test_main_edge_case_min_support(monkeypatch: MonkeyPatch):
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
    with patch("gsppy.cli.logger.info") as mock_info:
        main()
        mock_info.assert_any_call("Frequent Patterns Found:")

    # Case 2: `min_support` = -1.0 (Invalid Edge Case)
    monkeypatch.setattr(
        'sys.argv', ['main', '--file', temp_file_name, '--min_support', '-1.0']
    )
    with patch("gsppy.cli.logger.error") as mock_error:
        main()
        mock_error.assert_called_with("Error: min_support must be in the range (0.0, 1.0].")

    # Cleanup
    os.unlink(temp_file_name)


def test_main_gsp_exception(monkeypatch: MonkeyPatch):
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
    with patch('gsppy.gsp.GSP.search', side_effect=Exception("Simulated GSP failure")), \
        patch("gsppy.cli.logger.error") as mock_error:
        main()

        # Step 4: Assert the error message was logged
        mock_error.assert_called_with("Error executing GSP algorithm: Simulated GSP failure")

    # Step 5: Cleanup
    os.unlink(temp_file_name)


def test_setup_logging_verbose(monkeypatch: MonkeyPatch):
    """
    Test `setup_logging` sets logging level to DEBUG when `--verbose` is provided.
    """
    # Mock CLI arguments to include the verbose flag
    monkeypatch.setattr(
        'sys.argv', ['main', '--file', 'test_data.json', '--min_support', '0.2', '--verbose']
    )

    with patch('gsppy.cli.logger.setLevel') as mock_setLevel:
        with patch('gsppy.cli.detect_and_read_file', return_value=[["Bread", "Milk"]]):  # Mock file reading
            with patch('gsppy.cli.GSP.search', return_value=[{("Bread",): 1}]):  # Mock GSP search
                main()  # Run the CLI

        # Check that the logger level was set to DEBUG
        mock_setLevel.assert_called_with(logging.DEBUG)
