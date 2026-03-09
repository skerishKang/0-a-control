import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import scripts.db_base as db_base
import scripts.db_state as db_state
import scripts.file_queue as file_queue


class StaleVerdictTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.data_dir = self.root / "data"
        self.db_path = self.data_dir / "control_tower.db"
        self.queue_dir = self.data_dir / "queue"
        self.workdiary_dir = self.root / "workdiary"
        (self.workdiary_dir / "demo-project").mkdir(parents=True, exist_ok=True)

        self.original_env = {
            key: os.environ.get(key)
            for key in (
                "CONTROL_TOWER_DATA_DIR",
                "CONTROL_TOWER_DB_PATH",
                "CONTROL_TOWER_QUEUE_DIR",
                "CONTROL_TOWER_WORKDIARY_DIR",
            )
        }
        os.environ["CONTROL_TOWER_DATA_DIR"] = str(self.data_dir)
        os.environ["CONTROL_TOWER_DB_PATH"] = str(self.db_path)
        os.environ["CONTROL_TOWER_QUEUE_DIR"] = str(self.queue_dir)
        os.environ["CONTROL_TOWER_WORKDIARY_DIR"] = str(self.workdiary_dir)

        self.original_paths = {
            "db_data_dir": db_base.DATA_DIR,
            "db_db_path": db_base.DB_PATH,
            "db_workdiary_dir": db_base.WORKDIARY_DIR,
            "state_workdiary_dir": db_state.WORKDIARY_DIR,
            "queue_dir": file_queue.QUEUE_DIR,
            "reports_dir": file_queue.REPORTS_DIR,
            "verdicts_dir": file_queue.VERDICTS_DIR,
            "processed_dir": file_queue.PROCESSED_DIR,
        }

        db_base.DATA_DIR = self.data_dir
        db_base.DB_PATH = self.db_path
        db_base.WORKDIARY_DIR = self.workdiary_dir
        db_state.WORKDIARY_DIR = self.workdiary_dir
        file_queue.QUEUE_DIR = self.queue_dir
        file_queue.REPORTS_DIR = self.queue_dir / "reports"
        file_queue.VERDICTS_DIR = self.queue_dir / "verdicts"
        file_queue.PROCESSED_DIR = self.queue_dir / "processed"

        db_base.init_db()

    def tearDown(self) -> None:
        db_base.DATA_DIR = self.original_paths["db_data_dir"]
        db_base.DB_PATH = self.original_paths["db_db_path"]
        db_base.WORKDIARY_DIR = self.original_paths["db_workdiary_dir"]
        db_state.WORKDIARY_DIR = self.original_paths["state_workdiary_dir"]
        file_queue.QUEUE_DIR = self.original_paths["queue_dir"]
        file_queue.REPORTS_DIR = self.original_paths["reports_dir"]
        file_queue.VERDICTS_DIR = self.original_paths["verdicts_dir"]
        file_queue.PROCESSED_DIR = self.original_paths["processed_dir"]

        for key, value in self.original_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

        self.temp_dir.cleanup()

    def test_stale_verdict_detection(self) -> None:
        old_time = (datetime.now(timezone.utc) - timedelta(minutes=15)).isoformat()
        metadata = json.dumps({"report": {"reported_at": old_time}}, ensure_ascii=False)

        with db_base.connect() as conn:
            conn.execute(
                """
                INSERT INTO plan_items (id, bucket, title, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                ("test-plan-id", "today", "Test Plan", "active", old_time, old_time),
            )
            conn.execute(
                """
                INSERT INTO quests (id, title, status, plan_item_id, completion_criteria, created_at, updated_at, metadata_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "stale-quest-id",
                    "Stale Quest",
                    "pending",
                    "test-plan-id",
                    "Test Criteria",
                    old_time,
                    old_time,
                    metadata,
                ),
            )
            db_state.refresh_current_state(conn)
            state = conn.execute(
                "SELECT state_value FROM current_state WHERE state_key = 'quest_status_summary'"
            ).fetchone()

        summary = json.loads(state["state_value"])
        self.assertTrue(summary.get("is_pending"))
        self.assertTrue(summary.get("is_stale"), "Quest should be detected as stale")
        self.assertIn("지연되고 있습니다", summary.get("stale_reason", ""))


if __name__ == "__main__":
    unittest.main()
