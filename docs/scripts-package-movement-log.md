# scripts package movement log

This log records completed small package movement slices.

## Completed

- `scripts/checks/repo_hygiene.py` keeps `scripts/check_repo_hygiene.py` as the stable command wrapper.
- `scripts/checks/frontend_safety.py` keeps `scripts/check_frontend_safety.py` as the stable command wrapper.
- `scripts/checks/server_smoke.py` keeps `scripts/smoke_server.py` as the stable command wrapper.
- `scripts/db/workdiary.py` keeps `scripts/db_workdiary_helpers.py` as a compatibility wrapper.
- `scripts/db/state.py` keeps `scripts/db_state.py` as a compatibility wrapper.
- `scripts/db/inbox.py` keeps `scripts/db_inbox.py` as a compatibility wrapper.
- `scripts/db/seed.py` keeps `scripts/db_seed.py` as a compatibility wrapper.
- `scripts/db/briefing.py` keeps `scripts/db_briefing.py` as a compatibility wrapper.
- `scripts/services/starting_point.py` keeps `scripts/confirmed_starting_point.py` as a compatibility wrapper.
- `scripts/services/settings_guardrails.py` keeps `scripts/settings_guardrails.py` as a compatibility wrapper.
- `scripts/services/operations_summary.py` keeps `scripts/operations_summary.py` as a compatibility wrapper.
- `scripts/services/operational_state.py` keeps `scripts/operational_state.py` as a compatibility wrapper.
- `scripts/services/github_service.py` keeps `scripts/github_service.py` as a compatibility wrapper.

## Follow-up notes

- Keep old paths as wrappers until imports are fully migrated.
- Preserve public constants and module-level handles used by tests.
- Move central DB files only after smaller helpers are stable.
- Do not mix behavior, schema, or route changes into package movement PRs.
