"""Tests for external_inbox session foreign-key migration."""

from __future__ import annotations

import os
import sqlite3
import tempfile
import unittest
from pathlib import Path

import scripts.db_base as db_base


class ExternalInboxSessionFKMigrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.data_dir = self.root / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.orig_env = {
            "CONTROL_TOWER_DATA_DIR": os.environ.get("CONTROL_TOWER_DATA_DIR"),
            "CONTROL_TOWER_DB_PATH": os.environ.get("CONTROL_TOWER_DB_PATH"),
        }
        os.environ["CONTROL_TOWER_DATA_DIR"] = str(self.data_dir)
        os.environ["CONTROL_TOWER_DB_PATH"] = str(self.data_dir / "control_tower.db")

        self.orig_data_dir = db_base.DATA_DIR
        self.orig_db_path = db_base.DB_PATH
        db_base.DATA_DIR = self.data_dir
        db_base.DB_PATH = self.data_dir / "control_tower.db"

    def tearDown(self) -> None:
        db_base.DATA_DIR = self.orig_data_dir
        db_base.DB_PATH = self.orig_db_path
        for key, value in self.orig_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        self.temp_dir.cleanup()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.data_dir / "control_tower.db"), timeout=10)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _insert_session(self, conn: sqlite3.Connection, session_id: str = "sess-1") -> None:
        conn.execute(
            """INSERT INTO sessions
               (id, agent_name, source_type, started_at, status)
               VALUES (?, 'agent', 'test', '2026-01-01', 'active')""",
            (session_id,),
        )

    def _insert_inbox_item(
        self,
        conn: sqlite3.Connection,
        source_id: str,
        external_message_id: str,
        session_id: str | None = None,
    ) -> None:
        conn.execute(
            """INSERT INTO external_inbox
               (source_type, source_id, external_message_id, raw_content, imported_at, status, session_id)
               VALUES ('telegram', ?, ?, 'Content', '2026-01-01', 'new', ?)""",
            (source_id, external_message_id, session_id),
        )

    def test_schema_migrations_records_v10(self) -> None:
        db_base.init_db()
        conn = self._connect()
        try:
            versions = conn.execute(
                "SELECT version, name FROM schema_migrations ORDER BY version"
            ).fetchall()
            result = {int(r["version"]): r["name"] for r in versions}
            self.assertEqual(result[10], "external-inbox-session-fk")
            self.assertGreaterEqual(max(result), 10)
        finally:
            conn.close()

    def test_foreign_key_list_has_session_fk(self) -> None:
        db_base.init_db()
        conn = self._connect()
        try:
            fk_list = conn.execute("PRAGMA foreign_key_list(external_inbox)").fetchall()
            actual = {(r[2], r[3]) for r in fk_list}
            self.assertIn(("sessions", "session_id"), actual)
            for row in fk_list:
                if (row[2], row[3]) == ("sessions", "session_id"):
                    self.assertEqual(row[6], "SET NULL")
        finally:
            conn.close()

    def test_invalid_session_reference_raises(self) -> None:
        db_base.init_db()
        conn = self._connect()
        try:
            with self.assertRaises(sqlite3.IntegrityError):
                self._insert_inbox_item(conn, "s1", "bad-session", "missing-session")
                conn.commit()
            conn.rollback()
        finally:
            conn.close()

    def test_valid_session_reference_succeeds(self) -> None:
        db_base.init_db()
        conn = self._connect()
        try:
            self._insert_session(conn, "sess-valid")
            self._insert_inbox_item(conn, "s1", "valid-session", "sess-valid")
            conn.commit()
            row = conn.execute(
                "SELECT session_id FROM external_inbox WHERE source_id = 's1' AND external_message_id = 'valid-session'"
            ).fetchone()
            self.assertEqual(row["session_id"], "sess-valid")
        finally:
            conn.close()

    def test_delete_session_sets_inbox_session_null(self) -> None:
        db_base.init_db()
        conn = self._connect()
        try:
            self._insert_session(conn, "sess-del")
            self._insert_inbox_item(conn, "s1", "null-session", "sess-del")
            conn.commit()

            conn.execute("DELETE FROM sessions WHERE id = 'sess-del'")
            conn.commit()

            row = conn.execute(
                "SELECT session_id FROM external_inbox WHERE source_id = 's1' AND external_message_id = 'null-session'"
            ).fetchone()
            self.assertIsNone(row["session_id"])
        finally:
            conn.close()

    def test_unique_source_message_constraint_survives_migration(self) -> None:
        db_base.init_db()
        conn = self._connect()
        try:
            self._insert_inbox_item(conn, "s1", "duplicate")
            conn.commit()
            with self.assertRaises(sqlite3.IntegrityError):
                self._insert_inbox_item(conn, "s1", "duplicate")
                conn.commit()
            conn.rollback()
        finally:
            conn.close()

    def test_init_db_idempotent_for_v10(self) -> None:
        db_base.init_db()
        db_base.init_db()
        conn = self._connect()
        try:
            count = conn.execute(
                "SELECT COUNT(*) as cnt FROM schema_migrations WHERE version = 10"
            ).fetchone()
            self.assertEqual(count["cnt"], 1)
        finally:
            conn.close()

    def test_foreign_key_check_clean(self) -> None:
        db_base.init_db()
        conn = self._connect()
        try:
            errors = conn.execute("PRAGMA foreign_key_check").fetchall()
            self.assertEqual(errors, [])
        finally:
            conn.close()


if __name__ == "__main__":
    unittest.main()
