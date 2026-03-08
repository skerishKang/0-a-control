from __future__ import annotations

import json
import mimetypes
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from db import (
    ROOT_DIR,
    append_source_record,
    create_sample_data_if_empty,
    end_session,
    evaluate_quest,
    get_current_state,
    get_latest_briefs,
    get_plans,
    get_quests,
    get_recent_sessions,
    get_source_records,
    get_workdiary_priority_candidates,
    get_workdiary_top_level,
    report_quest_progress,
    refresh_current_state,
    start_session,
)


PUBLIC_DIR = ROOT_DIR / "public"
HOST = "0.0.0.0"
PORT = 4310
RUNTIME_DIR = ROOT_DIR / "data" / "runtime"
CURRENT_SESSION_FILE = RUNTIME_DIR / "current_session.json"


def get_active_session_runtime() -> dict:
    if not CURRENT_SESSION_FILE.exists():
        return {}
    try:
        return json.loads(CURRENT_SESSION_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


class ControlTowerHandler(BaseHTTPRequestHandler):
    server_version = "ControlTowerHTTP/0.1"

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path.startswith("/api/"):
            self.handle_api_get(parsed.path, parse_qs(parsed.query))
            return
        self.handle_static(parsed.path)

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
            if parsed.path == "/api/quests/evaluate":
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
            if parsed.path == "/api/current-state/refresh":
                result = refresh_current_state()
                self.send_json({"ok": True, "state": result})
                return
            if parsed.path == "/api/quests/report":
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
            if parsed.path == "/api/sessions/start":
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
            if parsed.path == "/api/sessions/log":
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
            if parsed.path == "/api/sessions/end":
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
        except KeyError as exc:
            self.send_json({"error": f"missing field: {exc.args[0]}"}, status=HTTPStatus.BAD_REQUEST)
            return
        except ValueError as exc:
            self.send_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return

        self.send_error(HTTPStatus.NOT_FOUND, "Unknown API endpoint")

    def handle_api_get(self, path: str, query: dict[str, list[str]]) -> None:
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
            limit = int(query.get("limit", ["10"])[0])
            self.send_json({"briefs": get_latest_briefs(limit)})
            return
        if path == "/api/sessions/recent":
            limit = int(query.get("limit", ["10"])[0])
            self.send_json({"sessions": get_recent_sessions(limit)})
            return
        if path == "/api/sessions/active":
            self.send_json({"session": get_active_session_runtime()})
            return
        if path == "/api/sessions/records":
            session_id = query.get("session_id", [""])[0]
            limit = int(query.get("limit", ["200"])[0])
            self.send_json({"records": get_source_records(session_id, limit)})
            return

        if path == "/api/workdiary/top-level":
            limit = int(query.get("limit", ["30"])[0])
            self.send_json({"items": get_workdiary_top_level(limit)})
            return
        if path == "/api/workdiary/priority-candidates":
            limit = int(query.get("limit", ["8"])[0])
            self.send_json({"items": get_workdiary_priority_candidates(limit)})
            return
        if path == "/api/health":
            self.send_json({"ok": True})
            return
        self.send_error(HTTPStatus.NOT_FOUND, "Unknown API endpoint")

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
        self.wfile.write(candidate.read_bytes())

    def send_json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format: str, *args) -> None:
        return


def main() -> None:
    create_sample_data_if_empty()
    server = ThreadingHTTPServer((HOST, PORT), ControlTowerHandler)
    print(f"Control tower server running at http://localhost:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()
