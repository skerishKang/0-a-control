import os
from pathlib import Path
import sqlite3

from scripts.db_base import TELEGRAM_INBOX_SCHEMA


# Respect environment variables if present
ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = Path(os.getenv("CONTROL_TOWER_DATA_DIR", str(ROOT_DIR / "data")))
DB_PATH = Path(os.getenv("CONTROL_TOWER_DB_PATH", str(DATA_DIR / "control_tower.db")))

# `external_inbox` stays as the canonical cross-source reference table for now.
# Telegram backfill/attachment expansion is intentionally planned in docs first:
# see docs/12-telegram-external-storage-design.md
SCHEMA = TELEGRAM_INBOX_SCHEMA


def get_db_path() -> Path:
    return Path(os.getenv("CONTROL_TOWER_DB_PATH", str(DATA_DIR / "control_tower.db")))


def get_db_connection():
    path = get_db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def migrate_schema(conn: sqlite3.Connection):
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='external_inbox'")
    table_exists = cursor.fetchone()
    if not table_exists:
        return

    cursor.execute("PRAGMA table_info(external_inbox)")
    columns = [row[1] for row in cursor.fetchall()]

    if "content" in columns and "raw_content" not in columns:
        cursor.execute("ALTER TABLE external_inbox RENAME COLUMN content TO raw_content")

    cursor.execute("UPDATE external_inbox SET source_type = 'telegram' WHERE source_type IS NULL OR source_type = ''")
    cursor.execute("UPDATE external_inbox SET item_type = 'text' WHERE item_type IS NULL OR item_type = ''")
    cursor.execute("UPDATE external_inbox SET status = 'new' WHERE status IS NULL OR status = ''")

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

    conn.commit()


def init_db():
    conn = get_db_connection()
    migrate_schema(conn)
    conn.executescript(SCHEMA)
    conn.close()


if __name__ == "__main__":
    init_db()
    print("Database initialized and migrated.")
