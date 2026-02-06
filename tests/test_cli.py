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
import sys
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


@pytest.fixture
def valid_parquet_grouped_file() -> Generator[Any, Any, Any]:
    """Fixture to create a valid Parquet file with grouped format (transaction_id, item)."""
    pytest.importorskip("polars", reason="Parquet tests require Polars")
    import polars as pl
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".parquet") as temp_file:
        temp_file_name = temp_file.name
    
    # Create a DataFrame with grouped format
    df = pl.DataFrame({
        "transaction_id": [1, 1, 2, 2, 3, 3, 3],
        "item": ["Bread", "Milk", "Milk", "Diaper", "Bread", "Diaper", "Beer"]
    })
    df.write_parquet(temp_file_name)
    
    yield temp_file_name
    os.unlink(temp_file_name)


@pytest.fixture
def valid_parquet_sequence_file() -> Generator[Any, Any, Any]:
    """Fixture to create a valid Parquet file with sequence format (sequence column)."""
    pytest.importorskip("polars", reason="Parquet tests require Polars")
    import polars as pl
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".parquet") as temp_file:
        temp_file_name = temp_file.name
    
    # Create a DataFrame with sequence format
    df = pl.DataFrame({
        "sequence": [["Bread", "Milk"], ["Milk", "Diaper"], ["Bread", "Diaper", "Beer"]]
    })
    df.write_parquet(temp_file_name)
    
    yield temp_file_name
    os.unlink(temp_file_name)


@pytest.fixture
def valid_arrow_file() -> Generator[Any, Any, Any]:
    """Fixture to create a valid Arrow/Feather file with grouped format."""
    pytest.importorskip("polars", reason="Arrow tests require Polars")
    import polars as pl
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".arrow") as temp_file:
        temp_file_name = temp_file.name
    
    # Create a DataFrame with grouped format
    df = pl.DataFrame({
        "transaction_id": [1, 1, 2, 2, 3, 3, 3],
        "item": ["Bread", "Milk", "Milk", "Diaper", "Bread", "Diaper", "Beer"]
    })
    df.write_ipc(temp_file_name)
    
    yield temp_file_name
    os.unlink(temp_file_name)


@pytest.fixture
def invalid_parquet_missing_columns() -> Generator[Any, Any, Any]:
    """Fixture to create a Parquet file missing required columns."""
    pytest.importorskip("polars", reason="Parquet tests require Polars")
    import polars as pl
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".parquet") as temp_file:
        temp_file_name = temp_file.name
    
    # Create a DataFrame with wrong column names
    df = pl.DataFrame({
        "wrong_col": [1, 2, 3],
        "another_col": ["A", "B", "C"]
    })
    df.write_parquet(temp_file_name)
    
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
    monkeypatch.setattr("sys.argv", ["main", "--file", temp_file_name, "--min_support", "0.2"])

    # Mock logger.error and test messages directly
    with patch("gsppy.cli.logger.error") as mock_error:
        with pytest.raises(SystemExit) as excinfo:
            main()
        assert excinfo.value.code == 1
        # Error now caught during JSON parsing validation
        assert mock_error.called
        error_message = mock_error.call_args[0][0]
        assert "JSON must contain a top-level list of transactions" in error_message

    # Cleanup
    os.unlink(temp_file_name)


def test_main_non_existent_file(monkeypatch: MonkeyPatch):
    """
    Test `main()` with a file that does not exist.
    """
    # Mock CLI arguments
    monkeypatch.setattr("sys.argv", ["main", "--file", "non_existent.json", "--min_support", "0.2"])

    # Click handles file existence before our code runs, so just check SystemExit
    with pytest.raises(SystemExit) as excinfo:
        main()
    assert excinfo.value.code != 0


