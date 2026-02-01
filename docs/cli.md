# Command-Line Interface

The `gsppy` CLI runs the Generalized Sequential Pattern algorithm on transactions stored in multiple file formats including JSON, CSV, SPM/GSP, Parquet, and Arrow.

## Usage

```bash
gsppy --file transactions.json --min_support 0.3 --backend rust --verbose
```

### Options

- `--file PATH` (required): Path to a transaction file. Supported formats: JSON, CSV, SPM, Parquet, Arrow.
- `--format [auto|json|csv|spm|parquet|arrow]`: File format to use (default: `auto`). Auto-detection works based on file extension.
- `--min_support FLOAT`: Minimum support threshold as a fraction of total transactions (default: `0.2`).
- `--backend [auto|python|rust|gpu]`: Backend for support counting (default: `auto`).
- `--verbose`: Enables verbose logging for debugging and progress visibility.
- `--mingap FLOAT`: Minimum time gap between consecutive items (requires timestamped transactions).
- `--maxgap FLOAT`: Maximum time gap between consecutive items (requires timestamped transactions).
- `--maxspan FLOAT`: Maximum time span from first to last item (requires timestamped transactions).
- `--transaction-col TEXT`: Column name for transaction IDs (Parquet/Arrow only).
- `--item-col TEXT`: Column name for items (Parquet/Arrow only).
- `--timestamp-col TEXT`: Column name for timestamps (Parquet/Arrow only).
- `--sequence-col TEXT`: Column name for sequences (Parquet/Arrow only).

## Examples

### Basic Usage

```bash
# JSON format
cat <<'DATA' > sample.json
[["A", "B", "C"], ["A", "C"], ["A", "B"]]
DATA

# Run with default settings
gsppy --file sample.json --min_support 0.4
```

### SPM/GSP Format

The SPM/GSP format is a classical format for sequential pattern mining datasets using delimiters:
- `-1`: Marks the end of an element (itemset)
- `-2`: Marks the end of a sequence (transaction)

```bash
# Create SPM format file
cat <<'DATA' > sample.txt
1 2 -1 3 -1 -2
4 -1 5 6 -1 -2
1 -1 2 3 -1 -2
DATA

# Load with explicit format specification
gsppy --file sample.txt --format spm --min_support 0.5
```

### CSV Format

```bash
cat <<'DATA' > sample.csv
A,B,C
A,C
A,B
DATA

gsppy --file sample.csv --min_support 0.4
```

### Parquet/Arrow Format

For DataFrame formats (requires `gsppy[dataframe]` extra):

```bash
# Install with DataFrame support
pip install 'gsppy[dataframe]'

# Parquet with transaction-item structure
gsppy --file data.parquet --min_support 0.3 \
      --transaction-col txn_id --item-col product

# Arrow with sequence column
gsppy --file sequences.arrow --min_support 0.3 \
      --sequence-col items
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
YYYY-MM-DDTHH:MM:SS | INFO | PID:4179 | gsppy.gsp | Pre-processing transactions...
YYYY-MM-DDTHH:MM:SS | DEBUG | PID:4179 | gsppy.gsp | Unique candidates: [('A',), ('B',), ('C',)]
YYYY-MM-DDTHH:MM:SS | INFO | PID:4179 | gsppy.gsp | Starting GSP algorithm with min_support=0.4...
...
```

Results are printed to standard output, grouped by sequence length.
