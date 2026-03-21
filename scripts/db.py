from __future__ import annotations

import sys
from pathlib import Path

if __package__ in (None, ""):
    project_root = Path(__file__).resolve().parents[1]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from scripts.db_base import DB_PATH, ROOT_DIR, WORKDIARY_DIR, UTC, connect, init_db, now_iso
    from scripts.db_ops import (
        approve_plan_candidates,
        evaluate_quest,
        get_current_state,
        get_latest_briefs,
        get_plans,
        get_quests,
        get_recent_sessions,
        report_quest_progress,
    )
    from scripts.db_sessions import (
        append_source_record,
        end_session,
        get_resume_context,
        get_session_view_model,
        get_source_records,
        start_session,
        update_session_summary,
    )
    from scripts.db_seed import create_sample_data_if_empty
    from scripts.db_state import (
        get_external_inbox_overview,
        get_external_inbox_source_messages,
        get_workdiary_priority_candidates,
        get_workdiary_top_level,
        refresh_current_state,
    )
else:
    from .db_base import DB_PATH, ROOT_DIR, WORKDIARY_DIR, UTC, connect, init_db, now_iso
    from .db_ops import (
        evaluate_quest,
        get_current_state,
        get_latest_briefs,
        get_plans,
        get_quests,
        get_recent_sessions,
        report_quest_progress,
    )
    from .db_sessions import (
        append_source_record,
        end_session,
        get_resume_context,
        get_session_view_model,
        get_source_records,
        start_session,
        update_session_summary,
    )
    from .db_seed import create_sample_data_if_empty
    from .db_state import (
        get_external_inbox_overview,
        get_external_inbox_source_messages,
        get_workdiary_priority_candidates,
        get_workdiary_top_level,
        refresh_current_state,
    )

__all__ = [
    "append_source_record",
    "DB_PATH",
    "ROOT_DIR",
    "WORKDIARY_DIR",
    "UTC",
    "connect",
    "create_sample_data_if_empty",
    "evaluate_quest",
    "get_external_inbox_overview",
    "get_external_inbox_source_messages",
    "end_session",
    "get_current_state",
    "get_plans",
    "get_quests",
    "get_recent_sessions",
    "get_resume_context",
    "get_session_view_model",
    "get_source_records",
    "report_quest_progress",
    "get_workdiary_priority_candidates",
    "get_workdiary_top_level",
    "init_db",
    "now_iso",
    "refresh_current_state",
    "start_session",
    "update_session_summary",
]
