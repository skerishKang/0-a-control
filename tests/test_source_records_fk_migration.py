"""Tests for migration v3: source_records.session_id -> sessions(id) ON DELETE SET NULL."""

from __future__ import annotations

import os
import sqlite3
import tempfile
import unittest
from pathlib import Path

import scripts.db_base as db_base


class SourceRecordsFKMigrationTests(unittest.TestCase):
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

    # ── tests ───────────────────────────────────────────────────────

    def test_schema_migrations_records_v1_v2_v3(self) -> None:
        db_base.init_db()
        conn = self._connect()
        try:
            versions = conn.execute(
                "SELECT version, name FROM schema_migrations ORDER BY version"
            ).fetchall()
            result = {int(r["version"]): r["name"] for r in versions}
            self.assertIn(1, result)
            self.assertIn(2, result)
            self.assertIn(3, result)
            self.assertEqual(result[3], "source-records-session-fk")
        finally:
            conn.close()

    def test_foreign_key_list_has_session_id(self) -> None:
        db_base.init_db()
        conn = self._connect()
        try:
            fk_list = conn.execute("PRAGMA foreign_key_list(source_records)").fetchall()
            session_fk = [
                r for r in fk_list if r[2] == "sessions" and r[3] == "session_id"
            ]
            self.assertEqual(len(session_fk), 1)
            self.assertEqual(session_fk[0][6], "SET NULL")  # on_delete
        finally:
            conn.close()

    def test_insert_invalid_session_id_raises(self) -> None:
        db_base.init_db()
        conn = self._connect()
        try:
            with self.assertRaises(sqlite3.IntegrityError):
                conn.execute(
                    """INSERT INTO source_records
                       (id, source_type, source_name, session_id, content, created_at)
                       VALUES ('sr-bad', 'test', 'test', 'nonexistent-session', 'x', '2026-01-01')"""
                )
                conn.commit()
        finally:
            conn.close()

    def test_insert_valid_session_id_succeeds(self) -> None:
        db_base.init_db()
        conn = self._connect()
        try:
            conn.execute(
                """INSERT INTO sessions
                   (id, agent_name, source_type, started_at, status)
                   VALUES ('sess-1', 'test-agent', 'test', '2026-01-01', 'active')"""
            )
            conn.execute(
                """INSERT INTO source_records
                   (id, source_type, source_name, session_id, content, created_at)
                   VALUES ('sr-good', 'test', 'test', 'sess-1', 'hello', '2026-01-01')"""
            )
            conn.commit()
            row = conn.execute(
                "SELECT session_id FROM source_records WHERE id = 'sr-good'"
            ).fetchone()
            self.assertEqual(row["session_id"], "sess-1")
        finally:
            conn.close()

    def test_delete_session_sets_null(self) -> None:
        db_base.init_db()
        conn = self._connect()
        try:
            conn.execute(
                """INSERT INTO sessions
                   (id, agent_name, source_type, started_at, status)
                   VALUES ('sess-del', 'test-agent', 'test', '2026-01-01', 'active')"""
            )
            conn.execute(
                """INSERT INTO source_records
                   (id, source_type, source_name, session_id, content, created_at)
                   VALUES ('sr-cascade', 'test', 'test', 'sess-del', 'hello', '2026-01-01')"""
            )
            conn.commit()

            conn.execute("DELETE FROM sessions WHERE id = 'sess-del'")
            conn.commit()

            row = conn.execute(
                "SELECT session_id FROM source_records WHERE id = 'sr-cascade'"
            ).fetchone()
            self.assertIsNone(row["session_id"])
        finally:
            conn.close()

    def test_init_db_idempotent(self) -> None:
        db_base.init_db()
        db_base.init_db()
        conn = self._connect()
        try:
            count = conn.execute(
                "SELECT COUNT(*) as cnt FROM schema_migrations WHERE version = 3"
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
