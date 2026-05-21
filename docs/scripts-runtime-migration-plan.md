# scripts runtime migration plan

This document records the planning direction and current status for migrating `scripts/` modules into structured subpackages.

## Current scripts structure

`scripts/` is being split by responsibility while preserving old command and import paths through compatibility wrappers. The directory still contains some flat runtime modules, but several responsibility groups now have canonical package locations.

Current responsibility groups include:

- database schema, migrations, integrity checks, and query helpers
- work queue and report/verdict pipeline helpers
- Telegram and external inbox import helpers
- local CLI commands and shell wrappers
- agent launcher registry and session wrappers
- CI, smoke, and static safety utilities

## Current package direction

### `scripts.cli`

Canonical home of command-line interface utilities and user-facing entrypoints.

Current completed moves include DB integrity, contract validation, Telegram CLI main/command helpers, session CLI, inbox CLI, and Telegram attachment/backfill helper entrypoints. Old flat paths remain compatibility wrappers unless explicitly removed in a later cleanup.

### `scripts.queue_runtime`

Canonical home of file queue and pipeline runtime components.

Current completed moves include queue worker, report export, verdict import, and file queue helpers. The package name intentionally avoids `scripts.queue` because that would shadow Python's standard library `queue` module.

### `scripts.integrations`

Canonical home of reusable third-party service integration helpers.

Current completed moves include Telegram progress tracking, session lock, shared Telegram helpers, and Telegram service helper functions. Standalone Telegram command helpers should stay under `scripts.cli` rather than being moved here just because they are Telegram-related.

### `scripts.db`, `scripts.services`, and `scripts.server_handlers`

These package areas hold DB helpers, service helpers shared by server handlers and CLIs, and HTTP route handler splits. Existing flat paths are kept as wrappers where compatibility is required.

## stdlib queue shadow risk

The original plan referenced `scripts/queue/` as a target package name. This name shadows Python's standard library `queue` module. Any code that does `import queue` inside the `scripts/` package tree could resolve to the local subpackage instead of the stdlib, causing subtle breakage.

The project uses `scripts.queue_runtime/` instead to avoid this collision. Future contributors should not reintroduce the `scripts/queue/` package name.

## Migration principles

### 1. Import compatibility is mandatory

Every moved module must leave a thin compatibility wrapper at its old import path unless a separate deliberate cleanup removes that path. Existing `from scripts.X import Y` statements should continue to work during migration.

### 2. Patch and module-state compatibility is part of the contract

Some tests and callers patch functions or mutate public module-level constants on old flat paths. Wrappers must preserve that behavior when it is part of the observed contract. This is especially important for modules such as `scripts.telegram_cli`, `scripts.telegram_service`, and `scripts.telegram_db`.

### 3. No behavior change first

Package movement PRs should not change runtime behavior. They should move files, add wrappers, update imports, and update tests/docs. Behavior, schema, or route changes belong in separate PRs after the move is stable.

### 4. Small PR strategy

Each movement slice should be:

- one responsibility group at a time
- reviewable in under 10 minutes
- independently revertible
- accompanied by wrapper-based compatibility

This follows the pattern recorded in `docs/scripts-package-movement-log.md`: small module moves, stable command wrappers, and no behavior changes in the same PR.

## What has been done

- `scripts/cli/` scaffold and multiple CLI canonical moves
- `scripts/queue_runtime/` scaffold and queue/runtime canonical moves
- `scripts/integrations/` scaffold and reusable Telegram integration helper moves
- `scripts/checks/` movement with stable command wrappers
- DB helper movement with compatibility wrappers
- service helper movement with compatibility wrappers
- Telegram migration audit documenting canonical paths and deferred flat modules

## What remains deliberately flat for now

- `scripts/telegram_service.py`: public runtime service module with Telethon connection, status, session-lock integration, chat discovery, message fetch, and attachment download orchestration. Movement is deferred because callers/tests import `scripts.telegram_service` directly and mutate module-level runtime constants.
- `scripts/telegram_db.py`: Telegram DB helper kept flat because `scripts/db.py` already exists as a public database facade and tests import/mutate `scripts.telegram_db.DB_PATH`.

See `docs/scripts-telegram-migration-audit.md` for the exact guardrails before attempting those moves.

## Related documents

- `docs/16-scripts-package-layout-plan.md` — full package layout plan
- `docs/scripts-package-scaffolds.md` — scaffold notes
- `docs/scripts-package-movement-log.md` — completed movement slices
- `docs/scripts-telegram-migration-audit.md` — Telegram-specific canonical paths and deferred movement notes
