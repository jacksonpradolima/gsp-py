# CHANGELOG


## v5.0.0 (2026-02-06)

### Chores

- Adds support for optional types in item filters and ignores types in metadata printouts.
  ([`79111b4`](https://github.com/jacksonpradolima/gsp-py/commit/79111b4c781a65b21a17f85b0b507b41ba6e51f9))

- Update uv.lock for version 4.2.0
  ([`f8f690f`](https://github.com/jacksonpradolima/gsp-py/commit/f8f690f7f0304dc4331c17c68487fe3411436149))

### Features

- Add preprocessing, postprocessing, and candidate filtering hooks to GSP algorithm
  ([`495d290`](https://github.com/jacksonpradolima/gsp-py/commit/495d29009abe862bf992831bd276181efa40c99d))

feat!: add preprocessing, postprocessing, and candidate filtering hooks to GSP algorithm


## v4.2.0 (2026-02-01)

### Chores

- Update uv.lock for version 4.1.0
  ([`5ed3d9e`](https://github.com/jacksonpradolima/gsp-py/commit/5ed3d9e46cf158a2261462cb8974b6bbb452f32e))

### Features

- Add itemset support for co-occurrence semantics in sequence mining
  ([`90805b1`](https://github.com/jacksonpradolima/gsp-py/commit/90805b190f40ebf34a72da0bbe949cb627140337))


## v4.1.0 (2026-02-01)

### Bug Fixes

- Address code review feedback - add type annotations and remove unused variables
  ([`bf62d14`](https://github.com/jacksonpradolima/gsp-py/commit/bf62d144d8f1be1e7716291d41af955450612c81))

Co-authored-by: jacksonpradolima <7774063+jacksonpradolima@users.noreply.github.com>

### Chores

- Update uv.lock for version 4.0.0
  ([`f1ae2af`](https://github.com/jacksonpradolima/gsp-py/commit/f1ae2af2aa71ea44b9d8625ed647da79259ec096))

### Documentation

- Add Sequence documentation and examples to README
  ([`62d0d02`](https://github.com/jacksonpradolima/gsp-py/commit/62d0d02c19c5751331df53e680cc0b9aee19677b))

Co-authored-by: jacksonpradolima <7774063+jacksonpradolima@users.noreply.github.com>

- Update docs/ with Sequence abstraction documentation
  ([`2368cf3`](https://github.com/jacksonpradolima/gsp-py/commit/2368cf30239139e8e2af5457ee6acf14db30ef06))

Co-authored-by: jacksonpradolima <7774063+jacksonpradolima@users.noreply.github.com>

### Features

- Add Sequence abstraction class with comprehensive tests
  ([`6011bdb`](https://github.com/jacksonpradolima/gsp-py/commit/6011bdb7104755d109b58261b36e1dd1c36b2d61))

Co-authored-by: jacksonpradolima <7774063+jacksonpradolima@users.noreply.github.com>

- Integrate Sequence objects with GSP.search() via return_sequences parameter
  ([`7476588`](https://github.com/jacksonpradolima/gsp-py/commit/7476588f2b277276748e0550366014f2a93d8ef5))

Co-authored-by: jacksonpradolima <7774063+jacksonpradolima@users.noreply.github.com>

- Introduce Sequence abstraction for typed pattern representation
  ([`01ca37b`](https://github.com/jacksonpradolima/gsp-py/commit/01ca37b9bc4572eb7b1c1eaf6fdf26ca2324a3c5))

### Refactoring

- Address code review feedback - remove redundant checks
  ([`621e940`](https://github.com/jacksonpradolima/gsp-py/commit/621e9403379ae0fd07bf45b97616b9979f2d4aa6))

Co-authored-by: jacksonpradolima <7774063+jacksonpradolima@users.noreply.github.com>

- Reduce cognitive complexity in sequence_example.py and fix f-string
  ([`63ac4f9`](https://github.com/jacksonpradolima/gsp-py/commit/63ac4f9ceb869a5228cdccdcf6a9d0b9f46f0350))

Co-authored-by: jacksonpradolima <7774063+jacksonpradolima@users.noreply.github.com>

- Update type annotations and improve search method in GSP class
  ([`e2e9a3f`](https://github.com/jacksonpradolima/gsp-py/commit/e2e9a3f473d1e0c5d6990c8b7c5837a251761032))


## v4.0.0 (2026-02-01)

### Chores

- Add additional VSCode extensions for improved development experience
  ([`107dfa4`](https://github.com/jacksonpradolima/gsp-py/commit/107dfa422005f4cdec4655a9751fd0d6e597773f))

- Update uv.lock for version 3.6.1
  ([`d8d7394`](https://github.com/jacksonpradolima/gsp-py/commit/d8d73947d570844c02e9d974b626da26f07cf1e6))

### Features

- Add SPM/GSP delimiter format loader and token mapping utilities
  ([`4ac1d34`](https://github.com/jacksonpradolima/gsp-py/commit/4ac1d34d166f21d30968872cf16c1bde3ff1f2aa))

### Refactoring

- Add type casting for return values in read_transactions_from_spm
  ([`2099bfd`](https://github.com/jacksonpradolima/gsp-py/commit/2099bfd5253a1dc058dd46bd0da077810958fa76))

- Update read_transactions_from_spm to return mappings and adjust tests
  ([`373b8ff`](https://github.com/jacksonpradolima/gsp-py/commit/373b8ff0d7f131140bcdbd039fae0d02572e86b7))


## v3.6.1 (2026-01-31)

### Bug Fixes

- Typing for polars and pandas
  ([`0773992`](https://github.com/jacksonpradolima/gsp-py/commit/07739921d074e55c8436a88a73e510b1d8761510))

### Build System

- **deps**: Bump actions/checkout in /.github/workflows
  ([`7af193d`](https://github.com/jacksonpradolima/gsp-py/commit/7af193d515972eeca5d8e354e91a60e488357cfb))

Bumps [actions/checkout](https://github.com/actions/checkout) from 4.3.1 to 6.0.2. - [Release
  notes](https://github.com/actions/checkout/releases) -
  [Changelog](https://github.com/actions/checkout/blob/main/CHANGELOG.md) -
  [Commits](https://github.com/actions/checkout/compare/v4.3.1...de0fac2e4500dabe0009e67214ff5f5447ce83dd)

--- updated-dependencies: - dependency-name: actions/checkout dependency-version: 6.0.2

dependency-type: direct:production

update-type: version-update:semver-major

...

Signed-off-by: dependabot[bot] <support@github.com>

- **deps**: Bump actions/github-script in /.github/workflows
  ([`03a7588`](https://github.com/jacksonpradolima/gsp-py/commit/03a7588301421369731d3d543f81b93c25c292ef))

Bumps [actions/github-script](https://github.com/actions/github-script) from 7.0.1 to 8.0.0. -
  [Release notes](https://github.com/actions/github-script/releases) -
  [Commits](https://github.com/actions/github-script/compare/60a0d83039c74a4aee543508d2ffcb1c3799cdea...ed597411d8f924073f98dfc5c65a23a2325f34cd)

--- updated-dependencies: - dependency-name: actions/github-script dependency-version: 8.0.0

dependency-type: direct:production

update-type: version-update:semver-major

...

Signed-off-by: dependabot[bot] <support@github.com>

- **deps**: Bump actions/setup-python in /.github/workflows
  ([`75771bf`](https://github.com/jacksonpradolima/gsp-py/commit/75771bff660b3842f2c8d84bdaeb013941e5abe0))

Bumps [actions/setup-python](https://github.com/actions/setup-python) from 5.6.0 to 6.2.0. -
  [Release notes](https://github.com/actions/setup-python/releases) -
  [Commits](https://github.com/actions/setup-python/compare/v5.6.0...a309ff8b426b58ec0e2a45f0f869d46889d02405)

--- updated-dependencies: - dependency-name: actions/setup-python dependency-version: 6.2.0

dependency-type: direct:production

update-type: version-update:semver-major

...

Signed-off-by: dependabot[bot] <support@github.com>

- **deps**: Bump actions/stale in /.github/workflows
  ([`e699ccd`](https://github.com/jacksonpradolima/gsp-py/commit/e699ccdac689734b4694665d924ace8bba479253))

Bumps [actions/stale](https://github.com/actions/stale) from 9.0.0 to 10.1.1. - [Release
  notes](https://github.com/actions/stale/releases) -
  [Changelog](https://github.com/actions/stale/blob/main/CHANGELOG.md) -
  [Commits](https://github.com/actions/stale/compare/28ca1036281a5e5922ead5184a1bbf96e5fc984e...997185467fa4f803885201cee163a9f38240193d)

--- updated-dependencies: - dependency-name: actions/stale dependency-version: 10.1.1

dependency-type: direct:production

update-type: version-update:semver-major

...

Signed-off-by: dependabot[bot] <support@github.com>

- **deps**: Bump actions/upload-artifact in /.github/workflows
  ([`17efaff`](https://github.com/jacksonpradolima/gsp-py/commit/17efaffc755c017e066c0286464899ead6e2cae4))

Bumps [actions/upload-artifact](https://github.com/actions/upload-artifact) from 4.6.2 to 6.0.0. -
  [Release notes](https://github.com/actions/upload-artifact/releases) -
  [Commits](https://github.com/actions/upload-artifact/compare/v4.6.2...b7c566a772e6b6bfb58ed0dc250532a479d7789f)

--- updated-dependencies: - dependency-name: actions/upload-artifact dependency-version: 6.0.0

dependency-type: direct:production

update-type: version-update:semver-major

...

Signed-off-by: dependabot[bot] <support@github.com>

### Chores

- Update uv.lock for version 3.6.0
  ([`4c2a5e5`](https://github.com/jacksonpradolima/gsp-py/commit/4c2a5e5967482443c2db645c9ba4744bd2110dd1))

- **deps**: Bump ty and ruff
  ([`07a20df`](https://github.com/jacksonpradolima/gsp-py/commit/07a20df9fb4ff3a3b022d28d152b586ca45383c8))


## v3.6.0 (2026-01-26)

### Chores

- Update uv.lock for version 3.5.0
  ([`e2c1be0`](https://github.com/jacksonpradolima/gsp-py/commit/e2c1be0945b0b124d8afa8981877513449b29ff0))

### Features

- Add flexible pruning strategy system to GSP algorithm
  ([`94089cc`](https://github.com/jacksonpradolima/gsp-py/commit/94089cc5716ec6d7c7a6e0720843162db116fca2))

feat: add flexible pruning strategy system to GSP algorithm

- Add typing-extensions as a dependency
  ([`6222945`](https://github.com/jacksonpradolima/gsp-py/commit/62229455ef3976c405d96e5ea9d5cafaf5eee6e3))

### Refactoring

- Pruning strategy initialization and enhance type hints; add typing_extensions dependency
  ([`ddc0abd`](https://github.com/jacksonpradolima/gsp-py/commit/ddc0abd9352797dd19988f60d6287da421ef60cf))


## v3.5.0 (2026-01-26)

### Bug Fixes

- Address code review feedback
  ([`1e7cf86`](https://github.com/jacksonpradolima/gsp-py/commit/1e7cf8681b3cd0432e6d1608187b7d518c27fcc0))

- Remove root logger modifications to prevent global side effects - Fix redundant logger
  configuration in CLI - Remove redundant subprocess imports in tests - Revert unrelated formatting
  changes in temporal constraints tests - Replace future dates with YYYY-MM-DD placeholders in
  documentation - Add explanation for not using Loguru in logging documentation

All changes address feedback from code review while maintaining backward compatibility and test
  coverage.

Co-authored-by: jacksonpradolima <7774063+jacksonpradolima@users.noreply.github.com>

- Specify logger name in caplog for verbose tests
  ([`cb477b0`](https://github.com/jacksonpradolima/gsp-py/commit/cb477b0f040ce38b60b6e3d485536e79d6d3ea19))

Update test_verbose_initialization, test_non_verbose_initialization, and
  test_verbose_override_in_search to use caplog.at_level(logging.DEBUG, logger='gsppy.gsp') instead
  of just caplog.at_level(logging.DEBUG). This ensures tests only capture logs from the gsppy.gsp
  logger, preventing interference from other loggers and making tests more reliable.

Co-authored-by: jacksonpradolima <7774063+jacksonpradolima@users.noreply.github.com>

- Update test_setup_logging_verbose to match refactored logging
  ([`ab78c33`](https://github.com/jacksonpradolima/gsp-py/commit/ab78c33ee1c09964773b1af835c9bb133a778824))

Update test to verify logging.basicConfig is called with DEBUG level instead of checking the removed
  explicit logger.setLevel call. This aligns with the refactored logging configuration that removed
  redundant logger level setting.

Co-authored-by: jacksonpradolima <7774063+jacksonpradolima@users.noreply.github.com>

### Chores

- Update uv.lock for version 3.4.3
  ([`6a78997`](https://github.com/jacksonpradolima/gsp-py/commit/6a789979fd6a7422c063dbe5b2ff46cd0d2141c6))

### Features

- Add explicit verbosity control and structured logging
  ([`44f56d9`](https://github.com/jacksonpradolima/gsp-py/commit/44f56d947978ddad1b7f2a2cca00f59def0ce4e4))

feat: add explicit verbosity control and structured logging

### Refactoring

- Gsp initialization in tests to handle constraints explicitly and improve verbosity handling
  ([`ced0243`](https://github.com/jacksonpradolima/gsp-py/commit/ced0243e58ff444988e37f5ae472f58d4478498e))

- Gsp initialization in tests to handle constraints explicitly and improve verbosity handling
  ([`479f305`](https://github.com/jacksonpradolima/gsp-py/commit/479f305aae02217ce7b75fede5e0fb249fd1b477))


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
