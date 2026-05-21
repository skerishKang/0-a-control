"""Session read services for dashboard GET handlers."""

from __future__ import annotations

import json
import re
from pathlib import Path

from scripts import db as _db

ROOT_DIR = _db.ROOT_DIR
RUNTIME_DIR = ROOT_DIR / "data" / "runtime"
SESSIONS_DIR = RUNTIME_DIR / "sessions"
CURRENT_SESSION_FILE = RUNTIME_DIR / "current_session.json"
SAFE_SESSION_ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,128}$")


def validate_session_id(session_id: str | None) -> bool:
    if not isinstance(session_id, str):
        return False
    return bool(SAFE_SESSION_ID_RE.fullmatch(session_id))


def _is_path_inside(child: Path, parent: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except (OSError, RuntimeError, ValueError):
        return False


def get_active_session_runtime(session_id: str | None = None) -> dict:
    target_file = CURRENT_SESSION_FILE
    if session_id:
        if not validate_session_id(session_id):
            return {}
        target_file = SESSIONS_DIR / f"{session_id}.json"
        if not _is_path_inside(target_file, SESSIONS_DIR):
            return {}
    if not target_file.exists():
        return {}
    try:
        return json.loads(target_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def get_active_session_payload(session_id: str | None = None) -> dict:
    return {"session": get_active_session_runtime(session_id)}


def get_session_records_payload(session_id: str, limit: int) -> dict:
    return {"records": _db.get_source_records(session_id, limit)}


def get_session_view_payload(session_id: str, record_limit: int) -> dict:
    return {"view": _db.get_session_view_model(session_id, record_limit)}
