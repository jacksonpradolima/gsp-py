# Typing

GSP-Py ships with strict type checking to keep the API predictable.

- **Type checker:** Pyright runs in `strict` mode (see `pyproject.toml`).
- **Type hints:** Public functions annotate arguments and return values, making them compatible with mkdocstrings.
- **Optional tools:** Mypy can be enabled locally via `uv run mypy` if desired.

When adding new code, prefer explicit types over inference and keep public docstrings aligned with the annotated
signatures so rendered API docs remain accurate.
