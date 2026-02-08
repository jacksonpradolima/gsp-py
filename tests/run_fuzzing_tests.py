#!/usr/bin/env python3
"""
Fuzzing test runner script for GSP-Py.

This script demonstrates how to run property-based fuzzing tests
for the GSP algorithm. It can be used locally or in CI/CD pipelines.

Usage:
    python run_fuzzing_tests.py                     # Run all fuzzing tests
    python run_fuzzing_tests.py --suite edge       # Run edge-case tests only
    python run_fuzzing_tests.py --suite cli        # Run CLI fuzzing tests only
    python run_fuzzing_tests.py --examples 200     # Run with custom example count
    python run_fuzzing_tests.py --verbose          # Verbose output

Author: Jackson Antonio do Prado Lima
Email: jacksonpradolima@gmail.com
"""

import sys
import argparse
import subprocess
from pathlib import Path
from typing import List, Optional


def run_pytest(
    test_paths: List[str],
    verbose: bool = True,
    max_examples: Optional[int] = None,
    seed: Optional[int] = None,
    extra_args: Optional[List[str]] = None
) -> int:
    """
    Run pytest with specified parameters.
    
    Args:
        test_paths: List of test file paths or patterns
        verbose: Enable verbose output
        max_examples: Override Hypothesis max_examples setting
        seed: Hypothesis random seed for reproducibility
        extra_args: Additional pytest arguments
        
    Returns:
        Exit code from pytest
    """
    cmd = ["python3", "-m", "pytest"]
    
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
    
    # Set environment variable for max_examples if specified
    import os
    env = os.environ.copy()
    if max_examples:
        print(f"Note: max_examples override ({max_examples}) requires modifying test code or using profiles")
        print("      Running with default example count from tests")
    
    # Run pytest
    result = subprocess.run(cmd, cwd=Path(__file__).parent.parent, env=env)
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
  
  # Run only edge-case tests with more examples
  python run_fuzzing_tests.py --suite edge --examples 200
  
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
        "--examples",
        type=int,
        help="Override Hypothesis max_examples setting"
    )
    
    parser.add_argument(
        "--seed",
        type=int,
        help="Hypothesis random seed for reproducibility"
    )
    
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output (default: enabled)"
    )
    
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Run with coverage reporting"
    )
    
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Quick run with fewer examples (for rapid testing)"
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
    
    if args.quick:
        # Override max_examples for quick testing
        args.examples = args.examples or 10
    
    # Run tests
    print("=" * 80)
    print("GSP-Py Property-Based Fuzzing Tests")
    print("=" * 80)
    print(f"Suite: {args.suite}")
    if args.examples:
        print(f"Max examples: {args.examples}")
    if args.seed is not None:
        print(f"Random seed: {args.seed}")
    print("=" * 80)
    print()
    
    return run_pytest(
        test_paths=test_paths,
        verbose=args.verbose,
        max_examples=args.examples,
        seed=args.seed,
        extra_args=extra_args
    )


if __name__ == "__main__":
    sys.exit(main())
