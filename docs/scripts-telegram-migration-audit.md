# Telegram script migration audit

This audit records the current canonical package locations for Telegram-related script migration work.

## Current canonical locations

| Old path | Current canonical path | Notes |
| --- | --- | --- |
| `scripts/telegram_progress.py` | `scripts/integrations/telegram_progress.py` | Integration progress helper. |
| `scripts/telegram_session_lock.py` | `scripts/integrations/telegram_session_lock.py` | Integration session lock helper. |
| `scripts/telegram_attachment_status.py` | `scripts/cli/telegram_attachment_status.py` | CLI entrypoint helper. Do not move to integrations without a separate deliberate cleanup. |
| `scripts/telegram_missing_attachment_count.py` | `scripts/cli/telegram_missing_attachment_count.py` | CLI entrypoint helper. Do not move to integrations without a separate deliberate cleanup. |
| `scripts/telegram_backfill_priority.py` | `scripts/cli/telegram_backfill_priority.py` | CLI entrypoint helper. |
| `scripts/telegram_cli_main.py` | `scripts/cli/telegram_cli_main.py` | CLI main entrypoint. |
| `scripts/telegram_cli.py` | `scripts/cli/telegram_cli.py` | CLI import/sync command implementation. |
| `scripts/telegram_service_helpers.py` | `scripts/integrations/telegram_service_helpers.py` | Integration service helper. |
| `scripts/telegram_helpers.py` | `scripts/integrations/telegram_helpers.py` | Shared Telegram helper functions. |

## Still flat in `scripts/`

These files remain in the flat `scripts/` namespace and need separate review before movement:

- `scripts/telegram_db.py`
- `scripts/telegram_service.py`

## Deferred movement notes

### `scripts/telegram_db.py`

`telegram_db.py` should not be moved to `scripts/db/` in the current layout because `scripts/db.py` already exists as the public database facade. Creating a `scripts/db/` package would therefore require a broader database-layer restructuring and is outside the safe Telegram migration slice.

Keep `scripts/telegram_db.py` flat until one of these is true:

- the database facade is deliberately renamed or split so a `scripts/db/` package can exist safely;
- a separate canonical location is approved for Telegram-specific DB storage helpers;
- tests that import and mutate `scripts.telegram_db.DB_PATH` are updated or a compatibility wrapper explicitly preserves that patching behavior.

## Guardrails

- Keep old paths as compatibility wrappers.
- Do not move CLI entrypoint helpers into `scripts/integrations/` just because they are Telegram-related.
- Prefer `scripts/cli/` for standalone command entrypoints.
- Prefer `scripts/integrations/` for reusable third-party service helpers.
- Move one file or one small dependency cluster per PR.
