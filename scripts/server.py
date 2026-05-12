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
    from scripts.settings_guardrails import build_guardrails_status, build_settings_status
    from scripts.telegram_cli import get_core_sources_sync_status, run_sync_core
    from scripts.telegram_service import fetch_chats, fetch_messages, get_telegram_status
    from scripts.operations_summary import build_operations_summary
    from scripts.manual_overrides import create_manual_override, list_manual_overrides, update_manual_override
    from scripts.server_handlers import server_get_routes, server_post_routes
else:
    from . import db as _db
    from .db_ops import approve_plan_candidates
    from .confirmed_starting_point import confirm_starting_point, clear_confirmed_starting_point
    from .planning_input import classify_conversation, parse_quick_input
    from .settings_guardrails import build_guardrails_status, build_settings_status
    from .telegram_cli import get_core_sources_sync_status, run_sync_core
    from .telegram_service import fetch_chats, fetch_messages, get_telegram_status
    from .operations_summary import build_operations_summary
    from .manual_overrides import create_manual_override, list_manual_overrides, update_manual_override
    from .server_handlers import server_get_routes, server_post_routes


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
get_work_queue_raw = _db.get_work_queue_raw
get_workdiary_priority_candidates = _db.get_workdiary_priority_candidates
get_workdiary_top_level = _db.get_workdiary_top_level
report_quest_progress = _db.report_quest_progress
refresh_current_state = _db.refresh_current_state
defer_current_quest_to_short_term = _db.defer_current_quest_to_short_term
promote_confirmed_starting_point_to_quest = _db.promote_confirmed_starting_point_to_quest
start_session = _db.start_session

PUBLIC_DIR = ROOT_DIR / "public"
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "4310"))
RUNTIME_DIR = ROOT_DIR / "data" / "runtime"
SESSIONS_DIR = RUNTIME_DIR / "sessions"
CURRENT_SESSION_FILE = RUNTIME_DIR / "current_session.json"


def get_active_session_runtime(session_id: str | None = None) -> dict:
    target_file = CURRENT_SESSION_FILE
    if session_id:
        target_file = SESSIONS_DIR / f"{session_id}.json"
    if not target_file.exists():
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


