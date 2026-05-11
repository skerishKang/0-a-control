from __future__ import annotations
from http import HTTPStatus
import json
import logging
from scripts.server import (
    ROOT_DIR, get_current_state, get_plans, get_quests,
    get_latest_briefs, get_recent_sessions, get_active_session_runtime,
    get_source_records, get_session_view_model, get_workdiary_top_level,
    get_workdiary_priority_candidates, get_external_inbox_overview,
    get_external_inbox_source_messages, get_agent_statuses,
    get_core_sources_sync_status, get_telegram_status,
    fetch_chats, fetch_messages, parse_limit,
    build_operations_summary, build_settings_status, build_guardrails_status,
    list_manual_overrides,
)


def handle_get_current_state(handler, query: dict[str, list[str]]) -> None:
    handler.send_json({"current_state": get_current_state()})

def handle_get_plans(handler, query: dict[str, list[str]]) -> None:
    handler.send_json({"plans": get_plans()})

def handle_get_quests(handler, query: dict[str, list[str]]) -> None:
    handler.send_json({"quests": get_quests()})

def handle_get_briefs_latest(handler, query: dict[str, list[str]]) -> None:
    limit = parse_limit(query, "limit", 10, 200)
    handler.send_json({"briefs": get_latest_briefs(limit)})

def handle_get_sessions_recent(handler, query: dict[str, list[str]]) -> None:
    limit = parse_limit(query, "limit", 10, 200)
    handler.send_json({"sessions": get_recent_sessions(limit)})

def handle_get_sessions_active(handler, query: dict[str, list[str]]) -> None:
    session_id = query.get("session_id", [None])[0]
    handler.send_json({"session": get_active_session_runtime(session_id)})

def handle_get_sessions_records(handler, query: dict[str, list[str]]) -> None:
    session_id = query.get("session_id", [""])[0]
    limit = parse_limit(query, "limit", 200, 200)
    handler.send_json({"records": get_source_records(session_id, limit)})

def handle_get_sessions_view(handler, path: str, query: dict[str, list[str]]) -> None:
    session_id = path.rsplit("/", 1)[-1]
    if not session_id:
        handler.send_json({"error": "session_id is required"}, status=HTTPStatus.BAD_REQUEST)
        return
    record_limit = parse_limit(query, "limit", 500, 2000)
    handler.send_json({"view": get_session_view_model(session_id, record_limit)})

def handle_get_workdiary_top_level(handler, query: dict[str, list[str]]) -> None:
    limit = parse_limit(query, "limit", 30, 200)
    handler.send_json({"items": get_workdiary_top_level(limit)})

def handle_get_workdiary_priority_candidates(handler, query: dict[str, list[str]]) -> None:
    limit = parse_limit(query, "limit", 8, 200)
    handler.send_json({"items": get_workdiary_priority_candidates(limit)})

def handle_get_external_inbox(handler, query: dict[str, list[str]]) -> None:
    limit = parse_limit(query, "limit", 8, 1000)
    status = query.get("status", [None])[0]
    category = query.get("category", [None])[0]
    handler.send_json(get_external_inbox_overview(limit, status, category))

def handle_get_external_inbox_source(handler, query: dict[str, list[str]]) -> None:
    source_id = query.get("source_id", [""])[0]
    if not source_id:
        handler.send_json({"error": "source_id is required"}, status=HTTPStatus.BAD_REQUEST)
        return
    day = query.get("day", ["today"])[0]
    before = query.get("before", [None])[0]
    limit = parse_limit(query, "limit", 500, 1000)
    handler.send_json(get_external_inbox_source_messages(source_id, day, limit, before))

def handle_get_health(handler, query: dict[str, list[str]]) -> None:
    handler.send_json({"ok": True})

def handle_get_agents_status(handler, query: dict[str, list[str]]) -> None:
    handler.send_json({"agents": get_agent_statuses()})

def handle_get_telegram_sync_status(handler, query: dict[str, list[str]]) -> None:
    handler.send_json({"sources": get_core_sources_sync_status()})

def handle_get_telegram_status(handler, query: dict[str, list[str]]) -> None:
    handler.send_json(get_telegram_status())

