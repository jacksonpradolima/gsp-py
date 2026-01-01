# Command-Line Interface

The `gsppy` CLI runs the Generalized Sequential Pattern algorithm on transactions stored in JSON or CSV files.

## Usage

```bash
gsppy --file transactions.json --min_support 0.3 --backend rust --verbose
```

### Options

- `--file PATH` (required): Path to a JSON or CSV file containing transactions.
- `--min_support FLOAT`: Minimum support threshold as a fraction of total transactions (default: `0.2`).
- `--backend [auto|python|rust|gpu]`: Backend for support counting (default: `auto`).
- `--verbose`: Enables verbose logging for debugging and progress visibility.

## Example

```bash
cat <<'DATA' > sample.json
[["A", "B", "C"], ["A", "C"], ["A", "B"]]
DATA

# Run with Rust acceleration if available
GSPPY_BACKEND=rust gsppy --file sample.json --min_support 0.4
```

Results are printed to standard output, grouped by sequence length.
