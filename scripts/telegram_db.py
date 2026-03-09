import sqlite3
from pathlib import Path
import json
from datetime import datetime, timezone

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "control_tower.db"

SCHEMA = """
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
    source_type TEXT NOT NULL,             -- 'telegram', 'email', etc.
    source_id TEXT NOT NULL,               -- chat_id or account id
    source_name TEXT,                      -- friendly name
    external_message_id TEXT,              -- original id from source
    author TEXT,                           -- sender name
    item_type TEXT DEFAULT 'text',         -- 'text', 'image', 'video', 'file', 'link'
    title TEXT,
    raw_content TEXT NOT NULL,             -- 원문 텍스트
    attachment_path TEXT,                  -- local blob path
    attachment_ref TEXT,                   -- external id or reference
    item_timestamp TEXT,                   -- original occurrence time
    imported_at TEXT NOT NULL,             -- time added to this DB
    processed_at TEXT,                     -- time status became 'accepted' or 'rejected'
    status TEXT NOT NULL DEFAULT 'new',    -- 'new', 'reviewing', 'accepted', 'rejected', 'archived'
    session_id TEXT,                       -- related session for processing
    metadata_json TEXT,
    UNIQUE(source_id, external_message_id)
);
"""

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def migrate_schema(conn: sqlite3.Connection):
    cursor = conn.cursor()
    
    # Check if table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='external_inbox'")
    table_exists = cursor.fetchone()
    
    if not table_exists:
        return # Will be created by executescript(SCHEMA)

    cursor.execute("PRAGMA table_info(external_inbox)")
    columns = [row[1] for row in cursor.fetchall()]
    
    # Handle content -> raw_content rename
    if "content" in columns and "raw_content" not in columns:
        print("Migrating 'content' column to 'raw_content'...")
        cursor.execute("ALTER TABLE external_inbox RENAME COLUMN content TO raw_content")
    
    # Backfill missing default values for existing rows
    cursor.execute("UPDATE external_inbox SET source_type = 'telegram' WHERE source_type IS NULL OR source_type = ''")
    cursor.execute("UPDATE external_inbox SET item_type = 'text' WHERE item_type IS NULL OR item_type = ''")
    cursor.execute("UPDATE external_inbox SET status = 'new' WHERE status IS NULL OR status = ''")
    
    # List of new columns to add (keeping existing logic for safety)
    new_cols = [
        ("source_type", "TEXT NOT NULL DEFAULT 'telegram'"),
        ("source_name", "TEXT"),
        ("author", "TEXT"),
        ("item_type", "TEXT DEFAULT 'text'"),
        ("attachment_path", "TEXT"),
        ("attachment_ref", "TEXT"),
        ("item_timestamp", "TEXT"),
        ("processed_at", "TEXT"),
        ("session_id", "TEXT"),
    ]
    
    for col_name, col_def in new_cols:
        if col_name not in columns:
            cursor.execute(f"ALTER TABLE external_inbox ADD COLUMN {col_name} {col_def}")
    
    # Fix external_message_id type if needed (was INTEGER, now TEXT in SCHEMA for flexibility)
    # SQLite ALTER COLUMN is limited, so we just leave it as is if it exists.

    conn.commit()

def init_db():
    conn = get_db_connection()
    # If the table already exists, executescript(SCHEMA) will skip CREATE TABLE.
    # So we need to migrate before or after.
    migrate_schema(conn)
    conn.executescript(SCHEMA)
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized and migrated.")
