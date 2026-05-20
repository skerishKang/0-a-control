# 16. scripts package layout plan

This document defines the proposed package split for `scripts/` before broad file movement.

Issue #250 should be implemented in small batches. The goal is not to reorganize everything at once, but to keep target boundaries explicit and move one responsibility group at a time.

## Current problem

`scripts/` currently mixes several responsibilities:

- database schema, migrations, integrity checks, and query helpers
- HTTP server entrypoint and route handlers
- work queue and report/verdict pipeline helpers
- Telegram and external inbox import helpers
- local CLI commands and shell wrappers
- agent launcher registry and session wrappers
- CI, smoke, and static safety utilities

This is workable for the current prototype, but it makes ownership unclear. The main risk of reorganizing it is breaking import paths, shell wrappers, Windows launchers, or CI entrypoints.

## Target layout

The proposed target is a gradual subpackage layout under `scripts/`:

| Target package | Responsibility | Example current files | Status |
| --- | --- | --- | --- |
| `scripts/db/` | SQLite schema, migrations, DB helpers, integrity checks, seed helpers | `db_base.py`, `db_schema.py`, `db_fk_migrations.py`, `db_integrity.py`, `db_seed.py` | Planned |
| `scripts/server/` | HTTP server entrypoint, route registration, handler utilities | `server.py`, `server_handlers/*` | Planned |
| `scripts/services/` | Business logic used by server handlers and CLIs | `plan_ops.py`, `quest_ops.py`, `verdict_ops.py`, briefing helpers | Planned |
| `scripts/queue/` | File queue, report/verdict pipeline, worker utilities | queue/report/verdict processing scripts | Planned |
| `scripts/telegram/` | Telegram sync, source registry, attachment handling | `telegram_cli.py`, `telegram_db.py`, Telegram sync helpers | Planned |
| `scripts/external/` | External inbox adapters that are not Telegram-specific | inbox/import helpers | Planned |
| `scripts/agents/` | Agent registry, session wrapper coordination, launcher support | `agent_registry.py`, `agent-work.sh` related helpers | Planned |
| `scripts/cli/` | User-facing command entrypoints and compatibility wrappers | small command modules and CLI entrypoints | Planned |
| `scripts/checks/` | CI/static/smoke validation utilities | `check_repo_hygiene.py`, `check_frontend_safety.py`, `smoke_server.py` | Implemented with wrappers |

The target package names are intentionally conservative. They describe responsibility boundaries without forcing a framework rewrite.

## Compatibility rules

Each movement PR should follow these rules:

1. Keep public CLI commands working.
2. Keep existing shell and batch launcher paths working, either by leaving thin wrappers or updating launchers in the same PR.
3. Do not move multiple responsibility groups in one PR.
4. Do not mix behavior changes with import-path moves.
5. Run the full CI workflow before merge.
6. Prefer compatibility wrappers during the transition.

## Completed movement slices

### PR B: Static and smoke checks

Status: completed.

Implementation modules now live under `scripts/checks/`:

- `scripts/checks/repo_hygiene.py`
- `scripts/checks/frontend_safety.py`
- `scripts/checks/server_smoke.py`

Compatibility wrappers remain at the old paths so existing workflow commands and direct local commands continue to work:

- `scripts/check_repo_hygiene.py`
- `scripts/check_frontend_safety.py`
- `scripts/smoke_server.py`

## Remaining suggested PR order

### PR A: DB package foundation

Move database-only modules because they already share naming conventions.

Candidate files:

- `scripts/db_base.py`
- `scripts/db_schema.py`
- `scripts/db_fk_migrations.py`
- `scripts/db_integrity.py`
- `scripts/db_state.py`
- `scripts/db_sessions.py`
- `scripts/db_briefing.py`
- `scripts/db_seed.py`

Recommended approach:

- Create `scripts/db/` with moved modules.
- Leave old module wrappers that re-export from the new package for one or more releases.
- Update direct imports gradually after wrappers are in place.
- Start with one or two low-risk DB modules before moving the central `db_base.py` import hub.

### PR C: Telegram package

Move Telegram-specific implementation behind `scripts/telegram/`.

Candidate files:

- `scripts/telegram_cli.py`
- `scripts/telegram_db.py`
- Telegram sync helper scripts

Recommended approach:

- Keep the CLI entrypoint path stable first.
- Move internal implementation before changing user-facing wrappers.

### PR D: Server service extraction

This overlaps with issue #249 and should be coordinated with that work.

Recommended approach:

- Introduce service modules before moving the server entrypoint.
- Migrate one route group at a time.
- Avoid changing route behavior and file layout in the same PR.

## Non-goals

- Do not rewrite the HTTP server framework.
- Do not change DB schema as part of package movement.
- Do not remove Windows launchers without replacement.
- Do not rename user-facing commands without a compatibility path.
- Do not move archived scripts unless there is a clear active use case.

## Current recommendation

The first code movement slice is complete for `scripts/checks/`. Continue with another small wrapper-based movement. The safest next options are either a minimal DB helper subpackage foundation or a Telegram implementation move that keeps `scripts/telegram_cli.py` as the stable CLI wrapper.
