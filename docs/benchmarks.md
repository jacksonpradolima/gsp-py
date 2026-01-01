# Benchmarks workflow

The **Benchmarks** GitHub Actions workflow runs a reduced-size benchmark to sanity-check the Rust acceleration and, on demand, capture a Python-only baseline.

## Triggers
- Scheduled: `0 6 * * 1` (Mondays at 06:00 UTC). Runs the Rust backend sanity check only; the Python baseline job is **not** executed on scheduled runs.
- Manual: `workflow_dispatch`, with a toggle to include the Python backend baseline. The Python-only baseline job runs **only** on these manual executions when the toggle is enabled.

## What it runs
- Sets up Python 3.13 and installs dependencies with `uv`.
- Builds the Rust backend via `make rust-build` (Rust toolchain installed with `dtolnay/rust-toolchain`).
- Executes:
  ```bash
  GSPPY_BACKEND=<rust|python> uv run python benchmarks/bench_support.py \
    --n_tx 5000 --tx_len 6 --vocab 200 --min_support 0.2 --warmup
  ```
  (Python-only job skips the Rust build.)

## Artifacts
Each job uploads:
- `benchmark_<backend>.log`: CLI output from `bench_support.py`.
- `benchmark_<backend>.json`: Parsed metrics. Fields:
  - `timestamp`: UTC ISO string.
  - `backend`: `rust` or `python`.
  - `n_tx`, `tx_len`, `vocab`, `min_support`: benchmark parameters.
  - `python_time_s`: observed Python runtime (always present when parsing succeeds).
  - `rust_time_s`: observed Rust runtime (Rust job only, when available).
  - `speedup_x`: Python time divided by Rust time (Rust job when both timings exist).
  - `improvement_pct`: Percent improvement vs Python (Rust job when both timings exist).

### How to interpret results
- Prefer the JSON for automation; use the log for troubleshooting when parsing fails.
- A higher `speedup_x` or `improvement_pct` means the Rust backend is faster relative to Python.
- If the Rust backend is unavailable or fails, the log will include the Python-only timing; JSON may omit `rust_time_s` and derived fields.

### Adding regression thresholds later
If you add regression detection in the future, consider:
- Comparing `rust_time_s` against a saved baseline or an allowed max (e.g., `< 2.0s` for this trimmed workload).
- Monitoring `speedup_x` to ensure Rust remains faster than Python (e.g., `speedup_x >= 2.0`).
- Allowing configurable thresholds via workflow `inputs` so you can tighten/relax gates without code changes.
- Failing fast when parsed metrics are missing to avoid silent regressions.

# Benchmarks

Benchmark scripts in the `benchmarks/` directory measure support-counting performance across backends.

## Running benchmarks

Use the provided Makefile targets to run common benchmarks:

```bash
make bench-small
make bench-big
```

You can also run the Python benchmark script directly with custom parameters:

```bash
uv run --python .venv/bin/python --no-project \
  python benchmarks/bench_support.py --n_tx 1000000 --tx_len 8 --vocab 50000 --min_support 0.2 --warmup
```

Adjust parameters to match your hardware. Large benchmarks can be resource-intensive.
