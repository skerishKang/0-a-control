import os
import sys
import tempfile
import json
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def _import_modules():
    global connect, init_db, get_current_state, report_quest_progress, refresh_current_state, REPORTS_DIR, VERDICTS_DIR, import_verdicts
    global db_base, db_state, file_queue, report_export, verdict_import
    from scripts import db_base, db_state, file_queue, report_export, verdict_import
    from scripts.db_base import connect, init_db
    from scripts.db_ops import get_current_state, report_quest_progress
    from scripts.db_state import refresh_current_state
    from scripts.file_queue import REPORTS_DIR, VERDICTS_DIR
    from scripts.verdict_import import import_verdicts


def _set_env_for_tests(temp_dir: str) -> dict[str, str | None]:
    overrides = {
        "CONTROL_TOWER_DATA_DIR": Path(temp_dir) / "data",
        "CONTROL_TOWER_DB_PATH": Path(temp_dir) / "data" / "control_tower.db",
        "CONTROL_TOWER_QUEUE_DIR": Path(temp_dir) / "data" / "queue",
    }
    previous = {}
    for key, path in overrides.items():
        previous[key] = os.environ.get(key)
        os.environ[key] = str(path)
    (Path(os.environ["CONTROL_TOWER_QUEUE_DIR"]) / "reports").mkdir(parents=True, exist_ok=True)
    (Path(os.environ["CONTROL_TOWER_QUEUE_DIR"]) / "verdicts").mkdir(parents=True, exist_ok=True)
    return previous


class PipelineFlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.previous_env = _set_env_for_tests(cls.temp_dir.name)
        _import_modules()
        init_db()

    @classmethod
    def tearDownClass(cls):
        for key, value in cls.previous_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        cls.temp_dir.cleanup()

    def setUp(self) -> None:
        self.root = Path(self.temp_dir.name)
        self.data_dir = self.root / "data"
        self.db_path = self.data_dir / "control_tower.db"
        self.queue_dir = self.data_dir / "queue"
        self.workdiary_dir = self.root / "workdiary"
        (self.workdiary_dir / "demo-project" / "scripts").mkdir(parents=True, exist_ok=True)
        (self.workdiary_dir / "demo-project" / "README.md").write_text("# demo\n", encoding="utf-8")

        self.original_env = {
            key: os.environ.get(key)
            for key in (
                "CONTROL_TOWER_DATA_DIR",
                "CONTROL_TOWER_DB_PATH",
                "CONTROL_TOWER_QUEUE_DIR",
                "CONTROL_TOWER_WORKDIARY_DIR",
            )
        }
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
            "report_export_reports_dir": report_export.REPORTS_DIR,
            "verdict_import_reports_dir": verdict_import.REPORTS_DIR,
            "verdict_import_verdicts_dir": verdict_import.VERDICTS_DIR,
        }

        db_base.DATA_DIR = self.data_dir
        db_base.DB_PATH = self.db_path
        db_base.WORKDIARY_DIR = self.workdiary_dir
        db_state.WORKDIARY_DIR = self.workdiary_dir
        file_queue.QUEUE_DIR = self.queue_dir
        file_queue.REPORTS_DIR = self.queue_dir / "reports"
        file_queue.VERDICTS_DIR = self.queue_dir / "verdicts"
        file_queue.PROCESSED_DIR = self.queue_dir / "processed"
        report_export.REPORTS_DIR = file_queue.REPORTS_DIR
        verdict_import.REPORTS_DIR = file_queue.REPORTS_DIR
        verdict_import.VERDICTS_DIR = file_queue.VERDICTS_DIR

        with connect() as conn:
            refresh_current_state(conn)
            conn.execute(
                """
                INSERT INTO plan_items (id, bucket, title, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                ("test-plan-id", "today", "Test Plan", "active", "2026-03-09T00:00:00Z", "2026-03-09T00:00:00Z"),
            )
            conn.execute(
                """
                INSERT INTO quests (id, title, status, plan_item_id, completion_criteria, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "test-quest-id",
                    "Test Quest",
                    "active",
                    "test-plan-id",
                    "Test Criteria",
                    "2026-03-09T00:00:00Z",
                    "2026-03-09T00:00:00Z",
                ),
            )
        self.quest_id = "test-quest-id"

    def tearDown(self) -> None:
        db_base.DATA_DIR = self.original_paths["db_data_dir"]
        db_base.DB_PATH = self.original_paths["db_db_path"]
        db_base.WORKDIARY_DIR = self.original_paths["db_workdiary_dir"]
        db_state.WORKDIARY_DIR = self.original_paths["state_workdiary_dir"]
        file_queue.QUEUE_DIR = self.original_paths["queue_dir"]
        file_queue.REPORTS_DIR = self.original_paths["reports_dir"]
        file_queue.VERDICTS_DIR = self.original_paths["verdicts_dir"]
        file_queue.PROCESSED_DIR = self.original_paths["processed_dir"]
        report_export.REPORTS_DIR = self.original_paths["report_export_reports_dir"]
        verdict_import.REPORTS_DIR = self.original_paths["verdict_import_reports_dir"]
        verdict_import.VERDICTS_DIR = self.original_paths["verdict_import_verdicts_dir"]

        for key, value in self.original_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    def test_full_pipeline_flow(self) -> None:
        report_quest_progress(
            quest_id=self.quest_id,
            work_summary="Automated test summary",
            remaining_work="None",
            blocker="None",
            self_assessment="done",
            session_id="",
        )

        state_pending = get_current_state()
        self.assertTrue(
            state_pending.get("quest_status_summary", {}).get("is_pending"),
            "Quest should be in pending state after report",
        )

        reports = sorted(file_queue.REPORTS_DIR.glob("*.report.json"))
        self.assertTrue(reports, "Report file should have been created")
        latest_report = reports[-1]
        report_data = json.loads(latest_report.read_text(encoding="utf-8"))
        report_id = report_data.get("report_id")
        self.assertIsNotNone(report_id)

        verdict_path = file_queue.VERDICTS_DIR / f"{report_id}.verdict.json"
        dummy_verdict = {
            "schema_version": "1.0",
            "report_ref": report_id,
            "quest_id": self.quest_id,
            "verdict": {
                "status": "done",
                "reason": "Automated test success",
                "restart_point": "Next Step",
                "next_hint": "Finish",
                "plan_impact": {
                    "today": "Done",
                    "short_term": "--",
                    "long_term": "--",
                    "recurring": "--",
                    "dated": "--",
                },
                "confidence": 1.0,
            },
            "judge": {"provider": "test-suite"},
        }
        verdict_path.write_text(json.dumps(dummy_verdict, ensure_ascii=False, indent=2), encoding="utf-8")

        import_verdicts()

        state_final = get_current_state()
        self.assertFalse(
            state_final.get("quest_status_summary", {}).get("is_pending"),
            "Quest should no longer be pending",
        )

        with db_base.connect() as conn:
            q_status = conn.execute("SELECT status FROM quests WHERE id = ?", (self.quest_id,)).fetchone()["status"]
        self.assertEqual(q_status, "done", "Quest should be marked as done in DB")
        self.assertFalse(list(file_queue.VERDICTS_DIR.glob("*.json")), "Verdict queue should be drained")


if __name__ == "__main__":
    unittest.main()
