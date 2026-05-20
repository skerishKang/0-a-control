# scripts runtime migration plan

This document records the planning direction for migrating `scripts/` modules into structured subpackages. It does not describe started runtime work — the actual runtime file migration has not begun.

## Current scripts structure

`scripts/` is a flat directory mixing several responsibilities:

- database schema, migrations, integrity checks, and query helpers
- work queue and report/verdict pipeline helpers
- Telegram and external inbox import helpers
- local CLI commands and shell wrappers
- agent launcher registry and session wrappers
- CI, smoke, and static safety utilities

This structure works for the current prototype but makes ownership boundaries unclear.

## Target package direction

Three new subpackage scaffolds have been added to define future boundaries:

### scripts.cli

Future home of command-line interface utilities and user-facing entrypoints.

Current candidate files: `operating_loop_cli.py`, `session_cli.py`, `inbox_cli.py`, `db_integrity_cli.py`, and similar user-facing CLI modules.

### scripts.queue_runtime

Future home of queue processing and runtime execution components.

Current candidate files: `queue_worker.py`, `work_queue.py`, `file_queue.py`, and related pipeline helpers.

### scripts.integrations

Future home of third-party service integrations.

Current candidate files: `telegram_cli.py`, `telegram_db.py`, `telegram_service.py`, Telegram sync helpers, and external inbox adapters.

## stdlib queue shadow risk

The original plan referenced `scripts/queue/` as a target package name. This name shadows Python's standard library `queue` module. Any code that does `import queue` inside the `scripts/` package tree would resolve to the local subpackage instead of the stdlib, causing subtle breakage.

The scaffold uses `scripts.queue_runtime/` instead to avoid this collision. This decision is documented here so future contributors do not reintroduce the `scripts/queue/` name.

## Migration principles

### 1. Import compatibility is mandatory

Every moved module must leave a thin compatibility wrapper at its old import path. Existing `from scripts.X import Y` statements must continue to work until explicit migration is completed.

### 2. Runtime move is a later phase

This document and the associated scaffolds define target boundaries only. The actual movement of runtime `.py` files into subpackages has not started. When it does, each move should be a separate PR.

### 3. No behavior change first

Package movement PRs must not change runtime behavior. They move files and add wrappers. Behavior changes, if any, happen in separate PRs after the move is stable.

### 4. Small PR strategy

Each movement slice should be:

- one responsibility group at a time
- reviewable in under 10 minutes
- independently revertible
- accompanied by wrapper-based compatibility

This follows the pattern established by the `scripts/checks/` movement, which moved three modules with wrappers in a single PR without breaking existing entrypoints.

## What has been done

- `scripts/cli/` scaffold with `__init__.py` and README
- `scripts/queue_runtime/` scaffold with `__init__.py` and README
- `scripts/integrations/` scaffold with `__init__.py` and README
- `scripts/checks/` movement completed (PR #325 pattern)
- DB helpers movement completed (compatibility wrappers in place)
- Services movement completed (compatibility wrappers in place)

## What has not been done

- No runtime `.py` files have been moved into `scripts/cli/`
- No runtime `.py` files have been moved into `scripts/queue_runtime/`
- No runtime `.py` files have been moved into `scripts/integrations/`
- No import paths have been changed for any active consumer
- No behavior changes have been introduced as part of package scaffolding

## Related documents

- `docs/16-scripts-package-layout-plan.md` — full package layout plan
- `docs/scripts-package-scaffolds.md` — scaffold notes
- `docs/scripts-package-movement-log.md` — completed movement slices
