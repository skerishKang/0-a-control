# server_handlers package — lazy imports to avoid circular dependency with scripts.server
from __future__ import annotations
from http import HTTPStatus
import logging


# ---- route method name mapping (used by dispatcher via getattr) ----
# Maps URL path → handler method name on the ControlTowerHandler instance.
# The dispatcher calls getattr(handler, method_name) so that:
#   - tests with mock handlers get their overridden method called
#   - production code delegates through the wrapper → module function
EXACT_ROUTE_METHODS: dict[str, str] = {
    "/api/current-state": "_get_current_state",
    "/api/plans": "_get_plans",
    "/api/quests": "_get_quests",
    "/api/briefs/latest": "_get_briefs_latest",
    "/api/sessions/recent": "_get_sessions_recent",
    "/api/sessions/active": "_get_sessions_active",
    "/api/sessions/records": "_get_sessions_records",
    "/api/workdiary/top-level": "_get_workdiary_top_level",
    "/api/workdiary/priority-candidates": "_get_workdiary_priority_candidates",
    "/api/external-inbox": "_get_external_inbox",
    "/api/external-inbox/source": "_get_external_inbox_source",
    "/api/health": "_get_health",
    "/api/agents/status": "_get_agents_status",
    "/api/telegram/sync-status": "_get_telegram_sync_status",
    "/api/telegram/status": "_get_telegram_status",
    "/api/telegram/chats": "_get_telegram_chats",
    "/api/telegram/messages": "_get_telegram_messages",
    "/api/suggestions": "_get_suggestions",
    "/api/operations/summary": "_get_operations_summary",
    "/api/github/summary": "_get_operations_summary",
    "/api/settings/status": "_get_settings_status",
    "/api/guardrails/status": "_get_guardrails_status",
    "/api/ops-overrides": "_get_ops_overrides",
    "/api/work-queue": "_get_work_queue",
    "/api/executor-prompts/templates": "_get_executor_prompt_templates",
}

PREFIX_ROUTE_METHODS: list[tuple[str, str]] = [
    ("/api/sessions/view/", "_get_sessions_view"),
]


def handle_get_dispatch(handler, path: str, query: dict) -> None:
    """Dispatch GET /api/ requests to the appropriate handler method.

    Uses getattr(handler, method_name) so mock handlers in tests can
    intercept calls, while production ControlTowerHandler delegates
    through its wrappers to the module-level logic below.
    """
    method_name = EXACT_ROUTE_METHODS.get(path)
    if method_name:
        getattr(handler, method_name)(query)
        return

    for prefix, prefix_method in PREFIX_ROUTE_METHODS:
        if path.startswith(prefix):
            getattr(handler, prefix_method)(path, query)
            return

    handler.send_error(HTTPStatus.NOT_FOUND, "Unknown API endpoint")


# ---- Actual logic helpers (called by handler wrappers in server.py) ----

def _get_db():
    """Lazy import to avoid circular dependency."""
    from scripts.server import (
        ROOT_DIR, get_current_state, get_plans, get_quests,
        get_latest_briefs, get_recent_sessions, get_active_session_runtime,
        get_source_records, get_work_queue_raw, get_session_view_model, get_workdiary_top_level,
        get_workdiary_priority_candidates, get_external_inbox_overview,
        get_external_inbox_source_messages, get_agent_statuses,
        get_core_sources_sync_status, get_telegram_status,
        fetch_chats, fetch_messages, parse_limit,
        build_operations_summary, build_settings_status, build_guardrails_status,
        list_manual_overrides,
        generate_executor_prompt,
        get_executor_prompt_templates,
    )
    return locals()


def handle_get_current_state(handler, query):
    handler.send_json({"current_state": _get_db()["get_current_state"]()})


def handle_get_plans(handler, query):
    handler.send_json({"plans": _get_db()["get_plans"]()})


def handle_get_quests(handler, query):
    handler.send_json({"quests": _get_db()["get_quests"]()})


def handle_get_briefs_latest(handler, query):
    limit = _get_db()["parse_limit"](query, "limit", 10, 200)
    handler.send_json({"briefs": _get_db()["get_latest_briefs"](limit)})


def handle_get_sessions_recent(handler, query):
    limit = _get_db()["parse_limit"](query, "limit", 10, 200)
    handler.send_json({"sessions": _get_db()["get_recent_sessions"](limit)})


def handle_get_sessions_active(handler, query):
    db = _get_db()
    session_id = query.get("session_id", [None])[0]
    handler.send_json({"session": db["get_active_session_runtime"](session_id)})


def handle_get_sessions_records(handler, query):
    db = _get_db()
    session_id = query.get("session_id", [""])[0]
    limit = db["parse_limit"](query, "limit", 200, 200)
    handler.send_json({"records": db["get_source_records"](session_id, limit)})


def handle_get_sessions_view(handler, path, query):
    db = _get_db()
    session_id = path.rsplit("/", 1)[-1]
    if not session_id:
        handler.send_json({"error": "session_id is required"}, status=HTTPStatus.BAD_REQUEST)
        return
    record_limit = db["parse_limit"](query, "limit", 500, 2000)
    handler.send_json({"view": db["get_session_view_model"](session_id, record_limit)})


