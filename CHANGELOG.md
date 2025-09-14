# Changelog

## [v3.0.0] - 2025-09-14

### **New Features**

* **Acceleration Backends Introduced**:

  * **Rust Backend**: Fast, parallelized subsequence matching using PyO3 + Rayon.
  * **GPU Backend (Experimental)**: Singleton (`k=1`) support counting accelerated via CuPy.
* **Unified Backend Selection**:

  * Backend can be selected via:

    * Python API (`backend="auto" | "rust" | "gpu" | "python"`)
    * CLI (`--backend`)
    * Environment variable (`GSPPY_BACKEND`)
  * Default: `auto` (tries Rust, falls back to Python).
* **Optional GPU Install**:

  * Install with `pip install "gsppy[gpu]"` for CuPy support.

### **CLI and API Enhancements**

* Updated CLI to support `--backend` option.
* Python API `GSP.search()` accepts `backend=` parameter for runtime selection.
* Environment variable fallback documented and supported.

### **Documentation Updates**

* **README.md** updated:

  * New “GPU Acceleration” section with installation/usage guidance.
  * Backend selector documentation for CLI, API, and env var.
  * Python version compatibility badge updated to 3.10+.
* **CONTRIBUTING.md**:

  * Rewritten with new setup instructions using `uv` and `Makefile`.
  * Added pre-commit and `tox-uv` instructions.

### **Tooling and Developer Experience**

* **Migrated Tooling**:

  * Moved from Rye to `uv` for dependency and environment management.
  * Introduced `uv.lock` for reproducible, cross-version installations.
* **Makefile**:

  * Common targets added (`make setup`, `make install`, `make lint`, etc.).
  * One-liner for full dev bootstrap: `make setup && make install && make pre-commit-install`
* **Pre-commit hooks**:

  * Added `.pre-commit-config.yaml` with `ruff`, `pyright`, and `pytest`.
* **DevContainer Support**:

  * Added `devcontainer.json` for VS Code one-click environment provisioning.

### **Testing and Quality**

* Test suite fully adapted to new tooling (`uv`, `tox-uv`).
* Static typing validated with both `mypy` and `pyright`.
* All 38 tests pass locally and in CI (Python 3.10–3.13).

### **CI/CD and Infrastructure**

* GitHub Actions updated:

  * All jobs use `uv` for setup and execution.
  * `tox` now powered by `tox-uv`, auto-provisions interpreters.
* Updated testing matrix in `codecov.yml` to Python 3.13.
* Simplified CI jobs by consolidating environment setup steps.

### **Packaging & Compatibility**

* Dropped Python 3.8 and 3.9 support:

  * Project now requires Python **3.10+**.
* `pyproject.toml` updated:

  * `requires-python = ">=3.10"`
  * Optional `[gpu]` extra defined for CuPy support.
  * Development dependencies and classifiers modernized.

### **Code Improvements**

* Improved type hints and formatting in:

  * `gsp.py`, `cli.py`, and `utils.py`
* Lint fixes and logging improvements.
* Code follows unified `ruff` formatting.

### **Breaking Changes**

* 🔥 Dropped support for Python 3.8 and 3.9.

  * Users must upgrade to Python 3.10 or newer.

### **Migration Guide**

For contributors or CI environments:

```bash
# Install uv (first time only)
curl -Ls https://astral.sh/uv/install.sh | bash

# Setup new local dev environment
make setup
make install
make pre-commit-install
```

### **Performance Notes**

* **GPU acceleration** boosts singleton (k=1) counting using CuPy’s `bincount`.
* **Rust backend** delivers robust multithreaded subsequence matching.
* Backend auto-dispatch adapts based on availability and selection.

---

## [v2.3.0] - 2025-01-05

### **New Features**
- Introduced parallel test execution using `pytest-xdist` for improved testing efficiency:
  - Updated `rye run test` script to include parallel execution with `pytest -n auto`.
