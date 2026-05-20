from __future__ import annotations


def test_db_helpers_wrapper_reexports_new_helpers_module() -> None:
    from scripts import db_helpers
    from scripts.db import helpers

    assert db_helpers.get_db_path is helpers.get_db_path
    assert db_helpers.now_iso is helpers.now_iso
    assert db_helpers.row_to_dict is helpers.row_to_dict
    assert db_helpers.rows_to_dicts is helpers.rows_to_dicts


def test_db_base_import_before_db_facade_does_not_cycle() -> None:
    from scripts.db_base import init_db
    from scripts import db

    assert callable(init_db)
    assert db.ROOT_DIR.name == "0-a-control"


def test_scripts_db_facade_exposes_server_compat_attrs() -> None:
    from scripts import db

    expected_attrs = [
        "ROOT_DIR",
        "append_source_record",
        "create_sample_data_if_empty",
        "end_session",
        "close_latest_active_session_for_agent",
        "evaluate_quest",
        "get_external_inbox_overview",
        "get_external_inbox_source_messages",
        "get_agent_statuses",
        "get_current_state",
        "get_latest_briefs",
        "get_plans",
        "get_quests",
        "get_recent_sessions",
        "get_session_view_model",
        "get_source_records",
        "get_work_queue_raw",
        "generate_executor_prompt",
        "get_executor_prompt_templates",
        "get_workdiary_priority_candidates",
        "get_workdiary_top_level",
        "report_quest_progress",
        "refresh_current_state",
        "defer_current_quest_to_short_term",
        "promote_confirmed_starting_point_to_quest",
        "start_session",
    ]

    for attr in expected_attrs:
        assert hasattr(db, attr), attr
