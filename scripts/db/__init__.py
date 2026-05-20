"""Public database facade for the control tower.

This package keeps the historical ``from scripts import db`` and
``from scripts.db import ...`` imports working while DB modules are moved into
subpackages one small slice at a time.
"""

from __future__ import annotations

from scripts.agent_registry import get_agent_statuses, list_registered_agents
from scripts.current_quest_ops import (
    defer_current_quest_to_short_term,
    mark_current_quest_unfinished,
    promote_confirmed_starting_point_to_quest,
    start_current_quest_from_main_mission,
)
from scripts.db_base import DB_PATH, ROOT_DIR, WORKDIARY_DIR, UTC, connect, init_db, now_iso
from scripts.db_inbox import get_external_inbox_overview, get_external_inbox_source_messages
from scripts.db_ops import (
    get_current_state,
    get_quests,
    get_recent_sessions,
    get_work_queue_raw,
)
from scripts.db_seed import create_sample_data_if_empty
from scripts.db_session_resume import get_resume_context
from scripts.db_session_view import get_session_view_model
from scripts.db_sessions import (
    append_source_record,
    close_latest_active_session_for_agent,
    end_session,
    get_source_records,
    start_session,
    update_session_summary,
)
from scripts.db_state import refresh_current_state
from scripts.db_workdiary_helpers import (
    get_workdiary_priority_candidates,
    get_workdiary_top_level,
)
from scripts.executor_prompt import (
    generate_executor_prompt,
    get_executor_prompt_templates,
)
from scripts.plan_ops import approve_plan_candidates, get_latest_briefs, get_plans
from scripts.verdict_ops import (
    DuplicateVerdict,
    apply_verdict,
    evaluate_quest,
    report_quest_progress,
)
from scripts.work_queue import (
    Queue,
    get_blocked_items,
    get_local_needed_items,
    get_now_items,
    get_validation_needed_items,
    group_by_queue,
    normalize_work_items,
    sort_work_items,
)

__all__ = [
    "append_source_record",
    "close_latest_active_session_for_agent",
    "DB_PATH",
    "ROOT_DIR",
    "WORKDIARY_DIR",
    "UTC",
    "connect",
    "create_sample_data_if_empty",
    "DuplicateVerdict",
    "apply_verdict",
    "evaluate_quest",
    "get_external_inbox_overview",
    "get_external_inbox_source_messages",
    "get_agent_statuses",
    "list_registered_agents",
    "end_session",
    "get_current_state",
    "mark_current_quest_unfinished",
    "start_current_quest_from_main_mission",
    "defer_current_quest_to_short_term",
    "get_plans",
    "get_quests",
    "get_recent_sessions",
    "get_resume_context",
    "get_session_view_model",
    "get_source_records",
    "get_work_queue_raw",
    "report_quest_progress",
    "get_workdiary_priority_candidates",
    "get_workdiary_top_level",
    "init_db",
    "now_iso",
    "promote_confirmed_starting_point_to_quest",
    "refresh_current_state",
    "start_session",
    "update_session_summary",
    "Queue",
    "get_blocked_items",
    "get_local_needed_items",
    "get_now_items",
    "get_validation_needed_items",
    "group_by_queue",
    "normalize_work_items",
    "sort_work_items",
    "generate_executor_prompt",
    "get_executor_prompt_templates",
]
