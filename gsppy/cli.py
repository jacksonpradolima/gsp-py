"""
This module implements a command-line interface (CLI) for running the Generalized Sequential Pattern (GSP) algorithm
on transactional data. It allows users to input transactional datasets in either JSON or CSV formats
and discover frequent sequential patterns based on a user-defined minimum support threshold.

Key Features:
1. Input Handling:
   - Supports transactional data in JSON and CSV formats.
   - Auto-detection of file type and parsing of transactions.
   - Error handling for unsupported file formats, non-existent files, and invalid data structures.

2. GSP Algorithm Integration:
   - Processes the parsed transactions using the GSP algorithm.
   - Accepts a configurable `min_support` threshold to determine the frequency of patterns.

3. User-Friendly CLI Interface:
   - `--file`: Specifies the path to the input file (JSON or CSV).
   - `--min_support`: Defines the minimum support threshold (default: 0.2).

4. Error Reporting:
   - Provides user-friendly messages for issues such as invalid input files, unsupported formats,
     and improper algorithm parameters.

5. Result Presentation:
   - Displays the discovered frequent patterns and their corresponding support counts.

This CLI empowers users to perform sequential pattern mining on transactional data efficiently through
a simple command-line interface.
"""

from __future__ import annotations

import os
import csv
import sys
import json
import logging
import importlib
from typing import Any, List, Tuple, Union, Callable, Optional, cast

import click

from gsppy.gsp import GSP
from gsppy.enums import (
    ARROW_EXTENSIONS,
    PARQUET_EXTENSIONS,
    DATAFRAME_EXTENSIONS,
    SUPPORTED_EXTENSIONS_MESSAGE,
    FileFormat,
    FileExtension,
)
from gsppy.utils import has_timestamps


def _load_hook_function(import_path: str, hook_type: str) -> Callable[..., Any]:
    """
    Load a hook function from a Python module import path.

    Parameters:
        import_path (str): Import path in format 'module.submodule.function_name'
        hook_type (str): Type of hook for error messages ('preprocess', 'postprocess', 'candidate_filter')

    Returns:
        Callable: The loaded hook function

    Raises:
        ValueError: If the import path is invalid or function cannot be loaded
    """
    try:
        # Split into module path and function name
        parts = import_path.rsplit(".", 1)
        if len(parts) != 2:
            raise ValueError(f"Invalid import path format. Expected 'module.function', got '{import_path}'")

        module_name, function_name = parts

        # Import the module
        module = importlib.import_module(module_name)

        # Get the function from the module
        if not hasattr(module, function_name):
            raise ValueError(f"Function '{function_name}' not found in module '{module_name}'")

        hook_fn = getattr(module, function_name)

        # Verify it's callable
        if not callable(hook_fn):
            raise ValueError(f"'{import_path}' is not a callable function")

        return hook_fn

    except ImportError as e:
        # Extract module name from import path for error message
        module_part = import_path.rsplit(".", 1)[0] if "." in import_path else import_path
        raise ValueError(f"Failed to import {hook_type} hook module '{module_part}': {e}") from e
    except ValueError:
        # Re-raise ValueError as-is
        raise
    except Exception as e:
        raise ValueError(f"Failed to load {hook_type} hook function '{import_path}': {e}") from e


def setup_logging(verbose: bool) -> None:
    """
    Configure logging with standardized format based on verbosity level.

    When verbose is enabled, provides detailed structured logging with:
    - Timestamps (ISO 8601 format)
    - Log levels
    - Process ID for traceability
    - Module context

    When verbose is disabled, uses simple format with just the message.

    Parameters:
        verbose: Whether to enable verbose logging with detailed formatting.
    """
    # Remove any existing handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    if verbose:
        # Detailed format with timestamps, levels, PID, and context for verbose mode
        log_format = "%(asctime)s | %(levelname)-8s | PID:%(process)d | %(name)s | %(message)s"
        date_format = "%Y-%m-%dT%H:%M:%S"
        log_level = logging.DEBUG
    else:
        # Simple format for default mode - just the message
        log_format = "%(message)s"
        date_format = None
        log_level = logging.INFO

    # Configure logging with the appropriate format
    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt=date_format,
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,  # Force reconfiguration even if already configured
    )


