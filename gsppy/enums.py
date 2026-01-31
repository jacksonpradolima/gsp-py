"""Shared enums and constants for GSP-Py.

This module centralizes reusable definitions for file formats and extension groups
used across the CLI and DataFrame helpers, keeping validation consistent and
reducing duplication.

Highlights:
    - `FileExtension` enum for canonical file suffixes
    - Predefined extension sets for format detection
    - Shared user-facing error message template
"""

from __future__ import annotations

from enum import Enum


class FileExtension(str, Enum):
    JSON = ".json"
    CSV = ".csv"
    PARQUET = ".parquet"
    PQ = ".pq"
    ARROW = ".arrow"
    FEATHER = ".feather"


class FileFormat(str, Enum):
    """Supported file formats for loading transaction data."""
    AUTO = "auto"
    JSON = "json"
    CSV = "csv"
    SPM = "spm"
    PARQUET = "parquet"
    ARROW = "arrow"


DATAFRAME_EXTENSIONS = {
    FileExtension.PARQUET.value,
    FileExtension.PQ.value,
    FileExtension.ARROW.value,
    FileExtension.FEATHER.value,
}

PARQUET_EXTENSIONS = {FileExtension.PARQUET.value, FileExtension.PQ.value}
ARROW_EXTENSIONS = {FileExtension.ARROW.value, FileExtension.FEATHER.value}

SUPPORTED_EXTENSIONS_MESSAGE = (
    "Unsupported file format '{extension}'. Supported formats: .json, .csv, .parquet, .arrow, .feather"
)
