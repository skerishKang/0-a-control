from __future__ import annotations

"""
scripts/db.py — Public facade for the database layer.

This module re-exports selected symbols from the internal ``scripts.db_*``
submodules so that callers can import everything they need from a single
entry point (``from scripts import db`` or ``from scripts.db import ...``).

**Stable public API** is explicitly listed in ``__all__``.  Anything not
present in ``__all__`` is an internal implementation detail and should not
be imported from this module.

Future direction: as the codebase grows, the facade may be split into
smaller domain-specific facades (e.g. ``scripts.db_quests``,
``scripts.db_sessions``) and this module will become a thin aggregator
that re-exports those.  For now, all re-exports live here.
"""

import sys
from pathlib import Path

if __package__ in (None, ""):
    project_root = Path(__file__).resolve().parents[1]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from scripts.agent_registry import get_agent_statuses, list_registered_agents
    from scripts.db_base import DB_PATH, ROOT_DIR, WORKDIARY_DIR, UTC, connect, init_db, now_iso
    from scripts.current_quest_ops import (
        defer_current_quest_to_short_term,
        mark_current_quest_unfinished,
        promote_confirmed_starting_point_to_quest,
        start_current_quest_from_main_mission,
    )
    from scripts.plan_ops import approve_plan_candidates, get_latest_briefs, get_plans
    from scripts.verdict_ops import (
        DuplicateVerdict,
        apply_verdict,
        evaluate_quest,
        report_quest_progress,
    )
    from scripts.db_ops import (
        get_current_state,
        get_quests,
        get_recent_sessions,
        get_work_queue_raw,
    )
    from scripts.db_session_view import get_session_view_model
    from scripts.db_session_resume import get_resume_context
    from scripts.db_inbox import get_external_inbox_overview, get_external_inbox_source_messages
    from scripts.db_sessions import (
        append_source_record,
        close_latest_active_session_for_agent,
        end_session,
        get_source_records,
        start_session,
        update_session_summary,
    )
    from scripts.db_seed import create_sample_data_if_empty
    from scripts.db_state import refresh_current_state
    from scripts.db_workdiary_helpers import (
        get_workdiary_priority_candidates,
        get_workdiary_top_level,
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
    from scripts.executor_prompt import (
        generate_executor_prompt,
        get_executor_prompt_templates,
    )
else:
    from .agent_registry import get_agent_statuses, list_registered_agents
    from .db_base import DB_PATH, ROOT_DIR, WORKDIARY_DIR, UTC, connect, init_db, now_iso
    from .current_quest_ops import (
        defer_current_quest_to_short_term,
        mark_current_quest_unfinished,
        promote_confirmed_starting_point_to_quest,
        start_current_quest_from_main_mission,
    )
    from .plan_ops import approve_plan_candidates, get_latest_briefs, get_plans
    from .verdict_ops import (
        DuplicateVerdict,
        apply_verdict,
        evaluate_quest,
        report_quest_progress,
    )
    from .db_ops import (
        get_current_state,
        get_quests,
        get_recent_sessions,
        get_work_queue_raw,
    )
    from .db_session_view import get_session_view_model
    from .db_session_resume import get_resume_context
    from .db_inbox import get_external_inbox_overview, get_external_inbox_source_messages
    from .db_sessions import (
        append_source_record,
        close_latest_active_session_for_agent,
        end_session,
        get_source_records,
        start_session,
        update_session_summary,
    )
    from .db_seed import create_sample_data_if_empty
    from .db_state import refresh_current_state
    from .db_workdiary_helpers import (
        get_workdiary_priority_candidates,
        get_workdiary_top_level,
    )
    from .work_queue import (
        Queue,
        get_blocked_items,
        get_local_needed_items,
        get_now_items,
        get_validation_needed_items,
        group_by_queue,
        normalize_work_items,
        sort_work_items,
    )
    from .executor_prompt import (
        generate_executor_prompt,
        get_executor_prompt_templates,
    )

__all__ = [
    # --- Sessions ---
    "append_source_record",
    "close_latest_active_session_for_agent",
    # --- Database connection & config ---
    "DB_PATH",
    "ROOT_DIR",
    "WORKDIARY_DIR",
    "UTC",
    "connect",
    # --- Seeding ---
    "create_sample_data_if_empty",
    # --- Verdicts ---
    "DuplicateVerdict",
    "apply_verdict",
    "evaluate_quest",
    # --- Inbox ---
    "get_external_inbox_overview",
    "get_external_inbox_source_messages",
    # --- Agents ---
    "get_agent_statuses",
    "list_registered_agents",
    # --- Sessions (cont.) ---
    "end_session",
    # --- State ---
    "get_current_state",
    # --- Quests ---
    "mark_current_quest_unfinished",
    "start_current_quest_from_main_mission",
    "defer_current_quest_to_short_term",
    # --- Plans ---
    "get_plans",
    # --- Quests ---
    "get_quests",
    # --- Sessions (cont.) ---
    "get_recent_sessions",
    "get_resume_context",
    "get_session_view_model",
    "get_source_records",
    # --- Work Queue ---
    "get_work_queue_raw",
    # --- Verdicts (cont.) ---
    "report_quest_progress",
    # --- State (cont.) ---
    "get_workdiary_priority_candidates",
    "get_workdiary_top_level",
    # --- Database connection & config (cont.) ---
    "init_db",
    "now_iso",
    # --- Quests (cont.) ---
    "promote_confirmed_starting_point_to_quest",
    # --- State (cont.) ---
    "refresh_current_state",
    # --- Sessions (cont.) ---
    "start_session",
    "update_session_summary",
    # --- Work Queue (cont.) ---
    "Queue",
    "get_blocked_items",
    "get_local_needed_items",
    "get_now_items",
    "get_validation_needed_items",
    "group_by_queue",
    "normalize_work_items",
    "sort_work_items",
    # --- Prompts ---
    "generate_executor_prompt",
    "get_executor_prompt_templates",
]