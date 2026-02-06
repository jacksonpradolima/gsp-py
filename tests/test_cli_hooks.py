"""
Example hook functions for testing CLI hook functionality.

These functions demonstrate how to create custom hooks for the GSP CLI.
"""

from typing import Any, Dict, Tuple


def simple_length_filter(candidate: Tuple[str, ...], support_count: int, context: Dict[str, Any]) -> bool:
    """Simple candidate filter that keeps patterns with length <= 2."""
    return len(candidate) <= 2


def high_support_filter(candidate: Tuple[str, ...], support_count: int, context: Dict[str, Any]) -> bool:
    """Filter that keeps candidates with high support (>= 3)."""
    return support_count >= 3


def postprocess_top_level(patterns: Any) -> Any:
    """Postprocess function that keeps only the first level of patterns."""
    return patterns[:1] if patterns else []


def postprocess_filter_support(patterns: Any) -> Any:
    """Postprocess function that filters patterns by support >= 2."""
    return [{k: v for k, v in level.items() if v >= 2} for level in patterns]


# Test cases for CLI hook loading
import json
import pytest
from click.testing import CliRunner
from gsppy.cli import main, _load_hook_function


class TestCLIHookLoading:
    """Tests for loading hook functions from import paths."""

    def test_load_hook_function_success(self) -> None:
        """Test successfully loading a hook function."""
        hook_fn = _load_hook_function("tests.test_cli_hooks.simple_length_filter", "candidate_filter")
        assert callable(hook_fn)
        # Test that it works
        result = hook_fn(("A", "B"), 5, {})
        assert result is True

    def test_load_hook_function_invalid_path(self) -> None:
        """Test loading with invalid import path."""
        with pytest.raises(ValueError, match="Invalid import path format"):
            _load_hook_function("invalid_path", "test")

    def test_load_hook_function_module_not_found(self) -> None:
        """Test loading from non-existent module."""
        with pytest.raises(ValueError, match="Failed to import"):
            _load_hook_function("nonexistent.module.function", "test")

    def test_load_hook_function_function_not_found(self) -> None:
        """Test loading non-existent function from valid module."""
        with pytest.raises(ValueError, match="not found"):
            _load_hook_function("tests.test_cli_hooks.nonexistent_function", "test")


class TestCLIHooksIntegration:
    """Integration tests for CLI with hooks."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.runner = CliRunner()
        # Create a temporary JSON file with test data
        self.test_data = [
            ["A", "B", "C"],
            ["A", "C", "D"],
            ["B", "C", "E"],
            ["A", "B", "C"],
            ["A", "C", "D"],
        ]

    def test_cli_with_candidate_filter(self) -> None:
        """Test CLI with candidate filter hook."""
        with self.runner.isolated_filesystem():
            # Write test data to file
            with open("test_data.json", "w") as f:
                json.dump(self.test_data, f)

            # Run CLI with candidate filter hook
            result = self.runner.invoke(
                main,
                [
                    "--file",
                    "test_data.json",
                    "--min_support",
                    "0.4",
                    "--candidate-filter-hook",
                    "tests.test_cli_hooks.simple_length_filter",
                ],
            )

            assert result.exit_code == 0, f"CLI failed with: {result.output}"
            assert "Frequent Patterns Found" in result.output

    def test_cli_with_postprocess_hook(self) -> None:
        """Test CLI with postprocess hook."""
        with self.runner.isolated_filesystem():
            # Write test data to file
            with open("test_data.json", "w") as f:
                json.dump(self.test_data, f)

            # Run CLI with postprocess hook
            result = self.runner.invoke(
                main,
                [
                    "--file",
                    "test_data.json",
                    "--min_support",
                    "0.4",
                    "--postprocess-hook",
                    "tests.test_cli_hooks.postprocess_top_level",
                ],
            )

            assert result.exit_code == 0, f"CLI failed with: {result.output}"
            assert "Frequent Patterns Found" in result.output
            # Should only have 1-Sequence Patterns
            assert "1-Sequence Patterns" in result.output
            # Should NOT have 2-Sequence Patterns (filtered by postprocess)
            assert "2-Sequence Patterns" not in result.output

    def test_cli_with_multiple_hooks(self) -> None:
        """Test CLI with multiple hooks combined."""
        with self.runner.isolated_filesystem():
            # Write test data to file
            with open("test_data.json", "w") as f:
                json.dump(self.test_data, f)

            # Run CLI with multiple hooks
            result = self.runner.invoke(
                main,
                [
                    "--file",
                    "test_data.json",
                    "--min_support",
                    "0.3",
                    "--candidate-filter-hook",
                    "tests.test_cli_hooks.simple_length_filter",
                    "--postprocess-hook",
                    "tests.test_cli_hooks.postprocess_filter_support",
                ],
            )

            assert result.exit_code == 0, f"CLI failed with: {result.output}"
            assert "Frequent Patterns Found" in result.output

    def test_cli_with_invalid_hook(self) -> None:
        """Test CLI with invalid hook import path."""
        with self.runner.isolated_filesystem():
            # Write test data to file
            with open("test_data.json", "w") as f:
                json.dump(self.test_data, f)

            # Run CLI with invalid hook
            result = self.runner.invoke(
                main,
                [
                    "--file",
                    "test_data.json",
                    "--min_support",
                    "0.4",
                    "--candidate-filter-hook",
                    "nonexistent.module.function",
                ],
            )

            assert result.exit_code != 0
            assert "Failed to import" in result.output or "Error" in result.output

    def test_cli_without_hooks(self) -> None:
        """Test that CLI works normally without hooks (backward compatibility)."""
        with self.runner.isolated_filesystem():
            # Write test data to file
            with open("test_data.json", "w") as f:
                json.dump(self.test_data, f)

            # Run CLI without hooks
            result = self.runner.invoke(
                main,
                [
                    "--file",
                    "test_data.json",
                    "--min_support",
                    "0.4",
                ],
            )

            assert result.exit_code == 0, f"CLI failed with: {result.output}"
            assert "Frequent Patterns Found" in result.output

