from __future__ import annotations
from http import HTTPStatus
from scripts.server import (
    evaluate_quest, refresh_current_state, _db,
    report_quest_progress, start_session, append_source_record,
    end_session, close_latest_active_session_for_agent, run_sync_core,
    classify_conversation, parse_quick_input, approve_plan_candidates,
    confirm_starting_point, promote_confirmed_starting_point_to_quest,
    clear_confirmed_starting_point, create_manual_override,
    get_current_state, defer_current_quest_to_short_term,
)


def handle_post_quests_evaluate(handler, body: dict) -> None:
    result = evaluate_quest(
        quest_id=body["quest_id"],
        verdict=body["verdict"],
        reason=body.get("reason", ""),
        restart_point=body.get("restart_point", ""),
        next_quest_hint=body.get("next_quest_hint", ""),
        plan_impact=body.get("plan_impact", ""),
    )
    handler.send_json({"ok": True, "quest": result, "current_state": get_current_state()})

def handle_post_current_state_refresh(handler, body: dict) -> None:
    result = refresh_current_state()
    handler.send_json({"ok": True, "state": result})

def handle_post_current_quest_hold(handler, body: dict) -> None:
    result = _db.mark_current_quest_unfinished()
    handler.send_json({"ok": True, **result})

def handle_post_current_quest_start(handler, body: dict) -> None:
    result = _db.start_current_quest_from_main_mission()
    handler.send_json({"ok": True, **result})

def handle_post_current_quest_defer(handler, body: dict) -> None:
    result = defer_current_quest_to_short_term()
    handler.send_json({"ok": True, **result})

def handle_post_quests_report(handler, body: dict) -> None:
    result = report_quest_progress(
        quest_id=body["quest_id"],
        work_summary=body.get("work_summary", ""),
        remaining_work=body.get("remaining_work", ""),
        blocker=body.get("blocker", ""),
        self_assessment=body.get("self_assessment", ""),
        session_id=body.get("session_id", ""),
    )
    handler.send_json({"ok": True, "quest": result, "current_state": get_current_state()})

def handle_post_sessions_start(handler, body: dict) -> None:
    result = start_session(
        agent_name=body["agent_name"],
        source_type=body["source_type"],
        model_name=body.get("model_name", ""),
        project_key=body.get("project_key", ""),
        working_dir=body.get("working_dir", ""),
        title=body.get("title", ""),
        metadata=body.get("metadata"),
    )
    handler.send_json({"ok": True, "session": result})

def handle_post_sessions_log(handler, body: dict) -> None:
    result = append_source_record(
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

def handle_post_sessions_end(handler, body: dict) -> None:
    result = end_session(
        session_id=body["session_id"],
        summary_md=body.get("summary_md", ""),
        status=body.get("status", "closed"),
        files_touched=body.get("files_touched"),
        actions=body.get("actions"),
        metadata=body.get("metadata"),
    )
    handler.send_json({"ok": True, "session": result})

def handle_post_agents_cleanup_stale(handler, body: dict) -> None:
    result = close_latest_active_session_for_agent(
        agent_name=body["agent_name"],
        summary_md=body.get("summary_md", "stale active session closed from dashboard"),
        metadata={"user_action": "cleanup_stale_agent_session"},
    )
    handler.send_json({"ok": True, "session": result})

def handle_post_telegram_sync_core(handler, body: dict) -> None:
    result = run_sync_core()
    handler.send_json(result)

def handle_post_bridge_parse(handler, body: dict) -> None:
    text = body.get("text", "").strip()
    if not text:
        handler.send_json({"error": "text is required"}, status=HTTPStatus.BAD_REQUEST)
        return
    classification = classify_conversation(text)
    handler.send_json({
        "classification": classification,
        "suggested_plans": classification.get("suggested_plans", []),
    })

def handle_post_bridge_quick_input(handler, body: dict) -> None:
    text = body.get("text", "").strip()
    if not text:
        handler.send_json({"error": "text is required"}, status=HTTPStatus.BAD_REQUEST)
        return
    result = parse_quick_input(text)
    handler.send_json(result)

def handle_post_bridge_create_plan(handler, body: dict) -> None:
    candidates = body.get("candidates", [])
    if not candidates:
        handler.send_json({"error": "candidates is required"}, status=HTTPStatus.BAD_REQUEST)
        return
    result = approve_plan_candidates(candidates)
    handler.send_json({"ok": True, "plans": result})

def handle_post_tomorrow_first_quest_confirm(handler, body: dict) -> None:
    title = body.get("title")
    reason = body.get("reason", "")
    source = body.get("source", "manual")
    if not title:
        handler.send_json({"error": "title is required"}, status=HTTPStatus.BAD_REQUEST)
        return
    result = confirm_starting_point(title=title, reason=reason, source=source)
    handler.send_json({**result, "current_state": get_current_state()})

def handle_post_tomorrow_first_quest_promote(handler, body: dict) -> None:
    result = promote_confirmed_starting_point_to_quest()
    handler.send_json({**result, "current_state": get_current_state()})

def handle_post_tomorrow_first_quest_clear(handler, body: dict) -> None:
    result = clear_confirmed_starting_point()
    handler.send_json({**result, "current_state": get_current_state()})

def handle_post_ops_overrides_create(handler, body: dict) -> None:
    result = create_manual_override(body)
    handler.send_json({"ok": True, "override": result})


def handle_post_dispatch(handler, path: str, body: dict) -> None:
    exact_routes = {
        "/api/quests/evaluate": handle_post_quests_evaluate,
        "/api/current-state/refresh": handle_post_current_state_refresh,
        "/api/quests/report": handle_post_quests_report,
        "/api/sessions/start": handle_post_sessions_start,
        "/api/sessions/log": handle_post_sessions_log,
        "/api/sessions/end": handle_post_sessions_end,
        "/api/agents/cleanup-stale": handle_post_agents_cleanup_stale,
        "/api/telegram/sync-core": handle_post_telegram_sync_core,
        "/api/bridge/parse": handle_post_bridge_parse,
        "/api/bridge/quick-input": handle_post_bridge_quick_input,
        "/api/bridge/create-plan": handle_post_bridge_create_plan,
        "/api/tomorrow-first-quest/confirm": handle_post_tomorrow_first_quest_confirm,
        "/api/tomorrow-first-quest/promote": handle_post_tomorrow_first_quest_promote,
        "/api/tomorrow-first-quest/clear": handle_post_tomorrow_first_quest_clear,
        "/api/ops-overrides": handle_post_ops_overrides_create,
    }
    prefix_routes = [
        ("/api/current-quest/hold", handle_post_current_quest_hold),
        ("/api/quest-hold", handle_post_current_quest_hold),
        ("/api/current-quest/start", handle_post_current_quest_start),
        ("/api/current-quest/defer", handle_post_current_quest_defer),
        ("/api/quest-defer", handle_post_current_quest_defer),
    ]

    handler_func = exact_routes.get(path)
    if handler_func:
        handler_func(handler, body)
        return

    for prefix, prefix_handler in prefix_routes:
        if path.startswith(prefix):
            prefix_handler(handler, body)
            return

    handler.send_error(HTTPStatus.NOT_FOUND, "Unknown API endpoint")
