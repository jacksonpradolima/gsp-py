# Typing

GSP-Py ships with strict type checking to keep the API predictable.

- **Type checkers:** Pyright runs in `strict` mode (see `pyproject.toml`), and ty provides fast type checking.
- **Type hints:** Public functions annotate arguments and return values, making them compatible with mkdocstrings.
- **Optional tools:** ty can be run locally via `uv run ty check` for fast type checking.

When adding new code, prefer explicit types over inference and keep public docstrings aligned with the annotated
signatures so rendered API docs remain accurate.
