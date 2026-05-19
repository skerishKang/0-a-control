# Branch policy

The canonical branch for this repository is `main`.

## Rules

- GitHub Actions run on `main` and pull requests targeting `main`.
- New work branches should branch from `main`.
- Pull requests should target `main` unless a temporary stacked-PR workflow is explicitly documented.
- Documentation, launcher instructions, and automation prompts should refer to `main` as the default branch.

## About `master`

If a `master` branch exists, treat it as stale or compatibility-only unless repository administrators confirm otherwise.

Do not delete or retarget branches blindly. Branch cleanup should be a separate admin task after confirming the repository default branch setting, whether `master` has unique commits, whether external automation still references it, and whether users or agents have active work based on it.

## Operator checklist

Before starting work, update local `main` from `origin/main`.

Before opening a pull request:

- Confirm the PR base branch is `main`.
- Confirm the branch is not accidentally stacked on an old feature branch.
- Compare against `main` and verify the changed-file count is expected.
- Avoid close keywords unless the PR is intended to close the issue.
