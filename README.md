[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/pradolima)
[![SonarCloud](https://sonarcloud.io/images/project_badges/sonarcloud-white.svg)](https://sonarcloud.io/summary/new_code?id=jacksonpradolima_gps-py)


# GSP-Py
A **Python implementation** of the Generalized Sequence Pattern (GSP) algorithm for mining sequential patterns in datasets. GSP is a powerful algorithm for discovering sequences of events or items that are frequently observed, making it suitable for a wide range of domains such as market basket analysis, web usage mining, and bioinformatics.

[![PyPI License](https://img.shields.io/pypi/l/gsppy.svg?style=flat-square)]()
![](https://img.shields.io/badge/python-3.11.4+-blue.svg)
[![DOI](https://zenodo.org/badge/108451832.svg)](https://zenodo.org/badge/latestdoi/108451832)

[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=jacksonpradolima_gsp-py&metric=bugs)](https://sonarcloud.io/summary/new_code?id=jacksonpradolima_gsp-py)
[![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=jacksonpradolima_gsp-py&metric=vulnerabilities)](https://sonarcloud.io/summary/new_code?id=jacksonpradolima_gsp-py)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=jacksonpradolima_gsp-py&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=jacksonpradolima_gsp-py)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=jacksonpradolima_gsp-py&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=jacksonpradolima_gsp-py)
[![codecov](https://codecov.io/github/jacksonpradolima/gsp-py/branch/main/graph/badge.svg?token=BW04LB0B5Y)](https://codecov.io/github/jacksonpradolima/gsp-py)

---

## 📚 Table of Contents
- [What is GSP?](#what-is-gsp)
- [Requirements](#requirements)
- [Installation](#installation)
- [Developer Installation](#developer-installation)
- [Usage](#usage)
- [Planned Features](#planned-features)
- [Contributing](#contributing)
- [License](#license)
- [Citation](#citation)

---

## 🔍 What is GSP?

The **Generalized Sequential Pattern (GSP)** algorithm is a sequential pattern mining technique based on **Apriori principles**. Using support thresholds, GSP identifies frequent sequences of items in transaction datasets.

### Key Features:
- **Support-based pruning**: Only retains sequences that meet the minimum support threshold.
- **Candidate generation**: Iteratively generates candidate sequences of increasing length.
- **General-purpose**: Useful in retail, web analytics, social networks, temporal sequence mining, and more.

For example:
- In a shopping dataset, GSP can identify patterns like "Customers who buy bread and milk often purchase diapers next."
- In a website clickstream, GSP might find patterns like "Users visit A, then go to B, and later proceed to C."

---

## ✅ Requirements

You will need Python installed on your system. On most Linux systems, you can install Python with:

```bash
sudo apt install python3
```

For package dependencies of GSP-Py, they will automatically be installed when using `pip`.

---

## 🚀 Installation

GSP-Py can be easily installed either by cloning the repository or using pip.

### Option 1: Clone the Repository
To manually clone the repository and install:
```bash
git clone https://github.com/jacksonpradolima/gsp-py.git
cd gsp-py
python setup.py install
```

### Option 2: Install via `pip`
Alternatively, install GSP-Py from PyPI with:
```bash
pip install gsppy
```

---

## 🛠️ Developer Installation

For contributors and developers, GSP-Py provides additional dependencies for development purposes (e.g., testing and linting).

To install the package along with development dependencies, use:
```bash
pip install .[dev]
```

The `dev` category includes tools such as `pytest`, `pylint`, and others to ensure code quality and maintainability.

## 💡 Usage

The library is designed to be easy to use and integrate with your own projects. Below is an example of how you can configure and run GSP-Py.

### Example Input Data
The input to the algorithm is a sequence of transactions, where each transaction contains a sequence of items:
```python
transactions = [
    ['Bread', 'Milk'],
    ['Bread', 'Diaper', 'Beer', 'Eggs'],
    ['Milk', 'Diaper', 'Beer', 'Coke'],
    ['Bread', 'Milk', 'Diaper', 'Beer'],
    ['Bread', 'Milk', 'Diaper', 'Coke']
]
```

### Importing and Initializing the GSP Algorithm
Import the `GSP` class from the `gsppy` package and call the `search` method to find frequent patterns with a support threshold (e.g., `0.3`):
```python
from gsppy.gsp import GSP

# Define the input data
transactions = [
    ['Bread', 'Milk'],
    ['Bread', 'Diaper', 'Beer', 'Eggs'],
    ['Milk', 'Diaper', 'Beer', 'Coke'],
    ['Bread', 'Milk', 'Diaper', 'Beer'],
    ['Bread', 'Milk', 'Diaper', 'Coke']
]

# Minimum support set to 30%
min_support = 0.3

# Find frequent patterns
result = GSP(transactions).search(min_support)

# Output the results
print(result)
```

### Output
The algorithm will return a list of patterns with their corresponding support.

### Understanding Support
The **support** of a sequence is the fraction of total data-sequences that "contain" the sequence. For instance, if the pattern `[Bread, Milk]` appears in 3 out of 5 transactions, its support is `3 / 5 = 0.6`.

For more complex examples, find example scripts in the [`gsppy/tests`](gsppy/tests) folder.

---

## 🌟 Planned Features

We are actively working to improve GSP-Py. Here are some exciting features planned for future releases:

1. **Custom Filters for Candidate Pruning**:
   - Enable users to define their own pruning logic during the mining process.

2. **Support for Preprocessing and Postprocessing**:
   - Add hooks to allow users to transform datasets before mining and customize the output results.

3. **Support for Time-Constrained Pattern Mining**:
   - Extend GSP-Py to handle temporal datasets by allowing users to define time constraints (e.g., maximum time gaps between events, time windows) during the sequence mining process.
   - Enable candidate pruning and support calculations based on these temporal constraints.

Want to contribute or suggest an improvement? [Open a discussion or issue!](https://github.com/jacksonpradolima/gsp-py/issues)

---

## 🤝 Contributing

We welcome contributions from the community! If you'd like to help improve GSP-Py, read our [CONTRIBUTING.md](CONTRIBUTING.md) guide to get started.

Development dependencies (e.g., testing and linting tools) are included in the `dev` category in `setup.py`. To install these dependencies, run:
```bash
pip install .[dev]
```

### General Steps:
1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/my-feature`.
3. Commit your changes: `git commit -m "Add my feature."`
4. Push to your branch: `git push origin feature/my-feature`.
5. Submit a pull request to the main repository!

Looking for ideas? Check out our [Planned Features](#planned-features) section.

---

## 📝 License
This project is licensed under the terms of the **MIT License**. For more details, refer to the [LICENSE](LICENSE) file.

---

## 📖 Citation

If GSP-Py contributed to your research or project that led to a publication, we kindly ask that you cite it as follows:
