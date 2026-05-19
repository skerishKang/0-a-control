"""Foreign-key constraint migrations applied as safe table rebuilds."""

from __future__ import annotations

import sqlite3

from scripts.db_schema import INDEXES, FTS_SCHEMA, rebuild_fts


def _has_fk_on_column(
    conn: sqlite3.Connection, table: str, column: str, ref_table: str
) -> bool:
    """Return True if *table.column* already has a FK referencing *ref_table*."""
    rows = conn.execute(f"PRAGMA foreign_key_list({table})").fetchall()
    for row in rows:
        # row layout: id, seq, table, from, to, on_update, on_delete, match
        if row[2] == ref_table and row[3] == column:
            return True
    return False


def _table_exists(conn: sqlite3.Connection, name: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
        (name,),
    ).fetchone()
    return row is not None


def _drop_source_records_fts_triggers(conn: sqlite3.Connection) -> None:
    for suffix in ("ai", "au", "ad"):
        conn.execute(f"DROP TRIGGER IF EXISTS source_records_{suffix}")


def _source_records_columns() -> list[str]:
    """Canonical column list for source_records (order matters for INSERT..SELECT)."""
    return [
        "id",
        "source_type",
        "source_name",
        "session_id",
        "project_key",
        "working_dir",
        "role",
        "content",
        "created_at",
        "metadata_json",
    ]


def apply_source_records_session_fk(conn: sqlite3.Connection) -> None:
    """Rebuild source_records with ``session_id -> sessions(id) ON DELETE SET NULL``.

    No-op when either table is missing or the FK already exists.
    """
    if not _table_exists(conn, "source_records") or not _table_exists(
        conn, "sessions"
    ):
        return

    if _has_fk_on_column(conn, "source_records", "session_id", "sessions"):
        return

    columns = _source_records_columns()
    col_sql = ", ".join(columns)

    # 1. Drop FTS triggers (will be recreated by FTS_SCHEMA)
    _drop_source_records_fts_triggers(conn)

    # 2. Rename current table
    conn.execute("ALTER TABLE source_records RENAME TO source_records_old")

    # 3. Create new table with FK constraint
    conn.execute(
        """
        CREATE TABLE source_records (
            id TEXT PRIMARY KEY,
            source_type TEXT NOT NULL,
            source_name TEXT NOT NULL,
            session_id TEXT
                REFERENCES sessions(id) ON DELETE SET NULL,
            project_key TEXT,
            working_dir TEXT,
            role TEXT,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL,
            metadata_json TEXT
        )
        """
    )

    # 4. Copy data
    conn.execute(
        f"INSERT INTO source_records ({col_sql}) "
        f"SELECT {col_sql} FROM source_records_old"
    )

    # 5. Drop old table
    conn.execute("DROP TABLE source_records_old")

    # 6. Re-apply indexes and FTS virtual tables/triggers
    conn.executescript(INDEXES)
    conn.executescript(FTS_SCHEMA)

    # 7. Rebuild all FTS indexes from current data
    rebuild_fts(conn)

    # 8. Verify FK integrity
    fk_errors = conn.execute("PRAGMA foreign_key_check").fetchall()
    if fk_errors:
        raise sqlite3.IntegrityError(
            f"foreign_key_check failed after source_records rebuild: {fk_errors}"
        )
