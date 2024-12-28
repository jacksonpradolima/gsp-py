[![PyPI License](https://img.shields.io/pypi/l/gsppy.svg?style=flat-square)]()
![](https://img.shields.io/badge/python-3.8+-blue.svg)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.3333987.svg)](https://doi.org/10.5281/zenodo.3333987)

[![PyPI Downloads](https://img.shields.io/pypi/dm/gsppy.svg?style=flat-square)](https://pypi.org/project/gsppy/)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=jacksonpradolima_gsp-py&metric=bugs)](https://sonarcloud.io/summary/new_code?id=jacksonpradolima_gsp-py)
[![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=jacksonpradolima_gsp-py&metric=vulnerabilities)](https://sonarcloud.io/summary/new_code?id=jacksonpradolima_gsp-py)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=jacksonpradolima_gsp-py&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=jacksonpradolima_gsp-py)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=jacksonpradolima_gsp-py&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=jacksonpradolima_gsp-py)
[![codecov](https://codecov.io/github/jacksonpradolima/gsp-py/graph/badge.svg?token=o1P0qXaYtJ)](https://codecov.io/github/jacksonpradolima/gsp-py)

# GSP-Py

**GSP-Py**: A Python-powered library to mine sequential patterns in large datasets, based on the robust **Generalized
Sequence Pattern (GSP)** algorithm. Ideal for market basket analysis, temporal mining, and user journey discovery.

> [!IMPORTANT]
> GSP-Py is compatible with Python 3.8 and later versions!

---

## 📚 Table of Contents

1. [🔍 What is GSP?](#what-is-gsp)
2. [🔧 Requirements](#requirements)
3. [🚀 Installation](#installation)
    - [❖ Clone Repository](#option-1-clone-the-repository)
    - [❖ Install via PyPI](#option-2-install-via-pip)
4. [🛠️ Developer Installation](#developer-installation)
5. [💡 Usage](#usage)
    - [✅ Example: Analyzing Sales Data](#example-analyzing-sales-data)
    - [📊 Explanation: Support and Results](#explanation-support-and-results)
6. [🌟 Planned Features](#planned-features)
7. [🤝 Contributing](#contributing)
8. [📝 License](#license)
9. [📖 Citation](#citation)

---

## 🔍 What is GSP?

The **Generalized Sequential Pattern (GSP)** algorithm is a sequential pattern mining technique based on **Apriori
principles**. Using support thresholds, GSP identifies frequent sequences of items in transaction datasets.

### Key Features:

- **Support-based pruning**: Only retains sequences that meet the minimum support threshold.
- **Candidate generation**: Iteratively generates candidate sequences of increasing length.
- **General-purpose**: Useful in retail, web analytics, social networks, temporal sequence mining, and more.

For example:

- In a shopping dataset, GSP can identify patterns like "Customers who buy bread and milk often purchase diapers next."
- In a website clickstream, GSP might find patterns like "Users visit A, then go to B, and later proceed to C."

---

## 🔧 Requirements

You will need Python installed on your system. On most Linux systems, you can install Python with:

```bash
sudo apt install python3
```

For package dependencies of GSP-Py, they will automatically be installed when using `pip`.

---

## 🚀 Installation

GSP-Py can be easily installed from either the **repository** or PyPI.

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

This project uses [Rye](https://github.com/mitsuhiko/rye) for managing dependencies, running scripts, and setting up the environment. Follow these steps to install and set up Rye for this project:

#### 1. Install Rye
Run the following command to install Rye:

```bash
curl -sSf https://rye.astral.sh/get | bash
```

If the `~/.rye/bin` directory is not in your PATH, add the following line to your shell configuration file (e.g., `~/.bashrc`, `~/.zshrc`, etc.):

```bash
export PATH="$HOME/.rye/bin:$PATH"
```

Reload your shell configuration file:

```bash
source ~/.bashrc  # or `source ~/.zshrc`
```

#### 2. Set Up the Project Environment
To configure the project environment and install its dependencies, run:

```bash
rye sync
```

#### 3. Use Rye Scripts
Once the environment is set up, you can run the following commands to simplify project tasks:

- Run tests: `rye run test`
- Format code: `rye run format`
- Lint code: `rye run lint`
- Type-check: `rye run typecheck`

#### Notes
- Rye automatically reads dependencies and scripts from the `pyproject.toml` file.
- No need for `requirements.txt`, as Rye manages all dependencies!

## 💡 Usage

The library is designed to be easy to use and integrate with your own projects. Below is an example of how you can
configure and run GSP-Py.

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

Import the `GSP` class from the `gsppy` package and call the `search` method to find frequent patterns with a support
threshold (e.g., `0.3`):

```python
from gsppy.gsp import GSP

# Example transactions: customer purchases
transactions = [
    ['Bread', 'Milk'],  # Transaction 1
    ['Bread', 'Diaper', 'Beer', 'Eggs'],  # Transaction 2
    ['Milk', 'Diaper', 'Beer', 'Coke'],  # Transaction 3
    ['Bread', 'Milk', 'Diaper', 'Beer'],  # Transaction 4
    ['Bread', 'Milk', 'Diaper', 'Coke']  # Transaction 5
]

# Set minimum support threshold (30%)
min_support = 0.3

# Find frequent patterns
result = GSP(transactions).search(min_support)

# Output the results
print(result)
```

### Output

The algorithm will return a list of patterns with their corresponding support.

Sample Output:

```python
[
    {('Bread',): 4, ('Milk',): 4, ('Diaper',): 4, ('Beer',): 3, ('Coke',): 2},
    {('Bread', 'Milk'): 3, ('Milk', 'Diaper'): 3, ('Diaper', 'Beer'): 3},
    {('Bread', 'Milk', 'Diaper'): 2, ('Milk', 'Diaper', 'Beer'): 2}
]
```

- The **first dictionary** contains single-item sequences with their frequencies (e.g., `('Bread',): 4` means "Bread"
  appears in 4 transactions).
- The **second dictionary** contains 2-item sequential patterns (e.g., `('Bread', 'Milk'): 3` means the sequence "
  Bread → Milk" appears in 3 transactions).
- The **third dictionary** contains 3-item sequential patterns (e.g., `('Bread', 'Milk', 'Diaper'): 2` means the
  sequence "Bread → Milk → Diaper" appears in 2 transactions).

> [!NOTE]
> The **support** of a sequence is calculated as the fraction of transactions containing the sequence, e.g.,
`[Bread, Milk]` appears in 3 out of 5 transactions → Support = `3 / 5 = 0.6` (60%).
> This insight helps identify frequently occurring sequential patterns in datasets, such as shopping trends or user
> behavior.


> [!TIP]
> For more complex examples, find example scripts in the [`gsppy/tests`](gsppy/tests) folder.

---

## 🌟 Planned Features

We are actively working to improve GSP-Py. Here are some exciting features planned for future releases:

1. **Custom Filters for Candidate Pruning**:
    - Enable users to define their own pruning logic during the mining process.

2. **Support for Preprocessing and Postprocessing**:
    - Add hooks to allow users to transform datasets before mining and customize the output results.

3. **Support for Time-Constrained Pattern Mining**:
    - Extend GSP-Py to handle temporal datasets by allowing users to define time constraints (e.g., maximum time gaps
      between events, time windows) during the sequence mining process.
    - Enable candidate pruning and support calculations based on these temporal constraints.

Want to contribute or suggest an
improvement? [Open a discussion or issue!](https://github.com/jacksonpradolima/gsp-py/issues)

---

## 🤝 Contributing

We welcome contributions from the community! If you'd like to help improve GSP-Py, read
our [CONTRIBUTING.md](CONTRIBUTING.md) guide to get started.

Development dependencies (e.g., testing and linting tools) are included in the `dev` category in `setup.py`. To install
these dependencies, run:

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

```
@misc{pradolima_gsppy,
  author       = {Prado Lima, Jackson Antonio do},
  title        = {{GSP-Py - Generalized Sequence Pattern algorithm in Python}},
  month        = Dec,
  year         = 2024,
  doi          = {10.5281/zenodo.3333987},
  url          = {https://doi.org/10.5281/zenodo.3333987}
}
```
