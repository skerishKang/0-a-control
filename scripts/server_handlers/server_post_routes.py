from __future__ import annotations
from http import HTTPStatus
import logging

from scripts.request_validation import validate_mutation_body


# ---- route method name mapping (string-based dispatch) ----
EXACT_ROUTE_METHODS: dict[str, str] = {
    "/api/quests/evaluate": "_post_quests_evaluate",
    "/api/current-state/refresh": "_post_current_state_refresh",
    "/api/quests/report": "_post_quests_report",
    "/api/sessions/start": "_post_sessions_start",
    "/api/sessions/log": "_post_sessions_log",
    "/api/sessions/end": "_post_sessions_end",
    "/api/agents/cleanup-stale": "_post_agents_cleanup_stale",
    "/api/telegram/sync-core": "_post_telegram_sync_core",
    "/api/bridge/parse": "_post_bridge_parse",
    "/api/bridge/quick-input": "_post_bridge_quick_input",
    "/api/bridge/create-plan": "_post_bridge_create_plan",
    "/api/tomorrow-first-quest/confirm": "_post_tomorrow_first_quest_confirm",
    "/api/tomorrow-first-quest/promote": "_post_tomorrow_first_quest_promote",
    "/api/tomorrow-first-quest/clear": "_post_tomorrow_first_quest_clear",
    "/api/ops-overrides": "_post_ops_overrides_create",
    "/api/executor-prompts/generate": "_post_executor_prompt_generate",
}

PREFIX_ROUTE_METHODS: list[tuple[str, str]] = [
    ("/api/current-quest/hold", "_post_current_quest_hold"),
    ("/api/quest-hold", "_post_current_quest_hold"),
    ("/api/current-quest/start", "_post_current_quest_start"),
    ("/api/current-quest/defer", "_post_current_quest_defer"),
    ("/api/quest-defer", "_post_current_quest_defer"),
]


def _clear_current_state_cache() -> None:
    from scripts.db_ops import clear_current_state_cache

    clear_current_state_cache()


def handle_post_dispatch(handler, path: str, body: dict) -> None:
    """Dispatch POST /api/ requests to the appropriate handler method.

    Validates registered mutation request bodies before dispatch. Uses
    getattr(handler, method_name) so mock handlers in tests can intercept calls,
    while production ControlTowerHandler delegates through its wrappers to the
    module-level logic below.

    Any registered mutation clears the in-process current-state cache before
    invoking the handler. Some handlers return a freshly computed current_state
    in the same response, so clearing first prevents stale cache reuse.
    """
    validation_error = validate_mutation_body(path, body)
    if validation_error:
        handler.send_json(validation_error, status=HTTPStatus.BAD_REQUEST)
        return

    method_name = EXACT_ROUTE_METHODS.get(path)
    if method_name:
        _clear_current_state_cache()
        getattr(handler, method_name)(body)
        return

    for prefix, prefix_method in PREFIX_ROUTE_METHODS:
        if path.startswith(prefix):
            _clear_current_state_cache()
            getattr(handler, prefix_method)(body)
            return

    handler.send_error(HTTPStatus.NOT_FOUND, "Unknown API endpoint")


# ---- Actual logic helpers (called by handler wrappers in server.py) ----

def _get_db():
    """Lazy import to avoid circular dependency."""
    from scripts.server import (
        evaluate_quest, refresh_current_state, _db,
        report_quest_progress, start_session, append_source_record,
        end_session, close_latest_active_session_for_agent, run_sync_core,
        classify_conversation, parse_quick_input, approve_plan_candidates,
        confirm_starting_point, promote_confirmed_starting_point_to_quest,
        clear_confirmed_starting_point, create_manual_override,
        get_current_state, defer_current_quest_to_short_term,
        update_manual_override,
    )
    return locals()


def handle_post_quests_evaluate(handler, body):
    db = _get_db()
    result = db["evaluate_quest"](
        quest_id=body["quest_id"],
        verdict=body["verdict"],
        reason=body.get("reason", ""),
        restart_point=body.get("restart_point", ""),
        next_quest_hint=body.get("next_quest_hint", ""),
        plan_impact=body.get("plan_impact", ""),
    )
    handler.send_json({"ok": True, "quest": result, "current_state": db["get_current_state"]()})


def handle_post_current_state_refresh(handler, body):
    result = _get_db()["refresh_current_state"]()
    handler.send_json({"ok": True, "state": result})


def handle_post_current_quest_hold(handler, body):
    result = _get_db()["_db"].mark_current_quest_unfinished()
    handler.send_json({"ok": True, **result})


def handle_post_current_quest_start(handler, body):
    result = _get_db()["_db"].start_current_quest_from_main_mission()
    handler.send_json({"ok": True, **result})


def handle_post_current_quest_defer(handler, body):
    result = _get_db()["defer_current_quest_to_short_term"]()
    handler.send_json({"ok": True, **result})


