# GSP-Py
Generalized Sequence Pattern (GSP) algorithm in Python

[![PyPI License](https://img.shields.io/pypi/l/jMetalPy.svg?style=flat-square)]()
[![PyPI Python version](https://img.shields.io/pypi/pyversions/jMetalPy.svg?style=flat-square)]()
[![DOI](https://zenodo.org/badge/108451832.svg)](https://zenodo.org/badge/latestdoi/108451832)

This package was created to use GSP with Python
## Table of Contents
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)
- [Citation](#citation)

## Requirements

Install Python:

```console
sudo apt install python3
```

## Installation
To download GSP-Py just clone the Git repository hosted in GitHub:

```console
git clone https://github.com/jacksonpradolima/gsp-py.git
python setup.py install
```

Alternatively, you can install it with `pip`:

```console
pip install gsppy
```

## Usage
Examples of configuring and running are located in the *test* folders [gsppy folder](gsppy).

To use it in a project, import it and use the GSP class.

```console
from gsppy.gsp import GSP
```

It is assumed that your transactions are a sequence of sequences representing items in baskets. 

```console
 transactions = [
            ['Bread', 'Milk'],
            ['Bread', 'Diaper', 'Beer', 'Eggs'],
            ['Milk', 'Diaper', 'Beer', 'Coke'],
            ['Bread', 'Milk', 'Diaper', 'Beer'],
            ['Bread', 'Milk', 'Diaper', 'Coke']
        ]
```

Init the class to prepare the transactions and to find patterns in baskets that occur over the support threshold (count):

```console
result = GSP(transactions).search(0.3)
```

The support count (or simply support) for a sequence is defined as the fraction of total data-sequences that "contain" this sequence.
(Although the word "contains" is not strictly accurate once we incorporate taxonomies, it captures the spirt of when a data-sequence contributes to the support of a sequential pattern.)

## License
This project is licensed under the terms of the MIT - see the [LICENSE](LICENSE) file for details.

# Citation

If this package contributes to a project which leads to a scientific publication, I would appreciate a citation.

```
@misc{pradolima_gsppy,
  author       = {Prado Lima, Jackson Antonio do},
  title        = {{GSP-Py - Generalized Sequence Pattern algorithm in Python}},
  month        = May,
  year         = 2020,
  doi          = {10.5281/zenodo.3333987},
  url          = {https://doi.org/10.5281/zenodo.3333987}
}
```