def handle_get_workdiary_top_level(handler, query):
    limit = _get_db()["parse_limit"](query, "limit", 30, 200)
    handler.send_json({"items": _get_db()["get_workdiary_top_level"](limit)})


def handle_get_workdiary_priority_candidates(handler, query):
    limit = _get_db()["parse_limit"](query, "limit", 8, 200)
    handler.send_json({"items": _get_db()["get_workdiary_priority_candidates"](limit)})


def handle_get_external_inbox(handler, query):
    db = _get_db()
    limit = db["parse_limit"](query, "limit", 8, 1000)
    status = query.get("status", [None])[0]
    category = query.get("category", [None])[0]
    handler.send_json(db["get_external_inbox_overview"](limit, status, category))


def handle_get_external_inbox_source(handler, query):
    db = _get_db()
    source_id = query.get("source_id", [""])[0]
    if not source_id:
        handler.send_json({"error": "source_id is required"}, status=HTTPStatus.BAD_REQUEST)
        return
    day = query.get("day", ["today"])[0]
    before = query.get("before", [None])[0]
    limit = db["parse_limit"](query, "limit", 500, 1000)
    handler.send_json(db["get_external_inbox_source_messages"](source_id, day, limit, before))


def handle_get_health(handler, query):
    handler.send_json({"ok": True})


def handle_get_agents_status(handler, query):
    handler.send_json({"agents": _get_db()["get_agent_statuses"]()})


def handle_get_telegram_sync_status(handler, query):
    handler.send_json({"sources": _get_db()["get_core_sources_sync_status"]()})


def handle_get_telegram_status(handler, query):
    handler.send_json(_get_db()["get_telegram_status"]())


def handle_get_telegram_chats(handler, query):
    db = _get_db()
    limit = db["parse_limit"](query, "limit", 50, 200)
    handler.send_json({"status": "ok", "chats": db["fetch_chats"](limit=limit)})


def handle_get_telegram_messages(handler, query):
    db = _get_db()
    chat_id = query.get("chat_id", [""])[0]
    if not chat_id:
        handler.send_json({"error": "chat_id is required"}, status=HTTPStatus.BAD_REQUEST)
        return
    limit = db["parse_limit"](query, "limit", 200, 500)
    handler.send_json({"status": "ok", "chat_id": chat_id, "messages": db["fetch_messages"](chat_id, limit=limit)})


def handle_get_suggestions(handler, query):
    db = _get_db()
    suggestions_path = db["ROOT_DIR"] / "data" / "runtime" / "quest_suggestions.json"
    limit = db["parse_limit"](query, "limit", 3, 20)
    if not suggestions_path.exists():
        handler.send_json({"suggestions": []})
        return
    try:
        import json
        with open(suggestions_path, encoding="utf-8") as f:
            data = json.load(f)
            suggestions = data.get("suggestions", [])[:limit]
            handler.send_json({"suggestions": suggestions})
    except json.JSONDecodeError as exc:
        logging.warning("quest_suggestions.json is corrupted, returning empty: %s", exc)
        handler.send_json({"suggestions": []})


def handle_get_operations_summary(handler, query):
    handler.send_json(_get_db()["build_operations_summary"]())


def handle_get_settings_status(handler, query):
    handler.send_json(_get_db()["build_settings_status"]())


def handle_get_guardrails_status(handler, query):
    handler.send_json(_get_db()["build_guardrails_status"]())


def handle_get_ops_overrides(handler, query):
    db = _get_db()
    include_inactive = query.get("include_inactive", ["false"])[0].lower() in {"1", "true", "yes"}
    target_type = query.get("target_type", [None])[0]
    target_id = query.get("target_id", [None])[0]
    overrides = db["list_manual_overrides"](
        include_inactive=include_inactive,
        target_type=target_type,
        target_id=target_id,
    )
    handler.send_json({"overrides": overrides})


def handle_get_work_queue(handler, query):
    from scripts.work_queue import normalize_work_items, group_by_queue

    limit = _get_db()["parse_limit"](query, "limit", 50, 200)
    queue_filter = query.get("queue", [None])[0]

    raw_items = _get_db()["get_work_queue_raw"](limit)
    items = normalize_work_items(raw_items)

    if queue_filter:
        queue_filter = queue_filter.upper()
        items = [i for i in items if i.queue.value == queue_filter]

    grouped = group_by_queue(items)
    queues = {}
    for q in grouped:
        queues[q.value] = [
            {"id": i.id, "title": i.title, "source": i.source,
             "priority": i.priority.value, "queue": i.queue.value,
             "status": i.effective_status, "updated_at": i.updated_at}
            for i in grouped[q]
        ]

    handler.send_json({
        "queues": queues,
        "items": [
            {"id": i.id, "title": i.title, "source": i.source,
             "priority": i.priority.value, "queue": i.queue.value,
             "status": i.effective_status, "updated_at": i.updated_at}
            for i in items
        ],
    })


def handle_get_executor_prompt_templates(handler, query):
    handler.send_json(_get_db()["get_executor_prompt_templates"]())