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


def _drop_index_if_exists(conn: sqlite3.Connection, name: str) -> None:
    conn.execute(f"DROP INDEX IF EXISTS {name}")


def _drop_fts_triggers(conn: sqlite3.Connection, table: str) -> None:
    for suffix in ("ai", "au", "ad"):
        conn.execute(f"DROP TRIGGER IF EXISTS {table}_{suffix}")


def _source_records_columns() -> list[str]:
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


def _quests_columns() -> list[str]:
    return [
        "id",
        "plan_item_id",
        "parent_quest_id",
        "title",
        "why_now",
        "completion_criteria",
        "status",
        "verdict_reason",
        "restart_point",
        "next_quest_hint",
        "created_at",
        "updated_at",
        "metadata_json",
    ]


def _decision_records_columns() -> list[str]:
    return [
        "id",
        "decision_type",
        "title",
        "reason",
        "impact_summary",
        "related_plan_item_id",
        "related_quest_id",
        "related_session_id",
        "created_at",
        "metadata_json",
    ]


def _brief_records_columns() -> list[str]:
    return [
        "id",
        "brief_type",
        "title",
        "content_md",
        "related_plan_item_id",
        "related_quest_id",
        "related_session_id",
        "created_at",
        "metadata_json",
    ]


def apply_source_records_session_fk(conn: sqlite3.Connection) -> None:
    """Rebuild source_records with ``session_id -> sessions(id) ON DELETE SET NULL``."""
    if not _table_exists(conn, "source_records") or not _table_exists(
        conn, "sessions"
    ):
        return

    if _has_fk_on_column(conn, "source_records", "session_id", "sessions"):
        return

    columns = _source_records_columns()
    col_sql = ", ".join(columns)

    _drop_fts_triggers(conn, "source_records")
    conn.execute("ALTER TABLE source_records RENAME TO source_records_old")

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

    conn.execute(
        f"INSERT INTO source_records ({col_sql}) "
        f"SELECT {col_sql} FROM source_records_old"
    )
    conn.execute("DROP TABLE source_records_old")
    conn.executescript(INDEXES)
    conn.executescript(FTS_SCHEMA)
    rebuild_fts(conn)

    fk_errors = conn.execute("PRAGMA foreign_key_check").fetchall()
    if fk_errors:
        raise sqlite3.IntegrityError(
            f"foreign_key_check failed after source_records rebuild: {fk_errors}"
        )


def apply_quests_plan_parent_fks(conn: sqlite3.Connection) -> None:
    """Rebuild quests with plan and parent quest foreign keys."""
    if not _table_exists(conn, "quests") or not _table_exists(conn, "plan_items"):
        return

    has_plan_fk = _has_fk_on_column(conn, "quests", "plan_item_id", "plan_items")
    has_parent_fk = _has_fk_on_column(conn, "quests", "parent_quest_id", "quests")
    if has_plan_fk and has_parent_fk:
        return

    columns = _quests_columns()
    col_sql = ", ".join(columns)

    _drop_index_if_exists(conn, "idx_quests_status_updated")
    conn.execute("ALTER TABLE quests RENAME TO quests_old")

    conn.execute(
        """
        CREATE TABLE quests (
            id TEXT PRIMARY KEY,
            plan_item_id TEXT
                REFERENCES plan_items(id) ON DELETE SET NULL,
            parent_quest_id TEXT
                REFERENCES quests(id) ON DELETE SET NULL,
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
        )
        """
    )

    conn.execute(f"INSERT INTO quests ({col_sql}) SELECT {col_sql} FROM quests_old")
    conn.execute("DROP TABLE quests_old")
    conn.executescript(INDEXES)

    fk_errors = conn.execute("PRAGMA foreign_key_check").fetchall()
    if fk_errors:
        raise sqlite3.IntegrityError(
            f"foreign_key_check failed after quests rebuild: {fk_errors}"
        )


