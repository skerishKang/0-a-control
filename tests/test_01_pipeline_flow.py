import os
import tempfile
import json
import shutil
import unittest
from pathlib import Path
import sys

# Isolation: Set env vars BEFORE any imports
temp_dir = tempfile.mkdtemp()
os.environ["CONTROL_TOWER_DATA_DIR"] = str(Path(temp_dir) / "data")
os.environ["CONTROL_TOWER_DB_PATH"] = str(Path(temp_dir) / "data" / "control_tower.db")
os.environ["CONTROL_TOWER_QUEUE_DIR"] = str(Path(temp_dir) / "data" / "queue")

# Add ROOT_DIR to path
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.db_base import connect, init_db
from scripts.db_ops import get_current_state, report_quest_progress
from scripts.db_state import refresh_current_state
from scripts.file_queue import REPORTS_DIR, VERDICTS_DIR
from scripts.verdict_import import import_verdicts

class PipelineFlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(temp_dir)

    def setUp(self):
        from scripts.db_base import DB_PATH
        print(f"DEBUG: Using DB: {DB_PATH}")
        with connect() as conn:
            refresh_current_state(conn)
            # Create a dummy quest
            conn.execute("""
                INSERT OR REPLACE INTO quests (id, title, status, plan_item_id, completion_criteria, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, ("test-quest-id", "Test Quest", "active", None, "Test Criteria", "2026-03-09T00:00:00Z", "2026-03-09T00:00:00Z"))
            conn.commit()
            self.quest_id = "test-quest-id"
            
            # Debug: Verify
            row = conn.execute("SELECT COUNT(*) as count FROM quests").fetchone()
            print(f"DEBUG: Quest count in DB: {row['count']}")

    def test_full_pipeline_flow(self):
        # 1. Start with an active quest (or force it)
        with connect() as conn:
            conn.execute("UPDATE quests SET status = 'active' WHERE id = ?", (self.quest_id,))
            conn.commit()
        
        # 2. Generate report
        print(f"DEBUG: quest_id in test: {self.quest_id}")
        report_quest_progress(
            quest_id=self.quest_id,
            work_summary="Automated test summary",
            remaining_work="None",
            blocker="None",
            self_assessment="done",
            session_id=""
        )
        
        # Verify status became 'pending'
        state_pending = get_current_state()
        quest_status = state_pending.get("quest_status_summary", {}).get("is_pending")
        self.assertTrue(quest_status, "Quest should be in pending state after report")
        
        # 3. Check for report file
        reports = list(REPORTS_DIR.glob("*.report.json"))
        self.assertTrue(len(reports) > 0, "Report file should have been created")
        
        reports.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        latest_report = reports[0]
        with open(latest_report, "r", encoding="utf-8") as f:
            report_data = json.load(f)
        
        report_id = report_data.get('report_id')
        self.assertIsNotNone(report_id)
        
        # 4. Mock external verdict
        verdict_path = VERDICTS_DIR / f"{report_id}.verdict.json"
        dummy_verdict = {
            "schema_version": "1.0",
            "report_ref": report_id,
            "verdict": {
                "status": "done",
                "reason": "Automated test success",
                "restart_point": "Next Step",
                "next_hint": "Finish",
                "plan_impact": {"today": "Done", "short_term": "--", "long_term": "--", "recurring": "--", "dated": "--"},
                "confidence": 1.0
            },
            "judge": {"provider": "test-suite"}
        }
        with open(verdict_path, "w", encoding="utf-8") as f:
            json.dump(dummy_verdict, f, ensure_ascii=False, indent=2)
            
        # 5. Ingest verdict
        import_verdicts()
        
        # 6. Verify final state
        state_final = get_current_state()
        self.assertFalse(state_final.get("quest_status_summary", {}).get("is_pending"), "Quest should no longer be pending")
        
        with connect() as conn:
            q_status = conn.execute("SELECT status FROM quests WHERE id = ?", (self.quest_id,)).fetchone()["status"]
        self.assertEqual(q_status, "done", "Quest should be marked as done in DB")

if __name__ == "__main__":
    unittest.main()
