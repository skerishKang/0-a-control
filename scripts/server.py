from __future__ import annotations

# Enable both `python scripts/foo.py` and `python -m scripts.foo`
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

if __package__ in (None, ""):
    from scripts import db as _db
    from scripts.db_ops import approve_plan_candidates
    from scripts.confirmed_starting_point import confirm_starting_point, clear_confirmed_starting_point
    from scripts.planning_input import classify_conversation, parse_quick_input
    from scripts.telegram_cli import get_core_sources_sync_status, run_sync_core
    from scripts.telegram_service import fetch_chats, fetch_messages, get_telegram_status
else:
    from . import db as _db
    from .db_ops import approve_plan_candidates
    from .confirmed_starting_point import confirm_starting_point, clear_confirmed_starting_point
    from .planning_input import classify_conversation, parse_quick_input
    from .telegram_cli import get_core_sources_sync_status, run_sync_core
    from .telegram_service import fetch_chats, fetch_messages, get_telegram_status

import json
import logging
import mimetypes
import os
import socket
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

MAX_BODY_SIZE = 1 * 1024 * 1024  # 1 MiB


def parse_limit(query, key: str, default: int, maximum: int) -> int:
    raw = query.get(key, [None])[0]
    if raw is None or raw == "":
        return default
    try:
        val = int(raw)
        if val <= 0:
            return default
        return min(val, maximum)
    except (ValueError, TypeError):
        return default


ROOT_DIR = _db.ROOT_DIR
append_source_record = _db.append_source_record
create_sample_data_if_empty = _db.create_sample_data_if_empty
end_session = _db.end_session
close_latest_active_session_for_agent = _db.close_latest_active_session_for_agent
evaluate_quest = _db.evaluate_quest
get_external_inbox_overview = _db.get_external_inbox_overview
get_external_inbox_source_messages = _db.get_external_inbox_source_messages
get_agent_statuses = _db.get_agent_statuses
get_current_state = _db.get_current_state
get_latest_briefs = _db.get_latest_briefs
get_plans = _db.get_plans
get_quests = _db.get_quests
get_recent_sessions = _db.get_recent_sessions
get_session_view_model = _db.get_session_view_model
get_source_records = _db.get_source_records
get_workdiary_priority_candidates = _db.get_workdiary_priority_candidates
get_workdiary_top_level = _db.get_workdiary_top_level
report_quest_progress = _db.report_quest_progress
refresh_current_state = _db.refresh_current_state
defer_current_quest_to_short_term = _db.defer_current_quest_to_short_term
promote_confirmed_starting_point_to_quest = _db.promote_confirmed_starting_point_to_quest
start_session = _db.start_session


PUBLIC_DIR = ROOT_DIR / "public"
HOST = os.getenv("HOST", "127.0.0.1")
PORT_ENV = os.getenv("PORT")
PORT = int(PORT_ENV or "4310")
RUNTIME_DIR = ROOT_DIR / "data" / "runtime"
SESSIONS_DIR = RUNTIME_DIR / "sessions"
CURRENT_SESSION_FILE = RUNTIME_DIR / "current_session.json"


