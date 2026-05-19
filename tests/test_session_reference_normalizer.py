from __future__ import annotations

import os
import sqlite3
import tempfile
import unittest
from pathlib import Path

import scripts.db_base as db_base


class SessionReferenceNormalizerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.orig_db_path = os.environ.get("CONTROL_TOWER_DB_PATH")
        os.environ["CONTROL_TOWER_DB_PATH"] = str(Path(self.temp_dir.name) / "control_tower.db")
        db_base.init_db()

    def tearDown(self) -> None:
        if self.orig_db_path is None:
            os.environ.pop("CONTROL_TOWER_DB_PATH", None)
        else:
            os.environ["CONTROL_TOWER_DB_PATH"] = self.orig_db_path
        self.temp_dir.cleanup()

    def test_blank_and_placeholder_values_return_none(self) -> None:
        with db_base.connect() as conn:
            self.assertIsNone(db_base.normalize_existing_session_id(conn, None))
            self.assertIsNone(db_base.normalize_existing_session_id(conn, ""))
            self.assertIsNone(db_base.normalize_existing_session_id(conn, "   "))
            self.assertIsNone(db_base.normalize_existing_session_id(conn, "_"))

    def test_missing_session_returns_none(self) -> None:
        with db_base.connect() as conn:
            self.assertIsNone(db_base.normalize_existing_session_id(conn, "missing-session"))

    def test_existing_session_returns_trimmed_session_id(self) -> None:
        with db_base.connect() as conn:
            conn.execute(
                """INSERT INTO sessions
                   (id, agent_name, source_type, started_at, status)
                   VALUES (?, 'agent', 'test', '2026-01-01', 'active')""",
                ("sess-1",),
            )
            self.assertEqual(
                db_base.normalize_existing_session_id(conn, " sess-1 "),
                "sess-1",
            )


if __name__ == "__main__":
    unittest.main()
