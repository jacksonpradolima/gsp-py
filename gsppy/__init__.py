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
    read_transactions_from_arrow,
    read_transactions_from_parquet,
    read_transactions_from_spm,
)
from gsppy.gsp import GSP
from gsppy.pruning import (
    CombinedPruning,
    PruningStrategy,
    SupportBasedPruning,
    TemporalAwarePruning,
    FrequencyBasedPruning,
    create_default_pruning_strategy,
)
from gsppy.utils import TokenMapper

# DataFrame adapters are optional - import only if dependencies are available
try:
    from gsppy.dataframe_adapters import (
        DataFrameAdapterError,
        pandas_to_transactions,
        polars_to_transactions,
        dataframe_to_transactions,
    )
except ImportError:
    DataFrameAdapterError = None  # type: ignore
    pandas_to_transactions = None  # type: ignore
    polars_to_transactions = None  # type: ignore
    dataframe_to_transactions = None  # type: ignore

_DATAFRAME_AVAILABLE = DataFrameAdapterError is not None

try:
    __version__ = importlib_metadata.version("gsppy")
except importlib_metadata.PackageNotFoundError:  # pragma: no cover - handled only in editable installs
    __version__ = "0.0.0"

__all__ = [
    "GSP",
    "detect_and_read_file",
    "read_transactions_from_csv",
    "read_transactions_from_json",
    "read_transactions_from_parquet",
    "read_transactions_from_arrow",
    "read_transactions_from_spm",
    "setup_logging",
    "__version__",
    "PruningStrategy",
    "SupportBasedPruning",
    "FrequencyBasedPruning",
    "TemporalAwarePruning",
    "CombinedPruning",
    "create_default_pruning_strategy",
    "TokenMapper",
]

# Add DataFrame adapters to __all__ if available
if _DATAFRAME_AVAILABLE:
    __all__.extend(
        [
            "dataframe_to_transactions",
            "polars_to_transactions",
            "pandas_to_transactions",
            "DataFrameAdapterError",
        ]
    )
