"""
CLI-based fuzzing tests for GSP algorithm.

This module provides property-based tests that exercise the CLI interface
with various inputs, testing end-to-end behavior including file parsing,
validation, and output generation.

Test Categories:
1. CLI Input Validation - Invalid arguments, missing files, bad formats
2. File Format Tests - JSON and CSV parsing with various edge cases
3. CLI Output Validation - Verify correct pattern output format
4. Integration Tests - End-to-end CLI workflow testing

Author: Jackson Antonio do Prado Lima
Email: jacksonpradolima@gmail.com
"""

import json
import tempfile
from typing import List
from pathlib import Path

from hypothesis import HealthCheck, given, settings, strategies as st
from click.testing import CliRunner

from gsppy.cli import main
from tests.hypothesis_strategies import transaction_lists, extreme_transaction_lists

# ============================================================================
# Helper Functions
# ============================================================================


def create_json_file(transactions: List[List[str]], file_path: Path) -> None:
    """Create a JSON file with transaction data."""
    with open(file_path, "w") as f:
        json.dump(transactions, f)


def create_csv_file(transactions: List[List[str]], file_path: Path) -> None:
    """Create a CSV file with transaction data."""
    with open(file_path, "w") as f:
        for transaction in transactions:
            f.write(",".join(transaction) + "\n")


# ============================================================================
# CLI Input Validation Tests
# ============================================================================


def test_cli_missing_file() -> None:
    """Test CLI with non-existent file."""
    runner = CliRunner()
    result = runner.invoke(main, ["--file", "/nonexistent/file.json", "--min_support", "0.5"])

    # Should fail with error
    assert result.exit_code != 0
    assert "does not exist" in result.output.lower() or "not found" in result.output.lower()


@given(support=st.floats(min_value=-1.0, max_value=-0.01))
@settings(max_examples=3, deadline=None)
def test_cli_invalid_negative_support(support: float) -> None:
    """Test CLI with negative support values."""
    runner = CliRunner()

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump([["A", "B"], ["A", "C"]], f)
        temp_path = f.name

    try:
        result = runner.invoke(main, ["--file", temp_path, "--min_support", str(support)])

        # Should fail with validation error
        assert result.exit_code != 0
        assert "support" in result.output.lower()
    finally:
        Path(temp_path).unlink(missing_ok=True)


@given(support=st.floats(min_value=1.01, max_value=10.0))
@settings(max_examples=3, deadline=None)
def test_cli_invalid_high_support(support: float) -> None:
    """Test CLI with support values > 1.0."""
    runner = CliRunner()

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump([["A", "B"], ["A", "C"]], f)
        temp_path = f.name

    try:
        result = runner.invoke(main, ["--file", temp_path, "--min_support", str(support)])

        # Should fail with validation error
        assert result.exit_code != 0
        assert "support" in result.output.lower()
    finally:
        Path(temp_path).unlink(missing_ok=True)


# ============================================================================
# JSON File Format Tests
# ============================================================================


@given(transactions=transaction_lists(min_transactions=2, max_transactions=20))  # type: ignore[missing-argument]
@settings(max_examples=3, deadline=None, suppress_health_check=[HealthCheck.too_slow])
def test_cli_json_format(transactions: List[List[str]]) -> None:
    """
    Property: CLI should correctly parse valid JSON transaction files.

    Tests that the CLI can read JSON files with various transaction structures
    and produce valid output.
    """
    runner = CliRunner()

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(transactions, f)
        temp_path = f.name

    try:
        result = runner.invoke(main, ["--file", temp_path, "--min_support", "0.3"])

        # Should succeed
        assert result.exit_code == 0, f"CLI failed with: {result.output}"

        # Output should contain pattern information
        # (either patterns found or message about no patterns)
        assert len(result.output) > 0
    finally:
        Path(temp_path).unlink(missing_ok=True)


def test_cli_json_malformed() -> None:
    """Test CLI with malformed JSON file."""
    runner = CliRunner()

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write('{"invalid": json syntax')
        temp_path = f.name

    try:
        result = runner.invoke(main, ["--file", temp_path, "--min_support", "0.5"])

        # Should fail with JSON parse error
        assert result.exit_code != 0
        assert "json" in result.output.lower() or "parse" in result.output.lower()
    finally:
        Path(temp_path).unlink(missing_ok=True)


def test_cli_json_wrong_structure() -> None:
    """Test CLI with JSON that doesn't contain transaction list."""
    runner = CliRunner()

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump({"not": "a transaction list"}, f)
        temp_path = f.name

    try:
        result = runner.invoke(main, ["--file", temp_path, "--min_support", "0.5"])

        # Should fail with structure error
        assert result.exit_code != 0
    finally:
        Path(temp_path).unlink(missing_ok=True)


# ============================================================================
# CSV File Format Tests
# ============================================================================


@given(transactions=transaction_lists(min_transactions=2, max_transactions=20))  # type: ignore[missing-argument]
@settings(max_examples=3, deadline=None, suppress_health_check=[HealthCheck.too_slow])
def test_cli_csv_format(transactions: List[List[str]]) -> None:
    """
    Property: CLI should correctly parse valid CSV transaction files.

    Tests that the CLI can read CSV files with various transaction structures.
    """
    runner = CliRunner()

    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        for transaction in transactions:
            # Only write non-empty transactions with valid items
            if transaction:
                valid_items = [item for item in transaction if item and "," not in item]
                if valid_items:
                    f.write(",".join(valid_items) + "\n")
        temp_path = f.name

    try:
        result = runner.invoke(main, ["--file", temp_path, "--min_support", "0.3"])

        # Should succeed or fail gracefully
        # (may fail if filtered transactions become invalid, which is acceptable)
        if result.exit_code != 0:
            # If it fails, should be due to data validation, not crash
            assert "error" in result.output.lower() or "invalid" in result.output.lower()
        else:
            # If succeeds, should have output
            assert len(result.output) > 0
    finally:
        Path(temp_path).unlink(missing_ok=True)


