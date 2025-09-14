import os
import time
import random
from typing import List, Optional

import click

from gsppy.gsp import GSP

random.seed(0)


def gen_data(n_tx: int, tx_len: int, vocab_size: int) -> List[List[str]]:
    vocab = [f"I{i}" for i in range(vocab_size)]
    # Using comprehension keeps it simple; for very large n, consider streaming
    return [random.sample(vocab, tx_len) for _ in range(n_tx)]


def run_once(backend: str, transactions: List[List[str]], min_support: float, max_k: Optional[int]) -> float:
    os.environ["GSPPY_BACKEND"] = backend
    t0 = time.perf_counter()
    GSP(transactions).search(min_support=min_support, max_k=max_k)
    return time.perf_counter() - t0


@click.command()
@click.option("--n_tx", default=10_000, show_default=True, type=int, help="Number of transactions (e.g., 1_000_000)")
@click.option("--tx_len", default=8, show_default=True, type=int, help="Items per transaction")
@click.option("--vocab", default=10_000, show_default=True, type=int, help="Vocabulary size")
@click.option("--min_support", default=0.2, show_default=True, type=float, help="Minimum fractional support (0,1]")
@click.option(
    "--max_k",
    default=1,
    show_default=True,
    type=int,
    help="Limit maximum sequence length (1 focuses on singleton support)",
)
@click.option("--warmup", is_flag=True, help="Do a Python warmup run before timing")
def main(n_tx: int, tx_len: int, vocab: int, min_support: float, max_k: int, warmup: bool) -> None:
    click.echo(f"Generating data: n_tx={n_tx:,}, tx_len={tx_len}, vocab={vocab:,}")
    transactions = gen_data(n_tx=n_tx, tx_len=tx_len, vocab_size=vocab)

    if warmup:
        try:
            run_once("python", transactions, min_support, max_k)
        except Exception:
            pass

    click.echo("Running Python backend...")
    t_py = run_once("python", transactions, min_support, max_k)

    click.echo("Running Rust backend...")
    try:
        t_rs = run_once("rust", transactions, min_support, max_k)
        speedup = t_py / t_rs if t_rs > 0 else float("inf")
        improvement = (t_py - t_rs) / t_py * 100.0
        click.echo(f"Python: {t_py:.3f}s\nRust:   {t_rs:.3f}s\nSpeedup: {speedup:.2f}x  (+{improvement:.1f}%)")
    except Exception as e:
        click.echo(f"Rust backend not available or failed: {e}\nPython time: {t_py:.3f}s")


if __name__ == "__main__":
    main()