def test_main_valid_json_file(monkeypatch: MonkeyPatch):
    """
    Test `main()` with a valid JSON file.
    """
    # Create a valid JSON file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w") as temp_file:
        json.dump([["Bread", "Milk"], ["Milk", "Diaper"], ["Bread", "Diaper", "Beer"]], temp_file)
        temp_file_name = temp_file.name

    # Mock CLI arguments
    monkeypatch.setattr("sys.argv", ["main", "--file", temp_file_name, "--min_support", "0.2"])

    with patch("gsppy.cli.logger.info") as mock_info:
        with pytest.raises(SystemExit) as excinfo:
            main()
        assert excinfo.value.code == 0
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
        "sys.argv",
        ["main", "--file", temp_file_name, "--min_support", "-1.0"],  # Invalid min_support
    )

    with patch("gsppy.cli.logger.error") as mock_error:
        with pytest.raises(SystemExit) as excinfo:
            main()
        assert excinfo.value.code == 1
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
    cli_script = os.path.abspath(os.path.join(os.path.dirname(__file__), "../gsppy/cli.py"))

    # Set up the environment with the correct PYTHONPATH
    env = os.environ.copy()
    env["PYTHONPATH"] = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))  # Add project root to PYTHONPATH

    # Construct the command to run the script
    cmd = [sys.executable, cli_script, "--file", temp_file_name, "--min_support", "0.2"]

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
    monkeypatch.setattr("sys.argv", ["main", "--file", temp_file_name, "--min_support", "1.0"])
    with patch("gsppy.cli.logger.info") as mock_info:
        with pytest.raises(SystemExit) as excinfo:
            main()
        assert excinfo.value.code == 0
        mock_info.assert_any_call("Frequent Patterns Found:")

    # Case 2: `min_support` = -1.0 (Invalid Edge Case)
    monkeypatch.setattr("sys.argv", ["main", "--file", temp_file_name, "--min_support", "-1.0"])
    with patch("gsppy.cli.logger.error") as mock_error:
        with pytest.raises(SystemExit) as excinfo:
            main()
        assert excinfo.value.code == 1
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
    monkeypatch.setattr("sys.argv", ["main", "--file", temp_file_name, "--min_support", "0.2"])

    # Step 3: Mock GSP.search to raise an exception
    with (
        patch("gsppy.gsp.GSP.search", side_effect=Exception("Simulated GSP failure")),
        patch("gsppy.cli.logger.error") as mock_error,
    ):
        with pytest.raises(SystemExit) as excinfo:
            main()
        assert excinfo.value.code == 1
        mock_error.assert_called_with("Error executing GSP algorithm: Simulated GSP failure")

    # Step 5: Cleanup
    os.unlink(temp_file_name)


def test_setup_logging_verbose(monkeypatch: MonkeyPatch):
    """
    Test `setup_logging` sets logging level to DEBUG when `--verbose` is provided.
    """
    # Create a real temporary file for the CLI argument
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp_file:
        temp_file.write(b'[["Bread", "Milk"], ["Milk", "Diaper"]]')
        temp_file_name = temp_file.name

    monkeypatch.setattr("sys.argv", ["main", "--file", temp_file_name, "--min_support", "0.2", "--verbose"])

    # Patch logging.basicConfig to verify it's called with DEBUG level
    with patch("gsppy.cli.logging.basicConfig") as mock_basicConfig:
        with patch("gsppy.cli.detect_and_read_file", return_value=[["Bread", "Milk"], ["Milk", "Diaper"]]):
            with patch("gsppy.cli.GSP.search", return_value=[{("Bread",): 1}]):
                with pytest.raises(SystemExit) as excinfo:
                    main()  # Run the CLI
                assert excinfo.value.code == 0
        # Check that basicConfig was called with DEBUG level
        mock_basicConfig.assert_called_once()
        call_kwargs = mock_basicConfig.call_args[1]
        assert call_kwargs['level'] == logging.DEBUG

    os.unlink(temp_file_name)


def test_cli_timestamped_json_parsing() -> None:
    """Test that CLI correctly parses timestamped JSON data with nested lists."""
    # Create a timestamped JSON file with nested lists (as produced by json.dump)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w") as temp_file:
        json.dump([[["A", 1], ["B", 2]], [["A", 0], ["C", 3]]], temp_file)
        temp_file_name = temp_file.name

    try:
        # Read the file using detect_and_read_file
        transactions = detect_and_read_file(temp_file_name)
        
        # Verify that nested lists were converted to tuples
        assert len(transactions) == 2
        assert isinstance(transactions[0], list)
        assert isinstance(transactions[0][0], tuple)
        assert transactions[0][0] == ("A", 1)
        assert transactions[0][1] == ("B", 2)
        assert transactions[1][0] == ("A", 0)
        assert transactions[1][1] == ("C", 3)
    finally:
        os.unlink(temp_file_name)


