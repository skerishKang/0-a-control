# scripts package movement audit

This note records the current package movement boundary for issue #250.

## Current canonical package map

The current target layout is:

- `scripts/cli/` for user-facing command entry points.
- `scripts/queue_runtime/` for queue, report, and verdict runtime modules.
- `scripts/integrations/` for reusable integration helpers.
- `scripts/db/` for database helper modules.
- `scripts/services/` for shared service and helper modules.
- `scripts/server_handlers/` for HTTP route handler modules.

## Completed safe movement areas

The movement log shows that the stable low-risk slices have already been moved in small batches while preserving compatibility wrappers.

Covered areas include:

- repository and frontend checks
- DB helper modules
- service helpers
- queue runtime helpers
- verdict/report runtime helpers
- session import/export CLIs
- Telegram command helpers and reusable Telegram integration helpers

The old top-level script paths remain as compatibility wrappers where needed.

## Deferred high-risk areas

The following areas should remain deferred until a dedicated narrow issue is created for each one:

- `scripts/server.py`
- `scripts/telegram_service.py`
- `scripts/telegram_db.py`
- `scripts/db.py`
- `scripts/db_base.py`
- `scripts/db_sessions.py`
- server runtime behavior
- route contracts
- database schema
- Telegram core behavior

These files are central coordination points. Moving them inside #250 without a narrower contract would increase regression risk.

## Recommended next gate

Before moving any remaining high-risk file, create a dedicated issue that defines:

- exact module boundary
- compatibility wrapper contract
- import fallback strategy
- focused tests
- expected unchanged runtime behavior
- rollback path

For #250, the safe package-movement phase is now near the audit/documentation stage rather than another broad movement step.

## Known unrelated local test issue

Local full-suite failures in `tests/test_04_promote_start.py` are tracked separately in issue #408.

Expected local full-suite pattern when this unrelated issue appears:

```text
417 passed, 5 failed
```

This should not be treated as a package movement regression when GitHub CI and focused tests pass.
