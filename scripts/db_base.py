from __future__ import annotations

import json
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = Path(os.getenv("CONTROL_TOWER_DATA_DIR", str(ROOT_DIR / "data")))
DB_PATH = Path(os.getenv("CONTROL_TOWER_DB_PATH", str(DATA_DIR / "control_tower.db")))
WORKDIARY_DIR = Path(os.getenv("CONTROL_TOWER_WORKDIARY_DIR", str(ROOT_DIR.parent)))
UTC = timezone.utc


def now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def get_db_path() -> Path:
    return Path(os.getenv("CONTROL_TOWER_DB_PATH", str(DATA_DIR / "control_tower.db")))

@contextmanager
def connect():
    path = get_db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout = 10000")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


SCHEMA = """
CREATE TABLE IF NOT EXISTS source_records (
    id TEXT PRIMARY KEY,
    source_type TEXT NOT NULL,
    source_name TEXT NOT NULL,
    session_id TEXT,
    project_key TEXT,
    working_dir TEXT,
    role TEXT,
    content TEXT NOT NULL,
    created_at TEXT NOT NULL,
    metadata_json TEXT
);

CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    agent_name TEXT NOT NULL,
    model_name TEXT,
    source_type TEXT NOT NULL,
    project_key TEXT,
    working_dir TEXT,
    title TEXT,
    started_at TEXT NOT NULL,
    ended_at TEXT,
    summary_md TEXT,
    status TEXT NOT NULL,
    files_touched_json TEXT,
    actions_json TEXT,
    metadata_json TEXT
);

CREATE TABLE IF NOT EXISTS plan_items (
    id TEXT PRIMARY KEY,
    bucket TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL,
    priority_score INTEGER,
    priority_reason TEXT,
    due_at TEXT,
    project_key TEXT,
    related_session_id TEXT,
    related_source_id TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    metadata_json TEXT
);

CREATE TABLE IF NOT EXISTS quests (
    id TEXT PRIMARY KEY,
    plan_item_id TEXT,
    parent_quest_id TEXT,
    title TEXT NOT NULL,
    why_now TEXT,
    completion_criteria TEXT NOT NULL,
    status TEXT NOT NULL,
    verdict_reason TEXT,
    restart_point TEXT,
    next_quest_hint TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    metadata_json TEXT
);

CREATE TABLE IF NOT EXISTS decision_records (
    id TEXT PRIMARY KEY,
    decision_type TEXT NOT NULL,
    title TEXT NOT NULL,
    reason TEXT,
    impact_summary TEXT,
    related_plan_item_id TEXT,
    related_quest_id TEXT,
    related_session_id TEXT,
    created_at TEXT NOT NULL,
    metadata_json TEXT
);

CREATE TABLE IF NOT EXISTS current_state (
    state_key TEXT PRIMARY KEY,
    state_value TEXT,
    updated_at TEXT NOT NULL,
    metadata_json TEXT
);

CREATE TABLE IF NOT EXISTS brief_records (
    id TEXT PRIMARY KEY,
    brief_type TEXT NOT NULL,
    title TEXT NOT NULL,
    content_md TEXT NOT NULL,
    related_plan_item_id TEXT,
    related_quest_id TEXT,
    related_session_id TEXT,
    created_at TEXT NOT NULL,
    metadata_json TEXT
);
"""


def init_db() -> None:
    with connect() as conn:
        conn.executescript(SCHEMA)


def row_to_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    if row is None:
        return None
    item = dict(row)
    for key, value in list(item.items()):
        if key.endswith("_json") and value:
            try:
                item[key] = json.loads(value)
            except json.JSONDecodeError:
                pass
    return item


def rows_to_dicts(rows: list[sqlite3.Row]) -> list[dict[str, Any]]:
    return [row_to_dict(row) for row in rows]


def upsert_state(conn: sqlite3.Connection, key: str, value: Any, metadata: dict[str, Any] | None = None) -> None:
    conn.execute(
        """
        INSERT INTO current_state (state_key, state_value, updated_at, metadata_json)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(state_key) DO UPDATE SET
            state_value = excluded.state_value,
            updated_at = excluded.updated_at,
            metadata_json = excluded.metadata_json
        """,
        (
            key,
            value if isinstance(value, str) else json.dumps(value, ensure_ascii=False),
            now_iso(),
            json.dumps(metadata, ensure_ascii=False) if metadata else None,
        ),
    )