def handle_get_telegram_chats(handler, query: dict[str, list[str]]) -> None:
    limit = parse_limit(query, "limit", 50, 200)
    handler.send_json({"status": "ok", "chats": fetch_chats(limit=limit)})

def handle_get_telegram_messages(handler, query: dict[str, list[str]]) -> None:
    chat_id = query.get("chat_id", [""])[0]
    if not chat_id:
        handler.send_json({"error": "chat_id is required"}, status=HTTPStatus.BAD_REQUEST)
        return
    limit = parse_limit(query, "limit", 200, 500)
    handler.send_json({"status": "ok", "chat_id": chat_id, "messages": fetch_messages(chat_id, limit=limit)})

def handle_get_suggestions(handler, query: dict[str, list[str]]) -> None:
    suggestions_path = ROOT_DIR / "data" / "runtime" / "quest_suggestions.json"
    limit = parse_limit(query, "limit", 3, 20)
    if not suggestions_path.exists():
        handler.send_json({"suggestions": []})
        return
    try:
        with open(suggestions_path, encoding="utf-8") as f:
            data = json.load(f)
            suggestions = data.get("suggestions", [])[:limit]
            handler.send_json({"suggestions": suggestions})
    except json.JSONDecodeError as exc:
        logging.warning("quest_suggestions.json is corrupted, returning empty: %s", exc)
        handler.send_json({"suggestions": []})

def handle_get_operations_summary(handler, query: dict[str, list[str]]) -> None:
    result = build_operations_summary()
    handler.send_json(result)

def handle_get_settings_status(handler, query: dict[str, list[str]]) -> None:
    handler.send_json(build_settings_status())

def handle_get_guardrails_status(handler, query: dict[str, list[str]]) -> None:
    handler.send_json(build_guardrails_status())

def handle_get_ops_overrides(handler, query: dict[str, list[str]]) -> None:
    include_inactive = query.get("include_inactive", ["false"])[0].lower() in {"1", "true", "yes"}
    target_type = query.get("target_type", [None])[0]
    target_id = query.get("target_id", [None])[0]
    overrides = list_manual_overrides(
        include_inactive=include_inactive,
        target_type=target_type,
        target_id=target_id,
    )
    handler.send_json({"overrides": overrides})


def handle_get_dispatch(handler, path: str, query: dict[str, list[str]]) -> None:
    exact_routes = {
        "/api/current-state": handle_get_current_state,
        "/api/plans": handle_get_plans,
        "/api/quests": handle_get_quests,
        "/api/briefs/latest": handle_get_briefs_latest,
        "/api/sessions/recent": handle_get_sessions_recent,
        "/api/sessions/active": handle_get_sessions_active,
        "/api/sessions/records": handle_get_sessions_records,
        "/api/workdiary/top-level": handle_get_workdiary_top_level,
        "/api/workdiary/priority-candidates": handle_get_workdiary_priority_candidates,
        "/api/external-inbox": handle_get_external_inbox,
        "/api/external-inbox/source": handle_get_external_inbox_source,
        "/api/health": handle_get_health,
        "/api/agents/status": handle_get_agents_status,
        "/api/telegram/sync-status": handle_get_telegram_sync_status,
        "/api/telegram/status": handle_get_telegram_status,
        "/api/telegram/chats": handle_get_telegram_chats,
        "/api/telegram/messages": handle_get_telegram_messages,
        "/api/suggestions": handle_get_suggestions,
        "/api/operations/summary": handle_get_operations_summary,
        "/api/github/summary": handle_get_operations_summary,
        "/api/settings/status": handle_get_settings_status,
        "/api/guardrails/status": handle_get_guardrails_status,
        "/api/ops-overrides": handle_get_ops_overrides,
    }
    prefix_routes = [
        ("/api/sessions/view/", handle_get_sessions_view),
    ]

    handler_func = exact_routes.get(path)
    if handler_func:
        handler_func(handler, query)
        return

    for prefix, prefix_handler in prefix_routes:
        if path.startswith(prefix):
            prefix_handler(handler, path, query)
            return

    handler.send_error(HTTPStatus.NOT_FOUND, "Unknown API endpoint")
