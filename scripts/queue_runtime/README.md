# Queue Runtime Package

Home for queue processing and runtime execution components.

## Completed moves

- `scripts/queue_runtime/queue_worker.py` keeps `scripts/queue_worker.py` as a compatibility wrapper.
- `scripts/queue_runtime/report_export.py` keeps `scripts/report_export.py` as a compatibility wrapper.

## Migration rules

- Keep old paths as wrappers until callers move to the new package.
- Do not use `scripts/queue/`; it can shadow Python's stdlib `queue` module.
- Do not mix queue movement with behavior changes.
