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
    from scripts.telegram_cli import get_core_sources_sync_status, run_sync_core
    from scripts.telegram_service import fetch_chats, fetch_messages, get_telegram_status
else:
    from . import db as _db
    from .db_ops import approve_plan_candidates
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


def classify_conversation(text: str) -> dict:
    """
    Classify conversation text into 6 layers and extract suggested plans.
    """
    text_lower = text.lower()

    layer = "short_term"
    bucket = "short_term"

    if any(k in text_lower for k in ["오늘", "지금", "당장", "today"]):
        layer = "today"
        bucket = "today"
    elif any(k in text_lower for k in ["이번 주", "주간", "다음 주", "short"]):
        layer = "short_term"
        bucket = "short_term"
    elif any(k in text_lower for k in ["장기", "올해", "long"]):
        layer = "long_term"
        bucket = "long_term"
    elif any(k in text_lower for k in ["매주", "반복", "정기", "매월", "recurring"]):
        layer = "recurring"
        bucket = "recurring"
    elif any(k in text_lower for k in ["프로젝트", "project"]):
        layer = "project"
        bucket = "short_term"

    is_philosophy = any(k in text_lower for k in [
        "철학", "아이디어", "방향", "principle", "philosophy",
        "통제", "위임", "판단", "협업", "운영", "체계"
    ])

    if is_philosophy:
        layer = "philosophy"
        bucket = "long_term"

    title = text.split("\n")[0][:100]

    return {
        "layer": layer,
        "bucket": bucket,
        "title": title,
        "description": text[:500],
        "suggested_plans": [{
            "title": title,
            "bucket": bucket,
            "description": text[:500],
            "priority_score": 50
        }]
    }