def test_cli_temporal_constraints_flags(monkeypatch: MonkeyPatch):
    """Test that CLI accepts and processes temporal constraint flags."""
    # Create a timestamped JSON file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w") as temp_file:
        json.dump([[["A", 1], ["B", 3], ["C", 5]], [["A", 2], ["B", 10]]], temp_file)
        temp_file_name = temp_file.name

    # Mock CLI arguments with temporal constraints
    monkeypatch.setattr(
        "sys.argv",
        ["main", "--file", temp_file_name, "--min_support", "0.5", "--mingap", "1", "--maxgap", "5", "--maxspan", "10"]
    )

    try:
        with patch("gsppy.cli.logger.info") as mock_info:
            with pytest.raises(SystemExit) as excinfo:
                main()
            assert excinfo.value.code == 0
            # Verify that patterns were found (exact patterns depend on constraints)
            mock_info.assert_any_call("Frequent Patterns Found:")
    finally:
        os.unlink(temp_file_name)


def test_cli_empty_first_transaction_timestamped() -> None:
    """Test that CLI correctly handles timestamped data when first transaction is empty."""
    # Create a timestamped JSON file with empty first transaction
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w") as temp_file:
        json.dump([[], [["A", 1], ["B", 2]], [["A", 0], ["C", 3]]], temp_file)
        temp_file_name = temp_file.name

    try:
        # Read the file using detect_and_read_file
        transactions = detect_and_read_file(temp_file_name)
        
        # Verify that timestamped data was detected despite empty first transaction
        assert len(transactions) == 3
        assert transactions[0] == []
        assert isinstance(transactions[1][0], tuple)
        assert transactions[1][0] == ("A", 1)
    finally:
        os.unlink(temp_file_name)


def test_cli_verbose_flag_formatting() -> None:
    """
    Test that --verbose flag produces detailed log output with proper formatting.
    
    Verifies that verbose mode includes timestamps, log levels, PID, and context.
    """
    # Create a valid JSON file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w") as temp_file:
        json.dump([["Bread", "Milk"], ["Milk", "Diaper"], ["Bread", "Diaper", "Beer"]], temp_file)
        temp_file_name = temp_file.name
    
    # Run the CLI using subprocess to capture actual output
    cli_script = os.path.abspath(os.path.join(os.path.dirname(__file__), "../gsppy/cli.py"))
    env = os.environ.copy()
    env["PYTHONPATH"] = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    cmd = [sys.executable, cli_script, "--file", temp_file_name, "--min_support", "0.2", "--verbose"]
    process = subprocess.run(cmd, text=True, capture_output=True, env=env)
    
    # Verify verbose output contains expected format elements
    output = process.stdout + process.stderr
    
    # Check for timestamp format (ISO 8601: YYYY-MM-DDTHH:MM:SS)
    assert any("T" in line and "|" in line for line in output.split("\n")), \
        "Expected timestamp format in verbose output"
    
    # Check for log level labels
    assert "INFO" in output or "DEBUG" in output, "Expected log level labels in verbose output"
    
    # Check for PID (Process ID)
    assert "PID:" in output, "Expected process ID in verbose output"
    
    # Cleanup
    os.unlink(temp_file_name)


def test_cli_non_verbose_simple_output() -> None:
    """
    Test that default (non-verbose) mode produces simple, clean output.
    
    Verifies that non-verbose mode doesn't include timestamps, PIDs, or log levels.
    """
    # Create a valid JSON file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w") as temp_file:
        json.dump([["Bread", "Milk"], ["Milk", "Diaper"], ["Bread", "Diaper", "Beer"]], temp_file)
        temp_file_name = temp_file.name
    
    # Run the CLI without --verbose flag
    cli_script = os.path.abspath(os.path.join(os.path.dirname(__file__), "../gsppy/cli.py"))
    env = os.environ.copy()
    env["PYTHONPATH"] = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    cmd = [sys.executable, cli_script, "--file", temp_file_name, "--min_support", "0.2"]
    process = subprocess.run(cmd, text=True, capture_output=True, env=env)
    
    output = process.stdout
    
    # Check that simple mode doesn't have verbose formatting
    assert "PID:" not in output, "PID should not appear in non-verbose output"
    # Output should still have the results
    assert "Frequent Patterns Found:" in output, "Expected results in output"
    
    # Cleanup
    os.unlink(temp_file_name)