- Added new Rye commands for dependency management:
  - `rye add <package-name>` to add dependencies.
  - `rye add --dev <package-name>` to add development dependencies.

### **Infrastructure Improvements**
- Enhanced the development environment setup:
  - Updated the README to include instructions for setting up the environment with `rye sync` instead of `python setup.py install`.
  - Deprecated usage of `setup.py` for manual installation.
- Updated `pyproject.toml`:
  - Added `pytest-xdist` as a development dependency to enable parallel testing.

### **Testing and Quality**
- Improved test performance by enabling parallel test execution with `pytest-xdist`.
- Updated `requirements-dev.lock`:
  - Added new dependencies: `pytest-xdist` and its related package `execnet`.

### **Documentation Updates**
- Enhanced the README:
  - Improved clarity and structure in the **Developer Installation** and **Contributing** sections.
  - Added new commands under **Use Rye Scripts** to streamline project tasks.
  - Clarified the process for adding new dependencies.

### **Dependency Management**
- Updated development dependencies in `pyproject.toml`:
  - Added `pytest-xdist>=3.6.1` for parallel testing.
  - Updated `ruff` to `0.8.6` for code formatting and linting.

### **Version Updates**
- Updated version to `2.3.0` in `pyproject.toml`, `README.md`, and `CITATION.cff`.
- Updated copyright year to 2025 in the `LICENSE` file.
---

## [v2.2.0] - 2024-12-27

### **New Features**
- Added a `.github/CODEOWNERS` file to automatically assign reviewers for pull requests.
- Introduced new issue templates:
  - `bug_report.yml` for structured bug reporting.
  - `feature_request.yml` for feature suggestions.
  - `config.yml` to disable blank issues and provide guidance for issue reporting.

