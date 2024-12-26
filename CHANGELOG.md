# Changelog

## [v2.0.1] - 2024-12-25
- Added **CITATION.cff** file for citation information.
- Removed the GitHub sponsor badge from the README

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

### From v1.1 to v2.0

- **Performance**: Introduced parallel processing for faster support calculation.
- **Usability**: Added CLI and extensive logging.
- **Documentation**: Improved and expanded documentation.
- **Testing**: Robust test suite added.
- **Workflow**: Automated CI/CD workflows integrated.
