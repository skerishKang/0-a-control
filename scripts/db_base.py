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

CREATE TABLE IF NOT EXISTS event_log (
    id TEXT PRIMARY KEY,
    event_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    detail TEXT,
    metadata_json TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS telegram_sources (
    source_id TEXT PRIMARY KEY,
    source_name TEXT NOT NULL,
    chat_class TEXT NOT NULL,
    is_core BOOLEAN NOT NULL DEFAULT 0,
    sync_mode TEXT NOT NULL DEFAULT 'manual',
    last_synced_at TEXT,
    last_message_id INTEGER NOT NULL DEFAULT 0,
    metadata_json TEXT
);

CREATE TABLE IF NOT EXISTS external_inbox (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_type TEXT NOT NULL,
    source_id TEXT NOT NULL,
    source_name TEXT,
    external_message_id TEXT,
    author TEXT,
    item_type TEXT DEFAULT 'text',
    title TEXT,
    raw_content TEXT NOT NULL,
    attachment_path TEXT,
    attachment_ref TEXT,
    item_timestamp TEXT,
    imported_at TEXT NOT NULL,
    processed_at TEXT,
    status TEXT NOT NULL DEFAULT 'new',
    session_id TEXT,
    metadata_json TEXT,
    UNIQUE(source_id, external_message_id)
);
"""


INDEXES = """
CREATE INDEX IF NOT EXISTS idx_event_log_entity
ON event_log(entity_type, entity_id);

CREATE INDEX IF NOT EXISTS idx_event_log_type_created
ON event_log(event_type, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_event_log_created
ON event_log(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_external_inbox_status_imported
ON external_inbox(status, imported_at DESC);

CREATE INDEX IF NOT EXISTS idx_external_inbox_source_timestamp
ON external_inbox(source_id, item_timestamp DESC, imported_at DESC);

CREATE INDEX IF NOT EXISTS idx_sessions_agent_started
ON sessions(agent_name, started_at DESC);

CREATE INDEX IF NOT EXISTS idx_sessions_project_started
ON sessions(project_key, started_at DESC);

CREATE INDEX IF NOT EXISTS idx_source_records_session_created
ON source_records(session_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_source_records_type_created
ON source_records(source_type, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_plan_items_bucket_status
ON plan_items(bucket, status);

CREATE INDEX IF NOT EXISTS idx_quests_status_updated
ON quests(status, updated_at DESC);
"""


FTS_SCHEMA = """
CREATE VIRTUAL TABLE IF NOT EXISTS sessions_fts USING fts5(
    id UNINDEXED,
    title,
    summary_md,
    tokenize = 'unicode61 remove_diacritics 1'
);

CREATE VIRTUAL TABLE IF NOT EXISTS source_records_fts USING fts5(
    id UNINDEXED,
    source_name,
    content,
    tokenize = 'unicode61 remove_diacritics 1'
);

CREATE VIRTUAL TABLE IF NOT EXISTS brief_records_fts USING fts5(
    id UNINDEXED,
    title,
    content_md,
    tokenize = 'unicode61 remove_diacritics 1'
);

CREATE VIRTUAL TABLE IF NOT EXISTS decision_records_fts USING fts5(
    id UNINDEXED,
    title,
    reason,
    impact_summary,
    tokenize = 'unicode61 remove_diacritics 1'
);

CREATE VIRTUAL TABLE IF NOT EXISTS external_inbox_fts USING fts5(
    id UNINDEXED,
    source_name,
    author,
    title,
    raw_content,
    attachment_path,
    tokenize = 'unicode61 remove_diacritics 1'
);

CREATE TRIGGER IF NOT EXISTS sessions_ai AFTER INSERT ON sessions BEGIN
    INSERT INTO sessions_fts(id, title, summary_md)
    VALUES (NEW.id, COALESCE(NEW.title, ''), COALESCE(NEW.summary_md, ''));
END;

CREATE TRIGGER IF NOT EXISTS sessions_au AFTER UPDATE ON sessions BEGIN
    DELETE FROM sessions_fts WHERE id = OLD.id;
    INSERT INTO sessions_fts(id, title, summary_md)
    VALUES (NEW.id, COALESCE(NEW.title, ''), COALESCE(NEW.summary_md, ''));
END;

CREATE TRIGGER IF NOT EXISTS sessions_ad AFTER DELETE ON sessions BEGIN
    DELETE FROM sessions_fts WHERE id = OLD.id;
END;

CREATE TRIGGER IF NOT EXISTS source_records_ai AFTER INSERT ON source_records BEGIN
    INSERT INTO source_records_fts(id, source_name, content)
    VALUES (NEW.id, COALESCE(NEW.source_name, ''), COALESCE(NEW.content, ''));
END;

CREATE TRIGGER IF NOT EXISTS source_records_au AFTER UPDATE ON source_records BEGIN
    DELETE FROM source_records_fts WHERE id = OLD.id;
    INSERT INTO source_records_fts(id, source_name, content)
    VALUES (NEW.id, COALESCE(NEW.source_name, ''), COALESCE(NEW.content, ''));
END;

CREATE TRIGGER IF NOT EXISTS source_records_ad AFTER DELETE ON source_records BEGIN
    DELETE FROM source_records_fts WHERE id = OLD.id;
END;

CREATE TRIGGER IF NOT EXISTS brief_records_ai AFTER INSERT ON brief_records BEGIN
    INSERT INTO brief_records_fts(id, title, content_md)
    VALUES (NEW.id, COALESCE(NEW.title, ''), COALESCE(NEW.content_md, ''));
END;

CREATE TRIGGER IF NOT EXISTS brief_records_au AFTER UPDATE ON brief_records BEGIN
    DELETE FROM brief_records_fts WHERE id = OLD.id;
    INSERT INTO brief_records_fts(id, title, content_md)
    VALUES (NEW.id, COALESCE(NEW.title, ''), COALESCE(NEW.content_md, ''));
END;

CREATE TRIGGER IF NOT EXISTS brief_records_ad AFTER DELETE ON brief_records BEGIN
    DELETE FROM brief_records_fts WHERE id = OLD.id;
END;

CREATE TRIGGER IF NOT EXISTS decision_records_ai AFTER INSERT ON decision_records BEGIN
    INSERT INTO decision_records_fts(id, title, reason, impact_summary)
    VALUES (
        NEW.id,
        COALESCE(NEW.title, ''),
        COALESCE(NEW.reason, ''),
        COALESCE(NEW.impact_summary, '')
    );
END;

CREATE TRIGGER IF NOT EXISTS decision_records_au AFTER UPDATE ON decision_records BEGIN
    DELETE FROM decision_records_fts WHERE id = OLD.id;
    INSERT INTO decision_records_fts(id, title, reason, impact_summary)
    VALUES (
        NEW.id,
        COALESCE(NEW.title, ''),
        COALESCE(NEW.reason, ''),
        COALESCE(NEW.impact_summary, '')
    );
END;

CREATE TRIGGER IF NOT EXISTS decision_records_ad AFTER DELETE ON decision_records BEGIN
    DELETE FROM decision_records_fts WHERE id = OLD.id;
END;

CREATE TRIGGER IF NOT EXISTS external_inbox_ai AFTER INSERT ON external_inbox BEGIN
    INSERT INTO external_inbox_fts(id, source_name, author, title, raw_content, attachment_path)
    VALUES (
        CAST(NEW.id AS TEXT),
        COALESCE(NEW.source_name, ''),
        COALESCE(NEW.author, ''),
        COALESCE(NEW.title, ''),
        COALESCE(NEW.raw_content, ''),
        COALESCE(NEW.attachment_path, '')
    );
END;

CREATE TRIGGER IF NOT EXISTS external_inbox_au AFTER UPDATE ON external_inbox BEGIN
    DELETE FROM external_inbox_fts WHERE id = CAST(OLD.id AS TEXT);
    INSERT INTO external_inbox_fts(id, source_name, author, title, raw_content, attachment_path)
    VALUES (
        CAST(NEW.id AS TEXT),
        COALESCE(NEW.source_name, ''),
        COALESCE(NEW.author, ''),
        COALESCE(NEW.title, ''),
        COALESCE(NEW.raw_content, ''),
        COALESCE(NEW.attachment_path, '')
    );
END;

CREATE TRIGGER IF NOT EXISTS external_inbox_ad AFTER DELETE ON external_inbox BEGIN
    DELETE FROM external_inbox_fts WHERE id = CAST(OLD.id AS TEXT);
END;
"""


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


def rebuild_fts(conn: sqlite3.Connection) -> None:
    conn.execute("DELETE FROM sessions_fts")
    conn.execute(
        """
        INSERT INTO sessions_fts(id, title, summary_md)
        SELECT id, COALESCE(title, ''), COALESCE(summary_md, '')
        FROM sessions
        """
    )

    conn.execute("DELETE FROM source_records_fts")
    conn.execute(
        """
        INSERT INTO source_records_fts(id, source_name, content)
        SELECT id, COALESCE(source_name, ''), COALESCE(content, '')
        FROM source_records
        """
    )

    conn.execute("DELETE FROM brief_records_fts")
    conn.execute(
        """
        INSERT INTO brief_records_fts(id, title, content_md)
        SELECT id, COALESCE(title, ''), COALESCE(content_md, '')
        FROM brief_records
        """
    )

    conn.execute("DELETE FROM decision_records_fts")
    conn.execute(
        """
        INSERT INTO decision_records_fts(id, title, reason, impact_summary)
        SELECT
            id,
            COALESCE(title, ''),
            COALESCE(reason, ''),
            COALESCE(impact_summary, '')
        FROM decision_records
        """
    )

    conn.execute("DELETE FROM external_inbox_fts")
    conn.execute(
        """
        INSERT INTO external_inbox_fts(id, source_name, author, title, raw_content, attachment_path)
        SELECT
            CAST(id AS TEXT),
            COALESCE(source_name, ''),
            COALESCE(author, ''),
            COALESCE(title, ''),
            COALESCE(raw_content, ''),
            COALESCE(attachment_path, '')
        FROM external_inbox
        """
    )


def backfill_event_log(conn: sqlite3.Connection) -> None:
    rows = conn.execute(
        """
        SELECT id, title, started_at, ended_at, status, project_key, agent_name
        FROM sessions
        """
    ).fetchall()
    for row in rows:
        metadata = {
            "agent_name": row["agent_name"] or "",
            "project_key": row["project_key"] or "",
            "status": row["status"] or "",
        }
        conn.execute(
            """
            INSERT OR IGNORE INTO event_log (
                id, event_type, entity_id, entity_type, detail, metadata_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                f"session-start:{row['id']}",
                "session_start",
                row["id"],
                "session",
                row["title"] or f"{row['agent_name']} session started",
                json.dumps(metadata, ensure_ascii=False),
                row["started_at"],
            ),
        )
        if row["ended_at"]:
            conn.execute(
                """
                INSERT OR IGNORE INTO event_log (
                    id, event_type, entity_id, entity_type, detail, metadata_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    f"session-end:{row['id']}",
                    "session_end",
                    row["id"],
                    "session",
                    row["title"] or f"{row['agent_name']} session ended",
                    json.dumps(metadata, ensure_ascii=False),
                    row["ended_at"],
                ),
            )

    rows = conn.execute(
        """
        SELECT id, decision_type, title, reason, created_at, related_quest_id, related_plan_item_id, related_session_id
        FROM decision_records
        """
    ).fetchall()
    for row in rows:
        conn.execute(
            """
            INSERT OR IGNORE INTO event_log (
                id, event_type, entity_id, entity_type, detail, metadata_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                f"decision:{row['id']}",
                row["decision_type"] or "decision_recorded",
                row["id"],
                "decision",
                row["title"] or row["reason"] or "decision recorded",
                json.dumps(
                    {
                        "related_quest_id": row["related_quest_id"] or "",
                        "related_plan_item_id": row["related_plan_item_id"] or "",
                        "related_session_id": row["related_session_id"] or "",
                    },
                    ensure_ascii=False,
                ),
                row["created_at"],
            ),
        )


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
