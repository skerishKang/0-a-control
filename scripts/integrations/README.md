# Integrations Package

Home of third-party service integrations.

## Completed moves

- `scripts/integrations/telegram_progress.py` keeps `scripts/telegram_progress.py` as a compatibility wrapper.

## Migration rules

- Keep old paths as wrappers until callers move to the new package.
- Move one integration helper at a time.
- Do not mix integration movement with behavior changes.
