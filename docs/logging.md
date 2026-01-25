# Logging and Verbosity

GSP-Py provides explicit verbosity control and standardized logging output for both API and CLI usage. This enables developers, researchers, and operators to trace execution, debug issues, and integrate GSP-Py into automated workflows.

## Overview

- **Default Mode**: Minimal output (WARNING level and above) for clean, production-ready execution
- **Verbose Mode**: Detailed structured logging with timestamps, log levels, process IDs, and execution context

## CLI Usage

### Basic Usage (Non-Verbose)

By default, the CLI produces clean, minimal output:

```bash
gsppy --file transactions.json --min_support 0.3
```

Output example:
```
Frequent Patterns Found:

1-Sequence Patterns:
Pattern: ('Bread',), Support: 4
Pattern: ('Milk',), Support: 4
...
```

### Verbose Mode

Enable detailed logging with the `--verbose` flag:

```bash
gsppy --file transactions.json --min_support 0.3 --verbose
```

Output example with structured logging:
```
2026-01-25T23:09:50 | INFO     | PID:4179 | gsppy.gsp | Pre-processing transactions...
2026-01-25T23:09:50 | DEBUG    | PID:4179 | gsppy.gsp | Unique candidates: [('Bread',), ('Milk',), ...]
2026-01-25T23:09:50 | INFO     | PID:4179 | gsppy.gsp | Starting GSP algorithm with min_support=0.3...
2026-01-25T23:09:50 | INFO     | PID:4179 | gsppy.gsp | Run 1: 6 candidates filtered to 5.
2026-01-25T23:09:50 | INFO     | PID:4179 | gsppy.gsp | Run 2: 20 candidates filtered to 8.
...
```

## API Usage

### Basic Usage (Non-Verbose)

By default, GSP instances operate in silent mode:

```python
from gsppy.gsp import GSP

transactions = [
    ["Bread", "Milk"],
    ["Bread", "Diaper", "Beer"],
    ["Milk", "Diaper", "Beer"],
]

# Non-verbose mode (default)
gsp = GSP(transactions)
patterns = gsp.search(min_support=0.3)
```

### Verbose Mode in Initialization

Enable verbose logging for the entire GSP instance:

```python
from gsppy.gsp import GSP

# Enable verbose mode for all operations
gsp = GSP(transactions, verbose=True)
patterns = gsp.search(min_support=0.3)
```

### Verbose Mode Per Search

Override verbosity for specific search operations:

```python
from gsppy.gsp import GSP

# Instance with verbose=False (default)
gsp = GSP(transactions, verbose=False)

# Enable verbose for this specific search
patterns = gsp.search(min_support=0.3, verbose=True)

# Back to non-verbose for subsequent searches
patterns2 = gsp.search(min_support=0.5)
```

## Log Format

### Verbose Mode Format

When verbose mode is enabled, logs follow this structure:

```
<timestamp> | <level> | PID:<process_id> | <module> | <message>
```

Components:
- **Timestamp**: ISO 8601 format (`YYYY-MM-DDTHH:MM:SS`) for precise time tracking
- **Level**: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- **PID**: Process ID for multi-process traceability
- **Module**: Source module (e.g., `gsppy.gsp`, `gsppy.cli`)
- **Message**: The actual log message with execution details

### Default Mode Format

In default (non-verbose) mode, only the message is shown for clean output:

```
<message>
```

## Log Levels

GSP-Py uses standard Python logging levels:

- **DEBUG**: Detailed diagnostic information (only in verbose mode)
  - Candidate generation details
  - Preprocessing information
  - Transaction statistics
  
- **INFO**: General informational messages
  - Algorithm start/completion
  - Progress updates (e.g., "Run 1: 6 candidates filtered to 5")
  - Pattern discovery summary
  
- **WARNING**: Warning messages (shown in both modes)
  - Temporal constraints ignored when timestamps absent
  - Configuration issues
  
- **ERROR**: Error messages (always shown)
  - Invalid input data
  - Invalid parameters
  - Algorithm failures

