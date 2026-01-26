"""
Benchmarking script for pruning strategies in the GSP algorithm.

This script evaluates the performance impact of different pruning strategies
on the GSP algorithm by measuring execution time and memory usage. It generates
synthetic datasets and compares the effectiveness of various pruning approaches.

Key Metrics:
-----------
1. Execution Time: Total time to complete the GSP search
2. Candidate Reduction: Number of candidates pruned at each level
3. Pattern Discovery: Number of frequent patterns found
4. Memory Efficiency: Estimated memory usage based on candidate counts

Usage:
------
Run with default settings:
    python benchmarks/bench_pruning.py

Run with custom parameters:
    python benchmarks/bench_pruning.py --n_tx 1000 --vocab 100 --min_support 0.3

Compare pruning strategies:
    python benchmarks/bench_pruning.py --strategy all
"""

import time
import random
import statistics
from typing import List, Dict, Tuple, Optional
import click

from gsppy.gsp import GSP
from gsppy.pruning import (
    SupportBasedPruning,
    FrequencyBasedPruning,
    TemporalAwarePruning,
    CombinedPruning,
)

# Note: Using random module for synthetic data generation in benchmarks.
# This is safe for non-cryptographic purposes (benchmarking/testing).
# For cryptographic use cases, use the secrets module instead.
random.seed(42)  # For reproducibility


def generate_synthetic_data(n_tx: int, tx_len: int, vocab_size: int) -> List[List[str]]:
    """
    Generate synthetic transactional data for benchmarking.

    Parameters:
        n_tx: Number of transactions to generate
        tx_len: Average number of items per transaction
        vocab_size: Size of the item vocabulary

    Returns:
        List of transactions, each containing a list of items
    """
    vocab = [f"Item{i:04d}" for i in range(vocab_size)]
    transactions = []

    for _ in range(n_tx):
        # Vary transaction length slightly for realism
        # Using random for synthetic benchmark data (non-cryptographic use)
        length = max(1, tx_len + random.randint(-2, 2))
        transactions.append(random.sample(vocab, min(length, len(vocab))))

    return transactions


def run_gsp_benchmark(
    transactions: List[List[str]],
    min_support: float,
    strategy_name: str,
    strategy_config: Optional[Dict] = None,
) -> Dict[str, any]:
    """
    Run GSP with a specific pruning strategy and collect metrics.

    Parameters:
        transactions: List of transaction sequences
        min_support: Minimum support threshold
        strategy_name: Name of the pruning strategy to use
        strategy_config: Optional configuration for the pruning strategy

    Returns:
        Dictionary containing benchmark results
    """
    config = strategy_config or {}

    # Create pruning strategy
    if strategy_name == "default":
        pruning_strategy = None
    elif strategy_name == "support":
        pruning_strategy = SupportBasedPruning(min_support_fraction=min_support)
    elif strategy_name == "frequency":
        min_freq = config.get("min_frequency", max(2, int(len(transactions) * min_support)))
        pruning_strategy = FrequencyBasedPruning(min_frequency=min_freq)
    elif strategy_name == "combined":
        strategies = [
            SupportBasedPruning(min_support_fraction=min_support),
            FrequencyBasedPruning(min_frequency=config.get("min_frequency", 3)),
        ]
        pruning_strategy = CombinedPruning(strategies)
    else:
        raise ValueError(f"Unknown strategy: {strategy_name}")

    # Initialize GSP
    gsp = GSP(transactions, pruning_strategy=pruning_strategy)

    # Run search and measure time
    start_time = time.perf_counter()
    result = gsp.search(min_support=min_support)
    elapsed_time = time.perf_counter() - start_time

    # Collect metrics
    total_patterns = sum(len(level) for level in result)
    max_level = len(result)

    return {
        "strategy": strategy_name,
        "time": elapsed_time,
        "total_patterns": total_patterns,
        "max_level": max_level,
        "patterns_per_level": [len(level) for level in result],
    }


def compare_strategies(
    transactions: List[List[str]], min_support: float, strategies: List[Tuple[str, Optional[Dict]]]
) -> List[Dict]:
    """
    Compare multiple pruning strategies on the same dataset.

    Parameters:
        transactions: List of transaction sequences
        min_support: Minimum support threshold
        strategies: List of (strategy_name, config) tuples to compare

    Returns:
        List of benchmark results for each strategy
    """
    results = []

    for strategy_name, config in strategies:
        click.echo(f"\n{'='*60}")
        click.echo(f"Benchmarking: {strategy_name}")
        click.echo(f"{'='*60}")

        result = run_gsp_benchmark(transactions, min_support, strategy_name, config)
        results.append(result)

        # Display results
        click.echo(f"Execution Time:     {result['time']:.4f} seconds")
        click.echo(f"Patterns Found:     {result['total_patterns']}")
        click.echo(f"Max Pattern Length: {result['max_level']}")
        click.echo(f"Patterns per Level: {result['patterns_per_level']}")

    return results


