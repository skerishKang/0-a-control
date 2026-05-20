# Integrations Package

Home of third-party service integrations.

## Completed moves

- `scripts/integrations/telegram_progress.py` keeps `scripts/telegram_progress.py` as a compatibility wrapper.
- `scripts/integrations/telegram_session_lock.py` keeps `scripts/telegram_session_lock.py` as a compatibility wrapper.
- `scripts/integrations/telegram_attachment_status.py` keeps `scripts/telegram_attachment_status.py` as a compatibility wrapper.
- `scripts/integrations/telegram_missing_attachment_count.py` keeps `scripts/telegram_missing_attachment_count.py` as a compatibility wrapper.

## Migration rules

- Keep old paths as wrappers until callers move to the new package.
- Move one integration helper at a time.
- Do not mix integration movement with behavior changes.
