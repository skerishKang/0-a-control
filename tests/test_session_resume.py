from __future__ import annotations

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import os
import tempfile
import unittest

import scripts.db_base as db_base
import scripts.db_state as db_state
from scripts.db_sessions import append_source_record, end_session, start_session, update_session_summary
from scripts.db_state import refresh_current_state


class SessionResumeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.data_dir = self.root / "data"
        self.workdiary_dir = self.root / "workdiary"
        (self.workdiary_dir / "demo-project").mkdir(parents=True, exist_ok=True)

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
        self.orig_state_workdiary_dir = db_state.WORKDIARY_DIR
        db_base.DATA_DIR = self.data_dir
        db_base.DB_PATH = self.data_dir / "control_tower.db"
        db_base.WORKDIARY_DIR = self.workdiary_dir
        db_state.WORKDIARY_DIR = self.workdiary_dir
        db_base.init_db()

        now = db_base.now_iso()
        with db_base.connect() as conn:
            conn.execute(
                """
                INSERT INTO plan_items (
                    id, bucket, title, description, status, priority_score, priority_reason,
                    due_at, project_key, related_session_id, related_source_id,
                    created_at, updated_at, metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "mission-1",
                    "today",
                    "resume mission",
                    "",
                    "active",
                    100,
                    "resume priority",
                    None,
                    "0-a-control",
                    None,
                    None,
                    now,
                    now,
                    None,
                ),
            )
            conn.execute(
                """
                INSERT INTO quests (
                    id, plan_item_id, parent_quest_id, title, why_now, completion_criteria,
                    status, verdict_reason, restart_point, next_quest_hint,
                    created_at, updated_at, metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "quest-1",
                    "mission-1",
                    None,
                    "resume quest",
                    "must resume",
                    "verify resume context",
                    "active",
                    None,
                    "Open the last session summary and continue from the saved breakpoint.",
                    "Implement resume injection in the wrapper.",
                    now,
                    now,
                    None,
                ),
            )
            refresh_current_state(conn)

    def tearDown(self) -> None:
        db_base.DATA_DIR = self.orig_data_dir
        db_base.DB_PATH = self.orig_db_path
        db_base.WORKDIARY_DIR = self.orig_workdiary_dir
        db_state.WORKDIARY_DIR = self.orig_state_workdiary_dir
        for key, value in self.orig_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        self.temp_dir.cleanup()

    def test_start_session_includes_resume_payload_from_previous_session(self) -> None:
        previous = start_session(
            agent_name="codex",
            source_type="cmd",
            project_key="0-a-control",
            working_dir="/tmp/0-a-control",
            title="previous session",
        )
        append_source_record(
            session_id=previous["id"],
            source_name="codex",
            source_type="agent_turn",
            role="user",
            project_key="0-a-control",
            working_dir="/tmp/0-a-control",
            content="Need automatic resume context on the next Codex session.",
        )
        append_source_record(
            session_id=previous["id"],
            source_name="codex",
            source_type="agent_turn",
            role="assistant",
            project_key="0-a-control",
            working_dir="/tmp/0-a-control",
            content="I will wire the latest summary and key turns into the next startup prompt.",
        )
        update_session_summary(
            previous["id"],
            "Added session logging and identified resume injection as the next step.",
        )
        end_session(previous["id"])

        current = start_session(
            agent_name="codex",
            source_type="cmd",
            project_key="0-a-control",
            working_dir="/tmp/0-a-control",
            title="new session",
            include_resume_context=True,
            resume_session_limit=2,
            resume_turn_limit=4,
        )

        context = current["resume_context"]
        self.assertEqual(context["source_session_id"], previous["id"])
        self.assertIn("Open the last session summary", context["current_state"]["restart_point"])
        self.assertTrue(context["current_state"]["recommended_next_quest"])
        self.assertIn("Added session logging", context["prompt"])
        self.assertIn("Need automatic resume context", context["prompt"])
        self.assertIn("resume quest", context["prompt"])
        self.assertEqual(sorted(turn["role"] for turn in context["recent_turns"]), ["assistant", "user"])


if __name__ == "__main__":
    unittest.main()
