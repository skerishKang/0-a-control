# SQLite Concurrency Policy

Refs #117.

## Purpose

0-a-control is a local-first control tower. Multiple local processes may access the SQLite database:

- HTTP server
- queue worker
- CLI/session wrappers
- Telegram sync tools
- tests and maintenance scripts

This document records the intended database access policy before making behavioral changes to connection pragmas or write transactions.

## Current baseline

`scripts/db_base.py` owns the central SQLite connection helper.

Current baseline expectations:

- Open the configured DB path.
- Ensure parent directory exists.
- Use `sqlite3.Row` row factory.
- Apply a busy timeout.
- Commit at the end of the context manager body.
- Close the connection after use.

## Policy decisions to make explicit in code

Future code changes should make these decisions explicit:

1. Whether `PRAGMA foreign_keys = ON` is required for every connection.
2. Whether WAL mode should be enabled for local multi-process reads/writes.
3. Whether write-heavy operations should use `BEGIN IMMEDIATE`.
4. Whether long-running workers should expose retry/backoff behavior at the DB layer or caller layer.
5. How tests should override `CONTROL_TOWER_DATA_DIR` and `CONTROL_TOWER_DB_PATH`.

## Recommended target behavior

Recommended connection setup:

```python
conn = sqlite3.connect(path, timeout=10)
conn.row_factory = sqlite3.Row
conn.execute("PRAGMA busy_timeout = 10000")
conn.execute("PRAGMA foreign_keys = ON")
```

WAL mode should be evaluated carefully:

```python
conn.execute("PRAGMA journal_mode = WAL")
```

WAL is useful for local multi-process read/write behavior, but the project should confirm that it is acceptable for all supported local environments before enabling it unconditionally.

## Write transaction guidance

Small writes may continue to use the existing context manager if tests show stable behavior.

For operations that update several related tables or queue files, prefer a clearly named helper or explicit transaction boundary so future maintainers can tell which operations are atomic.

## Test baseline

Before changing DB pragmas, add or verify tests for:

| Case | Expected result |
| --- | --- |
| DB initializes from empty path | pass |
| DB initialization is idempotent | pass |
| `connect()` enforces row factory | rows support key access |
| `foreign_keys` setting is visible if enabled | pragma returns `1` |
| concurrent read during write-like operation | no unexpected crash under local timeout |

## Non-goals

This project does not need to become a client/server database system. The target remains simple, local-first, and inspectable.