def handle_post_quests_report(handler, body):
    db = _get_db()
    result = db["report_quest_progress"](
        quest_id=body["quest_id"],
        work_summary=body.get("work_summary", ""),
        remaining_work=body.get("remaining_work", ""),
        blocker=body.get("blocker", ""),
        self_assessment=body.get("self_assessment", ""),
        session_id=body.get("session_id", ""),
    )
    handler.send_json({"ok": True, "quest": result, "current_state": db["get_current_state"]()})


def handle_post_sessions_start(handler, body):
    db = _get_db()
    result = db["start_session"](
        agent_name=body["agent_name"],
        source_type=body["source_type"],
        model_name=body.get("model_name", ""),
        project_key=body.get("project_key", ""),
        working_dir=body.get("working_dir", ""),
        title=body.get("title", ""),
        metadata=body.get("metadata"),
    )
    handler.send_json({"ok": True, "session": result})


def handle_post_sessions_log(handler, body):
    db = _get_db()
    result = db["append_source_record"](
        session_id=body["session_id"],
        source_name=body["source_name"],
        source_type=body["source_type"],
        content=body["content"],
        role=body.get("role", "user"),
        project_key=body.get("project_key", ""),
        working_dir=body.get("working_dir", ""),
        metadata=body.get("metadata"),
    )
    handler.send_json({"ok": True, "record": result})


def handle_post_sessions_end(handler, body):
    db = _get_db()
    result = db["end_session"](
        session_id=body["session_id"],
        summary_md=body.get("summary_md", ""),
        status=body.get("status", "closed"),
        files_touched=body.get("files_touched"),
        actions=body.get("actions"),
        metadata=body.get("metadata"),
    )
    handler.send_json({"ok": True, "session": result})


def handle_post_agents_cleanup_stale(handler, body):
    db = _get_db()
    result = db["close_latest_active_session_for_agent"](
        agent_name=body["agent_name"],
        summary_md=body.get("summary_md", "stale active session closed from dashboard"),
        metadata={"user_action": "cleanup_stale_agent_session"},
    )
    handler.send_json({"ok": True, "session": result})


def handle_post_telegram_sync_core(handler, body):
    result = _get_db()["run_sync_core"]()
    handler.send_json(result)


def handle_post_bridge_parse(handler, body):
    text = body.get("text", "").strip()
    if not text:
        handler.send_json({"error": "text is required"}, status=HTTPStatus.BAD_REQUEST)
        return
    db = _get_db()
    classification = db["classify_conversation"](text)
    handler.send_json({
        "classification": classification,
        "suggested_plans": classification.get("suggested_plans", []),
    })


def handle_post_bridge_quick_input(handler, body):
    text = body.get("text", "").strip()
    if not text:
        handler.send_json({"error": "text is required"}, status=HTTPStatus.BAD_REQUEST)
        return
    result = _get_db()["parse_quick_input"](text)
    handler.send_json(result)


def handle_post_bridge_create_plan(handler, body):
    candidates = body.get("candidates", [])
    if not candidates:
        handler.send_json({"error": "candidates is required"}, status=HTTPStatus.BAD_REQUEST)
        return
    result = _get_db()["approve_plan_candidates"](candidates)
    handler.send_json({"ok": True, "plans": result})


def handle_post_tomorrow_first_quest_confirm(handler, body):
    title = body.get("title")
    if not title:
        handler.send_json({"error": "title is required"}, status=HTTPStatus.BAD_REQUEST)
        return
    db = _get_db()
    result = db["confirm_starting_point"](
        title=title,
        reason=body.get("reason", ""),
        source=body.get("source", "manual"),
    )
    handler.send_json({**result, "current_state": db["get_current_state"]()})


def handle_post_tomorrow_first_quest_promote(handler, body):
    db = _get_db()
    result = db["promote_confirmed_starting_point_to_quest"]()
    handler.send_json({**result, "current_state": db["get_current_state"]()})


def handle_post_tomorrow_first_quest_clear(handler, body):
    db = _get_db()
    result = db["clear_confirmed_starting_point"]()
    handler.send_json({**result, "current_state": db["get_current_state"]()})


def handle_post_ops_overrides_create(handler, body):
    result = _get_db()["create_manual_override"](body)
    handler.send_json({"ok": True, "override": result})


def handle_post_executor_prompt_generate(handler, body):
    from scripts.executor_prompt import generate_executor_prompt

    result = generate_executor_prompt(
        prompt_type=body["prompt_type"],
        work_item=body.get("work_item"),
        classification=body.get("classification"),
        manual_override=body.get("manual_override"),
        validation_checklist=body.get("validation_checklist"),
        repository=body.get("repository"),
        changed_files=body.get("changed_files"),
        execution_context=body.get("execution_context", "remote_doable"),
        guards=tuple(body.get("guards", [])),
        links=body.get("links"),
        include_validation=body.get("include_validation", False),
        include_override=body.get("include_override", False),
        include_links=body.get("include_links", False),
    )
    handler.send_json(result)