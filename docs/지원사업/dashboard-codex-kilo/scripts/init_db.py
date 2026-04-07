#!/usr/bin/env python3
import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "db" / "notices.sqlite3"

NOTICE_TABLE = """
CREATE TABLE IF NOT EXISTS notices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_site TEXT NOT NULL,
    source_url TEXT NOT NULL UNIQUE,
    source_notice_id TEXT,
    title TEXT,
    category TEXT,
    posted_at TEXT,
    apply_start TEXT,
    apply_end TEXT,
    ministry TEXT,
    agency TEXT,
    apply_method TEXT,
    apply_site_url TEXT,
    source_origin_url TEXT,
    contact TEXT,
    summary_html TEXT,
    summary_text TEXT,
    status TEXT DEFAULT 'new',
    manual_note TEXT DEFAULT '',
    one_line_summary TEXT DEFAULT '',
    storage_path TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
)
"""

ATTACHMENT_TABLE = """
CREATE TABLE IF NOT EXISTS attachments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    notice_id INTEGER NOT NULL,
    section_name TEXT,
    name TEXT NOT NULL,
    view_url TEXT,
    download_url TEXT,
    local_path TEXT,
    downloaded INTEGER DEFAULT 0,
    sort_order INTEGER DEFAULT 0,
    FOREIGN KEY (notice_id) REFERENCES notices(id) ON DELETE CASCADE
)
"""

COMPANY_FIT_TABLE = """
CREATE TABLE IF NOT EXISTS company_fit (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    notice_id INTEGER NOT NULL,
    company_id TEXT,
    fit_score REAL,
    fit_reason TEXT,
    risk_notes TEXT,
    model_name TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (notice_id) REFERENCES notices(id) ON DELETE CASCADE
)
"""


def init_db(db_path: Path = None) -> None:
    if db_path is None:
        db_path = DB_PATH
    
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute(NOTICE_TABLE)
    cursor.execute(ATTACHMENT_TABLE)
    cursor.execute(COMPANY_FIT_TABLE)
    
    cursor.execute("PRAGMA table_info(notices)")
    columns = [row[1] for row in cursor.fetchall()]

    if 'manual_note' not in columns:
        cursor.execute("ALTER TABLE notices ADD COLUMN manual_note TEXT DEFAULT ''")
    if 'one_line_summary' not in columns:
        cursor.execute("ALTER TABLE notices ADD COLUMN one_line_summary TEXT DEFAULT ''")
    if 'status' not in columns:
        cursor.execute("ALTER TABLE notices ADD COLUMN status TEXT DEFAULT 'new'")

    # AI 분석 관련 필드 추가
    if 'ai_fit_score' not in columns:
        cursor.execute("ALTER TABLE notices ADD COLUMN ai_fit_score REAL")
    if 'ai_summary' not in columns:
        cursor.execute("ALTER TABLE notices ADD COLUMN ai_summary TEXT")
    if 'ai_strengths' not in columns:
        cursor.execute("ALTER TABLE notices ADD COLUMN ai_strengths TEXT")
    if 'ai_risks' not in columns:
        cursor.execute("ALTER TABLE notices ADD COLUMN ai_risks TEXT")
    if 'ai_next_actions' not in columns:
        cursor.execute("ALTER TABLE notices ADD COLUMN ai_next_actions TEXT")
    if 'ai_model' not in columns:
        cursor.execute("ALTER TABLE notices ADD COLUMN ai_model TEXT")
    if 'ai_updated_at' not in columns:
        cursor.execute("ALTER TABLE notices ADD COLUMN ai_updated_at TEXT")
    if 'ai_raw_json' not in columns:
        cursor.execute("ALTER TABLE notices ADD COLUMN ai_raw_json TEXT")
    if 'ai_mode' not in columns:
        cursor.execute("ALTER TABLE notices ADD COLUMN ai_mode TEXT")
    if 'ai_provider' not in columns:
        cursor.execute("ALTER TABLE notices ADD COLUMN ai_provider TEXT")
    if 'ai_fallback_used' not in columns:
        cursor.execute("ALTER TABLE notices ADD COLUMN ai_fallback_used INTEGER DEFAULT 0")
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_notices_source_site ON notices(source_site)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_notices_source_notice_id ON notices(source_notice_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_notices_apply_end ON notices(apply_end)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_attachments_notice_id ON attachments(notice_id)")
    
    conn.commit()
    conn.close()
    
    print(f"Database initialized at: {db_path}")


def get_connection(db_path: Path = None) -> sqlite3.Connection:
    if db_path is None:
        db_path = DB_PATH
    return sqlite3.connect(db_path)


if __name__ == "__main__":
    init_db()