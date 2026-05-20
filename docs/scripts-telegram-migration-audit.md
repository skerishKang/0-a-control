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
| `scripts/telegram_service_helpers.py` | `scripts/integrations/telegram_service_helpers.py` | Integration service helper. |

## Still flat in `scripts/`

These files remain in the flat `scripts/` namespace and need separate review before movement:

- `scripts/telegram_db.py`
- `scripts/telegram_cli.py`
- `scripts/telegram_helpers.py`
- `scripts/telegram_service.py`

## Guardrails

- Keep old paths as compatibility wrappers.
- Do not move CLI entrypoint helpers into `scripts/integrations/` just because they are Telegram-related.
- Prefer `scripts/cli/` for standalone command entrypoints.
- Prefer `scripts/integrations/` for reusable third-party service helpers.
- Move one file or one small dependency cluster per PR.
