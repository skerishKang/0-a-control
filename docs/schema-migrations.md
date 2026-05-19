# Schema migrations

The control tower database starts from idempotent schema SQL in `scripts/db_schema.py`.

`init_db()` now also records a baseline schema version in `schema_migrations`.
This baseline does not redesign existing tables. It only creates migration bookkeeping so future DB changes can be tracked safely.

## Current baseline

- Version: `1`
- Name: `baseline-current-schema`
- Meaning: the current schema after `SCHEMA`, `INDEXES`, and `FTS_SCHEMA` are applied

## Adding a future migration

1. Add a new integer version greater than the current baseline.
2. Keep the migration idempotent.
3. Apply it inside `apply_schema_migrations(conn)` only if its version is not already recorded.
4. Record the version in `schema_migrations` after the migration completes successfully.
5. Add a test proving the migration can run repeatedly without duplicating work.

## Rules

- Do not alter existing runtime data without a migration step.
- Keep fresh database initialization and existing database upgrade paths both working.
- Add tests for every non-trivial migration.
