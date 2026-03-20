# Fossil Local History

`0-a-control` uses two history layers:

- `Fossil`: local-first full snapshot history for recovery
- `Git`: selective history for GitHub sharing

## Principle
Commit to Fossil first.
Commit to Git only when the change is ready to be shared.

## Why
Git ignores many local files in this repo because GitHub publishing needs a cleaner tree.
Fossil exists to keep a broader local history so accidental deletion is easier to recover from.

## Standard Flow
1. Work normally in this folder.
2. Before cleanup or after a meaningful working block:
   - `fossil addremove`
   - `fossil commit -m "local snapshot: ..."`
3. When the change is ready for GitHub:
   - `git add ...`
   - `git commit -m "..."`
   - `git push ...`

## Minimum Fossil Ignore
Fossil should ignore only repo-internal or cache-like paths by default:

- `.git/`
- `.fslckout`
- `_FOSSIL_`
- `__pycache__/`
- `*.pyc`
- `.venv/`
- `venv/`
- `.pytest_cache/`

This keeps Fossil broad without versioning Git's own metadata.

## Recovery Mindset
- If a local file disappears, check Fossil first.
- If a shared code change needs rollback, Git may be enough.
- If a file was never committed to Fossil, Fossil cannot recover it.

## Current Command Pattern
Use Git Bash in this project:

```bash
fossil status
fossil addremove
fossil commit -m "local snapshot: describe the work"
```

Then later:

```bash
git status
git add -A
git commit -m "..."
git push
```