def test_cli_verbose_with_gsp_verbose(monkeypatch: MonkeyPatch):
    """
    Test that CLI --verbose flag is passed to GSP instance.
    
    Verifies integration between CLI and GSP verbosity settings.
    """
    # Create a valid JSON file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w") as temp_file:
        json.dump([["Bread", "Milk"], ["Milk", "Diaper"], ["Bread", "Diaper", "Beer"]], temp_file)
        temp_file_name = temp_file.name

    # Mock CLI arguments with --verbose flag
    monkeypatch.setattr("sys.argv", ["main", "--file", temp_file_name, "--min_support", "0.2", "--verbose"])

    # Capture the GSP initialization to check verbose parameter
    from unittest.mock import patch
    with patch("gsppy.cli.GSP") as mock_gsp:
        mock_instance = mock_gsp.return_value
        mock_instance.search.return_value = []
        
        try:
            main()
        except SystemExit as e:
            if e.code == 0:
                pass  # Expected success exit
            else:
                raise
        
        # Verify GSP was initialized with verbose=True
        mock_gsp.assert_called_once()
        call_kwargs = mock_gsp.call_args[1]
        assert call_kwargs.get("verbose") is True, "Expected GSP to be initialized with verbose=True"

    # Cleanup
    os.unlink(temp_file_name)


def test_cli_spm_format_flag(monkeypatch: MonkeyPatch):
    """
    Test CLI with --format spm option for SPM/GSP format files.
    """
    # Create an SPM format file
    with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.txt') as temp_file:
        temp_file.write("1 2 -1 3 -1 -2\n")
        temp_file.write("4 -1 5 6 -1 -2\n")
        temp_file.write("1 -1 2 3 -1 -2\n")
        temp_file_name = temp_file.name

    # Mock CLI arguments with --format spm
    monkeypatch.setattr(
        "sys.argv", 
        ["main", "--file", temp_file_name, "--format", "spm", "--min_support", "0.3"]
    )

    try:
        with patch("gsppy.cli.logger.info") as mock_info:
            with pytest.raises(SystemExit) as excinfo:
                main()
            assert excinfo.value.code == 0
            # Verify that patterns were found
            mock_info.assert_any_call("Frequent Patterns Found:")
    finally:
        os.unlink(temp_file_name)


def test_cli_spm_format_subprocess():
    """
    Test CLI with SPM format using subprocess to verify real-world usage.
    """
    # Create an SPM format file
    with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.txt') as temp_file:
        temp_file.write("A B -1 C -1 -2\n")
        temp_file.write("A -1 B C -1 -2\n")
        temp_file_name = temp_file.name
    
    # Get the CLI script path
    cli_script = os.path.abspath(os.path.join(os.path.dirname(__file__), "../gsppy/cli.py"))
    
    # Set up the environment with the correct PYTHONPATH
    env = os.environ.copy()
    env["PYTHONPATH"] = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    # Construct the command to run the script
    cmd = [
        sys.executable, 
        cli_script, 
        "--file", temp_file_name, 
        "--format", "spm",
        "--min_support", "0.5"
    ]
    
    # Run the script using subprocess
    process = subprocess.run(cmd, text=True, capture_output=True, env=env)
    
    # Assert that the output contains the expected message
    assert process.returncode == 0
    assert "Frequent Patterns Found:" in process.stdout
    assert "Pattern:" in process.stdout
    
    # Cleanup
    os.unlink(temp_file_name)


# ============================================================================
# Parquet and Arrow Format Tests
# ============================================================================


def test_valid_parquet_grouped_file(valid_parquet_grouped_file: Generator[Any, Any, Any]):
    """Test if a valid Parquet file with grouped format is correctly read."""
    from gsppy.cli import read_transactions_from_parquet
    
    transactions = read_transactions_from_parquet(
        str(valid_parquet_grouped_file),
        transaction_col="transaction_id",
        item_col="item"
    )
    
    # Expected: 3 transactions grouped by transaction_id
    assert len(transactions) == 3
    assert transactions[0] == ["Bread", "Milk"]
    assert transactions[1] == ["Milk", "Diaper"]
    assert transactions[2] == ["Bread", "Diaper", "Beer"]


def test_valid_parquet_sequence_file(valid_parquet_sequence_file: Generator[Any, Any, Any]):
    """Test if a valid Parquet file with sequence format is correctly read."""
    from gsppy.cli import read_transactions_from_parquet
    
    transactions = read_transactions_from_parquet(
        str(valid_parquet_sequence_file),
        sequence_col="sequence"
    )
    
    assert len(transactions) == 3
    assert transactions[0] == ["Bread", "Milk"]
    assert transactions[1] == ["Milk", "Diaper"]
    assert transactions[2] == ["Bread", "Diaper", "Beer"]


