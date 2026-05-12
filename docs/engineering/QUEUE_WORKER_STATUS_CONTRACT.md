# Queue Worker Status Contract

Refs #113.

## Purpose

`scripts/queue_worker.py` continuously polls verdict queue files and imports verdicts. Operators need a lightweight status artifact that can be inspected by humans, scripts, and eventually the board UI.

This document defines the status contract before runtime code writes it.

## Status file path

Recommended path:

```text
data/runtime/queue_worker_status.json
```

The file should be safe to delete. The worker should recreate it on the next loop.

## Minimal payload

```json
{
  "status": "running",
  "updated_at": "2026-05-12T06:00:00Z",
  "last_success_at": "2026-05-12T06:00:00Z",
  "last_error_at": null,
  "last_error": null,
  "processed_count": 0,
  "failed_count": 0,
  "duplicate_count": 0,
  "archive_revision_count": 0,
  "poll_interval_seconds": 2
}
```

## Field definitions

| Field | Meaning |
| --- | --- |
| `status` | `running`, `degraded`, `stopped`, or `unknown` |
| `updated_at` | time the status file was last written |
| `last_success_at` | last successful polling/import pass |
| `last_error_at` | most recent error timestamp, if any |
| `last_error` | sanitized error summary, not a full traceback |
| `processed_count` | total processed files since worker start |
| `failed_count` | total failed files since worker start |
| `duplicate_count` | total duplicate files since worker start |
| `archive_revision_count` | total stale revision files since worker start |
| `poll_interval_seconds` | current worker sleep/backoff interval |

## Error handling policy

- Store sanitized error summaries only.
- Do not store raw local file contents.
- Do not store secrets, tokens, or full tracebacks in the status JSON.
- Full diagnostics should remain in logs.

## Writer behavior

Recommended behavior:

1. Write status at worker startup.
2. Update status after every polling loop.
3. Mark `degraded` after an import exception.
4. Mark `running` after a clean import pass.
5. On graceful keyboard interruption, write `stopped` if practical.

## Reader behavior

Readers should treat a missing file as `unknown`, not as fatal.

Recommended stale threshold:

- If `updated_at` is older than 2x the expected polling interval plus backoff allowance, UI may show stale/degraded.

## Follow-up implementation path

1. Add a helper in `queue_worker.py` to write the status file atomically.
2. Optionally adjust `import_verdicts()` to return per-loop counters.
3. Add tests around status payload shape.
4. Later, expose status in operations/guardrails panels.
