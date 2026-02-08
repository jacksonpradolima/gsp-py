#!/usr/bin/env python3
"""
Fuzzing test runner script for GSP-Py.

This script demonstrates how to run property-based fuzzing tests
for the GSP algorithm. It can be used locally or in CI/CD pipelines.

Usage:
    python run_fuzzing_tests.py                     # Run all fuzzing tests
    python run_fuzzing_tests.py --suite edge       # Run edge-case tests only
    python run_fuzzing_tests.py --suite cli        # Run CLI fuzzing tests only
    python run_fuzzing_tests.py --seed 42          # Run with specific seed
    python run_fuzzing_tests.py --verbose          # Verbose output

Author: Jackson Antonio do Prado Lima
Email: jacksonpradolima@gmail.com
"""

import sys
import argparse
import subprocess
from typing import List, Optional
from pathlib import Path


def run_pytest(
    test_paths: List[str],
    verbose: bool = True,
    seed: Optional[int] = None,
    extra_args: Optional[List[str]] = None
) -> int:
    """
    Run pytest with specified parameters.
    
    Args:
        test_paths: List of test file paths or patterns
        verbose: Enable verbose output
        seed: Hypothesis random seed for reproducibility
        extra_args: Additional pytest arguments
        
    Returns:
        Exit code from pytest
    """
    cmd = [sys.executable, "-m", "pytest"]
    
    # Add test paths
    cmd.extend(test_paths)
    
    # Add verbosity
    if verbose:
        cmd.append("-v")
    
    # Add Hypothesis seed (this is a valid pytest argument)
    if seed is not None:
        cmd.append(f"--hypothesis-seed={seed}")
    
    # Add extra arguments
    if extra_args:
        cmd.extend(extra_args)
    
    # Show command being run
    print(f"Running: {' '.join(cmd)}")
    print("-" * 80)
    
    # Run pytest
    result = subprocess.run(cmd, cwd=Path(__file__).parent.parent)
    return result.returncode


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run property-based fuzzing tests for GSP-Py",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all fuzzing tests
  python run_fuzzing_tests.py
  
  # Run only edge-case tests
  python run_fuzzing_tests.py --suite edge
  
  # Run CLI fuzzing with specific seed
  python run_fuzzing_tests.py --suite cli --seed 42
  
  # Run with coverage
  python run_fuzzing_tests.py --coverage
        """
    )
    
    parser.add_argument(
        "--suite",
        choices=["all", "standard", "edge", "cli"],
        default="all",
        help="Which test suite to run (default: all)"
    )
    
    parser.add_argument(
        "--seed",
        type=int,
        help="Hypothesis random seed for reproducibility"
    )
    
    parser.add_argument(
        "--verbose",
        "-v",
        dest="verbose",
        action="store_true",
        default=True,
        help="Enable verbose output (default: enabled)"
    )
    
    parser.add_argument(
        "--quiet",
        "-q",
        dest="verbose",
        action="store_false",
        help="Disable verbose output"
    )
    
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Run with coverage reporting"
    )
    
    args = parser.parse_args()
    
    # Determine which tests to run
    if args.suite == "all":
        test_paths = [
            "tests/test_gsp_fuzzing.py",
            "tests/test_gsp_edge_cases.py",
            "tests/test_cli_fuzzing.py"
        ]
    elif args.suite == "standard":
        test_paths = ["tests/test_gsp_fuzzing.py"]
    elif args.suite == "edge":
        test_paths = ["tests/test_gsp_edge_cases.py"]
    elif args.suite == "cli":
        test_paths = ["tests/test_cli_fuzzing.py"]
    else:
        print(f"Unknown suite: {args.suite}", file=sys.stderr)
        return 1
    
    # Build extra arguments
    extra_args = []
    
    if args.coverage:
        extra_args.extend(["--cov=gsppy", "--cov-report=term", "--cov-report=html"])
    
    # Run tests
    print("=" * 80)
    print("GSP-Py Property-Based Fuzzing Tests")
    print("=" * 80)
    print(f"Suite: {args.suite}")
    if args.seed is not None:
        print(f"Random seed: {args.seed}")
    print("=" * 80)
    print()
    
    return run_pytest(
        test_paths=test_paths,
        verbose=args.verbose,
        seed=args.seed,
        extra_args=extra_args
    )


if __name__ == "__main__":
    sys.exit(main())
