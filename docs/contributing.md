# Contributing

Contributions are welcome! Please review the repository's contribution guidelines and code-quality tools before
submitting a pull request.

## Development setup

1. Install uv and create a virtual environment:

   ```bash
   uv venv .venv
   uv sync --frozen --extra dev
   uv pip install -e .
   ```

2. Run quality checks locally:

   ```bash
   uv run ruff check .
   uv run pyright
   uv run pytest -n auto
   ```

3. Optional: build the Rust extension for faster local testing:

   ```bash
   make rust-build
   ```

## Pull requests

- Keep changes focused and include tests where practical.
- Update documentation when user-facing behavior changes.
- Ensure type hints remain accurate; see the [Typing](typing.md) page for details.
