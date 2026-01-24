# Release Management Guide

This repository uses automated release management powered by [Python Semantic Release](https://python-semantic-release.readthedocs.io/) and [Conventional Commits](https://www.conventionalcommits.org/).

## How It Works

The release automation workflow automatically:

1. **Analyzes commit messages** since the last release
2. **Determines the next version** based on conventional commits
3. **Updates the version** in `pyproject.toml`
4. **Generates/updates CHANGELOG.md** with structured release notes
5. **Creates a Git tag** (e.g., `v3.4.0`)
6. **Publishes a GitHub Release** with release notes

## Conventional Commit Format

All commits should follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Commit Types

The following commit types determine how versions are bumped:

| Type | Description | Version Bump |
|------|-------------|--------------|
| `fix:` | Bug fixes | **Patch** (3.3.0 → 3.3.1) |
| `feat:` | New features | **Minor** (3.3.0 → 3.4.0) |
| `BREAKING CHANGE:` | Breaking changes (in footer or with `!`) | **Major** (3.3.0 → 4.0.0) |
| `perf:` | Performance improvements | **Patch** (3.3.0 → 3.3.1) |
| `docs:` | Documentation changes | No release |
| `style:` | Code style changes | No release |
| `refactor:` | Code refactoring | No release |
| `test:` | Test changes | No release |
| `build:` | Build system changes | No release |
| `ci:` | CI/CD changes | No release |
| `chore:` | Maintenance tasks | No release |

### Examples

#### Patch Release (Bug Fix)

```bash
git commit -m "fix: correct off-by-one error in pattern matching"
```

#### Minor Release (New Feature)

```bash
git commit -m "feat: add support for time-constrained pattern mining"
```

#### Major Release (Breaking Change)

Option 1 - Using `!` suffix:
```bash
git commit -m "feat!: redesign API to use async/await pattern

BREAKING CHANGE: All public methods now return coroutines"
```

Option 2 - Using footer:
```bash
git commit -m "refactor: change GSP initialization parameters

BREAKING CHANGE: GSP constructor now requires `backend` parameter"
```

#### Scoped Commits

```bash
git commit -m "feat(cli): add --export-format option for JSON output"
git commit -m "fix(gpu): resolve memory leak in CuPy backend"
git commit -m "docs(readme): update installation instructions"
```

## Triggering a Release

Releases are **automatically triggered** when commits are pushed to the `main` branch. The workflow:

1. Runs on every push to `main`
2. Analyzes commits since the last release
3. If a version bump is warranted (e.g., `fix:`, `feat:`), it creates a release
4. If no version bump is needed, the workflow exits gracefully

### Manual Testing (Dry Run)

To preview what the next release will be without making changes:

```bash
pip install python-semantic-release==9.17.0
semantic-release version --print
```

To see what changes would be made:

```bash
semantic-release version --no-push --no-tag --no-commit --no-vcs-release
```

## Release Workflow

The automated release workflow (`.github/workflows/release.yml`) performs these steps:

1. **Checkout** - Fetches the full Git history
2. **Setup** - Installs Python and Python Semantic Release
3. **Version** - Analyzes commits and bumps version in `pyproject.toml`
4. **Changelog** - Generates/updates `CHANGELOG.md`
5. **Commit** - Commits version and changelog changes
6. **Tag** - Creates an annotated Git tag
7. **Release** - Creates a GitHub Release with release notes (no assets)

The existing `publish.yml` workflow then triggers on release creation to build and upload distribution assets.

## Configuration

Release automation is configured in `pyproject.toml`:

```toml
[tool.semantic_release]
version_toml = ["pyproject.toml:project.version"]
branch = "main"
upload_to_vcs_release = false  # Assets uploaded by publish.yml
upload_to_pypi = false  # PyPI publishing handled separately
build_command = "python -m build"
tag_format = "v{version}"

[tool.semantic_release.commit_parser_options]
allowed_tags = ["feat", "fix", "docs", "style", "refactor", "perf", "test", "build", "ci", "chore", "revert"]
minor_tags = ["feat"]
patch_tags = ["fix", "perf"]
```

## Integration with Existing Workflows

The automated release workflow complements the existing `publish.yml` workflow:

1. **release.yml** - Creates GitHub releases with tags from conventional commits
2. **publish.yml** - Builds package, uploads assets to release, and publishes to PyPI

This separation allows:
- Automated version management and release notes
- Controlled PyPI publishing with SBOM generation and Sigstore signing
- No duplicate asset uploads

This separation allows:
- Automated releases on every significant commit to `main`
- Manual control over PyPI publishing (triggered by GitHub releases)
- SBOM generation and Sigstore signing during PyPI publication

## Best Practices

### For Contributors

1. **Use conventional commits** for all commits
2. **Include scope** when relevant (e.g., `feat(cli):`, `fix(gpu):`)
3. **Write clear descriptions** in the commit message
4. **Add body/footer** for complex changes
5. **Mark breaking changes** explicitly with `BREAKING CHANGE:` or `!`

### For Maintainers

1. **Review commit messages** in PRs to ensure they follow conventions
2. **Squash merge** PRs with a proper conventional commit message
3. **Monitor release workflow** for successful execution
4. **Verify changelogs** are accurate and complete
5. **Update documentation** when releasing breaking changes

## Troubleshooting

### "No release will be made"

This means no commits since the last release warrant a version bump. Only commits with types `fix:`, `feat:`, `perf:`, or `BREAKING CHANGE:` trigger releases.

### Release workflow failed

Check the workflow logs in GitHub Actions. Common issues:
- Git conflicts (rare, usually self-resolving)
- Missing permissions (check `GITHUB_TOKEN` permissions)
- Invalid commit messages (check conventional commit format)

### Changelog not updating

Ensure commits follow the conventional commit format. The changelog generator only parses properly formatted commits.

## References

- [Conventional Commits Specification](https://www.conventionalcommits.org/)
- [Python Semantic Release Documentation](https://python-semantic-release.readthedocs.io/)
- [Semantic Versioning](https://semver.org/)