def apply_decision_records_reference_fks(conn: sqlite3.Connection) -> None:
    """Rebuild decision_records with plan and quest reference FKs.

    ``related_session_id`` is intentionally left unconstrained in this slice
    because legacy report imports may pass placeholder or external session ids.
    """
    required_tables = ("decision_records", "plan_items", "quests")
    if not all(_table_exists(conn, table) for table in required_tables):
        return

    has_plan_fk = _has_fk_on_column(
        conn, "decision_records", "related_plan_item_id", "plan_items"
    )
    has_quest_fk = _has_fk_on_column(
        conn, "decision_records", "related_quest_id", "quests"
    )
    if has_plan_fk and has_quest_fk:
        return

    columns = _decision_records_columns()
    col_sql = ", ".join(columns)

    _drop_fts_triggers(conn, "decision_records")
    conn.execute("ALTER TABLE decision_records RENAME TO decision_records_old")

    conn.execute(
        """
        CREATE TABLE decision_records (
            id TEXT PRIMARY KEY,
            decision_type TEXT NOT NULL,
            title TEXT NOT NULL,
            reason TEXT,
            impact_summary TEXT,
            related_plan_item_id TEXT
                REFERENCES plan_items(id) ON DELETE SET NULL,
            related_quest_id TEXT
                REFERENCES quests(id) ON DELETE SET NULL,
            related_session_id TEXT,
            created_at TEXT NOT NULL,
            metadata_json TEXT
        )
        """
    )

    conn.execute(
        f"INSERT INTO decision_records ({col_sql}) "
        f"SELECT {col_sql} FROM decision_records_old"
    )
    conn.execute("DROP TABLE decision_records_old")
    conn.executescript(INDEXES)
    conn.executescript(FTS_SCHEMA)
    rebuild_fts(conn)

    fk_errors = conn.execute("PRAGMA foreign_key_check").fetchall()
    if fk_errors:
        raise sqlite3.IntegrityError(
            f"foreign_key_check failed after decision_records rebuild: {fk_errors}"
        )


def apply_brief_records_reference_fks(conn: sqlite3.Connection) -> None:
    """Rebuild brief_records with plan and quest reference FKs.

    ``related_session_id`` is intentionally left unconstrained in this slice
    because legacy brief/import paths may pass placeholder or external session ids.
    """
    required_tables = ("brief_records", "plan_items", "quests")
    if not all(_table_exists(conn, table) for table in required_tables):
        return

    has_plan_fk = _has_fk_on_column(
        conn, "brief_records", "related_plan_item_id", "plan_items"
    )
    has_quest_fk = _has_fk_on_column(
        conn, "brief_records", "related_quest_id", "quests"
    )
    if has_plan_fk and has_quest_fk:
        return

    columns = _brief_records_columns()
    col_sql = ", ".join(columns)

    _drop_fts_triggers(conn, "brief_records")
    conn.execute("ALTER TABLE brief_records RENAME TO brief_records_old")

    conn.execute(
        """
        CREATE TABLE brief_records (
            id TEXT PRIMARY KEY,
            brief_type TEXT NOT NULL,
            title TEXT NOT NULL,
            content_md TEXT NOT NULL,
            related_plan_item_id TEXT
                REFERENCES plan_items(id) ON DELETE SET NULL,
            related_quest_id TEXT
                REFERENCES quests(id) ON DELETE SET NULL,
            related_session_id TEXT,
            created_at TEXT NOT NULL,
            metadata_json TEXT
        )
        """
    )

    conn.execute(
        f"INSERT INTO brief_records ({col_sql}) "
        f"SELECT {col_sql} FROM brief_records_old"
    )
    conn.execute("DROP TABLE brief_records_old")
    conn.executescript(INDEXES)
    conn.executescript(FTS_SCHEMA)
    rebuild_fts(conn)

    fk_errors = conn.execute("PRAGMA foreign_key_check").fetchall()
    if fk_errors:
        raise sqlite3.IntegrityError(
            f"foreign_key_check failed after brief_records rebuild: {fk_errors}"
        )
