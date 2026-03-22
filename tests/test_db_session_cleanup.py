from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

import scripts.db_base as db_base
from scripts.db_sessions import close_latest_active_session_for_agent, start_session


class SessionCleanupTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.data_dir = self.root / "data"
        self.workdiary_dir = self.root / "workdiary"
        self.workdiary_dir.mkdir(parents=True, exist_ok=True)

        self.orig_env = {
            "CONTROL_TOWER_DATA_DIR": os.environ.get("CONTROL_TOWER_DATA_DIR"),
            "CONTROL_TOWER_DB_PATH": os.environ.get("CONTROL_TOWER_DB_PATH"),
            "CONTROL_TOWER_WORKDIARY_DIR": os.environ.get("CONTROL_TOWER_WORKDIARY_DIR"),
        }
        os.environ["CONTROL_TOWER_DATA_DIR"] = str(self.data_dir)
        os.environ["CONTROL_TOWER_DB_PATH"] = str(self.data_dir / "control_tower.db")
        os.environ["CONTROL_TOWER_WORKDIARY_DIR"] = str(self.workdiary_dir)

        self.orig_data_dir = db_base.DATA_DIR
        self.orig_db_path = db_base.DB_PATH
        self.orig_workdiary_dir = db_base.WORKDIARY_DIR

        db_base.DATA_DIR = self.data_dir
        db_base.DB_PATH = self.data_dir / "control_tower.db"
        db_base.WORKDIARY_DIR = self.workdiary_dir
        db_base.init_db()

    def tearDown(self) -> None:
        db_base.DATA_DIR = self.orig_data_dir
        db_base.DB_PATH = self.orig_db_path
        db_base.WORKDIARY_DIR = self.orig_workdiary_dir
        for key, value in self.orig_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        self.temp_dir.cleanup()

    def test_close_latest_active_session_for_agent_closes_most_recent(self) -> None:
        older = start_session(
            agent_name="codex",
            source_type="cmd",
            project_key="0-a-control",
            working_dir=str(self.workdiary_dir),
            title="older",
        )
        newer = start_session(
            agent_name="codex",
            source_type="cmd",
            project_key="0-a-control",
            working_dir=str(self.workdiary_dir),
            title="newer",
        )

        with db_base.connect() as conn:
            conn.execute(
                "UPDATE sessions SET started_at = ? WHERE id = ?",
                ("2000-01-01T00:00:00+00:00", older["id"]),
            )

        result = close_latest_active_session_for_agent("codex")
        self.assertEqual(result["id"], newer["id"])
        self.assertEqual(result["status"], "closed")
        self.assertIsNotNone(result["ended_at"])

        with db_base.connect() as conn:
            older_row = conn.execute("SELECT status FROM sessions WHERE id = ?", (older["id"],)).fetchone()
            newer_row = conn.execute("SELECT status, metadata_json FROM sessions WHERE id = ?", (newer["id"],)).fetchone()

        self.assertEqual(older_row["status"], "active")
        self.assertEqual(newer_row["status"], "closed")
        self.assertIn("dashboard_agent_status", newer_row["metadata_json"])


if __name__ == "__main__":
    unittest.main()
