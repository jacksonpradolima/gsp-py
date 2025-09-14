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
	$(UV) sync --frozen --extra dev
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
	$(UV) run --python $(PYTHON) --no-project mypy .

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
	rm -rf .pytest_cache/ .ruff_cache/ .mypy_cache/ .tox/ .nox/ coverage.xml htmlcov/

check: lint typecheck test

# Centralized target for pre-commit: runs tests and type checks
check-precommit: ensure-uv install
	$(MAKE) test
	$(MAKE) typecheck
