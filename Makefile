SHELL := /bin/bash
# Resolve uv path: if not found in PATH, default to ~/.local/bin/uv (where installer places it)
UV := $(shell command -v uv 2>/dev/null || echo $(HOME)/.local/bin/uv)
PYTHON := .venv/bin/python
PYTEST := .venv/bin/pytest
PRE_COMMIT := .venv/bin/pre-commit

# Default link mode for uv to avoid hardlink warnings on some filesystems
export UV_LINK_MODE ?= copy

.DEFAULT_GOAL := help

.PHONY: help ensure-uv setup install dev-install test coverage lint format typecheck tox pre-commit-install pre-commit-run pre-commit-autoupdate clean check check-precommit

help:
	@echo "Available targets:"
	@echo "  setup                  - Create .venv using Python 3.13 (downloads if needed)"
	@echo "  install                - Install deps from lockfiles and project in editable mode"
	@echo "  dev-install            - install + ensure pre-commit is available"
	@echo "  test                   - Run pytest in parallel (xdist)"
	@echo "  coverage               - Run tests with coverage (xml + html reports)"
	@echo "  lint                   - Run ruff lint"
	@echo "  format                 - Auto-fix with ruff"
	@echo "  typecheck              - Run pyright type checker"
	@echo "  tox                    - Run tox matrix"
	@echo "  pre-commit-install     - Install pre-commit git hook"
	@echo "  pre-commit-run         - Run pre-commit on all files"
	@echo "  pre-commit-autoupdate  - Update pre-commit hook versions"
	@echo "  clean                  - Remove build/test caches"
	@echo "  check                  - lint + typecheck + test"
	@echo "\nEnvironment:"
	@echo "  UV_LINK_MODE=$(UV_LINK_MODE) (default: copy)"
	@echo "\nRust acceleration:"
	@echo "  rust-setup             - Install Rust toolchain (rustup)"
	@echo "  rust-build             - Build and develop-install Rust extension via maturin (skips if up-to-date)"
	@echo "  bench-small            - Run small benchmark (default sizes)"
	@echo "  bench-big              - Run large benchmark (e.g., 1M tx; beware memory/CPU)"

# Ensure uv is installed; install if missing
ensure-uv:
	@if ! command -v $(UV) >/dev/null 2>&1; then \
	  echo "uv not found, installing..."; \
	  curl -Ls https://astral.sh/uv/install.sh | bash; \
	  echo "uv installed at $$HOME/.local/bin/uv"; \
	fi

# Default to Python 3.13 for local development
setup: ensure-uv
	$(UV) python install 3.13
	# Ensure project Python is pinned to a compatible version for uv (avoids reading an old .python-version)
	$(UV) python pin 3.13
	$(UV) venv .venv --python 3.13 --allow-existing

install: ensure-uv setup
	# Sync dependencies from uv.lock (project + dev extras) into .venv
	$(UV) sync --frozen --extra dev --extra dataframe
	# Ensure project is installed in editable mode
	$(UV) run --python $(PYTHON) --no-project pip install -e .

dev-install: ensure-uv install
	# Ensure pre-commit is present even if not in the lockfile
	$(UV) run --python $(PYTHON) --no-project pip install pre-commit

test: ensure-uv install
	# Run in parallel if xdist is available; otherwise, run serially
	@if $(UV) run --python $(PYTHON) --no-project python -c 'import xdist' >/dev/null 2>&1; then \
	  $(UV) run --python $(PYTHON) --no-project pytest -n auto; \
	else \
	  echo "pytest-xdist não encontrado; executando em série..."; \
	  $(UV) run --python $(PYTHON) --no-project pytest; \
	fi

# Coverage: generates coverage.xml and htmlcov/
coverage: ensure-uv install
	# Ensure pytest-cov is available (compatible pin for 3.8+)
	@if ! $(UV) run --python $(PYTHON) --no-project python -c 'import pytest_cov' >/dev/null 2>&1; then \
	  $(UV) pip install pytest-cov==5.0.0; \
	fi
	# Run coverage; prefer parallel if xdist is available
	@if $(UV) run --python $(PYTHON) --no-project python -c 'import xdist' >/dev/null 2>&1; then \
	  $(UV) run --python $(PYTHON) --no-project pytest -n auto \
	    --cov=gsppy --cov-branch \
	    --cov-report=term-missing:skip-covered \
	    --cov-report=xml \
	    --cov-report=html; \
	else \
	  $(UV) run --python $(PYTHON) --no-project pytest \
	    --cov=gsppy --cov-branch \
	    --cov-report=term-missing:skip-covered \
	    --cov-report=xml \
	    --cov-report=html; \
	fi

lint: ensure-uv
	$(UV) run ruff check .