def test_cli_empty_csv() -> None:
    """Test CLI with empty CSV file."""
    runner = CliRunner()

    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        # Write nothing
        temp_path = f.name

    try:
        result = runner.invoke(main, ["--file", temp_path, "--min_support", "0.5"])

        # Should fail with empty data error
        assert result.exit_code != 0
        assert "empty" in result.output.lower()
    finally:
        Path(temp_path).unlink(missing_ok=True)


# ============================================================================
# CLI Output Validation Tests
# ============================================================================


def test_cli_output_structure() -> None:
    """Test that CLI produces properly structured output."""
    runner = CliRunner()

    # Simple test data with known patterns
    transactions = [["A", "B", "C"], ["A", "B", "D"], ["A", "C", "D"], ["A", "B", "C", "D"]]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(transactions, f)
        temp_path = f.name

    try:
        result = runner.invoke(main, ["--file", temp_path, "--min_support", "0.5"])

        # Should succeed
        assert result.exit_code == 0

        # Output should contain pattern information
        output = result.output.lower()

        # Should mention patterns or sequences
        assert "pattern" in output or "sequence" in output or "support" in output
    finally:
        Path(temp_path).unlink(missing_ok=True)


@given(
    transactions=transaction_lists(min_transactions=5, max_transactions=15),  # type: ignore[missing-argument]
    support=st.floats(min_value=0.1, max_value=0.9),
)
@settings(max_examples=3, deadline=None, suppress_health_check=[HealthCheck.too_slow])
def test_cli_varying_support_output(transactions: List[List[str]], support: float) -> None:
    """
    Property: CLI should produce valid output for various support values.

    Tests that different support thresholds produce appropriate results.
    """
    runner = CliRunner()

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(transactions, f)
        temp_path = f.name

    try:
        result = runner.invoke(main, ["--file", temp_path, "--min_support", str(support)])

        # Should succeed
        assert result.exit_code == 0, f"CLI failed: {result.output}"

        # Output should be present
        assert len(result.output) > 0
    finally:
        Path(temp_path).unlink(missing_ok=True)


# ============================================================================
# Integration Tests
# ============================================================================


@given(transactions=extreme_transaction_lists(size_type="minimal"))  # type: ignore[missing-argument]
@settings(max_examples=3, deadline=None)
def test_cli_minimal_valid_input(transactions: List[List[str]]) -> None:
    """
    Property: CLI should handle minimal valid inputs.

    Tests with the smallest valid transaction sets (2 transactions).
    """
    runner = CliRunner()

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(transactions, f)
        temp_path = f.name

    try:
        result = runner.invoke(main, ["--file", temp_path, "--min_support", "0.5"])

        # Should succeed with minimal input
        assert result.exit_code == 0
        assert len(result.output) > 0
    finally:
        Path(temp_path).unlink(missing_ok=True)


def test_cli_help() -> None:
    """Test that CLI help command works."""
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])

    # Should succeed
    assert result.exit_code == 0

    # Should contain usage information
    output = result.output.lower()
    assert "usage" in output or "options" in output
    assert "file" in output
    assert "min_support" in output or "support" in output


def test_cli_single_transaction_error() -> None:
    """Test CLI with single transaction (should fail)."""
    runner = CliRunner()

    transactions = [["A", "B", "C"]]  # Only one transaction

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(transactions, f)
        temp_path = f.name

    try:
        result = runner.invoke(main, ["--file", temp_path, "--min_support", "0.5"])

        # Should fail with multiple transactions error
        assert result.exit_code != 0
        assert "multiple" in result.output.lower() or "transaction" in result.output.lower()
    finally:
        Path(temp_path).unlink(missing_ok=True)


# ============================================================================
# Stress Tests
# ============================================================================


@given(transactions=extreme_transaction_lists(size_type="many"))  # type: ignore[missing-argument]
@settings(max_examples=2, deadline=None, suppress_health_check=[HealthCheck.too_slow])
def test_cli_stress_many_transactions(transactions: List[List[str]]) -> None:
    """
    Stress test: CLI should handle large transaction files.

    Tests with 100+ transactions to verify CLI scalability.
    """
    runner = CliRunner()

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(transactions, f)
        temp_path = f.name

    try:
        result = runner.invoke(main, ["--file", temp_path, "--min_support", "0.1"])

        # Should complete (though may be slow)
        assert result.exit_code == 0, f"CLI failed: {result.output}"
    finally:
        Path(temp_path).unlink(missing_ok=True)


def test_cli_unsupported_format() -> None:
    """Test CLI with unsupported file format."""
    runner = CliRunner()

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("A,B,C\n")
        temp_path = f.name

    try:
        result = runner.invoke(main, ["--file", temp_path, "--min_support", "0.5"])

        # Should fail with format error
        assert result.exit_code != 0
        assert "format" in result.output.lower() or "extension" in result.output.lower()
    finally:
        Path(temp_path).unlink(missing_ok=True)
