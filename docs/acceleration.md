# Acceleration

GSP-Py supports multiple acceleration backends for computing support counts. Backend selection can be controlled via the
`backend` keyword argument on `GSP.search` or through the `GSPPY_BACKEND` environment variable.

## Backends

- **Rust (`rust`)**: Uses the optional `_gsppy_rust` PyO3 extension for fast support counting. This is attempted first
  when running with the default `auto` backend.
- **GPU (`gpu`)**: Experimental CuPy-backed singleton counting. Falls back to CPU for longer sequences.
- **Python (`python`)**: Pure-Python implementation for environments without compiled extensions or GPUs.
- **Auto (`auto`)**: Default behavior that tries Rust, then Python. When `GSPPY_BACKEND` is set to `gpu`, GPU handling is
  preferred for singletons.

## Environment variables

- `GSPPY_BACKEND`: Chooses the backend (`auto`, `python`, `rust`, or `gpu`).

## Installation tips

- Install the Rust extension locally with `make rust-build` or include the `rust` extra when using uv:

  ```bash
  uv sync --extra rust
  ```

- Install GPU support with the `gpu` extra (ensure that the correct CuPy build for your CUDA/ROCm stack is selected):

  ```bash
  uv sync --extra gpu
  ```

If a backend is unavailable, the library automatically falls back to the pure-Python implementation unless an explicit
backend is required.
