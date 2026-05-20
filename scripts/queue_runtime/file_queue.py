from __future__ import annotations

import json
import os
import re
import uuid
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
QUEUE_DIR = Path(os.getenv("CONTROL_TOWER_QUEUE_DIR", str(ROOT_DIR / "data" / "queue")))
REPORTS_DIR = QUEUE_DIR / "reports"
VERDICTS_DIR = QUEUE_DIR / "verdicts"
PROCESSED_DIR = QUEUE_DIR / "processed"

# Pattern for a well-formed UUID (xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)
_UUID_PATTERN = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I)
# Allowed characters in filename tokens: alphanumeric, hyphen, underscore, dot
_SAFE_TOKEN_RE = re.compile(r"[^a-zA-Z0-9._-]")
# Suffix allowlist — only these suffixes are accepted
SAFE_SUFFIXES: frozenset[str] = frozenset({
    "quest-report",
    "phase-report",
    "quest-plan",
    "session-log",
    "verdict",
    "event",
    "summary",
    "checkpoint",
    "debug",
    "plan",
    "revision",
    "detail",
})


def get_iso8601_basic(dt: datetime) -> str:
    # Generate ISO8601 basic format (e.g., 20260309T053100Z)
    return dt.strftime("%Y%m%dT%H%M%SZ")


def _safe_token(value: str, placeholder: str = "_") -> str:
    """Normalize *value* into a filesystem-safe token.

    - Removes characters that are not alphanumeric, ``-``, ``_``, or ``.``
    - Strips leading/trailing dots to avoid hidden files and traversal tokens
    - Returns *placeholder* if the result is empty.
    """
    cleaned = _SAFE_TOKEN_RE.sub("", value).strip(".")
    return cleaned if cleaned else placeholder


def generate_report_id(quest_id: str, session_id: str = "") -> str:
    now = datetime.now(timezone.utc)
    ts = get_iso8601_basic(now)
    safe_quest = _safe_token(quest_id)
    sid = _safe_token(session_id) if session_id else "_"
    return f"{ts}-{safe_quest}-{sid}"


def generate_filename(report_id: str, suffix: str) -> str:
    """Produce a ``{report_id}.{suffix}.json`` filename.

    If *suffix* is not in :data:`SAFE_SUFFIXES`, it is normalized via
    :func:`_safe_token` to prevent arbitrary extensions or path fragments.
    """
    if suffix not in SAFE_SUFFIXES:
        suffix = _safe_token(suffix, "report")
    safe_id = _safe_token(report_id)
    return f"{safe_id}.{suffix}.json"


def save_json(directory: Path, filename: str, data: dict) -> Path:
    """Saves a dictionary to a JSON file atomically."""
    directory.mkdir(parents=True, exist_ok=True)
    file_path = directory / filename
    temp_path = file_path.with_suffix(f"{file_path.suffix}.tmp_{uuid.uuid4().hex}")
    
    try:
        temp_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(temp_path, file_path)
    except Exception as e:
        print(f"Error saving JSON to {file_path}: {e}")
        # Clean up temp file if it exists
        if temp_path.exists():
            temp_path.unlink()
        raise
        
    return file_path


def move_to_processed(file_path: Path):
    target_dir = PROCESSED_DIR / file_path.parent.name
    target_dir.mkdir(parents=True, exist_ok=True)
    shutil.move(str(file_path), str(target_dir / file_path.name))


def move_to_failed(file_path: Path):
    target_dir = QUEUE_DIR / "failed" / file_path.parent.name
    target_dir.mkdir(parents=True, exist_ok=True)
    shutil.move(str(file_path), str(target_dir / file_path.name))


def move_to_duplicate(file_path: Path):
    target_dir = PROCESSED_DIR / "duplicates" / file_path.parent.name
    target_dir.mkdir(parents=True, exist_ok=True)
    shutil.move(str(file_path), str(target_dir / file_path.name))


def move_to_archive_revision(file_path: Path):
    target_dir = QUEUE_DIR / "archive" / "revisions"
    target_dir.mkdir(parents=True, exist_ok=True)
    # Append UUID to prevent overwriting existing revisions of the same report_id
    new_name = f"{file_path.stem}.{str(uuid.uuid4())[:8]}{file_path.suffix}"
    shutil.move(str(file_path), str(target_dir / new_name))
