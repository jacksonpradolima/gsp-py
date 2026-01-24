# Automated Pull Request Labeling System

This repository uses an advanced automated labeling system to help manage pull requests efficiently. Labels are automatically applied based on various criteria to improve project management and review processes.

## Label Categories

### 1. File Type Labels (`type/*`)

These labels are automatically applied based on the files changed in the PR:

- **`type/code`** - Changes to Python source code in `gsppy/` directory
- **`type/tests`** - Changes to test files in `tests/` directory
- **`type/docs`** - Changes to documentation files (`.md` files, `docs/`, `mkdocs.yml`)
- **`type/ci`** - Changes to GitHub workflows or CI configuration
- **`type/dependencies`** - Changes to project dependencies (`pyproject.toml`, `uv.lock`)
- **`type/rust`** - Changes to Rust backend code
- **`type/config`** - Changes to configuration files (`.pylintrc`, `.editorconfig`, etc.)
- **`type/benchmarks`** - Changes to benchmark files
- **`type/build`** - Changes to build/packaging configuration
- **`security`** - Changes to security-related files

### 2. Size Labels (`size/*`)

PRs are automatically labeled based on the number of lines changed (excluding lock files and markdown):

- **`size/XS`** - Extra small (1-10 lines)
- **`size/S`** - Small (11-100 lines)
- **`size/M`** - Medium (101-500 lines)
- **`size/L`** - Large (501-1000 lines)
- **`size/XL`** - Extra large (1000+ lines)

💡 **Tip**: PRs labeled as `size/XL` will receive a comment suggesting to split them into smaller PRs for easier review.

### 3. Status Labels (`status/*`)

These labels track the current state of the PR:

- **`status/draft`** - PR is in draft mode
- **`status/conflicts`** - PR has merge conflicts with the base branch
- **`status/stale`** - PR hasn't been updated in 30+ days
- **`status/blocked`** - PR is blocked by dependencies or other issues
- **`status/on-hold`** - PR is temporarily on hold
- **`status/needs-review`** - PR needs review from maintainers
- **`status/changes-requested`** - Reviewers have requested changes

### 4. Priority Labels

Some labels can be manually added to control automated behavior:

- **`priority/critical`** - Critical PRs are exempt from stale marking

## How It Works

### File-Based Labeling

When a PR is opened or updated, the system analyzes which files have changed and automatically applies appropriate `type/*` labels. This helps reviewers quickly understand what areas of the codebase are affected.

### Size-Based Labeling

The system counts the number of lines changed (additions + deletions) and applies the appropriate `size/*` label. This helps set expectations for review time and complexity.

### Conflict Detection

The system automatically checks for merge conflicts and applies the `status/conflicts` label when conflicts are detected. The label is removed automatically when conflicts are resolved.

### Draft PR Detection

Draft PRs automatically receive the `status/draft` label. When a PR is marked as ready for review, this label is automatically removed.

### Stale PR Management

The system runs daily to check for stale PRs:

1. PRs inactive for 30+ days receive the `status/stale` label and a notification comment
2. If no activity occurs within 7 days after being marked stale, the PR is automatically closed
3. Any new activity removes the stale label
4. PRs with `status/on-hold`, `status/blocked`, or `priority/critical` labels are exempt

### Blocked Status Detection

The system scans PR titles, descriptions, and comments for blocking keywords:

**Blocked Keywords:**
- "blocked"
- "blocking"
- "waiting for"
- "depends on"
- "blocked by"
- "do not merge"
- "dnm"

**On-Hold Keywords:**
- "on hold"
- "hold"
- "waiting for decision"
- "needs discussion"

When these keywords are detected, appropriate labels (`status/blocked` or `status/on-hold`) are applied automatically.

### Review Status Tracking

The system monitors the review state of PRs:

- New PRs without any reviews receive `status/needs-review`
- PRs with requested changes receive `status/changes-requested`
- Labels are automatically removed when the status changes (e.g., after approval)

## Best Practices

### For Contributors

1. **Keep PRs focused** - Aim for smaller PRs (size/S or size/M) for faster reviews
2. **Mark WIP as draft** - Use draft PRs for work-in-progress to avoid premature reviews
3. **Communicate blocks** - Use keywords like "blocked by #123" to auto-label blocked PRs
4. **Respond to staleness** - Comment on stale PRs to keep them active or close them if no longer needed

### For Reviewers

1. **Use labels for prioritization** - Filter by size and type to batch similar reviews
2. **Check status labels** - Prioritize PRs with `status/needs-review` that aren't blocked or on hold
3. **Monitor stale PRs** - Review stale PRs to decide if they should be closed or need attention

### For Maintainers

1. **Exempt important PRs** - Add `priority/critical` to PRs that shouldn't be marked stale
2. **Use on-hold for parking** - Apply `status/on-hold` to PRs waiting for external decisions
3. **Monitor blocked PRs** - Regularly review `status/blocked` PRs to unblock them

## Workflow Triggers

The labeling workflow runs on:

- PR opened, synchronized, reopened, ready for review, converted to draft, or edited
- New comments on PRs
- New review comments on PRs
- Daily at 00:00 UTC (for stale PR checks)

## Manual Label Management

While most labels are managed automatically, you can always:

- Manually add labels that aren't automatically managed
- Remove incorrect labels
- Override automatic labels if needed

The automation will respect manual changes and won't conflict with them in most cases.

## Troubleshooting

### Label not applied

- Check if the workflow has run successfully in the Actions tab
- Verify the PR matches the criteria in `.github/labeler.yml`
- Some labels may take a few seconds to appear after workflow completion

### Incorrect label

- The automation may occasionally mislabel; feel free to manually correct
- Report persistent issues to maintainers

### Stale PR closed prematurely

- PRs are only closed after being stale for 37+ days (30 days + 7 day grace period)
- Any comment or update removes the stale label
- Reopen the PR if closed incorrectly

## Configuration Files

- **Workflow**: `.github/workflows/pr-labeler.yml`
- **File-based rules**: `.github/labeler.yml`

## Benefits

✅ **Faster triage** - Reviewers can quickly identify PR types and sizes
✅ **Better organization** - Clear status indicators for all PRs
✅ **Reduced noise** - Automatic cleanup of stale PRs
✅ **Improved communication** - Blocked and on-hold PRs are clearly marked
✅ **Consistent process** - Automated labeling ensures consistency across all PRs
