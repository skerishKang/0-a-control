# scripts package movement log

This log records completed small package movement slices.

## Completed

- `scripts/checks/repo_hygiene.py` keeps `scripts/check_repo_hygiene.py` as the stable command wrapper.
- `scripts/checks/frontend_safety.py` keeps `scripts/check_frontend_safety.py` as the stable command wrapper.
- `scripts/checks/server_smoke.py` keeps `scripts/smoke_server.py` as the stable command wrapper.
- `scripts/db/helpers.py` keeps `scripts/db_helpers.py` as a compatibility wrapper.
- `scripts/db/ops.py` keeps `scripts/db_ops.py` as a compatibility wrapper.
- `scripts/db/workdiary.py` keeps `scripts/db_workdiary_helpers.py` as a compatibility wrapper.
- `scripts/db/state.py` keeps `scripts/db_state.py` as a compatibility wrapper.
- `scripts/db/inbox.py` keeps `scripts/db_inbox.py` as a compatibility wrapper.
- `scripts/db/seed.py` keeps `scripts/db_seed.py` as a compatibility wrapper.
- `scripts/db/briefing.py` keeps `scripts/db_briefing.py` as a compatibility wrapper.
- `scripts/db/session_view.py` keeps `scripts/db_session_view.py` as a compatibility wrapper.
- `scripts/db/session_resume.py` keeps `scripts/db_session_resume.py` as a compatibility wrapper.
- `scripts/services/starting_point.py` keeps `scripts/confirmed_starting_point.py` as a compatibility wrapper.
- `scripts/services/settings_guardrails.py` keeps `scripts/settings_guardrails.py` as a compatibility wrapper.
- `scripts/services/operations_summary.py` keeps `scripts/operations_summary.py` as a compatibility wrapper.
- `scripts/services/operational_state.py` keeps `scripts/operational_state.py` as a compatibility wrapper.
- `scripts/services/github_service.py` keeps `scripts/github_service.py` as a compatibility wrapper.
- `scripts/services/manual_overrides.py` keeps `scripts/manual_overrides.py` as a compatibility wrapper.
- `scripts/services/executor_prompt.py` keeps `scripts/executor_prompt.py` as a compatibility wrapper.
- `scripts/services/request_validation.py` keeps `scripts/request_validation.py` as a compatibility wrapper.
- `scripts/services/agent_registry.py` keeps `scripts/agent_registry.py` as a compatibility wrapper.
- `scripts/services/validation_checklist.py` keeps `scripts/validation_checklist.py` as a compatibility wrapper.
- `scripts/services/work_queue.py` keeps `scripts/work_queue.py` as a compatibility wrapper.
- `scripts/services/planning_input.py` keeps `scripts/planning_input.py` as a compatibility wrapper.
- `scripts/services/plan_ops.py` keeps `scripts/plan_ops.py` as a compatibility wrapper.
- `scripts/services/current_quest_ops.py` keeps `scripts/current_quest_ops.py` as a compatibility wrapper.
- `scripts/services/ai_verdict.py` keeps `scripts/ai_verdict.py` as a compatibility wrapper.
- `scripts/cli/operating_loop_cli.py` keeps `scripts/operating_loop_cli.py` as a compatibility wrapper.
- `scripts/cli/import_agent_transcript.py` keeps `scripts/import_agent_transcript.py` as a compatibility wrapper.
- `scripts/cli/cleanup_import_verification_sessions.py` keeps `scripts/cleanup_import_verification_sessions.py` as a compatibility wrapper.
- `scripts/cli/db_search.py` keeps `scripts/db_search.py` as a compatibility wrapper.
- `scripts/cli/db_integrity_cli.py` keeps `scripts/db_integrity_cli.py` as a compatibility wrapper.
- `scripts/cli/validate_contract.py` keeps `scripts/validate_contract.py` as a compatibility wrapper.
- `scripts/cli/telegram_cli_main.py` keeps `scripts/telegram_cli_main.py` as a compatibility wrapper.
- `scripts/cli/telegram_cli.py` keeps `scripts/telegram_cli.py` as a compatibility wrapper.
- `scripts/cli/session_cli.py` keeps `scripts/session_cli.py` as a compatibility wrapper.
- `scripts/cli/inbox_cli.py` keeps `scripts/inbox_cli.py` as a compatibility wrapper.
- `scripts/cli/repair_stale_pending.py` keeps `scripts/repair_stale_pending.py` as a compatibility wrapper.
- `scripts/queue_runtime/queue_worker.py` keeps `scripts/queue_worker.py` as a compatibility wrapper.
- `scripts/queue_runtime/report_export.py` keeps `scripts/report_export.py` as a compatibility wrapper.
- `scripts/queue_runtime/verdict_import.py` keeps `scripts/verdict_import.py` as a compatibility wrapper.
- `scripts/queue_runtime/file_queue.py` keeps `scripts/file_queue.py` as a compatibility wrapper.
- `scripts/integrations/telegram_progress.py` keeps `scripts/telegram_progress.py` as a compatibility wrapper.
- `scripts/integrations/telegram_session_lock.py` keeps `scripts/telegram_session_lock.py` as a compatibility wrapper.
- `scripts/integrations/telegram_attachment_status.py` remains a historical intermediate command helper path; the current canonical command path is `scripts/cli/telegram_attachment_status.py`.
- `scripts/cli/telegram_attachment_status.py` keeps `scripts/telegram_attachment_status.py` as a compatibility wrapper.
- `scripts/cli/telegram_missing_attachment_count.py` keeps `scripts/telegram_missing_attachment_count.py` as a compatibility wrapper.
- `scripts/cli/telegram_backfill_priority.py` keeps `scripts/telegram_backfill_priority.py` as a compatibility wrapper.
- `scripts/integrations/telegram_service_helpers.py` keeps `scripts/telegram_service_helpers.py` as a compatibility wrapper.
- `scripts/integrations/telegram_helpers.py` keeps `scripts/telegram_helpers.py` as a compatibility wrapper.

## Follow-up notes

- Keep old paths as wrappers until imports are fully migrated.
- Preserve public constants and module-level handles used by tests.
- Move central DB files only after smaller helpers are stable.
- Do not mix behavior, schema, or route changes into package movement PRs.
- For Telegram command helpers, prefer `scripts/cli/`; use `scripts/integrations/` for reusable service helpers only.