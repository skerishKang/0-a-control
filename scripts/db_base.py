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
BASELINE_SCHEMA_VERSION = 1
BASELINE_SCHEMA_NAME = "baseline-current-schema"
ORPHAN_REFERENCE_CLEANUP_VERSION = 2
ORPHAN_REFERENCE_CLEANUP_NAME = "null-orphan-relational-references"
SOURCE_RECORDS_SESSION_FK_VERSION = 3
SOURCE_RECORDS_SESSION_FK_NAME = "source-records-session-fk"


def configure_connection(conn: sqlite3.Connection) -> None:
    conn.execute("PRAGMA busy_timeout = 10000")
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        journal_mode = conn.execute("PRAGMA journal_mode = WAL").fetchone()
        if journal_mode and str(journal_mode[0]).lower() == "wal":
            conn.execute("PRAGMA synchronous = NORMAL")
    except sqlite3.DatabaseError:
        pass


@contextmanager
def connect():
    path = get_db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, timeout=10)
    conn.row_factory = sqlite3.Row
    configure_connection(conn)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def ensure_schema_migrations(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            applied_at TEXT NOT NULL
        )
        """
    )


def record_schema_migration(conn: sqlite3.Connection, version: int, name: str) -> None:
    conn.execute(
        """
        INSERT OR IGNORE INTO schema_migrations (version, name, applied_at)
        VALUES (?, ?, ?)
        """,
        (version, name, now_iso()),
    )


def schema_migration_applied(conn: sqlite3.Connection, version: int) -> bool:
    ensure_schema_migrations(conn)
    row = conn.execute(
        "SELECT 1 FROM schema_migrations WHERE version = ?",
        (version,),
    ).fetchone()
    return row is not None


def apply_schema_migrations(conn: sqlite3.Connection) -> None:
    """Apply schema/data migrations in order."""
    ensure_schema_migrations(conn)
    record_schema_migration(conn, BASELINE_SCHEMA_VERSION, BASELINE_SCHEMA_NAME)
    if not schema_migration_applied(conn, ORPHAN_REFERENCE_CLEANUP_VERSION):
        from scripts.db_integrity import clear_orphan_references

        clear_orphan_references(conn)
        record_schema_migration(
            conn,
            ORPHAN_REFERENCE_CLEANUP_VERSION,
            ORPHAN_REFERENCE_CLEANUP_NAME,
        )
    if not schema_migration_applied(conn, SOURCE_RECORDS_SESSION_FK_VERSION):
        from scripts.db_fk_migrations import apply_source_records_session_fk

        apply_source_records_session_fk(conn)
        record_schema_migration(
            conn,
            SOURCE_RECORDS_SESSION_FK_VERSION,
            SOURCE_RECORDS_SESSION_FK_NAME,
        )


def get_applied_schema_versions(conn: sqlite3.Connection) -> list[int]:
    ensure_schema_migrations(conn)
    rows = conn.execute("SELECT version FROM schema_migrations ORDER BY version ASC").fetchall()
    return [int(row["version"]) for row in rows]


def init_db() -> None:
    with connect() as conn:
        conn.executescript(SCHEMA)
        conn.executescript(INDEXES)
        conn.executescript(FTS_SCHEMA)
        apply_schema_migrations(conn)
        clean_stale_state_keys(conn)


def clean_stale_state_keys(conn: sqlite3.Connection) -> None:
    """Remove stale state keys that are no longer written by the system."""
    stale_keys = [
        "workdiary_top_level",
        "workdiary_priority_candidates",
        "priority_recommendation",
    ]
    for key in stale_keys:
        conn.execute("DELETE FROM current_state WHERE state_key = ?", (key,))


def migrate_search_state() -> None:
    with connect() as conn:
        conn.executescript(SCHEMA)
        conn.executescript(INDEXES)
        conn.executescript(FTS_SCHEMA)
        apply_schema_migrations(conn)
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