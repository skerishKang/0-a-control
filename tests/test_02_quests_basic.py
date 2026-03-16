import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import scripts.db_base as db_base
import scripts.db_state as db_state


class QuestsBasicTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.data_dir = self.root / "data"
        self.db_path = self.data_dir / "control_tower.db"
        self.workdiary_dir = self.root / "workdiary"
        (self.workdiary_dir / "demo-project").mkdir(parents=True, exist_ok=True)

        self.original_env = {
            key: os.environ.get(key)
            for key in ("CONTROL_TOWER_DATA_DIR", "CONTROL_TOWER_DB_PATH", "CONTROL_TOWER_WORKDIARY_DIR")
        }
        os.environ["CONTROL_TOWER_DATA_DIR"] = str(self.data_dir)
        os.environ["CONTROL_TOWER_DB_PATH"] = str(self.db_path)
        os.environ["CONTROL_TOWER_WORKDIARY_DIR"] = str(self.workdiary_dir)

        self.original_paths = {
            "db_data_dir": db_base.DATA_DIR,
            "db_db_path": db_base.DB_PATH,
            "db_workdiary_dir": db_base.WORKDIARY_DIR,
            "state_workdiary_dir": db_state.WORKDIARY_DIR,
        }

        db_base.DATA_DIR = self.data_dir
        db_base.DB_PATH = self.db_path
        db_base.WORKDIARY_DIR = self.workdiary_dir
        db_state.WORKDIARY_DIR = self.workdiary_dir
        db_base.init_db()

    def tearDown(self) -> None:
        db_base.DATA_DIR = self.original_paths["db_data_dir"]
        db_base.DB_PATH = self.original_paths["db_db_path"]
        db_base.WORKDIARY_DIR = self.original_paths["db_workdiary_dir"]
        db_state.WORKDIARY_DIR = self.original_paths["state_workdiary_dir"]

        for key, value in self.original_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

        self.temp_dir.cleanup()

    def test_db_connectivity_and_quests_table(self) -> None:
        with db_base.connect() as conn:
            row = conn.execute("SELECT COUNT(*) as count FROM quests").fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row["count"], 0)

    def test_plan_items_table(self) -> None:
        with db_base.connect() as conn:
            row = conn.execute("SELECT COUNT(*) as count FROM plan_items").fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row["count"], 0)

    def test_refresh_current_state_keeps_today_mission_when_pending_quest_exists(self) -> None:
        with db_base.connect() as conn:
            conn.execute(
                """
                INSERT INTO plan_items (id, bucket, title, status, priority_score, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "today-plan-1",
                    "today",
                    "오늘 플랜",
                    "done",
                    100,
                    "2026-03-10T00:00:00+00:00",
                    "2026-03-10T00:00:00+00:00",
                ),
            )
            conn.execute(
                """
                INSERT INTO quests (id, title, status, plan_item_id, completion_criteria, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "quest-1",
                    "보류 중이 아닌 판정 대기 퀘스트",
                    "pending",
                    "today-plan-1",
                    "완료 기준",
                    "2026-03-10T00:00:00+00:00",
                    "2026-03-10T00:00:00+00:00",
                ),
            )

            state = db_state.refresh_current_state(conn)

        self.assertEqual(state["main_mission"]["id"], "today-plan-1")
        self.assertEqual(state["current_quest"]["id"], "quest-1")


if __name__ == "__main__":
    unittest.main()