## Integration with CI/CD and Automation

### Capturing Logs in Scripts

```bash
#!/bin/bash
# Capture verbose logs to a file
gsppy --file data.json --min_support 0.3 --verbose > gsp_output.log 2>&1

# Extract specific information
grep "Starting GSP algorithm" gsp_output.log
grep "Run [0-9]:" gsp_output.log
```

### Filtering by Log Level

```bash
# Only show errors
gsppy --file data.json --min_support 0.3 2>&1 | grep "ERROR"

# Show INFO and above in verbose mode
gsppy --file data.json --min_support 0.3 --verbose 2>&1 | grep -E "INFO|WARNING|ERROR"
```

### Using with Python Logging Infrastructure

Integrate GSP-Py logging with your application's logging system:

```python
import logging
from gsppy.gsp import GSP

# Configure your application's logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('application.log'),
        logging.StreamHandler()
    ]
)

# GSP will respect your logging configuration
gsp = GSP(transactions, verbose=True)
patterns = gsp.search(min_support=0.3)
```

## Traceability Metadata

When running in verbose mode, GSP-Py provides rich metadata for traceability:

1. **Process ID (PID)**: Identifies which process generated each log entry
   - Useful in multi-process environments
   - Helps trace execution in distributed systems
   
2. **Timestamps**: Precise timing information
   - ISO 8601 format for international compatibility
   - Microsecond precision for performance analysis
   
3. **Module Context**: Shows which component generated the log
   - `gsppy.gsp`: Core algorithm execution
   - `gsppy.cli`: CLI-specific operations
   - Helps identify bottlenecks and issues

4. **Iteration Information**: Progress tracking
   - Current k-sequence level
   - Number of candidates generated vs. filtered
   - Helps understand algorithm progression

## Best Practices

### Development and Debugging

```python
# Use verbose mode during development
gsp = GSP(transactions, verbose=True)
```

### Production Deployment

```python
# Keep verbose=False (default) for production
gsp = GSP(transactions)  # Clean output
```

### Automated Testing

```bash
# Verbose mode for CI/CD diagnostics
if [ "$CI" = "true" ]; then
  gsppy --file test_data.json --min_support 0.3 --verbose
else
  gsppy --file test_data.json --min_support 0.3
fi
```

### Research and Analysis

```python
import logging

# Set up detailed logging for research
logging.basicConfig(
    level=logging.DEBUG,
    filename=f'gsp_experiment_{timestamp}.log',
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s'
)

gsp = GSP(transactions, verbose=True)
results = gsp.search(min_support=0.3)
```

## Performance Considerations

- Verbose mode adds minimal overhead (typically < 5%)
- Log formatting is optimized for production use
- Process ID lookup is cached for efficiency
- Timestamp generation uses high-resolution timers

## Customization

For advanced logging customization, you can configure Python's logging module directly:

```python
import logging

# Custom formatter
formatter = logging.Formatter(
    '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Add custom handler
handler = logging.FileHandler('gsp_custom.log')
handler.setFormatter(formatter)
logging.getLogger('gsppy').addHandler(handler)

# Use GSP with custom logging
gsp = GSP(transactions, verbose=True)
patterns = gsp.search(min_support=0.3)
```

## Examples

### Example 1: Debugging Algorithm Behavior

```python
from gsppy.gsp import GSP

transactions = [
    ["A", "B", "C"],
    ["A", "C"],
    ["B", "C"],
]

# Enable verbose to see candidate generation
gsp = GSP(transactions, verbose=True)
patterns = gsp.search(min_support=0.5)
```

### Example 2: Silent Batch Processing

```python
# Process multiple datasets silently
for dataset in datasets:
    gsp = GSP(dataset)  # No verbose output
    patterns = gsp.search(min_support=0.3)
    save_results(patterns)
```

### Example 3: Conditional Verbosity

```python
import os

# Enable verbose in development environment
is_dev = os.getenv('ENV') == 'development'
gsp = GSP(transactions, verbose=is_dev)
patterns = gsp.search(min_support=0.3)
```
