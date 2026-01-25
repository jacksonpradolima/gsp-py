# CHANGELOG


## v3.4.3 (2026-01-25)

### Bug Fixes

- **publish**: Update PyPI publish action version
  ([`0f23d45`](https://github.com/jacksonpradolima/gsp-py/commit/0f23d45c8b23d8f2a811934349cb7e020f2e4695))

Signed-off-by: Jackson Antonio do Prado Lima <jacksonpradolima@users.noreply.github.com>


## v3.4.2 (2026-01-25)

### Bug Fixes

- Update PyPI publish action version
  ([`eeebf53`](https://github.com/jacksonpradolima/gsp-py/commit/eeebf53fdfd319292d739946f9725dec37a1b6ed))

Signed-off-by: Jackson Antonio do Prado Lima <jacksonpradolima@users.noreply.github.com>

### Chores

- Update uv.lock for version 3.4.1
  ([`aac8fc1`](https://github.com/jacksonpradolima/gsp-py/commit/aac8fc118aca8ed2c58f4bf265d2fa45d9fb1f41))


## v3.4.1 (2026-01-25)

### Bug Fixes

- Update checkout action to use specific tag reference
  ([`3a33cb6`](https://github.com/jacksonpradolima/gsp-py/commit/3a33cb6243ae7e9dc46fc4f883662b3c7371ea97))

Added ref input to checkout action for specific tag reference.

Signed-off-by: Jackson Antonio do Prado Lima <jacksonpradolima@users.noreply.github.com>


## v3.4.0 (2026-01-25)

### Bug Fixes

- Configure semantic release workflow for branch protection
  ([`a01912c`](https://github.com/jacksonpradolima/gsp-py/commit/a01912c9ad63ab0d28eeeb6f21278e76e45d0456))

Co-authored-by: jacksonpradolima <7774063+jacksonpradolima@users.noreply.github.com>

- Correct GPG secret condition check in workflow
  ([`5f949fe`](https://github.com/jacksonpradolima/gsp-py/commit/5f949fe28bc791b7ac7aa360f7394054f545cfe2))

Co-authored-by: jacksonpradolima <7774063+jacksonpradolima@users.noreply.github.com>

- Prevent duplicate asset uploads between workflows
  ([`eb80fc5`](https://github.com/jacksonpradolima/gsp-py/commit/eb80fc518e8c58a84adbac594eb3309fcd98d6d6))

- Disable semantic-release asset uploads (upload_to_vcs_release = false) - Remove
  [tool.semantic_release.publish] section from pyproject.toml - Update release.yml to only run
  semantic-release version (no publish step) - Update documentation to clarify workflow separation:
  * release.yml: Creates releases with tags (no assets) * publish.yml: Builds and uploads assets to
  releases - This prevents duplicate asset upload failures

Addresses feedback from code review about duplicate uploads.

Co-authored-by: jacksonpradolima <7774063+jacksonpradolima@users.noreply.github.com>

- Remove duplicate keywords from blocked/on-hold detection
  ([`1d1dfa9`](https://github.com/jacksonpradolima/gsp-py/commit/1d1dfa996bdb21a9723976038f3cf44e04c21c9d))

Co-authored-by: jacksonpradolima <7774063+jacksonpradolima@users.noreply.github.com>

- Revert to original workflow and update docs with branch protection config
  ([`64e092f`](https://github.com/jacksonpradolima/gsp-py/commit/64e092f73bc60c39e5bd87c083233076e91cb8aa))

Co-authored-by: jacksonpradolima <7774063+jacksonpradolima@users.noreply.github.com>

- Update action SHAs for pr-size-labeler and merge-conflict labeler
  ([`72df80a`](https://github.com/jacksonpradolima/gsp-py/commit/72df80a1480d9f5231d06d542bfdd775017f26a3))

Co-authored-by: jacksonpradolima <7774063+jacksonpradolima@users.noreply.github.com>

- Update labeler action SHA, permissions, and improve keyword/review detection
  ([`c684c19`](https://github.com/jacksonpradolima/gsp-py/commit/c684c1998facd23243835e34f8b7e57f4d6bb3ec))

Co-authored-by: jacksonpradolima <7774063+jacksonpradolima@users.noreply.github.com>

- Update semantic release branch config to master
  ([`7558959`](https://github.com/jacksonpradolima/gsp-py/commit/7558959d8aa40410003293e298e0da78b96e9e9c))

Co-authored-by: jacksonpradolima <7774063+jacksonpradolima@users.noreply.github.com>

- Update semantic-release config to fix deprecation warning
  ([`e9a8d82`](https://github.com/jacksonpradolima/gsp-py/commit/e9a8d8242b8c94a8aae69033c0bda610546faf1c))

Move changelog_file configuration to the new location as required by semantic-release v10
  compatibility.

Co-authored-by: jacksonpradolima <7774063+jacksonpradolima@users.noreply.github.com>

- Use full commit SHA for action-semantic-pull-request
  ([`6c8964f`](https://github.com/jacksonpradolima/gsp-py/commit/6c8964f8748ed40871cc0ee31b581d142b2107eb))

Update amannn/action-semantic-pull-request from tag reference v5.5.4 (which doesn't exist) to v6.1.1
  with full commit SHA hash (48f256284bd46cdaab1048c3721360e808335d50) for better security and
  consistency with other workflows.

Co-authored-by: jacksonpradolima <7774063+jacksonpradolima@users.noreply.github.com>

- Use proper expression syntax for GPG secret check
  ([`81e1fe9`](https://github.com/jacksonpradolima/gsp-py/commit/81e1fe9f0da9761da653b1409dec1478cc896a31))

Co-authored-by: jacksonpradolima <7774063+jacksonpradolima@users.noreply.github.com>

### Code Style

- Remove trailing whitespace from workflow file
  ([`4a7a86d`](https://github.com/jacksonpradolima/gsp-py/commit/4a7a86db4adc375218d1ea050278e853ed19cbf9))

Co-authored-by: jacksonpradolima <7774063+jacksonpradolima@users.noreply.github.com>

### Documentation

- Add comprehensive implementation summary
  ([`f318343`](https://github.com/jacksonpradolima/gsp-py/commit/f3183432cedbf22a84cbcd9c60971f0d31ef7fbe))

Add detailed documentation of the automated release management implementation, including: - Overview
  of all components - How the system works - Testing instructions - Migration notes - Examples and
  best practices

Co-authored-by: jacksonpradolima <7774063+jacksonpradolima@users.noreply.github.com>

- Fix secret name and permissions in RELEASE_MANAGEMENT.md
  ([`a633221`](https://github.com/jacksonpradolima/gsp-py/commit/a633221f9c13442fffeb9ce52441706491493771))

Co-authored-by: jacksonpradolima <7774063+jacksonpradolima@users.noreply.github.com>

### Features

- Add automated release management with semantic-release
  ([`a5b3a05`](https://github.com/jacksonpradolima/gsp-py/commit/a5b3a059b4bf51cef6d431b73d39f8ef499eb7e6))

- Add Python Semantic Release configuration in pyproject.toml - Create automated release workflow
  (.github/workflows/release.yml) - Add conventional commit validation to pre-commit hooks - Add
  comprehensive Release Management Guide (docs/RELEASE_MANAGEMENT.md) - Update CONTRIBUTING.md with
  conventional commit requirements - Update README.md with release management section

This enables automatic version bumps, changelog updates, Git tags, and GitHub releases based on
  conventional commits.

Co-authored-by: jacksonpradolima <7774063+jacksonpradolima@users.noreply.github.com>

- Add comprehensive automated PR labeling workflow
  ([`eed5910`](https://github.com/jacksonpradolima/gsp-py/commit/eed59101544013199e102e47a60635569b6315dd))

Co-authored-by: jacksonpradolima <7774063+jacksonpradolima@users.noreply.github.com>

- Use ORG_RELEASE_TOKEN with fallback to GITHUB_TOKEN
  ([`911defc`](https://github.com/jacksonpradolima/gsp-py/commit/911defce1c276f51727abbc514e8fab1e0ac6928))

Co-authored-by: jacksonpradolima <7774063+jacksonpradolima@users.noreply.github.com>

### Performance Improvements

- Remove redundant toLowerCase() calls in keyword matching
  ([`d4ad61d`](https://github.com/jacksonpradolima/gsp-py/commit/d4ad61d36e7f411b1a798c201fe6b651d9e6d413))

Co-authored-by: jacksonpradolima <7774063+jacksonpradolima@users.noreply.github.com>

### Refactoring

- Add pagination for comments and improve code clarity
  ([`2c2b10b`](https://github.com/jacksonpradolima/gsp-py/commit/2c2b10b49860b5d4de244c683b6745d998bbf0cd))

Co-authored-by: jacksonpradolima <7774063+jacksonpradolima@users.noreply.github.com>

- Improve test script security and readability
  ([`a03427c`](https://github.com/jacksonpradolima/gsp-py/commit/a03427c56572d3edd0e93270dcdc524e3b8f86f6))

- Replace shell=True with list-based subprocess calls for better security - Use regex for version
  parsing instead of shell commands - Improve code readability by using explicit newline characters

Addresses code review feedback.

Co-authored-by: jacksonpradolima <7774063+jacksonpradolima@users.noreply.github.com>

- Optimize on-hold keyword detection to avoid redundancy
  ([`da6b5ac`](https://github.com/jacksonpradolima/gsp-py/commit/da6b5accd24edf198c8752579a4aeb8b740a45b9))

Co-authored-by: jacksonpradolima <7774063+jacksonpradolima@users.noreply.github.com>

- Remove unnecessary files and clarify release triggers
  ([`ac69207`](https://github.com/jacksonpradolima/gsp-py/commit/ac69207829c207df16e2198b14502e418bf442f0))

- Remove test_release_config.py (validation script not needed as proper test) - Remove
  IMPLEMENTATION_SUMMARY.md (redundant with docs/RELEASE_MANAGEMENT.md) - Update README to clearly
  specify which commit types trigger releases - Clarify that docs, refactor, style, test, build, ci,
  chore do NOT trigger releases

Co-authored-by: jacksonpradolima <7774063+jacksonpradolima@users.noreply.github.com>

- Scope permissions to job level and remove documentation file
  ([`2d69faa`](https://github.com/jacksonpradolima/gsp-py/commit/2d69faa26dfdcf84b7e991532c399b35ffead0ad))

Co-authored-by: jacksonpradolima <7774063+jacksonpradolima@users.noreply.github.com>

### Testing

- Add release configuration validation script and PR title check
  ([`b33335c`](https://github.com/jacksonpradolima/gsp-py/commit/b33335c522731dd02921605b24a2ba7194fcbffa))

- Add test script to validate semantic-release configuration - Add GitHub Actions workflow to
  validate PR titles follow conventional commits - Ensures all PRs have properly formatted titles
  for automated releases

Co-authored-by: jacksonpradolima <7774063+jacksonpradolima@users.noreply.github.com>


## v3.3.1 (2026-01-18)

### Continuous Integration

- Add pip ecosystem back to Dependabot alongside uv for complete dependency updates
  ([`76e9b42`](https://github.com/jacksonpradolima/gsp-py/commit/76e9b429e1879cdc3544ae1fda216d9c2021f041))

- Configure Dependabot uv ecosystem and optimize lock check to run on Python 3.12 only
  ([`e2e31d1`](https://github.com/jacksonpradolima/gsp-py/commit/e2e31d1a1b8c7b9b37d41dd1c4cfedcaf8783566))


## v3.3.0 (2026-01-01)

### Bug Fixes

- Add explicit contents:read permission to build job
  ([`7e30362`](https://github.com/jacksonpradolima/gsp-py/commit/7e303623b4f4279072eb6f98c84c02a4c89b43e5))

Add explicit permissions to the build job for clarity and security best practices. The build job
  needs contents:read to check out the repository.

Co-authored-by: jacksonpradolima <7774063+jacksonpradolima@users.noreply.github.com>

- Make file pattern explicit and add error handling in hash generation
  ([`23cd1a3`](https://github.com/jacksonpradolima/gsp-py/commit/23cd1a3e4f92d8348ce6930079e7200f5ebcedbe))

- Use find with explicit patterns (*.whl, *.tar.gz) instead of wildcard - Add check to ensure Python
  package artifacts exist before hashing - Exit with error if no artifacts found in dist directory -
  Sort files for consistent ordering

Co-authored-by: jacksonpradolima <7774063+jacksonpradolima@users.noreply.github.com>

- Remove ./ prefix from filenames in hash output
  ([`e604e2c`](https://github.com/jacksonpradolima/gsp-py/commit/e604e2c9c75bf55d74ec3c25f6e6845bd4815f65))

Use sed to strip the ./ prefix from find command output to ensure clean filenames in sha256sum
  output, matching the format expected by SLSA provenance.

Co-authored-by: jacksonpradolima <7774063+jacksonpradolima@users.noreply.github.com>

- Replace build-command with base64-subjects in SLSA provenance workflow
  ([`03255b3`](https://github.com/jacksonpradolima/gsp-py/commit/03255b32f8de775dec90f746ae7cdb02f13a85fd))

- Restructure workflow to have separate build and provenance jobs - Build job creates Python
  packages and generates SHA256 hashes - Provenance job uses base64-subjects input with generated
  hashes - Remove invalid build-command parameter that doesn't exist in
  generator_generic_slsa3.yml@v1.10.0

Co-authored-by: jacksonpradolima <7774063+jacksonpradolima@users.noreply.github.com>

- Update SLSA generator to v2.1.0 to fix deprecated actions
  ([`56b04b6`](https://github.com/jacksonpradolima/gsp-py/commit/56b04b65e560e26c81272e457d00ce851ff25199))

Update slsa-framework/slsa-github-generator from v1.10.0 to v2.1.0 to resolve the issue with
  deprecated actions/upload-artifact@v3. The v2.1.0 version uses the latest actions and is
  recommended by the SLSA framework documentation.

Co-authored-by: jacksonpradolima <7774063+jacksonpradolima@users.noreply.github.com>

### Refactoring

- Use -printf '%f\n' for cleaner filename extraction
  ([`d02c4be`](https://github.com/jacksonpradolima/gsp-py/commit/d02c4bebea18ab3b710a175f7bac2398f42f9798))

Replace sed-based ./ prefix removal with find's -printf option for more robust and direct filename
  extraction without path prefixes.

Co-authored-by: jacksonpradolima <7774063+jacksonpradolima@users.noreply.github.com>


## v3.2.8 (2026-01-01)

### Chores

- Updatte uv.lock
  ([`4c03dd0`](https://github.com/jacksonpradolima/gsp-py/commit/4c03dd06e8519e618fef28c9fc2a7f2bfe688f9e))


## v3.2.7 (2026-01-01)


## v3.2.6 (2026-01-01)


## v3.2.5 (2026-01-01)


## v3.2.4 (2026-01-01)


## v3.2.2 (2026-01-01)


## v3.2.1 (2026-01-01)


## v3.2.0 (2026-01-01)

### Bug Fixes

- Correct syntax errors in benchmarks.yml workflow
  ([`a30022d`](https://github.com/jacksonpradolima/gsp-py/commit/a30022d84c6bd8b793a9a315be297ebad1bebac1))

Co-authored-by: jacksonpradolima <7774063+jacksonpradolima@users.noreply.github.com>


## v3.1.1 (2025-12-21)


## v3.0.1 (2025-09-16)


## v3.0.0 (2025-09-14)

### Build System

- Migrate to uv, require Python 3.10+, add pre-commit/Makefile
  ([`16a2549`](https://github.com/jacksonpradolima/gsp-py/commit/16a2549d68ef4777ebb1ddf59817cd4b9da5ef98))

Replace Rye with uv for dependency management and execution to speed installs and simplify tooling
  across CI and local dev Update GitHub Actions to install/use uv and run ruff/pyright/pytest via
  uv; set Python 3.13 in CI and streamline virtualenv creation Raise minimum supported Python to
  3.10; update pyproject requires-python, classifiers, linter/type checker targets, and README
  badges/docs Add pre-commit configuration (ruff + hygiene hooks) and a Makefile with common tasks
  (setup, install, test, lint, format, typecheck, tox, coverage, pre-commit) Remove Rye-specific
  config and lockfiles; adjust dev dependency pins (e.g., pytest-cov 5.x, pylint 3.2.x) for
  compatibility with the new toolchain Apply minor code style and typing cleanups
  (quotes/formatting, type hints) and align tests; no functional behavior changes

BREAKING CHANGE: Drop support for Python 3.8 and 3.9

### Documentation

- Add committer prompt for conventional commit messages
  ([`84e7e63`](https://github.com/jacksonpradolima/gsp-py/commit/84e7e63d226acba629e70896506bc7d7277bbe12))

Introduce committer.prompt.md for agent-generated messages Provide clear steps, examples, and a
  shell command template Standardize commit message quality and consistency across the repo

### Features

- Add optional GPU backend and CLI/API backend selector
  ([`972609a`](https://github.com/jacksonpradolima/gsp-py/commit/972609adefbcb2d5900adb88239ed3fac21d6605))

Introduce experimental GPU backend using CuPy to accelerate singleton (k=1) support counting;
  non-singleton candidates fall back to Rust (if available) or Python Expose backend selection
  across layers: accelerate.support_counts now accepts backend: Optional[str] (overrides
  GSPPY_BACKEND env when provided) GSP._support and GSP.search accept a backend parameter and
  forward it to the acceleration layer Add --backend option to CLI (choices: auto, python, rust,
  gpu); when non-auto, it sets GSPPY_BACKEND for the run Update README with a new GPU acceleration
  section, installation via optional extra, runtime selection instructions, and revised CLI examples
  including --backend Add gpu extra in pyproject.toml (cupy>=11,<14) to keep GPU dependencies
  optional Maintain default CPU behavior (auto: try Rust, then Python) for backward compatibility

- Add optional Rust acceleration, benchmarks, and CI integration
  ([`2d98162`](https://github.com/jacksonpradolima/gsp-py/commit/2d981622526b7e2f4dd0572a93826f2472032066))

Introduce acceleration layer (gsppy/accelerate.py) that uses a PyO3 Rust extension for support
  counting and gracefully falls back to pure Python; runtime backend selection via GSPPY_BACKEND
  (rust/python/auto). Add bench_support.py (Click CLI) to compare Python vs Rust backends with
  options like --max_k and --warmup for reproducible micro-benchmarks. Extend Makefile with Rust
  helpers: rust-setup, rust-build (idempotent skip when up-to-date by checking the installed .so vs
  Rust sources), bench-small, and bench-big; update help output with a Rust acceleration section.
  Update README.md and CONTRIBUTING.md with instructions to build the Rust extension, choose a
  backend at runtime, and run benchmarks of various sizes. CI: update codecov workflow to optionally
  install Rust and build the extension in tests, and add a dedicated test-rust job that builds the
  extension, runs tests with GSPPY_BACKEND=rust, and uploads coverage/test results flagged as
  "rust".

Motivation: improve performance of hot support-counting loops while preserving a zero-dependency
  Python fallback; provide tooling and CI coverage to ensure stability and reproducibility.

- **cli**: Migrate to Click-based CLI and improve docs
  ([`f9939e6`](https://github.com/jacksonpradolima/gsp-py/commit/f9939e628f0dd0fcf0a61f8f516ad9c9f23f8703))

Replaced argparse CLI with Click for better usability and error handling Updated CLI options and
  error handling to use Click conventions Enhanced README with detailed CLI usage instructions,
  examples, and error handling Added Click as a dependency in pyproject.toml Refactored tests to
  handle Click's SystemExit and updated assertions for new CLI behavior Improved logging and exit
  codes for invalid input and errors

### BREAKING CHANGES

- Drop support for Python 3.8 and 3.9


## v2.3.0 (2025-01-05)


## v2.2.0 (2024-12-28)


## v2.1.0 (2024-12-26)


## v2.0.1 (2024-12-25)


## v2.0.0 (2024-12-25)

### Chores

- **project**: Update dependencies, setup configuration, and documentation
  ([`9f49f41`](https://github.com/jacksonpradolima/gsp-py/commit/9f49f41249ef6173c6bacba91a85799529b4b593))

- **Dependency Updates**: - Updated `requirements.txt` to include necessary package versions for
  compatibility and performance improvements. - Removed unused dependencies to streamline the
  project environment.

- **Setup Configuration**: - Enhanced `setup.py` for better packaging and distribution. - Updated
  metadata fields such as author information, project URL, and long description handling using the
  README file. - Improved classifiers for better PyPI categorization.

- **Documentation Enhancements**: - Revised `README.md` to reflect the latest project features and
  usage instructions. - Added examples for common use cases and clarified installation steps. -
  Fixed typos and restructured sections for better readability.

- **Files Modified**: - `requirements.txt`: Dependency updates and cleanup. - `setup.py`:
  Configuration and metadata improvements. - `README.md`: Documentation updates for features,
  installation, and usage.

### Continuous Integration

- **config**: Update linting, GitHub workflows, and editor configuration
  ([`4fca581`](https://github.com/jacksonpradolima/gsp-py/commit/4fca5811724729c755cd917724e63310b1d7c1ba))

- Updated `.pylintrc` for stricter linting rules to enforce consistency. - Modified `.editorconfig`
  for uniform whitespace and indentation. - Adjusted GitHub Actions in `.github` to streamline CI/CD
  pipeline execution.

### Documentation

- **project**: Update project documentation and guidelines
  ([`fbb89dc`](https://github.com/jacksonpradolima/gsp-py/commit/fbb89dccfe08c14da8e5235febdde9c8ee4cc8a8))

- Updated `LICENSE` to clarify usage and copyright terms. - Improved `CONTRIBUTING` guidelines to
  provide clear instructions for contributors.

### Features

- **cli**: Enhance CLI functionality and expand test coverage
  ([`fbce510`](https://github.com/jacksonpradolima/gsp-py/commit/fbce5103cb6155da4123fd08fa22fcf233f06160))

- **CLI Improvements**: - Refactored the CLI command structure for better usability and
  maintainability. - Improved error handling and added user-friendly messages for invalid inputs. -
  Enhanced logging output for better traceability during execution.

- **Test Enhancements**: - Added comprehensive test cases in `test_cli` to ensure full coverage of
  CLI commands. - Validated edge cases, including incorrect parameters and missing configurations. -
  Benchmarked CLI execution to identify and optimize bottlenecks.

- **Files Modified**: - `cli`: Improved command parsing and added user-friendly error messages. -
  `test_cli`: Expanded test coverage and introduced new edge case validations.

- **core**: Optimize GSP algorithm and enhance test coverage
  ([`7865f8c`](https://github.com/jacksonpradolima/gsp-py/commit/7865f8c377e9d3aa8017ad2453a81ca9089ed343))

- **Performance Improvements**: - Refactored the GSP algorithm to significantly improve candidate
  generation. - Replaced nested loops with optimized `itertools` usage, reducing computational
  overhead. - Enhanced `generate_candidates_from_previous` to be more efficient and maintainable by
  removing redundant checks. - Performance benchmarks: - Old implementation: ~2,874 ms. - New
  implementation: ~47 ms. - Overall improvement: ~61x (~98.37%).

- **Test Enhancements**: - Updated `test_generate_candidates_from_previous` to cover edge cases such
  as disjoint patterns and single-element sequences. - Adjusted test cases in `test_gsp` and
  `test_utils` to validate the new implementation. - Verified backward compatibility to ensure
  correctness with the old GSP logic. - Added benchmarks for comparative analysis of old vs. new
  utility functions.

- **Code Refactor**: - Improved the readability and maintainability of core utility functions in
  `utils`. - Simplified the logic for candidate generation using a compressed for-loop approach.

- **Files Modified**: - `gsp`: Core GSP algorithm optimization. - `test_gsp`: Adjustments for GSP
  test validation. - `utils`: Refactored candidate generation utilities. - `tests/test_gsp`:
  Enhanced test cases for edge cases and performance benchmarks. - `tests/test_utils`: Improved unit
  tests for utility functions.
