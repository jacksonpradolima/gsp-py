"""Public interface for the :mod:`gsppy` package.

This module centralizes the primary entry points, including the :class:`~gsppy.gsp.GSP`
implementation, CLI helpers for loading transactional data, and the package version string.
"""

from importlib import metadata as importlib_metadata

from gsppy.cli import (
    setup_logging,
    detect_and_read_file,
    read_transactions_from_csv,
    read_transactions_from_json,
)
from gsppy.gsp import GSP

try:
    __version__ = importlib_metadata.version("gsppy")
except importlib_metadata.PackageNotFoundError:  # pragma: no cover - handled only in editable installs
    __version__ = "0.0.0"

__all__ = [
    "GSP",
    "detect_and_read_file",
    "read_transactions_from_csv",
    "read_transactions_from_json",
    "setup_logging",
    "__version__",
]
