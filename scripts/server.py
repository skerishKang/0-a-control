from __future__ import annotations

# Enable both `python scripts/foo.py` and `python -m scripts.foo`
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

if __package__ in (None, ""):
    from scripts import db as _db
    from scripts.telegram_cli import get_core_sources_sync_status, run_sync_core
    from scripts.telegram_service import fetch_chats, fetch_messages, get_telegram_status
else:
    from . import db as _db
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
ROOT_DIR = _db.ROOT_DIR
append_source_record = _db.append_source_record
create_sample_data_if_empty = _db.create_sample_data_if_empty
end_session = _db.end_session
evaluate_quest = _db.evaluate_quest
get_external_inbox_overview = _db.get_external_inbox_overview
get_external_inbox_source_messages = _db.get_external_inbox_source_messages
get_current_state = _db.get_current_state
get_latest_briefs = _db.get_latest_briefs
get_plans = _db.get_plans
get_quests = _db.get_quests
get_recent_sessions = _db.get_recent_sessions
get_source_records = _db.get_source_records
get_workdiary_priority_candidates = _db.get_workdiary_priority_candidates
get_workdiary_top_level = _db.get_workdiary_top_level
report_quest_progress = _db.report_quest_progress
refresh_current_state = _db.refresh_current_state
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
        self.handle_static(parsed.path)

    def handle_api_post_dispatch(self, path: str, body: dict) -> None:
        if path == "/api/quests/evaluate":
            result = evaluate_quest(
                quest_id=body["quest_id"],
                verdict=body["verdict"],
                reason=body.get("reason", ""),
                restart_point=body.get("restart_point", ""),
                next_quest_hint=body.get("next_quest_hint", ""),
                plan_impact=body.get("plan_impact", ""),
            )
            self.send_json({"ok": True, "quest": result, "current_state": get_current_state()})
            return
        if path == "/api/current-state/refresh":
            result = refresh_current_state()
            self.send_json({"ok": True, "state": result})
            return
        if path == "/api/quests/report":
            result = report_quest_progress(
                quest_id=body["quest_id"],
                work_summary=body.get("work_summary", ""),
                remaining_work=body.get("remaining_work", ""),
                blocker=body.get("blocker", ""),
                self_assessment=body.get("self_assessment", ""),
                session_id=body.get("session_id", ""),
            )
            self.send_json({"ok": True, "quest": result, "current_state": get_current_state()})
            return
        if path == "/api/sessions/start":
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
            return
        if path == "/api/sessions/log":
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
            return
        if path == "/api/sessions/end":
            result = end_session(
                session_id=body["session_id"],
                summary_md=body.get("summary_md", ""),
                status=body.get("status", "closed"),
                files_touched=body.get("files_touched"),
                actions=body.get("actions"),
                metadata=body.get("metadata"),
            )
            self.send_json({"ok": True, "session": result})
            return
        if path == "/api/telegram/sync-core":
            result = run_sync_core()
            self.send_json(result)
            return
        self.send_error(HTTPStatus.NOT_FOUND, "Unknown API endpoint")

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if not parsed.path.startswith("/api/"):
            self.send_error(HTTPStatus.NOT_FOUND, "Not found")
            return
        content_length = int(self.headers.get("Content-Length", "0"))
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

    def handle_api_get_dispatch(self, path: str, query: dict[str, list[str]]) -> None:
        if path == "/api/current-state":
            self.send_json({"current_state": get_current_state()})
            return
        if path == "/api/plans":
            self.send_json({"plans": get_plans()})
            return
        if path == "/api/quests":
            self.send_json({"quests": get_quests()})
            return
        if path == "/api/briefs/latest":
            limit = min(200, int(query.get("limit", ["10"])[0]))
            self.send_json({"briefs": get_latest_briefs(limit)})
            return
        if path == "/api/sessions/recent":
            limit = min(200, int(query.get("limit", ["10"])[0]))
            self.send_json({"sessions": get_recent_sessions(limit)})
            return
        if path == "/api/sessions/active":
            session_id = query.get("session_id", [None])[0]
            self.send_json({"session": get_active_session_runtime(session_id)})
            return
        if path == "/api/sessions/records":
            session_id = query.get("session_id", [""])[0]
            limit = min(200, int(query.get("limit", ["200"])[0]))
            self.send_json({"records": get_source_records(session_id, limit)})
            return

        if path == "/api/workdiary/top-level":
            limit = min(200, int(query.get("limit", ["30"])[0]))
            self.send_json({"items": get_workdiary_top_level(limit)})
            return
        if path == "/api/workdiary/priority-candidates":
            limit = min(200, int(query.get("limit", ["8"])[0]))
            self.send_json({"items": get_workdiary_priority_candidates(limit)})
            return
        if path == "/api/external-inbox":
            limit = min(1000, int(query.get("limit", ["8"])[0]))
            status = query.get("status", [None])[0]
            category = query.get("category", [None])[0]
            self.send_json(get_external_inbox_overview(limit, status, category))
            return
        if path == "/api/external-inbox/source":
            source_id = query.get("source_id", [""])[0]
            if not source_id:
                self.send_json({"error": "source_id is required"}, status=HTTPStatus.BAD_REQUEST)
                return
            day = query.get("day", ["today"])[0]
            before = query.get("before", [None])[0]
            limit = min(1000, int(query.get("limit", ["500"])[0]))
            self.send_json(get_external_inbox_source_messages(source_id, day, limit, before))
            return
        if path == "/api/health":
            self.send_json({"ok": True})
            return
        
        if path == "/api/telegram/sync-status":
            self.send_json({"sources": get_core_sources_sync_status()})
            return

        if path == "/api/telegram/status":
            self.send_json(get_telegram_status())
            return

        if path == "/api/telegram/chats":
            limit = min(200, int(query.get("limit", ["50"])[0]))
            self.send_json({"status": "ok", "chats": fetch_chats(limit=limit)})
            return

        if path == "/api/telegram/messages":
            chat_id = query.get("chat_id", [""])[0]
            if not chat_id:
                self.send_json({"error": "chat_id is required"}, status=HTTPStatus.BAD_REQUEST)
                return

            limit = min(500, int(query.get("limit", ["200"])[0]))
            self.send_json({"status": "ok", "chat_id": chat_id, "messages": fetch_messages(chat_id, limit=limit)})
            return

        if path == "/api/suggestions":
            suggestions_path = ROOT_DIR / "data" / "runtime" / "quest_suggestions.json"
            limit = 3
            try:
                raw_limit = query.get("limit", [None])[0]
                if raw_limit is not None:
                    limit = min(20, max(1, int(raw_limit)))
            except (ValueError, TypeError):
                pass

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
        if path in {"", "/"}:
            path = "/index.html"
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
