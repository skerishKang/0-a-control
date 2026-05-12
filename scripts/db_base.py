from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from contextlib import contextmanager
from typing import Any

from scripts.db_helpers import get_db_path, now_iso, row_to_dict, rows_to_dicts

# ── Schema strings live in db_schema.py ────────────────────────────

from scripts.db_schema import SCHEMA, INDEXES, FTS_SCHEMA, rebuild_fts, backfill_event_log


ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = Path(os.getenv("CONTROL_TOWER_DATA_DIR", str(ROOT_DIR / "data")))
DB_PATH = Path(os.getenv("CONTROL_TOWER_DB_PATH", str(DATA_DIR / "control_tower.db")))
WORKDIARY_DIR = Path(os.getenv("CONTROL_TOWER_WORKDIARY_DIR", str(ROOT_DIR.parent)))
UTC = timezone.utc


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


def init_db() -> None:
    with connect() as conn:
        conn.executescript(SCHEMA)
        conn.executescript(INDEXES)
        conn.executescript(FTS_SCHEMA)


def migrate_search_state() -> None:
    with connect() as conn:
        conn.executescript(SCHEMA)
        conn.executescript(INDEXES)
        conn.executescript(FTS_SCHEMA)
        backfill_event_log(conn)
        rebuild_fts(conn)


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


def merge_metadata(existing: str | None, updates: dict[str, Any] | None = None) -> dict[str, Any]:
    merged: dict[str, Any] = {}
    if existing:
        try:
            merged.update(json.loads(existing))
        except json.JSONDecodeError:
            pass
    if updates:
        merged.update(updates)
    return merged


def record_event(
    conn: sqlite3.Connection,
    event_type: str,
    entity_id: str,
    entity_type: str,
    detail: str = "",
    metadata: dict[str, Any] | None = None,
    event_id: str | None = None,
    created_at: str | None = None,
) -> str:
    event_id = event_id or os.urandom(16).hex()
    created_at = created_at or now_iso()
    conn.execute(
        """
        INSERT INTO event_log (
            id, event_type, entity_id, entity_type, detail, metadata_json, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            event_id,
            event_type,
            entity_id,
            entity_type,
            detail or None,
            json.dumps(metadata, ensure_ascii=False) if metadata else None,
            created_at,
        ),
    )
    return event_id