def get_active_session_runtime(session_id: str | None = None) -> dict:
    target_file = CURRENT_SESSION_FILE
    if session_id:
        target_file = SESSIONS_DIR / f"{session_id}.json"
    
    if not target_file.exists():
        if session_id: # Fallback to current if requested session not found? 
                       # Or just return empty. Better return empty.
            return {}
        return {}

    try:
        return json.loads(target_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def is_client_disconnect_error(exc: BaseException) -> bool:
    if isinstance(exc, (BrokenPipeError, ConnectionAbortedError, ConnectionResetError)):
        return True
    if isinstance(exc, socket.error):
        win_error = getattr(exc, "winerror", None)
        return win_error in {10053, 10054}
    return False


class ControlTowerHandler(BaseHTTPRequestHandler):
    server_version = "ControlTowerHTTP/0.1"

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path.startswith("/api/"):
            self.handle_api_get(parsed.path, parse_qs(parsed.query))
            return
        if parsed.path in {"", "/"}:
            self.send_response(HTTPStatus.FOUND)
            self.send_header("Location", "/board-v2.html")
            self.end_headers()
            return
        self.handle_static(parsed.path)

    def _post_quests_evaluate(self, body: dict) -> None:
        result = evaluate_quest(
            quest_id=body["quest_id"],
            verdict=body["verdict"],
            reason=body.get("reason", ""),
            restart_point=body.get("restart_point", ""),
            next_quest_hint=body.get("next_quest_hint", ""),
            plan_impact=body.get("plan_impact", ""),
        )
        self.send_json({"ok": True, "quest": result, "current_state": get_current_state()})

    def _post_current_state_refresh(self, body: dict) -> None:
        result = refresh_current_state()
        self.send_json({"ok": True, "state": result})

    def _post_current_quest_hold(self, body: dict) -> None:
        result = _db.mark_current_quest_unfinished()
        self.send_json({"ok": True, **result})

    def _post_current_quest_start(self, body: dict) -> None:
        result = _db.start_current_quest_from_main_mission()
        self.send_json({"ok": True, **result})

    def _post_current_quest_defer(self, body: dict) -> None:
        result = defer_current_quest_to_short_term()
        self.send_json({"ok": True, **result})

    def _post_quests_report(self, body: dict) -> None:
        result = report_quest_progress(
            quest_id=body["quest_id"],
            work_summary=body.get("work_summary", ""),
            remaining_work=body.get("remaining_work", ""),
            blocker=body.get("blocker", ""),
            self_assessment=body.get("self_assessment", ""),
            session_id=body.get("session_id", ""),
        )
        self.send_json({"ok": True, "quest": result, "current_state": get_current_state()})

    def _post_sessions_start(self, body: dict) -> None:
        result = start_session(
            agent_name=body["agent_name"],
            source_type=body["source_type"],
            model_name=body.get("model_name", ""),
            project_key=body.get("project_key", ""),
            working_dir=body.get("working_dir", ""),
            title=body.get("title", ""),
            metadata=body.get("metadata"),
        )
        self.send_json({"ok": True, "session": result})

    def _post_sessions_log(self, body: dict) -> None:
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
        self.send_json({"ok": True, "record": result})

    def _post_sessions_end(self, body: dict) -> None:
        result = end_session(
            session_id=body["session_id"],
            summary_md=body.get("summary_md", ""),
            status=body.get("status", "closed"),
            files_touched=body.get("files_touched"),
            actions=body.get("actions"),
            metadata=body.get("metadata"),
        )
        self.send_json({"ok": True, "session": result})

    def _post_agents_cleanup_stale(self, body: dict) -> None:
        result = close_latest_active_session_for_agent(
            agent_name=body["agent_name"],
            summary_md=body.get("summary_md", "stale active session closed from dashboard"),
            metadata={"user_action": "cleanup_stale_agent_session"},
        )
        self.send_json({"ok": True, "session": result})

    def _post_telegram_sync_core(self, body: dict) -> None:
        result = run_sync_core()
        self.send_json(result)

    def _post_bridge_parse(self, body: dict) -> None:
        text = body.get("text", "").strip()
        if not text:
            self.send_json({"error": "text is required"}, status=HTTPStatus.BAD_REQUEST)
            return
        classification = classify_conversation(text)
        self.send_json({
            "classification": classification,
            "suggested_plans": classification.get("suggested_plans", []),
        })

    def _post_bridge_quick_input(self, body: dict) -> None:
        text = body.get("text", "").strip()
        if not text:
            self.send_json({"error": "text is required"}, status=HTTPStatus.BAD_REQUEST)
            return
        result = parse_quick_input(text)
        self.send_json(result)

    def _post_bridge_create_plan(self, body: dict) -> None:
        candidates = body.get("candidates", [])
        if not candidates:
            self.send_json({"error": "candidates is required"}, status=HTTPStatus.BAD_REQUEST)
            return
        result = approve_plan_candidates(candidates)
        self.send_json({"ok": True, "plans": result})

    def _post_tomorrow_first_quest_confirm(self, body: dict) -> None:
        title = body.get("title")
        reason = body.get("reason", "")
        source = body.get("source", "manual")
        if not title:
            self.send_json({"error": "title is required"}, status=HTTPStatus.BAD_REQUEST)
            return
        result = confirm_starting_point(title=title, reason=reason, source=source)
        self.send_json({**result, "current_state": get_current_state()})

    def _post_tomorrow_first_quest_promote(self, body: dict) -> None:
        result = promote_confirmed_starting_point_to_quest()
        self.send_json({**result, "current_state": get_current_state()})

    def _post_tomorrow_first_quest_clear(self, body: dict) -> None:
        result = clear_confirmed_starting_point()
        self.send_json({**result, "current_state": get_current_state()})

    def handle_api_post_dispatch(self, path: str, body: dict) -> None:
        exact_routes = {
            "/api/quests/evaluate": self._post_quests_evaluate,
            "/api/current-state/refresh": self._post_current_state_refresh,
            "/api/quests/report": self._post_quests_report,
            "/api/sessions/start": self._post_sessions_start,
            "/api/sessions/log": self._post_sessions_log,
            "/api/sessions/end": self._post_sessions_end,
            "/api/agents/cleanup-stale": self._post_agents_cleanup_stale,
            "/api/telegram/sync-core": self._post_telegram_sync_core,
            "/api/bridge/parse": self._post_bridge_parse,
            "/api/bridge/quick-input": self._post_bridge_quick_input,
            "/api/bridge/create-plan": self._post_bridge_create_plan,
            "/api/tomorrow-first-quest/confirm": self._post_tomorrow_first_quest_confirm,
            "/api/tomorrow-first-quest/promote": self._post_tomorrow_first_quest_promote,
            "/api/tomorrow-first-quest/clear": self._post_tomorrow_first_quest_clear,
        }
        prefix_routes = [
            ("/api/current-quest/hold", self._post_current_quest_hold),
            ("/api/quest-hold", self._post_current_quest_hold),
            ("/api/current-quest/start", self._post_current_quest_start),
            ("/api/current-quest/defer", self._post_current_quest_defer),
            ("/api/quest-defer", self._post_current_quest_defer),
        ]

        handler = exact_routes.get(path)
        if handler:
            handler(body)
            return

        for prefix, prefix_handler in prefix_routes:
            if path.startswith(prefix):
                prefix_handler(body)
                return

        self.send_error(HTTPStatus.NOT_FOUND, "Unknown API endpoint")

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if not parsed.path.startswith("/api/"):
            self.send_error(HTTPStatus.NOT_FOUND, "Not found")
            return
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except (TypeError, ValueError):
            self.send_json({"error": "invalid Content-Length"}, status=HTTPStatus.BAD_REQUEST)
            return
        if content_length < 0:
            self.send_json({"error": "invalid Content-Length"}, status=HTTPStatus.BAD_REQUEST)
            return
        if content_length > MAX_BODY_SIZE:
            self.send_json({"error": "request body too large"}, status=HTTPStatus.REQUEST_ENTITY_TOO_LARGE)
            return
        raw_body = self.rfile.read(content_length) if content_length else b"{}"
        try:
            body = json.loads(raw_body.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            self.send_json({"error": "invalid JSON body"}, status=HTTPStatus.BAD_REQUEST)
            return

        try:
            self.handle_api_post_dispatch(parsed.path, body)
        except KeyError as exc:
            self.send_json({"error": f"missing field: {exc.args[0]}"}, status=HTTPStatus.BAD_REQUEST)
            return
        except ValueError as exc:
            self.send_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return
        except Exception as exc:
            logging.error(f"POST API error: {exc}", exc_info=True)
            self.send_json({"error": "Internal Server Error", "details": str(exc)}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
            return

    def _get_current_state(self, query: dict[str, list[str]]) -> None:
        self.send_json({"current_state": get_current_state()})

    def _get_plans(self, query: dict[str, list[str]]) -> None:
        self.send_json({"plans": get_plans()})

    def _get_quests(self, query: dict[str, list[str]]) -> None:
        self.send_json({"quests": get_quests()})

    def _get_briefs_latest(self, query: dict[str, list[str]]) -> None:
        limit = parse_limit(query, "limit", 10, 200)
        self.send_json({"briefs": get_latest_briefs(limit)})

    def _get_sessions_recent(self, query: dict[str, list[str]]) -> None:
        limit = parse_limit(query, "limit", 10, 200)
        self.send_json({"sessions": get_recent_sessions(limit)})

    def _get_sessions_active(self, query: dict[str, list[str]]) -> None:
        session_id = query.get("session_id", [None])[0]
        self.send_json({"session": get_active_session_runtime(session_id)})

    def _get_sessions_records(self, query: dict[str, list[str]]) -> None:
        session_id = query.get("session_id", [""])[0]
        limit = parse_limit(query, "limit", 200, 200)
        self.send_json({"records": get_source_records(session_id, limit)})

    def _get_sessions_view(self, path: str, query: dict[str, list[str]]) -> None:
        session_id = path.rsplit("/", 1)[-1]
        if not session_id:
            self.send_json({"error": "session_id is required"}, status=HTTPStatus.BAD_REQUEST)
            return
        record_limit = parse_limit(query, "limit", 500, 2000)
        self.send_json({"view": get_session_view_model(session_id, record_limit)})

    def _get_workdiary_top_level(self, query: dict[str, list[str]]) -> None:
        limit = parse_limit(query, "limit", 30, 200)
        self.send_json({"items": get_workdiary_top_level(limit)})

    def _get_workdiary_priority_candidates(self, query: dict[str, list[str]]) -> None:
        limit = parse_limit(query, "limit", 8, 200)
        self.send_json({"items": get_workdiary_priority_candidates(limit)})

    def _get_external_inbox(self, query: dict[str, list[str]]) -> None:
        limit = parse_limit(query, "limit", 8, 1000)
        status = query.get("status", [None])[0]
        category = query.get("category", [None])[0]
        self.send_json(get_external_inbox_overview(limit, status, category))

    def _get_external_inbox_source(self, query: dict[str, list[str]]) -> None:
        source_id = query.get("source_id", [""])[0]
        if not source_id:
            self.send_json({"error": "source_id is required"}, status=HTTPStatus.BAD_REQUEST)
            return
        day = query.get("day", ["today"])[0]
        before = query.get("before", [None])[0]
        limit = parse_limit(query, "limit", 500, 1000)
        self.send_json(get_external_inbox_source_messages(source_id, day, limit, before))

    def _get_health(self, query: dict[str, list[str]]) -> None:
        self.send_json({"ok": True})

    def _get_agents_status(self, query: dict[str, list[str]]) -> None:
        self.send_json({"agents": get_agent_statuses()})

    def _get_telegram_sync_status(self, query: dict[str, list[str]]) -> None:
        self.send_json({"sources": get_core_sources_sync_status()})

    def _get_telegram_status(self, query: dict[str, list[str]]) -> None:
        self.send_json(get_telegram_status())

    def _get_telegram_chats(self, query: dict[str, list[str]]) -> None:
        limit = parse_limit(query, "limit", 50, 200)
        self.send_json({"status": "ok", "chats": fetch_chats(limit=limit)})

    def _get_telegram_messages(self, query: dict[str, list[str]]) -> None:
        chat_id = query.get("chat_id", [""])[0]
        if not chat_id:
            self.send_json({"error": "chat_id is required"}, status=HTTPStatus.BAD_REQUEST)
            return
        limit = parse_limit(query, "limit", 200, 500)
        self.send_json({"status": "ok", "chat_id": chat_id, "messages": fetch_messages(chat_id, limit=limit)})

    def _get_suggestions(self, query: dict[str, list[str]]) -> None:
        suggestions_path = ROOT_DIR / "data" / "runtime" / "quest_suggestions.json"
        limit = parse_limit(query, "limit", 3, 20)
        if not suggestions_path.exists():
            self.send_json({"suggestions": []})
            return
        try:
            with open(suggestions_path, encoding="utf-8") as f:
                data = json.load(f)
                suggestions = data.get("suggestions", [])[:limit]
                self.send_json({"suggestions": suggestions})
        except json.JSONDecodeError as exc:
            logging.warning("quest_suggestions.json is corrupted, returning empty: %s", exc)
            self.send_json({"suggestions": []})

    def handle_api_get_dispatch(self, path: str, query: dict[str, list[str]]) -> None:
        exact_routes = {
            "/api/current-state": self._get_current_state,
            "/api/plans": self._get_plans,
            "/api/quests": self._get_quests,
            "/api/briefs/latest": self._get_briefs_latest,
            "/api/sessions/recent": self._get_sessions_recent,
            "/api/sessions/active": self._get_sessions_active,
            "/api/sessions/records": self._get_sessions_records,
            "/api/workdiary/top-level": self._get_workdiary_top_level,
            "/api/workdiary/priority-candidates": self._get_workdiary_priority_candidates,
            "/api/external-inbox": self._get_external_inbox,
            "/api/external-inbox/source": self._get_external_inbox_source,
            "/api/health": self._get_health,
            "/api/agents/status": self._get_agents_status,
            "/api/telegram/sync-status": self._get_telegram_sync_status,
            "/api/telegram/status": self._get_telegram_status,
            "/api/telegram/chats": self._get_telegram_chats,
            "/api/telegram/messages": self._get_telegram_messages,
            "/api/suggestions": self._get_suggestions,
        }
        prefix_routes = [
            ("/api/sessions/view/", self._get_sessions_view),
        ]

        handler = exact_routes.get(path)
        if handler:
            handler(query)
            return

        for prefix, prefix_handler in prefix_routes:
            if path.startswith(prefix):
                prefix_handler(path, query)
                return

        self.send_error(HTTPStatus.NOT_FOUND, "Unknown API endpoint")

    def handle_api_get(self, path: str, query: dict[str, list[str]]) -> None:
        try:
            self.handle_api_get_dispatch(path, query)
        except Exception as exc:
            if is_client_disconnect_error(exc):
                logging.info("GET request aborted by client: %s", path)
                return
            logging.error(f"GET API error: {exc}", exc_info=True)
            try:
                self.send_json({"error": "Internal Server Error", "details": str(exc)}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
            except Exception as send_exc:
                if is_client_disconnect_error(send_exc):
                    logging.info("GET error response aborted by client: %s", path)
                    return
                raise

    def handle_static(self, path: str) -> None:
        # 1. Check PUBLIC_DIR first
        candidate = (PUBLIC_DIR / path.lstrip("/")).resolve()
        if not str(candidate).startswith(str(PUBLIC_DIR.resolve())) or not candidate.exists():
            # 2. Check '작업철' directory if the path starts with /작업철/
            if path.lstrip("/").startswith("작업철/"):
                candidate = (ROOT_DIR / path.lstrip("/")).resolve()
                if not str(candidate).startswith(str(ROOT_DIR.resolve())) or not candidate.exists():
                    self.send_error(HTTPStatus.NOT_FOUND, "Workfile not found")
                    return
            else:
                self.send_error(HTTPStatus.NOT_FOUND, "Static file not found")
                return

        content_type, _ = mimetypes.guess_type(str(candidate))
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type or "application/octet-stream")
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        self.end_headers()
        try:
            self.wfile.write(candidate.read_bytes())
        except Exception as exc:
            if is_client_disconnect_error(exc):
                logging.info("Static response aborted by client: %s", path)
                return
            raise

    def send_json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        try:
            self.wfile.write(data)
        except Exception as exc:
            if is_client_disconnect_error(exc):
                return
            raise

    def log_message(self, format: str, *args) -> None:
        if os.getenv("DEBUG"):
            super().log_message(format, *args)

    def log_error(self, format: str, *args) -> None:
        logging.error(f"{self.address_string()} - {format % args}")


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
    create_sample_data_if_empty()
    bind_errors: list[tuple[int, BaseException]] = []
    candidate_bindings: list[tuple[str, int]] = [(HOST, PORT)]
    if PORT_ENV is None:
        candidate_bindings.extend((HOST, candidate_port) for candidate_port in range(PORT + 1, PORT + 21))
        if HOST == "127.0.0.1":
            candidate_bindings.extend(("0.0.0.0", candidate_port) for candidate_port in range(PORT, PORT + 21))
        candidate_bindings.append((HOST, 0))
        if HOST == "127.0.0.1":
            candidate_bindings.append(("0.0.0.0", 0))

    server = None
    bound_host = None
    bound_port = None
    for candidate_host, candidate_port in candidate_bindings:
        try:
            server = ThreadingHTTPServer((candidate_host, candidate_port), ControlTowerHandler)
            actual_host, actual_port = server.server_address[:2]
            bound_host = actual_host
            bound_port = actual_port
            break
        except OSError as exc:
            bind_errors.append((candidate_port, exc))

    if server is None or bound_host is None or bound_port is None:
        if bind_errors:
            attempted = ", ".join(
                f"{port} ({type(exc).__name__}: {exc})" for port, exc in bind_errors
            )
            raise OSError(f"Failed to bind control tower server. Tried: {attempted}")
        raise OSError("Failed to bind control tower server")

    display_host = "localhost" if bound_host in {"127.0.0.1", "0.0.0.0"} else bound_host
    if bound_port != PORT or bound_host != HOST:
        logging.warning(
            "Default binding %s:%s unavailable; using http://%s:%s instead.",
            HOST,
            PORT,
            display_host,
            bound_port,
        )
    print(f"Control tower server running at http://{display_host}:{bound_port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