### **Infrastructure Improvements**
- Added `SECURITY.md` to define the project's security policy, including supported versions and responsible disclosure practices.
- Updated `.python-version` to include support for Python versions `3.12.8` and `3.13.1`.
- **Migrated Dependency and Virtual Environment Management to Rye**:
  - Introduced [Rye](https://github.com/mitsuhiko/rye) for managing Python dependencies and virtual environments.
  - Deprecated the `requirements-dev.txt` file in favor of managing dependencies in `pyproject.toml`.
  - Updated documentation to include instructions for using `rye sync` to set up the project environment.
  - Updated CI workflows to install and use dependencies directly via Rye.

### **CLI Enhancements**
- Improved `gsppy/cli.py`:
  - Enhanced logging setup with verbosity options (`--verbose`).
  - Added type annotations for improved readability and maintainability.
  - Refined error handling and user feedback for invalid inputs.

### **Algorithm and Utility Enhancements**
- Updated GSP implementation in `gsppy/gsp.py`:
  - Added type annotations and clarified logic in methods.
  - Improved `_worker_batch` and `_support` functions for better performance and readability.
- Enhanced utility functions in `gsppy/utils.py`:
  - Added stricter typing and validation in utilities like `is_subsequence_in_list`.

### **Testing and Quality**
- Reorganized tests:
  - Moved test files from `gsppy/tests/` to `tests/` for a cleaner structure.
  - Refactored test cases with type annotations and enhanced mock handling.
- Introduced additional dev dependencies in `requirements-dev.txt`:
  - `mypy`, `pyright`, and `ruff` for static analysis and linting.
  - `cython` for performance optimization in future releases.
- Added `mypy.ini` and updated `pyproject.toml` for stricter type-checking and configuration consistency.

### **Build and Packaging**
- Migrated to `pyproject.toml` for modern Python packaging:
  - Removed `setup.py` and `setup.cfg`.
  - Introduced `hatch` and `hatchling` for streamlined builds.
- Updated GitHub Actions workflows:
  - Fixed PyPI URL in `publish.yml`.
  - Updated build steps to use `python -m build` for consistency.

---

## [v2.1.0] - 2024-12-26

### **Compatibility Updates**
- Updated **Python Compatibility**:
  - Lowered the minimum Python version requirement from 3.11 to 3.8 in `setup.py`.
  - Updated `README.md` to reflect compatibility with Python 3.8 and later.
  - Added `tox.ini` configuration to test across Python versions 3.8 to 3.11.
  - Added `.python-version` file specifying supported Python versions: 3.6.15, 3.7.12, 3.8.10, 3.9.16, 3.10.12, and 3.11.4.

### **Dependency Management**
- Split development dependencies:
  - Moved development-specific dependencies to `requirements-dev.txt`.
  - Removed redundant dependencies from `requirements.txt`.
- Added `tox` as a development dependency in `requirements-dev.txt`.

### **Testing Enhancements**
- Introduced `tox` for managing tests across multiple Python versions.
- Refactored GitHub Actions workflow (`codecov.yml`):
  - Updated to install dependencies from `requirements-dev.txt`.
  - Expanded testing configuration to include Python 3.8 compatibility.

### **Documentation Updates**
- Enhanced **README.md**:
  - Updated Python badge to reflect compatibility with Python 3.8+.
  - Included a clear statement of compatibility with Python 3.8 and later versions.

### **Other Improvements**
- Added classifiers in `setup.py` for Python 3.8, 3.9, and 3.10.
- Improved project structure with the addition of `tox.ini` for environment management.

---

## [v2.0.1] - 2024-12-25
- Added **CITATION.cff** file for citation information.
- Removed the GitHub sponsor badge from the README.

---

## [v2.0] - 2024-12-25

### **New Features**
- Introduced **CLI Interface**:
  - Added `cli.py` for command-line usage of the GSP algorithm.
  - Supports input in JSON and CSV formats.
  - Allows configuration of the `min_support` threshold via CLI arguments.
- Added **Parallel Processing for Support Calculation**:
  - Optimized support calculation using multiprocessing for better performance on large datasets.
- Enhanced **Logging**:
  - Configurable logs to monitor progress and debugging.

### **Improved Documentation**
- Comprehensive updates to the `README.md`:
  - Detailed explanation of GSP with examples.
  - Added "What is GSP?" and "Planned Features" sections.
  - Expanded installation and usage guides.
- Added `CONTRIBUTING.md`:
  - Clear guidelines for contributing code, documentation, and bug reports.
- Added badges for PyPI, code coverage, and security metrics.

### **Testing**
- Added a robust test suite:
  - Moved test cases to the `gsppy/tests` directory.
  - Comprehensive unit tests for the CLI, GSP algorithm, and utility functions.
  - Tests include edge cases, large datasets, and benchmarking.

### **Utilities**
- Introduced helper utilities for GSP:
  - `split_into_batches`: Efficiently split candidates into manageable batches.
  - `is_subsequence_in_list`: Improved subsequence matching logic.

### **Workflow and Configuration**
- Integrated GitHub Actions workflows:
  - Added workflows for testing, linting, and publishing to PyPI.
- Added `.editorconfig` for consistent code formatting.
- Integrated Dependabot for automated dependency updates.

---

## **[v1.1]** - 2020-05-01

### **Features**
- Initial release of the **GSP-Py** library.
- Basic implementation of the Generalized Sequential Pattern (GSP) algorithm:
  - Single-threaded support calculation.
  - Basic candidate generation and pruning.
- Test cases for supermarket transactions.

### **Documentation**
- Basic `README.md` with:
  - Installation instructions.
  - Example usage of the GSP algorithm.

### **Miscellaneous**
- Added setup files (`setup.py`, `setup.cfg`) for publishing to PyPI.
- Licensed under MIT.

---

## **Summary of Changes**

### From v2.2.0 to v2.3.0
- Enhanced test efficiency with parallel execution.
- Simplified developer setup and dependency management.
- Improved documentation for clarity and usability.
