"""Compatibility package for database modules during scripts package split."""

from __future__ import annotations

import os
from datetime import timezone
from importlib import import_module
from pathlib import Path
from typing import Any

UTC = timezone.utc
ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = Path(os.getenv("CONTROL_TOWER_DATA_DIR", str(ROOT_DIR / "data")))
DB_PATH = Path(os.getenv("CONTROL_TOWER_DB_PATH", str(DATA_DIR / "control_tower.db")))
WORKDIARY_DIR = Path(os.getenv("CONTROL_TOWER_WORKDIARY_DIR", str(ROOT_DIR.parent)))

_LAZY_EXPORTS: dict[str, tuple[str, str]] = {
    "append_source_record": ("scripts.db_sessions", "append_source_record"),
    "create_sample_data_if_empty": ("scripts.db_seed", "create_sample_data_if_empty"),
    "end_session": ("scripts.db_sessions", "end_session"),
    "close_latest_active_session_for_agent": ("scripts.db_sessions", "close_latest_active_session_for_agent"),
    "evaluate_quest": ("scripts.verdict_ops", "evaluate_quest"),
    "get_external_inbox_overview": ("scripts.db.inbox", "get_external_inbox_overview"),
    "get_external_inbox_source_messages": ("scripts.db.inbox", "get_external_inbox_source_messages"),
    "get_agent_statuses": ("scripts.agent_registry", "get_agent_statuses"),
    "get_current_state": ("scripts.db.ops", "get_current_state"),
    "get_latest_briefs": ("scripts.plan_ops", "get_latest_briefs"),
    "get_plans": ("scripts.plan_ops", "get_plans"),
    "get_quests": ("scripts.db.ops", "get_quests"),
    "get_recent_sessions": ("scripts.db.ops", "get_recent_sessions"),
    "get_resume_context": ("scripts.db.session_resume", "get_resume_context"),
    "get_session_view_model": ("scripts.db.session_view", "get_session_view_model"),
    "get_source_records": ("scripts.db_sessions", "get_source_records"),
    "get_work_queue_raw": ("scripts.db.ops", "get_work_queue_raw"),
    "generate_executor_prompt": ("scripts.executor_prompt", "generate_executor_prompt"),
    "get_executor_prompt_templates": ("scripts.executor_prompt", "get_executor_prompt_templates"),
    "get_workdiary_priority_candidates": ("scripts.db.workdiary", "get_workdiary_priority_candidates"),
    "get_workdiary_top_level": ("scripts.db.workdiary", "get_workdiary_top_level"),
    "report_quest_progress": ("scripts.verdict_ops", "report_quest_progress"),
    "refresh_current_state": ("scripts.db.state", "refresh_current_state"),
    "defer_current_quest_to_short_term": ("scripts.current_quest_ops", "defer_current_quest_to_short_term"),
    "promote_confirmed_starting_point_to_quest": ("scripts.current_quest_ops", "promote_confirmed_starting_point_to_quest"),
    "start_session": ("scripts.db_sessions", "start_session"),
}

__all__ = ["DB_PATH", "ROOT_DIR", "WORKDIARY_DIR", "UTC", *_LAZY_EXPORTS]


def __getattr__(name: str) -> Any:
    try:
        module_name, attr_name = _LAZY_EXPORTS[name]
    except KeyError as exc:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from exc
    value = getattr(import_module(module_name), attr_name)
    globals()[name] = value
    return value
