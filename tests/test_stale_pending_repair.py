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
from scripts.repair_stale_pending import apply_repair, find_repair_candidates


class StalePendingRepairTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.data_dir = self.root / "data"
        self.db_path = self.data_dir / "control_tower.db"
        self.workdiary_dir = self.root / "workdiary"
        self.workdiary_dir.mkdir(parents=True, exist_ok=True)

        self.original_env = {
            key: os.environ.get(key)
            for key in (
                "CONTROL_TOWER_DATA_DIR",
                "CONTROL_TOWER_DB_PATH",
                "CONTROL_TOWER_WORKDIARY_DIR",
            )
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

    def test_repair_reverts_stale_pending_to_last_final_verdict(self) -> None:
        old_verdict_time = (datetime.now(timezone.utc) - timedelta(minutes=30)).replace(microsecond=0).isoformat()
        old_report_time = (datetime.now(timezone.utc) - timedelta(minutes=20)).replace(microsecond=0).isoformat()
        metadata = {
            "report": {
                "work_summary": "new report",
                "remaining_work": "none",
                "blocker": "",
                "self_assessment": "done",
                "reported_at": old_report_time,
            },
            "latest_report": {
                "report_ref": "new-report-ref",
                "file_name": "new-report-ref.report.json",
                "reported_at": old_report_time,
            },
            "preliminary_ai_verdict": {
                "verdict": "partial",
                "reason": "heuristic pending",
                "provider": "heuristic",
                "is_preliminary": True,
            },
            "ai_verdict": {
                "verdict": "done",
                "reason": "older final verdict",
                "restart_point": "resume here",
                "next_hint": "next quest",
                "provider": "test",
                "updated_at": old_verdict_time,
                "report_ref": "older-report-ref",
                "is_preliminary": False,
            },
        }

        with db_base.connect() as conn:
            conn.execute(
                """
                INSERT INTO plan_items (id, bucket, title, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                ("plan-1", "today", "Plan", "done", old_verdict_time, old_verdict_time),
            )
            conn.execute(
                """
                INSERT INTO quests (id, title, status, plan_item_id, completion_criteria, verdict_reason, restart_point, next_quest_hint, created_at, updated_at, metadata_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "quest-1",
                    "Quest",
                    "pending",
                    "plan-1",
                    "criteria",
                    "",
                    "",
                    "",
                    old_verdict_time,
                    old_report_time,
                    json.dumps(metadata, ensure_ascii=False),
                ),
            )

        candidates = find_repair_candidates(stale_minutes=10)
        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0]["quest_id"], "quest-1")

        repaired = apply_repair(stale_minutes=10)
        self.assertEqual(len(repaired), 1)

        with db_base.connect() as conn:
            quest = conn.execute("SELECT * FROM quests WHERE id = ?", ("quest-1",)).fetchone()
            plan = conn.execute("SELECT * FROM plan_items WHERE id = ?", ("plan-1",)).fetchone()
            state = conn.execute(
                "SELECT state_value FROM current_state WHERE state_key = 'quest_status_summary'"
            ).fetchone()

        meta = json.loads(quest["metadata_json"])
        self.assertEqual(quest["status"], "done")
        self.assertEqual(plan["status"], "done")
        self.assertNotIn("report", meta)
        self.assertNotIn("latest_report", meta)
        self.assertNotIn("preliminary_ai_verdict", meta)
        self.assertIn("stale_report_archive", meta)
        self.assertIn("stale_pending_recovery", meta)

        summary = json.loads(state["state_value"])
        self.assertFalse(summary.get("is_pending"))


if __name__ == "__main__":
    unittest.main()