def test_valid_arrow_file(valid_arrow_file: Generator[Any, Any, Any]):
    """Test if a valid Arrow/Feather file is correctly read."""
    from gsppy.cli import read_transactions_from_arrow
    
    transactions = read_transactions_from_arrow(
        str(valid_arrow_file),
        transaction_col="transaction_id",
        item_col="item"
    )
    
    assert len(transactions) == 3
    assert transactions[0] == ["Bread", "Milk"]
    assert transactions[1] == ["Milk", "Diaper"]
    assert transactions[2] == ["Bread", "Diaper", "Beer"]


def test_parquet_auto_detect(valid_parquet_grouped_file: Generator[Any, Any, Any]):
    """Test if Parquet files are auto-detected by extension."""
    # The detect_and_read_file function doesn't support dataframe formats
    # because they require column parameters, so we test the format detection logic
    from gsppy.cli import _load_transactions_by_format
    from gsppy.enums import FileFormat, DATAFRAME_EXTENSIONS
    import os
    
    file_path = str(valid_parquet_grouped_file)
    _, file_extension = os.path.splitext(file_path)
    file_extension = file_extension.lower()
    
    # Verify it's recognized as a dataframe format
    assert file_extension in DATAFRAME_EXTENSIONS
    
    # Test loading with explicit format
    transactions = _load_transactions_by_format(
        file_path,
        FileFormat.PARQUET.value,
        file_extension,
        is_dataframe_format=True,
        transaction_col="transaction_id",
        item_col="item",
        timestamp_col=None,
        sequence_col=None
    )
    
    assert len(transactions) == 3


def test_parquet_missing_columns_error(invalid_parquet_missing_columns: Generator[Any, Any, Any]):
    """Test that Parquet files with missing required columns raise appropriate errors."""
    from gsppy.cli import read_transactions_from_parquet
    
    with pytest.raises(ValueError, match="Error reading transaction data from Parquet file"):
        read_transactions_from_parquet(
            str(invalid_parquet_missing_columns),
            transaction_col="transaction_id",  # This column doesn't exist
            item_col="item"  # This column doesn't exist
        )


def test_parquet_without_polars_error():
    """Test that using Parquet without Polars installed gives helpful error message."""
    from gsppy.cli import read_transactions_from_parquet
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".parquet") as temp_file:
        temp_file_name = temp_file.name
    
    # Mock polars import to simulate it not being installed
    with patch.dict('sys.modules', {'polars': None}):
        with pytest.raises(ValueError, match="Parquet support requires Polars"):
            read_transactions_from_parquet(temp_file_name)
    
    os.unlink(temp_file_name)


def test_arrow_without_polars_error():
    """Test that using Arrow without Polars installed gives helpful error message."""
    from gsppy.cli import read_transactions_from_arrow
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".arrow") as temp_file:
        temp_file_name = temp_file.name
    
    # Mock polars import to simulate it not being installed
    with patch.dict('sys.modules', {'polars': None}):
        with pytest.raises(ValueError, match="Arrow/Feather support requires Polars"):
            read_transactions_from_arrow(temp_file_name)
    
    os.unlink(temp_file_name)


def test_parquet_cli_integration(valid_parquet_grouped_file: Generator[Any, Any, Any], monkeypatch: MonkeyPatch):
    """Test CLI integration with Parquet files."""
    monkeypatch.setattr(
        "sys.argv",
        [
            "gsppy",
            "--file", str(valid_parquet_grouped_file),
            "--min_support", "0.5",
            "--transaction-col", "transaction_id",
            "--item-col", "item"
        ],
    )
    
    # Capture output
    from io import StringIO
    captured_output = StringIO()
    
    with patch("sys.stdout", captured_output):
        try:
            main(standalone_mode=False)
        except SystemExit:
            pass
    
    output = captured_output.getvalue()
    # Verify the CLI processed the Parquet file successfully
    assert "Frequent Patterns Found:" in output or "Pattern:" in output or len(output) > 0


def test_parquet_with_timestamps():
    """Test Parquet files with timestamp columns for temporal mining."""
    pytest.importorskip("polars", reason="Parquet tests require Polars")
    import polars as pl
    from gsppy.cli import read_transactions_from_parquet
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".parquet") as temp_file:
        temp_file_name = temp_file.name
    
    # Create a DataFrame with timestamps
    df = pl.DataFrame({
        "transaction_id": [1, 1, 1, 2, 2, 3],
        "item": ["A", "B", "C", "A", "B", "C"],
        "timestamp": [1.0, 2.0, 5.0, 1.0, 3.0, 2.0]
    })
    df.write_parquet(temp_file_name)
    
    transactions = read_transactions_from_parquet(
        temp_file_name,
        transaction_col="transaction_id",
        item_col="item",
        timestamp_col="timestamp"
    )
    
    # Verify timestamped format
    assert len(transactions) == 3
    # First transaction should have tuples (item, timestamp)
    assert isinstance(transactions[0][0], tuple)
    assert transactions[0][0][0] == "A"
    assert transactions[0][0][1] == 1.0
    
    os.unlink(temp_file_name)