class ControlTowerHandler(BaseHTTPRequestHandler):
    server_version = "ControlTowerHTTP/0.1"

    # ---- GET dispatch (string-based → getattr for test compatibility) ----

    # ---- class-level dispatch so tests can call ControlTowerHandler.handle_api_get_dispatch ----
    handle_api_get_dispatch = server_get_routes.handle_get_dispatch
    handle_api_post_dispatch = server_post_routes.handle_post_dispatch

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path.startswith("/api/"):
            self.handle_api_get_dispatch(self, parsed.path, parse_qs(parsed.query))
            return
        if parsed.path in {"", "/"}:
            self.send_response(HTTPStatus.FOUND)
            self.send_header("Location", "/board-v2.html")
            self.end_headers()
            return
        self.handle_static(parsed.path)

    # ---- GET route handlers (wrappers → module-level functions) ----

    def _get_current_state(self, query):
        server_get_routes.handle_get_current_state(self, query)

    def _get_plans(self, query):
        server_get_routes.handle_get_plans(self, query)

    def _get_quests(self, query):
        server_get_routes.handle_get_quests(self, query)

    def _get_briefs_latest(self, query):
        server_get_routes.handle_get_briefs_latest(self, query)

    def _get_sessions_recent(self, query):
        server_get_routes.handle_get_sessions_recent(self, query)

    def _get_sessions_active(self, query):
        server_get_routes.handle_get_sessions_active(self, query)

    def _get_sessions_records(self, query):
        server_get_routes.handle_get_sessions_records(self, query)

    def _get_sessions_view(self, path, query):
        server_get_routes.handle_get_sessions_view(self, path, query)

    def _get_workdiary_top_level(self, query):
        server_get_routes.handle_get_workdiary_top_level(self, query)

    def _get_workdiary_priority_candidates(self, query):
        server_get_routes.handle_get_workdiary_priority_candidates(self, query)

    def _get_external_inbox(self, query):
        server_get_routes.handle_get_external_inbox(self, query)

    def _get_external_inbox_source(self, query):
        server_get_routes.handle_get_external_inbox_source(self, query)

    def _get_health(self, query):
        server_get_routes.handle_get_health(self, query)

    def _get_agents_status(self, query):
        server_get_routes.handle_get_agents_status(self, query)

    def _get_telegram_sync_status(self, query):
        server_get_routes.handle_get_telegram_sync_status(self, query)

    def _get_telegram_status(self, query):
        server_get_routes.handle_get_telegram_status(self, query)

    def _get_telegram_chats(self, query):
        server_get_routes.handle_get_telegram_chats(self, query)

    def _get_telegram_messages(self, query):
        server_get_routes.handle_get_telegram_messages(self, query)

    def _get_suggestions(self, query):
        server_get_routes.handle_get_suggestions(self, query)

    def _get_operations_summary(self, query):
        server_get_routes.handle_get_operations_summary(self, query)

    def _get_settings_status(self, query):
        server_get_routes.handle_get_settings_status(self, query)

    def _get_guardrails_status(self, query):
        server_get_routes.handle_get_guardrails_status(self, query)

    def _get_ops_overrides(self, query):
        server_get_routes.handle_get_ops_overrides(self, query)

    def _get_work_queue(self, query):
        server_get_routes.handle_get_work_queue(self, query)

    # ---- POST route handlers (wrappers → module-level functions) ----
    handle_api_post_dispatch = server_post_routes.handle_post_dispatch

    def _post_quests_evaluate(self, body):
        server_post_routes.handle_post_quests_evaluate(self, body)

    def _post_current_state_refresh(self, body):
        server_post_routes.handle_post_current_state_refresh(self, body)

    def _post_current_quest_hold(self, body):
        server_post_routes.handle_post_current_quest_hold(self, body)

    def _post_current_quest_start(self, body):
        server_post_routes.handle_post_current_quest_start(self, body)

    def _post_current_quest_defer(self, body):
        server_post_routes.handle_post_current_quest_defer(self, body)

    def _post_quests_report(self, body):
        server_post_routes.handle_post_quests_report(self, body)

    def _post_sessions_start(self, body):
        server_post_routes.handle_post_sessions_start(self, body)

    def _post_sessions_log(self, body):
        server_post_routes.handle_post_sessions_log(self, body)

    def _post_sessions_end(self, body):
        server_post_routes.handle_post_sessions_end(self, body)

    def _post_agents_cleanup_stale(self, body):
        server_post_routes.handle_post_agents_cleanup_stale(self, body)

    def _post_telegram_sync_core(self, body):
        server_post_routes.handle_post_telegram_sync_core(self, body)

    def _post_bridge_parse(self, body):
        server_post_routes.handle_post_bridge_parse(self, body)

    def _post_bridge_quick_input(self, body):
        server_post_routes.handle_post_bridge_quick_input(self, body)

    def _post_bridge_create_plan(self, body):
        server_post_routes.handle_post_bridge_create_plan(self, body)

    def _post_tomorrow_first_quest_confirm(self, body):
        server_post_routes.handle_post_tomorrow_first_quest_confirm(self, body)

    def _post_tomorrow_first_quest_promote(self, body):
        server_post_routes.handle_post_tomorrow_first_quest_promote(self, body)

    def _post_tomorrow_first_quest_clear(self, body):
        server_post_routes.handle_post_tomorrow_first_quest_clear(self, body)

    def _post_ops_overrides_create(self, body):
        server_post_routes.handle_post_ops_overrides_create(self, body)

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
            self.handle_api_post_dispatch(self, parsed.path, body)
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

    def do_PATCH(self) -> None:
        parsed = urlparse(self.path)
        if not parsed.path.startswith("/api/ops-overrides/"):
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
            override_id = parsed.path.rsplit("/", 1)[-1]
            override = update_manual_override(override_id, body)
            self.send_json({"ok": True, "override": override})
        except json.JSONDecodeError:
            self.send_json({"error": "invalid JSON body"}, status=HTTPStatus.BAD_REQUEST)
        except ValueError as exc:
            self.send_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
        except Exception as exc:
            logging.error(f"PATCH API error: {exc}", exc_info=True)
            self.send_json({"error": "Internal Server Error", "details": str(exc)}, status=HTTPStatus.INTERNAL_SERVER_ERROR)

    def handle_static(self, path: str) -> None:
        candidate = (PUBLIC_DIR / path.lstrip("/")).resolve()
        if not str(candidate).startswith(str(PUBLIC_DIR.resolve())) or not candidate.exists():
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
    server = ThreadingHTTPServer((HOST, PORT), ControlTowerHandler)
    print(f"Control tower server running at http://localhost:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()