format: ensure-uv
	$(UV) run ruff check --fix .

typecheck: ensure-uv
	# Run both static type checkers
	$(UV) run --python $(PYTHON) --no-project pyright gsppy
	$(UV) run --python $(PYTHON) --no-project ty check .

tox: dev-install
	# Use the project venv and avoid re-resolving the project
	$(UV) run --python $(PYTHON) --no-project tox -r

pre-commit-install: dev-install
	@if [ -x "$(PRE_COMMIT)" ]; then \
	  $(PRE_COMMIT) install; \
	else \
	  $(UV) run --python $(PYTHON) --no-project pre-commit install; \
	fi

pre-commit-run: dev-install
	@if [ -x "$(PRE_COMMIT)" ]; then \
	  $(PRE_COMMIT) run --all-files; \
	else \
	  $(UV) run --python $(PYTHON) --no-project pre-commit run --all-files; \
	fi

pre-commit-autoupdate: dev-install
	@if [ -x "$(PRE_COMMIT)" ]; then \
	  $(PRE_COMMIT) autoupdate; \
	else \
	  $(UV) run --python $(PYTHON) --no-project pre-commit autoupdate; \
	fi

clean:
	rm -rf build/ dist/ *.egg-info
	rm -rf .pytest_cache/ .ruff_cache/ .tox/ .nox/ coverage.xml htmlcov/

check: lint typecheck test

# Centralized target for pre-commit: runs tests and type checks
check-precommit: ensure-uv install
	$(MAKE) test
	$(MAKE) typecheck

# --- Rust acceleration helpers ---
.PHONY: rust-setup rust-build bench-small bench-big

rust-setup:
	@if ! command -v rustc >/dev/null 2>&1; then \
	  echo "Installing Rust toolchain..."; \
	  curl -Ls https://sh.rustup.rs | bash -s -- -y; \
	  source $$HOME/.cargo/env; \
	  rustc --version; \
	else \
	  rustc --version; \
	fi

rust-build: ensure-uv rust-setup
	@# Optionally force rebuild: make rust-build FORCE_RUST_BUILD=1
	@force_build="$(FORCE_RUST_BUILD)"; \
	 if [ "$$force_build" = "1" ]; then \
	   echo "FORCE_RUST_BUILD=1 set; rebuilding Rust extension"; \
	   source $$HOME/.cargo/env; \
	   $(UV) pip install --python $(PYTHON) --upgrade pip setuptools wheel maturin==1.6.0 >/dev/null; \
	   $(UV) run --python $(PYTHON) --no-project python -m maturin develop --release -m rust/Cargo.toml; \
	   exit $$?; \
	 fi; \
	 # Determine if extension is already installed and up-to-date (resolve the .so path) \
	 so_path="$$( \
	   $(UV) run --python $(PYTHON) --no-project python -c 'import importlib.util as u; s=u.find_spec("_gsppy_rust._gsppy_rust"); print(s.origin if s and s.origin else(""))' \
	 )"; \
	 if [ -n "$$so_path" ] && [ -f "$$so_path" ]; then \
	   up_to_date=1; \
	   for src in rust/Cargo.toml $$(find rust/src -type f -name '*.rs'); do \
	     if [ "$$src" -nt "$$so_path" ]; then up_to_date=0; break; fi; \
	   done; \
	   if [ "$$up_to_date" -eq 1 ]; then \
	     echo "Rust extension is up-to-date at $$so_path; skipping build"; \
	     exit 0; \
	   else \
	     echo "Rust sources changed; rebuilding"; \
	   fi; \
	 else \
	   echo "Rust extension missing; building"; \
	 fi; \
	 source $$HOME/.cargo/env; \
	 $(UV) pip install --python $(PYTHON) --upgrade pip setuptools wheel maturin==1.6.0 >/dev/null; \
	 $(UV) run --python $(PYTHON) --no-project python -m maturin develop --release -m rust/Cargo.toml

bench-small: rust-build
	@$(UV) run --python $(PYTHON) --no-project pip install -e . >/dev/null; \
	 GSPPY_BACKEND=auto $(UV) run --python $(PYTHON) --no-project python benchmarks/bench_support.py --n_tx 100000 --tx_len 8 --vocab 10 --min_support 0.2 --warmup

bench-big: rust-build
	@echo "WARNING: This may take significant memory/CPU. Adjust sizes to your machine."; \
	 $(UV) run --python $(PYTHON) --no-project pip install -e . >/dev/null; \
	 GSPPY_BACKEND=auto $(UV) run --python $(PYTHON) --no-project python benchmarks/bench_support.py --n_tx 1000000 --tx_len 8 --vocab 50000 --min_support 0.2
