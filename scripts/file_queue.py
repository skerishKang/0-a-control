from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
REPORTS_DIR = ROOT_DIR / "quest_reports"
VERDICTS_DIR = ROOT_DIR / "quest_verdicts"


def get_iso8601_basic(dt: datetime) -> str:
    # Generate ISO8601 basic format (e.g., 20260309T053100Z)
    return dt.strftime("%Y%m%dT%H%M%SZ")


def generate_report_id(quest_id: str, session_id: str = "") -> str:
    now = datetime.now(timezone.utc)
    ts = get_iso8601_basic(now)
    sid = session_id if session_id else "_"
    return f"{ts}-{quest_id}-{sid}"


def generate_filename(report_id: str, suffix: str) -> str:
    return f"{report_id}.{suffix}.json"


def save_json(directory: Path, filename: str, data: dict) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    file_path = directory / filename
    file_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return file_path


def move_to_processed(file_path: Path):
    processed_dir = file_path.parent / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)
    file_path.rename(processed_dir / file_path.name)


def move_to_failed(file_path: Path):
    failed_dir = file_path.parent / "failed"
    failed_dir.mkdir(parents=True, exist_ok=True)
    file_path.rename(failed_dir / file_path.name)


def move_to_duplicate(file_path: Path):
    dup_dir = file_path.parent.parent / "processed" / "duplicates"
    dup_dir.mkdir(parents=True, exist_ok=True)
    file_path.rename(dup_dir / file_path.name)


def move_to_archive_revision(file_path: Path):
    rev_dir = file_path.parent.parent / "archive" / "revisions"
    rev_dir.mkdir(parents=True, exist_ok=True)
    # Append UUID to prevent overwriting existing revisions of the same report_id
    new_name = f"{file_path.stem}.{str(uuid.uuid4())[:8]}{file_path.suffix}"
    file_path.rename(rev_dir / new_name)