def print_comparison_summary(results: List[Dict]) -> None:
    """
    Print a summary comparison of different strategies.

    Parameters:
        results: List of benchmark results to compare
    """
    click.echo(f"\n{'='*60}")
    click.echo("COMPARISON SUMMARY")
    click.echo(f"{'='*60}")

    # Find baseline (usually the first strategy)
    baseline = results[0]
    baseline_time = baseline["time"]

    click.echo(f"\n{'Strategy':<20} {'Time (s)':<12} {'Speedup':<10} {'Patterns':<10}")
    click.echo("-" * 60)

    for result in results:
        speedup = baseline_time / result["time"] if result["time"] > 0 else float("inf")
        click.echo(
            f"{result['strategy']:<20} {result['time']:<12.4f} "
            f"{speedup:<10.2f}x {result['total_patterns']:<10}"
        )

    # Additional statistics
    times = [r["time"] for r in results]
    click.echo(f"\n{'='*60}")
    click.echo("STATISTICS")
    click.echo(f"{'='*60}")
    click.echo(f"Fastest Strategy:  {min(results, key=lambda r: r['time'])['strategy']}")
    click.echo(f"Slowest Strategy:  {max(results, key=lambda r: r['time'])['strategy']}")
    click.echo(f"Average Time:      {statistics.mean(times):.4f} seconds")
    click.echo(f"Std Dev:           {statistics.stdev(times):.4f} seconds" if len(times) > 1 else "")


@click.command()
@click.option("--n_tx", default=1000, show_default=True, type=int, help="Number of transactions")
@click.option("--tx_len", default=8, show_default=True, type=int, help="Average items per transaction")
@click.option("--vocab", default=100, show_default=True, type=int, help="Vocabulary size")
@click.option("--min_support", default=0.2, show_default=True, type=float, help="Minimum support threshold")
@click.option(
    "--strategy",
    default="all",
    type=click.Choice(["all", "default", "support", "frequency", "combined"], case_sensitive=False),
    help="Pruning strategy to benchmark",
)
@click.option("--rounds", default=1, show_default=True, type=int, help="Number of benchmark rounds")
def main(n_tx: int, tx_len: int, vocab: int, min_support: float, strategy: str, rounds: int) -> None:
    """
    Benchmark pruning strategies for the GSP algorithm.

    This script generates synthetic transactional data and evaluates the performance
    of different pruning strategies. Use --strategy all to compare all available strategies.
    """
    click.echo("="*60)
    click.echo("GSP PRUNING STRATEGIES BENCHMARK")
    click.echo("="*60)
    click.echo(f"\nDataset Parameters:")
    click.echo(f"  Transactions:     {n_tx:,}")
    click.echo(f"  Transaction Len:  {tx_len}")
    click.echo(f"  Vocabulary Size:  {vocab:,}")
    click.echo(f"  Min Support:      {min_support}")
    click.echo(f"  Benchmark Rounds: {rounds}")

    # Generate data
    click.echo(f"\nGenerating synthetic data...")
    transactions = generate_synthetic_data(n_tx, tx_len, vocab)
    click.echo(f"Generated {len(transactions):,} transactions")

    # Define strategies to test
    if strategy == "all":
        strategies_to_test = [
            ("default", None),
            ("support", None),
            ("frequency", {"min_frequency": max(2, int(n_tx * min_support))}),
            ("combined", {"min_frequency": max(2, int(n_tx * min_support * 0.8))}),
        ]
    else:
        strategies_to_test = [(strategy, None)]

    # Run benchmarks multiple rounds if specified
    all_results = []
    for round_num in range(rounds):
        if rounds > 1:
            click.echo(f"\n{'='*60}")
            click.echo(f"Round {round_num + 1} of {rounds}")
            click.echo(f"{'='*60}")

        results = compare_strategies(transactions, min_support, strategies_to_test)
        all_results.extend(results)

    # Print summary
    if strategy == "all":
        # Aggregate results across rounds
        if rounds > 1:
            click.echo(f"\n{'='*60}")
            click.echo("AVERAGE RESULTS ACROSS ALL ROUNDS")
            click.echo(f"{'='*60}")

            # Group by strategy and average
            strategy_results = {}
            for result in all_results:
                strat_name = result["strategy"]
                if strat_name not in strategy_results:
                    strategy_results[strat_name] = {"times": [], "patterns": []}
                strategy_results[strat_name]["times"].append(result["time"])
                strategy_results[strat_name]["patterns"].append(result["total_patterns"])

            averaged_results = []
            for strat_name, data in strategy_results.items():
                averaged_results.append(
                    {
                        "strategy": strat_name,
                        "time": statistics.mean(data["times"]),
                        "total_patterns": int(statistics.mean(data["patterns"])),
                        "patterns_per_level": [],  # Not averaged for simplicity
                        "max_level": 0,  # Not averaged
                    }
                )

            print_comparison_summary(averaged_results)
        else:
            print_comparison_summary(results)

    click.echo(f"\n{'='*60}")
    click.echo("Benchmark completed!")
    click.echo(f"{'='*60}")


if __name__ == "__main__":
    main()