logger: logging.Logger = logging.getLogger(__name__)


def read_transactions_from_json(file_path: str) -> Union[List[List[str]], List[List[Tuple[str, float]]]]:
    """
    Read transactions from a JSON file.

    Supports both simple transactions and timestamped transactions:
    - Simple: [["A", "B", "C"], ["D", "E"]]
    - Timestamped: [[["A", 1], ["B", 3]], [["D", 2], ["E", 5]]]
      where the first element is the item and the second element is the timestamp

    Parameters:
        file_path (str): Path to the file containing transactions.

    Returns:
        Union[List[List[str]], List[List[Tuple[str, float]]]]:
            Parsed transactions from the file. For timestamped data,
            inner lists are converted to tuples (item, timestamp).

    Raises:
        ValueError: If the file cannot be read or does not contain valid JSON.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            raw_data: Any = json.load(f)

        if not isinstance(raw_data, list):
            raise ValueError("JSON must contain a top-level list of transactions.")

        raw_transactions: List[List[Union[str, Tuple[str, float]]]] = cast(
            List[List[Union[str, Tuple[str, float]]]], raw_data
        )

        # Check if this is timestamped data using the helper function.
        # Use defensive checks to avoid errors on malformed data:
        # - Find the first non-empty transaction instead of assuming index 0 is non-empty.
        # - Normalize inner list pairs (from json.load) to tuples before calling has_timestamps.
        first_non_empty_transaction: Optional[List[Union[str, Tuple[str, float]]]] = next(
            (transaction for transaction in raw_transactions if transaction),
            None,
        )

        is_timestamped = False
        if first_non_empty_transaction is not None:
            # Normalize to the exact input type expected by has_timestamps
            normalized_first: List[Union[str, Tuple[str, float]]] = []
            for item in first_non_empty_transaction:
                if isinstance(item, list) and len(item) == 2:
                    normalized_first.append((str(item[0]), float(item[1])))
                elif isinstance(item, tuple):
                    normalized_first.append(cast(Tuple[str, float], item))
                else:
                    normalized_first.append(str(item))

            is_timestamped = has_timestamps(normalized_first)

        if is_timestamped:
            # Convert timestamped data: [[["A", 1], ["B", 2]]] -> [[("A", 1), ("B", 2)]]
            transactions: List[List[Tuple[str, float]]] = [
                [cast(Tuple[str, float], tuple(item) if isinstance(item, list) else item) for item in transaction]
                for transaction in raw_transactions
            ]
            return transactions

        # Simple transactions remain as-is (or invalid data passed through for GSP to validate)
        simple_transactions: List[List[str]] = [[str(item) for item in transaction] for transaction in raw_transactions]
        return simple_transactions
    except Exception as e:
        msg = f"Error reading transaction data from JSON file '{file_path}': {e}"
        logging.error(msg)
        raise ValueError(msg) from e


def read_transactions_from_csv(file_path: str) -> List[List[str]]:
    """
    Read transactions from a CSV file.

    Parameters:
        file_path (str): Path to the file containing transactions.

    Returns:
        List[List]: Parsed transactions from the file.

    Raises:
        ValueError: If the file cannot be read or contains invalid data.
    """
    try:
        transactions: List[List[str]] = []
        with open(file_path, newline="", encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                # Check if the row is empty
                if not row or all(not item.strip() for item in row):
                    raise ValueError("Empty or invalid rows are not allowed in the CSV.")
                # Process valid rows
                transactions.append([item.strip() for item in row if item.strip()])
        return transactions
    except Exception as e:
        msg = f"Error reading transaction data from CSV file '{file_path}': {e}"
        logging.error(msg)
        raise ValueError(msg) from e


def read_transactions_from_spm(file_path: str) -> List[List[str]]:
    """
    Read transactions from an SPM/GSP format file.

    The SPM/GSP format uses delimiters:
    - `-1`: End of element (item set)
    - `-2`: End of sequence (transaction)

    Parameters:
        file_path (str): Path to the file containing transactions.

    Returns:
        List[List[str]]: Parsed transactions from the file.

    Raises:
        ValueError: If the file cannot be read or contains invalid data.
    """
    try:
        from gsppy.utils import read_transactions_from_spm as read_spm

        return cast(List[List[str]], read_spm(file_path, return_mappings=False))
    except Exception as e:
        msg = f"Error reading transaction data from SPM file '{file_path}': {e}"
        logging.error(msg)
        raise ValueError(msg) from e


def detect_and_read_file(file_path: str) -> Union[List[List[str]], List[List[Tuple[str, float]]]]:
    """
    Detect file format (CSV, JSON, Parquet, Arrow) and read transactions.

    Supports traditional formats (CSV, JSON) and modern DataFrame formats (Parquet, Arrow).
    For DataFrame formats, requires 'gsppy[dataframe]' to be installed.

    Parameters:
        file_path (str): Path to the file containing transactions.

    Returns:
        Union[List[List[str]], List[List[Tuple[str, float]]]]:
            Parsed transactions from the file.

    Raises:
        ValueError: If the file format is unsupported or reading fails.
    """
    if not os.path.exists(file_path):
        raise ValueError(f"File '{file_path}' does not exist.")

    _, file_extension = os.path.splitext(file_path)
    file_extension = file_extension.lower()

    if file_extension == FileExtension.JSON.value:
        return read_transactions_from_json(file_path)

    if file_extension == FileExtension.CSV.value:
        return read_transactions_from_csv(file_path)

    if file_extension in PARQUET_EXTENSIONS:
        return read_transactions_from_parquet(file_path)

    if file_extension in ARROW_EXTENSIONS:
        return read_transactions_from_arrow(file_path)

    raise ValueError(SUPPORTED_EXTENSIONS_MESSAGE.format(extension=file_extension))


def read_transactions_from_parquet(
    file_path: str,
    transaction_col: Optional[str] = None,
    item_col: Optional[str] = None,
    timestamp_col: Optional[str] = None,
    sequence_col: Optional[str] = None,
) -> Union[List[List[str]], List[List[Tuple[str, float]]]]:
    """
    Read transactions from a Parquet file using Polars.

    Parameters:
        file_path (str): Path to the Parquet file.
        transaction_col (Optional[str]): Column name for transaction IDs (grouped format).
        item_col (Optional[str]): Column name for items (grouped format).
        timestamp_col (Optional[str]): Column name for timestamps.
        sequence_col (Optional[str]): Column name containing sequences (sequence format).

    Returns:
        Union[List[List[str]], List[List[Tuple[str, float]]]]:
            Parsed transactions from the file.

    Raises:
        ValueError: If the file cannot be read or Polars is not installed.
    """
    try:
        import polars as pl

        from gsppy.dataframe_adapters import polars_to_transactions
    except ImportError as e:
        raise ValueError("Parquet support requires Polars. Install with: pip install 'gsppy[dataframe]'") from e

    try:
        df: Any = pl.read_parquet(file_path)
        return polars_to_transactions(
            df,
            transaction_col=transaction_col,
            item_col=item_col,
            timestamp_col=timestamp_col,
            sequence_col=sequence_col,
        )
    except Exception as e:
        msg = f"Error reading transaction data from Parquet file '{file_path}': {e}"
        logging.error(msg)
        raise ValueError(msg) from e


def read_transactions_from_arrow(
    file_path: str,
    transaction_col: Optional[str] = None,
    item_col: Optional[str] = None,
    timestamp_col: Optional[str] = None,
    sequence_col: Optional[str] = None,
) -> Union[List[List[str]], List[List[Tuple[str, float]]]]:
    """
    Read transactions from an Arrow/Feather file using Polars.

    Parameters:
        file_path (str): Path to the Arrow/Feather file.
        transaction_col (Optional[str]): Column name for transaction IDs (grouped format).
        item_col (Optional[str]): Column name for items (grouped format).
        timestamp_col (Optional[str]): Column name for timestamps.
        sequence_col (Optional[str]): Column name containing sequences (sequence format).

    Returns:
        Union[List[List[str]], List[List[Tuple[str, float]]]]:
            Parsed transactions from the file.

    Raises:
        ValueError: If the file cannot be read or Polars is not installed.
    """
    try:
        import polars as pl

        from gsppy.dataframe_adapters import polars_to_transactions
    except ImportError as e:
        raise ValueError("Arrow/Feather support requires Polars. Install with: pip install 'gsppy[dataframe]'") from e

    try:
        df: Any = pl.read_ipc(file_path)
        return polars_to_transactions(
            df,
            transaction_col=transaction_col,
            item_col=item_col,
            timestamp_col=timestamp_col,
            sequence_col=sequence_col,
        )
    except Exception as e:
        msg = f"Error reading transaction data from Arrow file '{file_path}': {e}"
        logging.error(msg)
        raise ValueError(msg) from e


def write_patterns_to_parquet(
    patterns: List[dict],
    output_path: str,
    include_level: bool = True,
) -> None:
    """
    Write GSP patterns to a Parquet file using Polars.

    Parameters:
        patterns (List[dict]): GSP search results (list of dicts mapping patterns to support).
        output_path (str): Path to the output Parquet file.
        include_level (bool): Whether to include pattern level (length) in output.

    Raises:
        ValueError: If Polars is not installed or writing fails.
    """
    try:
        import polars as pl
    except ImportError as e:
        raise ValueError("Parquet export requires Polars. Install with: pip install 'gsppy[dataframe]'") from e

    try:
        # Flatten patterns into rows
        rows = []
        for level_idx, level_patterns in enumerate(patterns, start=1):
            for pattern, support in level_patterns.items():
                row = {
                    "pattern": str(pattern),
                    "support": support,
                }
                if include_level:
                    row["level"] = level_idx
                rows.append(row)

        # Create DataFrame and write to Parquet
        df = pl.DataFrame(rows)
        df.write_parquet(output_path)
        logging.info(f"Successfully wrote {len(rows)} patterns to {output_path}")

    except Exception as e:
        msg = f"Error writing patterns to Parquet file '{output_path}': {e}"
        logging.error(msg)
        raise ValueError(msg) from e


def write_patterns_to_arrow(
    patterns: List[dict],
    output_path: str,
    include_level: bool = True,
) -> None:
    """
    Write GSP patterns to an Arrow/Feather file using Polars.

    Parameters:
        patterns (List[dict]): GSP search results (list of dicts mapping patterns to support).
        output_path (str): Path to the output Arrow/Feather file.
        include_level (bool): Whether to include pattern level (length) in output.

    Raises:
        ValueError: If Polars is not installed or writing fails.
    """
    try:
        import polars as pl
    except ImportError as e:
        raise ValueError("Arrow export requires Polars. Install with: pip install 'gsppy[dataframe]'") from e

    try:
        # Flatten patterns into rows
        rows = []
        for level_idx, level_patterns in enumerate(patterns, start=1):
            for pattern, support in level_patterns.items():
                row = {
                    "pattern": str(pattern),
                    "support": support,
                }
                if include_level:
                    row["level"] = level_idx
                rows.append(row)

        # Create DataFrame and write to Arrow/Feather
        df = pl.DataFrame(rows)
        df.write_ipc(output_path)
        logging.info(f"Successfully wrote {len(rows)} patterns to {output_path}")

    except Exception as e:
        msg = f"Error writing patterns to Arrow file '{output_path}': {e}"
        logging.error(msg)
        raise ValueError(msg) from e


def write_patterns_to_csv(
    patterns: List[dict],
    output_path: str,
    include_level: bool = True,
) -> None:
    """
    Write GSP patterns to a CSV file.

    Parameters:
        patterns (List[dict]): GSP search results (list of dicts mapping patterns to support).
        output_path (str): Path to the output CSV file.
        include_level (bool): Whether to include pattern level (length) in output.

    Raises:
        ValueError: If writing fails.
    """
    try:
        import csv

        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['level', 'pattern', 'support'] if include_level else ['pattern', 'support']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for level_idx, level_patterns in enumerate(patterns, start=1):
                for pattern, support in level_patterns.items():
                    row = {
                        'pattern': str(pattern),
                        'support': support,
                    }
                    if include_level:
                        row['level'] = level_idx
                    writer.writerow(row)

        logging.info(f"Successfully wrote patterns to {output_path}")

    except Exception as e:
        msg = f"Error writing patterns to CSV file '{output_path}': {e}"
        logging.error(msg)
        raise ValueError(msg) from e


def write_patterns_to_json(
    patterns: List[dict],
    output_path: str,
) -> None:
    """
    Write GSP patterns to a JSON file.

    Parameters:
        patterns (List[dict]): GSP search results (list of dicts mapping patterns to support).
        output_path (str): Path to the output JSON file.

    Raises:
        ValueError: If writing fails.
    """
    try:
        # Convert pattern tuples to lists for JSON serialization
        serializable_patterns = []
        for level_idx, level_patterns in enumerate(patterns, start=1):
            level_data = []
            for pattern, support in level_patterns.items():
                level_data.append({
                    'pattern': list(pattern),
                    'support': support,
                    'level': level_idx
                })
            serializable_patterns.append(level_data)

        with open(output_path, 'w', encoding='utf-8') as jsonfile:
            json.dump(serializable_patterns, jsonfile, indent=2)

        logging.info(f"Successfully wrote patterns to {output_path}")

    except Exception as e:
        msg = f"Error writing patterns to JSON file '{output_path}': {e}"
        logging.error(msg)
        raise ValueError(msg) from e


def _load_dataframe_format(
    file_path: str,
    file_extension: str,
    transaction_col: Optional[str],
    item_col: Optional[str],
    timestamp_col: Optional[str],
    sequence_col: Optional[str],
) -> Union[List[List[str]], List[List[Tuple[str, float]]]]:
    """
    Load transactions from DataFrame formats (Parquet/Arrow).

    Parameters:
        file_path: Path to the file
        file_extension: File extension (lowercase)
        transaction_col: Transaction ID column name
        item_col: Item column name
        timestamp_col: Timestamp column name
        sequence_col: Sequence column name

    Returns:
        Loaded transactions
    """
    if file_extension in PARQUET_EXTENSIONS:
        return read_transactions_from_parquet(
            file_path,
            transaction_col=transaction_col,
            item_col=item_col,
            timestamp_col=timestamp_col,
            sequence_col=sequence_col,
        )
    else:  # Arrow/Feather
        return read_transactions_from_arrow(
            file_path,
            transaction_col=transaction_col,
            item_col=item_col,
            timestamp_col=timestamp_col,
            sequence_col=sequence_col,
        )


def _load_transactions_by_format(
    file_path: str,
    file_format: str,
    file_extension: str,
    is_dataframe_format: bool,
    transaction_col: Optional[str],
    item_col: Optional[str],
    timestamp_col: Optional[str],
    sequence_col: Optional[str],
) -> Union[List[List[str]], List[List[Tuple[str, float]]]]:
    """
    Load transactions based on specified format.

    Parameters:
        file_path: Path to the file
        file_format: Format string (lowercase)
        file_extension: File extension (lowercase)
        is_dataframe_format: Whether file is a DataFrame format
        transaction_col: Transaction ID column name
        item_col: Item column name
        timestamp_col: Timestamp column name
        sequence_col: Sequence column name

    Returns:
        Loaded transactions

    Raises:
        ValueError: If format is unknown
    """
    if file_format == FileFormat.SPM.value:
        return read_transactions_from_spm(file_path)
    elif file_format == FileFormat.JSON.value:
        return read_transactions_from_json(file_path)
    elif file_format == FileFormat.CSV.value:
        return read_transactions_from_csv(file_path)
    elif file_format in (FileFormat.PARQUET.value, FileFormat.ARROW.value):
        return _load_dataframe_format(file_path, file_extension, transaction_col, item_col, timestamp_col, sequence_col)
    elif file_format == FileFormat.AUTO.value:
        # Auto-detect format
        if is_dataframe_format:
            return _load_dataframe_format(
                file_path, file_extension, transaction_col, item_col, timestamp_col, sequence_col
            )
        else:
            return detect_and_read_file(file_path)
    else:
        raise ValueError(f"Unknown format: {file_format}")


# Click-based CLI
@click.command()
@click.option(
    "--file",
    "file_path",
    required=True,
    type=click.Path(exists=True),
    help="Path to a transaction file (JSON, CSV, SPM, Parquet, or Arrow format).",
)
@click.option(
    "--min_support",
    default=0.2,
    show_default=True,
    type=float,
    help="Minimum support threshold as a fraction of total transactions.",
)
@click.option(
    "--backend",
    type=click.Choice(["auto", "python", "rust", "gpu"], case_sensitive=False),
    default="auto",
    show_default=True,
    help="Backend to use for support counting.",
)
@click.option(
    "--mingap",
    type=float,
    default=None,
    help="Minimum time gap required between consecutive items in patterns (requires timestamped transactions).",
)
@click.option(
    "--maxgap",
    type=float,
    default=None,
    help="Maximum time gap allowed between consecutive items in patterns (requires timestamped transactions).",
)
@click.option(
    "--maxspan",
    type=float,
    default=None,
    help="Maximum time span from first to last item in patterns (requires timestamped transactions).",
)
@click.option(
    "--transaction-col",
    type=str,
    default=None,
    help="DataFrame: column name for transaction IDs (grouped format).",
)
@click.option(
    "--item-col",
    type=str,
    default=None,
    help="DataFrame: column name for items (grouped format).",
)
@click.option(
    "--timestamp-col",
    type=str,
    default=None,
    help="DataFrame: column name for timestamps.",
)
@click.option(
    "--sequence-col",
    type=str,
    default=None,
    help="DataFrame: column name containing sequences (sequence format).",
)
@click.option(
    "--format",
    type=click.Choice([fmt.value for fmt in FileFormat], case_sensitive=False),
    default=FileFormat.AUTO.value,
    show_default=True,
    help="File format to use. 'auto' detects format from file extension.",
)
@click.option("--verbose", is_flag=True, help="Enable verbose output for debugging purposes.")
@click.option(
    "--preprocess-hook",
    type=str,
    default=None,
    help="Python import path to preprocessing hook function (e.g., 'mymodule.preprocess_fn').",
)
@click.option(
    "--postprocess-hook",
    type=str,
    default=None,
    help="Python import path to postprocessing hook function (e.g., 'mymodule.postprocess_fn').",
)
@click.option(
    "--candidate-filter-hook",
    type=str,
    default=None,
    help="Python import path to candidate filter hook function (e.g., 'mymodule.filter_fn').",
)
@click.option(
    "--output",
    type=str,
    default=None,
    help="Path to save mining results. Format is auto-detected from extension (.parquet, .arrow, .csv, .json).",
)
@click.option(
    "--output-format",
    type=click.Choice(["auto", "parquet", "arrow", "csv", "json"], case_sensitive=False),
    default="auto",
    show_default=True,
    help="Output format for mining results. 'auto' detects format from file extension.",
)
@click.pass_context
def main(ctx: click.Context, **kwargs: Any) -> None:
    """
    Run the GSP algorithm on transactional data from a file.

    Supports multiple file formats:
    - JSON/CSV/SPM: Traditional transaction formats
    - Parquet/Arrow: Modern DataFrame formats (requires 'gsppy[dataframe]')
    - Polars/Pandas DataFrames: Can be passed directly (requires 'gsppy[dataframe]')

    Supports both simple transactions (items only) and timestamped transactions
    (item-timestamp pairs) for temporal pattern mining.

    Examples:
        Basic usage without temporal constraints:

        ```bash
        gsppy --file transactions.json --min_support 0.3
        ```

        With temporal constraints:

        ```bash
        gsppy --file temporal_data.json --min_support 0.3 --maxgap 10
        gsppy --file events.json --min_support 0.5 --mingap 2 --maxgap 10 --maxspan 20
        ```

        With Parquet files (grouped format):

        ```bash
        gsppy --file data.parquet --min_support 0.3 \
              --transaction-col txn_id --item-col product
        ```

        With Arrow files (sequence format):

        ```bash
        gsppy --file sequences.arrow --min_support 0.3 \
              --sequence-col items
        ```

        With SPM format files:

        ```bash
        gsppy --file data.txt --format spm --min_support 0.3
        ```

        With custom hooks (requires Python module with hook functions):

        ```bash
        # Create a hooks module first (hooks.py):
        # def my_filter(candidate, support, context):
        #     return len(candidate) <= 2  # Keep only short patterns
        #
        # def my_postprocess(patterns):
        #     return patterns[:2]  # Keep only first 2 levels

        gsppy --file data.json --min_support 0.3 \
              --candidate-filter-hook hooks.my_filter \
              --postprocess-hook hooks.my_postprocess
        ```
    """
    # Extract parameters from kwargs
    file_path = kwargs['file_path']
    min_support = kwargs['min_support']
    backend = kwargs['backend']
    mingap = kwargs.get('mingap')
    maxgap = kwargs.get('maxgap')
    maxspan = kwargs.get('maxspan')
    transaction_col = kwargs.get('transaction_col')
    item_col = kwargs.get('item_col')
    timestamp_col = kwargs.get('timestamp_col')
    sequence_col = kwargs.get('sequence_col')
    file_format = kwargs['format']
    verbose = kwargs['verbose']
    preprocess_hook = kwargs.get('preprocess_hook')
    postprocess_hook = kwargs.get('postprocess_hook')
    candidate_filter_hook = kwargs.get('candidate_filter_hook')
    output_path = kwargs.get('output')
    output_format = kwargs.get('output_format', 'auto')
    
    setup_logging(verbose)

    # Load hook functions if specified
    try:
        preprocess_fn = _load_hook_function(preprocess_hook, "preprocess") if preprocess_hook else None
        postprocess_fn = _load_hook_function(postprocess_hook, "postprocess") if postprocess_hook else None
        candidate_filter_fn = (
            _load_hook_function(candidate_filter_hook, "candidate_filter") if candidate_filter_hook else None
        )

        if preprocess_fn:
            logger.info(f"Loaded preprocessing hook: {preprocess_hook}")
        if postprocess_fn:
            logger.info(f"Loaded postprocessing hook: {postprocess_hook}")
        if candidate_filter_fn:
            logger.info(f"Loaded candidate filter hook: {candidate_filter_hook}")
    except ValueError as e:
        logger.error(f"Error loading hook function: {e}")
        sys.exit(1)

    # Detect file extension to determine if DataFrame column params are needed
    _, file_extension = os.path.splitext(file_path)
    file_extension = file_extension.lower()
    is_dataframe_format = file_extension in DATAFRAME_EXTENSIONS

    # Automatically detect and load transactions
    try:
        file_format_lower = file_format.lower()
        transactions = _load_transactions_by_format(
            file_path,
            file_format_lower,
            file_extension,
            is_dataframe_format,
            transaction_col,
            item_col,
            timestamp_col,
            sequence_col,
        )
    except ValueError as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

    # Validate parameters
    _validate_parameters(min_support, mingap, maxgap, maxspan)

    # Select backend for acceleration layer
    if backend and backend.lower() != "auto":
        os.environ["GSPPY_BACKEND"] = backend.lower()

    # Initialize and run GSP algorithm
    try:
        gsp = GSP(transactions, mingap=mingap, maxgap=maxgap, maxspan=maxspan, verbose=verbose)
        patterns = gsp.search(
            min_support=min_support,
            return_sequences=False,
            preprocess_fn=preprocess_fn,
            postprocess_fn=postprocess_fn,
            candidate_filter_fn=candidate_filter_fn,
        )
        
        # Display results to stdout
        logger.info("Frequent Patterns Found:")
        for i, level in enumerate(patterns, start=1):
            logger.info(f"\n{i}-Sequence Patterns:")
            for pattern, support in level.items():
                logger.info(f"Pattern: {pattern}, Support: {support}")
        
        # Write results to file if output path specified
        if output_path:
            _write_patterns_to_file(patterns, output_path, output_format)
            
    except Exception as e:
        logger.error(f"Error executing GSP algorithm: {e}")
        sys.exit(1)


def _validate_parameters(
    min_support: float,
    mingap: Optional[float],
    maxgap: Optional[float],
    maxspan: Optional[float],
) -> None:
    """
    Validate input parameters for GSP algorithm.

    Args:
        min_support: Minimum support threshold
        mingap: Minimum time gap constraint
        maxgap: Maximum time gap constraint
        maxspan: Maximum time span constraint

    Raises:
        SystemExit: If validation fails
    """
    # Check min_support
    if min_support <= 0.0 or min_support > 1.0:
        logger.error("Error: min_support must be in the range (0.0, 1.0].")
        sys.exit(1)

    # Validate temporal constraints
    if mingap is not None and mingap < 0:
        logger.error("Error: mingap must be non-negative.")
        sys.exit(1)
    if maxgap is not None and maxgap < 0:
        logger.error("Error: maxgap must be non-negative.")
        sys.exit(1)
    if maxspan is not None and maxspan < 0:
        logger.error("Error: maxspan must be non-negative.")
        sys.exit(1)
    if mingap is not None and maxgap is not None and mingap > maxgap:
        logger.error("Error: mingap cannot be greater than maxgap.")
        sys.exit(1)


def _write_patterns_to_file(
    patterns: List[dict],
    output_path: str,
    output_format: str = "auto"
) -> None:
    """
    Write GSP patterns to a file in the specified format.

    Args:
        patterns: GSP search results
        output_path: Path to output file
        output_format: Output format (auto, parquet, arrow, csv, json)

    Raises:
        SystemExit: If writing fails
    """
    try:
        # Auto-detect format from file extension if needed
        if output_format.lower() == "auto":
            _, ext = os.path.splitext(output_path)
            ext = ext.lower()
            if ext in PARQUET_EXTENSIONS:
                output_format = "parquet"
            elif ext in ARROW_EXTENSIONS:
                output_format = "arrow"
            elif ext == ".csv":
                output_format = "csv"
            elif ext == ".json":
                output_format = "json"
            else:
                raise ValueError(f"Cannot auto-detect format from extension: {ext}")

        # Write patterns based on format
        format_lower = output_format.lower()
        if format_lower == "parquet":
            write_patterns_to_parquet(patterns, output_path)
        elif format_lower == "arrow":
            write_patterns_to_arrow(patterns, output_path)
        elif format_lower == "csv":
            write_patterns_to_csv(patterns, output_path)
        elif format_lower == "json":
            write_patterns_to_json(patterns, output_path)
        else:
            raise ValueError(f"Unknown output format: {output_format}")

    except Exception as e:
        logger.error(f"Error writing patterns to file: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
