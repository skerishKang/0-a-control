# Core Test Coverage Matrix

Refs #120.

## Purpose

This document defines the minimum test baseline for 0-a-control as it moves from prototype behavior toward a more reliable local operations tool.

The matrix is intentionally focused on high-value regression coverage:

1. DB initialization and state persistence.
2. Verdict/report queue ingest behavior.
3. Server route error handling and core API routes.
4. Board-v2 smoke and escaping behavior.

## Local test command baseline

Recommended default command:

```bash
python -m pytest
```

If future tests require optional external services, they should be skipped by default and activated through an explicit marker or environment variable.

Example:

```bash
python -m pytest -m integration
```

## 1. DB initialization and migration

| Test area | Case | Expected result |
| --- | --- | --- |
| Empty DB | initialize from no database file | schema exists and core tables are available |
| Idempotency | run initialization twice | no duplicate table/index failure |
| Current state | write/read basic state value | value round-trips as expected |
| Event log | record a simple event | event exists with expected type/entity fields |
| Work queue state | missing work queue | returns empty list rather than crashing |

## 2. Report and verdict ingest

| Test area | Case | Expected result |
| --- | --- | --- |
| Valid verdict | complete verdict payload with report ref and plan impact | verdict is applied and source file moves to processed |
| Invalid JSON | malformed verdict JSON | file moves to failed |
| Missing report ref | no `report_ref` or compatible fallback | file moves to failed |
| Missing quest id | cannot resolve quest ID from verdict/report/correlation | file moves to failed |
| Missing plan impact | verdict has no plan-impact data | file moves to failed |
| Duplicate verdict | same verdict imported twice | duplicate routing is used |
| Stale revision | older revision imported after newer one | archive-revision routing is used |

## 3. Server routes

| Test area | Case | Expected result |
| --- | --- | --- |
| Health | GET health route | returns 200 JSON payload |
| Current state | GET current-state | returns JSON object with current state key |
| Invalid JSON | POST route with malformed JSON | returns 400 JSON error |
| Oversized body | POST body over configured limit | returns 413 JSON error |
| Missing required field | route raises KeyError | returns 400 with sanitized missing-field message |
| Internal error | unexpected exception | returns 500 without leaking raw internal details |
| Static path traversal | request path outside public dir | returns 404 |

## 4. Board-v2 smoke coverage

These can start as manual fixtures or browserless smoke tests and later move to Playwright or equivalent.

| Test area | Case | Expected result |
| --- | --- | --- |
| Initial load | mock successful API responses | board renders non-empty layout |
| Partial load | sessions or plans API fails | board still renders and records partial error state |
| Modal text | open modal with plain text | title/body are displayed |
| Escaping | modal/list text includes `<script>`-like content | text is displayed inertly, not executed |
| Quick input | submit non-empty quick input | POST is issued and draft clears on success |
| Polling guard | form has unsent content | polling does not overwrite active input |

## 5. Dependency and marker policy

Suggested markers:

```ini
[pytest]
markers =
    integration: requires optional local/external service
    browser: requires browser automation
```

Default test runs should avoid requiring:

- Telegram credentials.
- External network access.
- Running browser services.
- A user’s real production-like local data directory.

## 6. Fixture data policy

Test fixtures should use temporary directories and temporary SQLite database paths.

Recommended environment override pattern:

```bash
CONTROL_TOWER_DATA_DIR=/tmp/0-a-control-test-data
CONTROL_TOWER_DB_PATH=/tmp/0-a-control-test-data/control_tower.db
```

Tests must not depend on real `data/` contents in the repository root.

## 7. Follow-up implementation sequence

1. Add DB init/idempotency tests.
2. Add verdict ingest fixtures for valid/missing/duplicate/stale cases.
3. Add server request parsing and error response tests.
4. Add board-v2 smoke fixtures or a documented browser test harness.
5. Add CI command documentation once the local baseline is stable.