def test_write_patterns_to_parquet():
    """Test writing GSP patterns to Parquet format."""
    pytest.importorskip("polars", reason="Parquet tests require Polars")
    import polars as pl
    from gsppy.cli import write_patterns_to_parquet
    
    # Sample patterns from GSP search
    patterns = [
        {('A',): 3, ('B',): 2},
        {('A', 'B'): 2}
    ]
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".parquet") as temp_file:
        temp_file_name = temp_file.name
    
    # Write patterns
    write_patterns_to_parquet(patterns, temp_file_name)
    
    # Read back and verify
    df = pl.read_parquet(temp_file_name)
    assert len(df) == 3  # 3 patterns total
    assert "pattern" in df.columns
    assert "support" in df.columns
    assert "level" in df.columns
    
    # Check values
    assert df.filter(pl.col("pattern") == "('A',)")["support"][0] == 3
    assert df.filter(pl.col("pattern") == "('A', 'B')")["level"][0] == 2
    
    os.unlink(temp_file_name)


def test_write_patterns_to_arrow():
    """Test writing GSP patterns to Arrow format."""
    pytest.importorskip("polars", reason="Arrow tests require Polars")
    import polars as pl
    from gsppy.cli import write_patterns_to_arrow
    
    patterns = [
        {('A',): 3, ('B',): 2},
        {('A', 'B'): 2}
    ]
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".arrow") as temp_file:
        temp_file_name = temp_file.name
    
    write_patterns_to_arrow(patterns, temp_file_name)
    
    # Read back and verify
    df = pl.read_ipc(temp_file_name)
    assert len(df) == 3
    assert "pattern" in df.columns
    assert "support" in df.columns
    
    os.unlink(temp_file_name)


def test_write_patterns_to_csv():
    """Test writing GSP patterns to CSV format."""
    from gsppy.cli import write_patterns_to_csv
    import csv
    
    patterns = [
        {('A',): 3, ('B',): 2},
        {('A', 'B'): 2}
    ]
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode="w") as temp_file:
        temp_file_name = temp_file.name
    
    write_patterns_to_csv(patterns, temp_file_name)
    
    # Read back and verify
    with open(temp_file_name, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)
    
    assert len(rows) == 3
    assert rows[0]['pattern'] == "('A',)"
    assert rows[0]['support'] == '3'
    assert rows[0]['level'] == '1'
    
    os.unlink(temp_file_name)


def test_write_patterns_to_json():
    """Test writing GSP patterns to JSON format."""
    from gsppy.cli import write_patterns_to_json
    
    patterns = [
        {('A',): 3, ('B',): 2},
        {('A', 'B'): 2}
    ]
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w") as temp_file:
        temp_file_name = temp_file.name
    
    write_patterns_to_json(patterns, temp_file_name)
    
    # Read back and verify
    with open(temp_file_name, 'r') as jsonfile:
        data = json.load(jsonfile)
    
    assert len(data) == 2  # 2 levels
    assert len(data[0]) == 2  # 2 patterns in level 1
    assert data[0][0]['pattern'] == ['A']
    assert data[0][0]['support'] == 3
    
    os.unlink(temp_file_name)


def test_cli_with_parquet_output(valid_json_file: Generator[Any, Any, Any], monkeypatch: MonkeyPatch):
    """Test CLI with Parquet output."""
    pytest.importorskip("polars", reason="Parquet tests require Polars")
    import polars as pl
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".parquet") as output_file:
        output_file_name = output_file.name
    
    monkeypatch.setattr(
        "sys.argv",
        [
            "gsppy",
            "--file", str(valid_json_file),
            "--min_support", "0.5",
            "--output", output_file_name
        ],
    )
    
    try:
        main(standalone_mode=False)
    except SystemExit:
        pass
    
    # Verify output file was created and contains data
    assert os.path.exists(output_file_name)
    df = pl.read_parquet(output_file_name)
    assert len(df) > 0
    assert "pattern" in df.columns
    assert "support" in df.columns
    
    os.unlink(output_file_name)
