# Changelog

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

### From v2.1.0 to v2.2.0
- **New Features**:
  - Added `.github/CODEOWNERS` and issue templates for better pull request and issue management.
  - Introduced a `SECURITY.md` file to define project security policies.

- **Infrastructure Improvements**:
  - Added Python 3.12.8 and 3.13.1 compatibility in `.python-version`.
  - Migrated to `pyproject.toml` for modern Python packaging, replacing `setup.py` and `setup.cfg`.
  - Adopted **Rye** for dependency management and virtual environment setup:
    - Deprecated `requirements-dev.txt` in favor of managing all dependencies in `pyproject.toml`.
    - Updated workflows and documentation to reflect the use of `rye sync` for environment setu

- **CLI Enhancements**:
  - Improved logging, error handling, and added type annotations in the CLI.

- **Algorithm & Utility Enhancements**:
  - Refactored the GSP algorithm for better performance and clarity.
  - Enhanced utility functions with stricter typing and validation.

- **Testing & Quality**:
  - Reorganized tests into a cleaner structure, added static analysis tools, and improved type-checking configurations.

- **Build & Packaging**:
  - Streamlined the build process with `hatch` and `hatchling`.
  - Updated GitHub Actions workflows for improved consistency and functionality.
