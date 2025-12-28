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
