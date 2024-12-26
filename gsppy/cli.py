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
import argparse
import csv
import json
import logging
import os
from typing import List

from gsppy.gsp import GSP


def read_transactions_from_json(file_path: str) -> List[List]:
    """
    Read transactions from a JSON file.

    Parameters:
        file_path (str): Path to the file containing transactions.

    Returns:
        List[List]: Parsed transactions from the file.

    Raises:
        ValueError: If the file cannot be read or does not contain valid JSON.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            transactions = json.load(f)
            if not isinstance(transactions, list) or not all(isinstance(t, list) for t in transactions):
                raise ValueError("File should contain a JSON array of transaction lists.")
        return transactions
    except Exception as e:
        msg = f"Error reading transaction data from JSON file '{file_path}': {e}"
        logging.error(msg)
        raise ValueError(msg) from e


def read_transactions_from_csv(file_path: str) -> List[List]:
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
        transactions = []
        with open(file_path, newline='', encoding='utf-8') as csvfile:
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


def detect_and_read_file(file_path: str) -> List[List]:
    """
    Detect file format (CSV or JSON) and read transactions.

    Parameters:
        file_path (str): Path to the file containing transactions.

    Returns:
        List[List]: Parsed transactions from the file.

    Raises:
        ValueError: If the file format is unsupported or reading fails.
    """
    if not os.path.exists(file_path):
        raise ValueError(f"File '{file_path}' does not exist.")

    _, file_extension = os.path.splitext(file_path)
    file_extension = file_extension.lower()

    if file_extension == ".json":
        return read_transactions_from_json(file_path)

    if file_extension == ".csv":
        return read_transactions_from_csv(file_path)

    raise ValueError("Unsupported file format. Please provide a JSON or CSV file.")


def main():
    """
    Main function to handle CLI input and run the GSP algorithm.

    Arguments:
        - `--file` (str): Path to a JSON or CSV file containing transactions.
        - `--min_support` (float): Minimum support threshold (default: 0.2).
    """
    parser = argparse.ArgumentParser(
        description="GSP (Generalized Sequential Pattern) Algorithm - "
                    "Find frequent sequential patterns in transactional data."
    )

    # Single file argument
    parser.add_argument(
        '--file',
        type=str,
        required=True,
        help='Path to a JSON or CSV file containing transactions (e.g., [["A", "B"], ["B", "C"]] '
             'or CSV rows per transaction)'
    )

    # Minimum support argument
    parser.add_argument(
        '--min_support',
        type=float,
        default=0.2,
        help="Minimum support threshold as a fraction of total transactions (default: 0.2)"
    )

    # Parse arguments
    args = parser.parse_args()

    # Automatically detect and load transactions
    try:
        transactions = detect_and_read_file(args.file)
    except ValueError as e:
        print(f"Error: {e}")
        return

    # Check min_support
    if args.min_support <= 0.0 or args.min_support > 1.0:
        print("Error: min_support must be in the range (0.0, 1.0].")
        return

    # Initialize and run GSP algorithm
    try:
        gsp = GSP(transactions)
        patterns = gsp.search(min_support=args.min_support)
        print("Frequent Patterns Found:")
        for i, level in enumerate(patterns, start=1):
            print(f"\n{i}-Sequence Patterns:")
            for pattern, support in level.items():
                print(f"Pattern: {pattern}, Support: {support}")
    except Exception as e:
        print(f"Error executing GSP algorithm: {e}")


if __name__ == '__main__':
    main()