def parse_quick_input(text: str) -> dict:
    """
    Parse natural language quick input into plan candidates with bucket classification.
    
    Expected format:
        오늘:
        - 9시 광주시 사단법인 문의
        - 신보 카톡 확인 후 전화
        
        기한:
        - 3/20 소상공인 지원사업 준비
        
        보류:
        - 테무 보조모니터 보기
    
    Returns:
        {
            "candidates": [...],
            "main_mission": {...},
            "current_quest": {...}
        }
    """
    import re
    from datetime import datetime
    
    BUCKET_PATTERNS = {
        "today": re.compile(r"^(오늘|today|지금|당장|오늘之内)\s*[:：]?", re.MULTILINE | re.IGNORECASE),
        "dated": re.compile(r"^(기한|마감|，截止|dealine|due)\s*[:：]?", re.MULTILINE | re.IGNORECASE),
        "hold": re.compile(r"^(보류|대기|잠시|hold|waiting)\s*[:：]?", re.MULTILINE | re.IGNORECASE),
        "short_term": re.compile(r"^(이번 주|주간|short.?term|주차)\s*[:：]?", re.MULTILINE | re.IGNORECASE),
        "long_term": re.compile(r"^(장기|올해|long.?term|年内)\s*[:：]?", re.MULTILINE | re.IGNORECASE),
        "recurring": re.compile(r"^(매주|반복|정기|recurring|매일|매월)\s*[:：]?", re.MULTILINE | re.IGNORECASE),
    }
    
    TIME_PATTERN = re.compile(r"(\d{1,2})[시시]")
    DATE_PATTERN = re.compile(r"(\d{1,2})[/월\-.月](\d{1,2})")
    URGENT_KEYWORDS = ["당장", "지금", "紧迫", "긴급", "urgent", "asap"]
    
    def extract_items_by_section(text: str) -> dict[str, list[str]]:
        sections = {section: [] for section in ["today", "dated", "hold", "short_term", "long_term", "recurring"]}
        current_bucket = None
        lines = text.strip().split("\n")
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            matched_section = None
            for section, pattern in BUCKET_PATTERNS.items():
                if pattern.match(line):
                    matched_section = section
                    break
            
            if matched_section:
                current_bucket = matched_section
                continue
            
            if current_bucket and (line.startswith("-") or line.startswith("•") or line.startswith("*")):
                item = line.lstrip("-•* ").strip()
                if item:
                    sections[current_bucket].append(item)
            elif current_bucket and line:
                sections[current_bucket].append(line)
        
        if not any(sections.values()):
            sections["today"].extend([l.strip().lstrip("-•* ") for l in lines if l.strip()])
        
        return sections
    
    def estimate_priority_score(item: str, bucket: str) -> int:
        score = 50
        
        item_lower = item.lower()
        
        if any(k in item_lower for k in URGENT_KEYWORDS):
            score += 20
        
        if TIME_PATTERN.search(item):
            score += 10
        
        if bucket == "today":
            score += 15
        elif bucket == "dated":
            score += 5
        elif bucket == "hold":
            score -= 20
        
        if any(k in item_lower for k in ["문의", "확인", "전화", "연락", "체크", "check"]):
            score += 10
        
        if len(item) < 20:
            score += 5
        
        return max(0, min(100, score))
    
    def extract_due_date(item: str) -> str | None:
        match = DATE_PATTERN.search(item)
        if match:
            month, day = int(match.group(1)), int(match.group(2))
            now = datetime.now()
            year = now.year if month >= now.month else now.year + 1
            return f"{year}-{month:02d}-{day:02d}"
        
        time_match = TIME_PATTERN.search(item)
        if time_match:
            hour = int(time_match.group(1))
            now = datetime.now()
            return f"{now.year}-{now.month:02d}-{now.day:02d}T{hour:02d}:00"
        
        return None
    
    sections = extract_items_by_section(text)
    
    candidates = []
    all_items = []
    
    for bucket, items in sections.items():
        for item in items:
            priority_score = estimate_priority_score(item, bucket)
            due_date = extract_due_date(item) if bucket == "dated" else None
            
            candidate = {
                "title": item,
                "bucket": bucket,
                "description": f"[{bucket}] {item}",
                "priority_score": priority_score,
            }
            if due_date:
                candidate["due_date"] = due_date
            
            candidates.append(candidate)
            all_items.append((item, bucket, priority_score))
    
    candidates.sort(key=lambda x: x["priority_score"], reverse=True)
    
    today_items = [(i, b, p) for i, b, p in all_items if b == "today"]
    dated_items = [(i, b, p) for i, b, p in all_items if b == "dated"]
    hold_items = [(i, b, p) for i, b, p in all_items if b == "hold"]
    
    main_mission = None
    if today_items:
        main_mission = max(today_items, key=lambda x: x[2])
        main_mission = {
            "title": main_mission[0],
            "bucket": "today",
            "reason": "오늘 해야 할 가장 중요한 일",
            "priority_score": main_mission[2]
        }
    elif dated_items:
        main_mission = max(dated_items, key=lambda x: x[2])
        main_mission = {
            "title": main_mission[0],
            "bucket": "dated",
            "reason": "기한이 가장 가까운 중요 일",
            "priority_score": main_mission[2]
        }
    elif candidates:
        main_mission = {
            "title": candidates[0]["title"],
            "bucket": candidates[0]["bucket"],
            "reason": "우선순위가 가장 높은 항목",
            "priority_score": candidates[0]["priority_score"]
        }
    
    current_quest = None
    actionable_items = [(i, b, p) for i, b, p in all_items if any(k in i.lower() for k in ["문의", "전화", "확인", "체크", "연락", "보내기", "작성", "준비", "제출"])]
    
    if actionable_items:
        current_quest = max(actionable_items, key=lambda x: x[2])
    elif today_items:
        current_quest = today_items[0]
    elif candidates:
        current_quest = (candidates[0]["title"], candidates[0]["bucket"], candidates[0]["priority_score"])
    
    if current_quest:
        current_quest = {
            "title": current_quest[0],
            "bucket": current_quest[1],
            "reason": "가장 실행 가능한 다음 행동",
            "priority_score": current_quest[2]
        }
    
    return {
        "candidates": candidates,
        "main_mission": main_mission,
        "current_quest": current_quest,
        "summary": {
            "today_count": len(today_items),
            "dated_count": len(dated_items),
            "hold_count": len(hold_items),
            "total_count": len(candidates)
        }
    }


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
get_session_view_model = _db.get_session_view_model
get_source_records = _db.get_source_records
get_workdiary_priority_candidates = _db.get_workdiary_priority_candidates
get_workdiary_top_level = _db.get_workdiary_top_level
report_quest_progress = _db.report_quest_progress
refresh_current_state = _db.refresh_current_state
defer_current_quest_to_short_term = _db.defer_current_quest_to_short_term
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
        if path.startswith("/api/current-quest/hold") or path.startswith("/api/quest-hold"):
            result = _db.mark_current_quest_unfinished()
            self.send_json({"ok": True, **result})
            return
        if path.startswith("/api/current-quest/defer") or path.startswith("/api/quest-defer"):
            result = defer_current_quest_to_short_term()
            self.send_json({"ok": True, **result})
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

        if path == "/api/bridge/parse":
            text = body.get("text", "").strip()
            if not text:
                self.send_json({"error": "text is required"}, status=HTTPStatus.BAD_REQUEST)
                return

            classification = classify_conversation(text)
            self.send_json({
                "classification": classification,
                "suggested_plans": classification.get("suggested_plans", [])
            })
            return

        if path == "/api/bridge/quick-input":
            text = body.get("text", "").strip()
            if not text:
                self.send_json({"error": "text is required"}, status=HTTPStatus.BAD_REQUEST)
                return

            result = parse_quick_input(text)
            self.send_json(result)
            return

        if path == "/api/bridge/create-plan":
            candidates = body.get("candidates", [])
            if not candidates:
                self.send_json({"error": "candidates is required"}, status=HTTPStatus.BAD_REQUEST)
                return

            result = approve_plan_candidates(candidates)
            self.send_json({"ok": True, "plans": result})
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
            limit = parse_limit(query, "limit", 10, 200)
            self.send_json({"briefs": get_latest_briefs(limit)})
            return
        if path == "/api/sessions/recent":
            limit = parse_limit(query, "limit", 10, 200)
            self.send_json({"sessions": get_recent_sessions(limit)})
            return
        if path == "/api/sessions/active":
            session_id = query.get("session_id", [None])[0]
            self.send_json({"session": get_active_session_runtime(session_id)})
            return
        if path == "/api/sessions/records":
            session_id = query.get("session_id", [""])[0]
            limit = parse_limit(query, "limit", 200, 200)
            self.send_json({"records": get_source_records(session_id, limit)})
            return
        if path.startswith("/api/sessions/view/"):
            session_id = path.rsplit("/", 1)[-1]
            if not session_id:
                self.send_json({"error": "session_id is required"}, status=HTTPStatus.BAD_REQUEST)
                return
            record_limit = parse_limit(query, "limit", 500, 2000)
            self.send_json({"view": get_session_view_model(session_id, record_limit)})
            return

        if path == "/api/workdiary/top-level":
            limit = parse_limit(query, "limit", 30, 200)
            self.send_json({"items": get_workdiary_top_level(limit)})
            return
        if path == "/api/workdiary/priority-candidates":
            limit = parse_limit(query, "limit", 8, 200)
            self.send_json({"items": get_workdiary_priority_candidates(limit)})
            return
        if path == "/api/external-inbox":
            limit = parse_limit(query, "limit", 8, 1000)
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
            limit = parse_limit(query, "limit", 500, 1000)
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
            limit = parse_limit(query, "limit", 50, 200)
            self.send_json({"status": "ok", "chats": fetch_chats(limit=limit)})
            return

        if path == "/api/telegram/messages":
            chat_id = query.get("chat_id", [""])[0]
            if not chat_id:
                self.send_json({"error": "chat_id is required"}, status=HTTPStatus.BAD_REQUEST)
                return

            limit = parse_limit(query, "limit", 200, 500)
            self.send_json({"status": "ok", "chat_id": chat_id, "messages": fetch_messages(chat_id, limit=limit)})
            return

        if path == "/api/suggestions":
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
