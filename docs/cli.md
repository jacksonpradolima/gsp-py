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
- `--mingap FLOAT`: Minimum time gap between consecutive items (requires timestamped transactions).
- `--maxgap FLOAT`: Maximum time gap between consecutive items (requires timestamped transactions).
- `--maxspan FLOAT`: Maximum time span from first to last item (requires timestamped transactions).

## Examples

### Basic Usage

```bash
cat <<'DATA' > sample.json
[["A", "B", "C"], ["A", "C"], ["A", "B"]]
DATA

# Run with default settings
gsppy --file sample.json --min_support 0.4
```

### Verbose Mode

Enable detailed logging with timestamps and progress information:

```bash
# Verbose output with structured logging
gsppy --file sample.json --min_support 0.4 --verbose
```

Output includes:
- Timestamps in ISO 8601 format
- Log levels (DEBUG, INFO, WARNING, ERROR)
- Process ID for traceability
- Module context and detailed progress

For complete logging documentation, see the [Logging Guide](logging.md).

### With Acceleration

```bash
# Run with Rust acceleration if available
GSPPY_BACKEND=rust gsppy --file sample.json --min_support 0.4
```

### With Temporal Constraints

```bash
# Timestamped transaction file
cat <<'DATA' > temporal.json
[[["A", 1], ["B", 3], ["C", 5]], [["A", 2], ["B", 10]]]
DATA

# Apply time constraints
gsppy --file temporal.json --min_support 0.5 --maxgap 5 --verbose
```

## Output Format

### Default Mode

Clean, minimal output suitable for production:

```
Frequent Patterns Found:

1-Sequence Patterns:
Pattern: ('A',), Support: 3
Pattern: ('B',), Support: 2
...
```

### Verbose Mode

Detailed structured output for debugging and analysis:

```
2026-01-25T23:09:50 | INFO | PID:4179 | gsppy.gsp | Pre-processing transactions...
2026-01-25T23:09:50 | DEBUG | PID:4179 | gsppy.gsp | Unique candidates: [('A',), ('B',), ('C',)]
2026-01-25T23:09:50 | INFO | PID:4179 | gsppy.gsp | Starting GSP algorithm with min_support=0.4...
...
```

Results are printed to standard output, grouped by sequence length.
