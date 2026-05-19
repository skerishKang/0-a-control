from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

import scripts.db_base as db_base
from scripts.db_integrity import audit_orphan_references, has_orphan_references


class RelationalOrphanAuditTests(unittest.TestCase):
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

    def test_audit_returns_empty_for_fresh_database(self) -> None:
        with db_base.connect() as conn:
            self.assertEqual(audit_orphan_references(conn), [])
            self.assertFalse(has_orphan_references(conn))

    def test_audit_detects_missing_session_for_source_record(self) -> None:
        with db_base.connect() as conn:
            conn.execute("PRAGMA foreign_keys = OFF")
            conn.execute(
                """
                INSERT INTO source_records (
                    id, source_type, source_name, session_id, content, created_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                ("src-1", "manual", "tester", "missing-session", "hello", db_base.now_iso()),
            )
            conn.execute("PRAGMA foreign_keys = ON")
            findings = audit_orphan_references(conn)

        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["relationship"], "source_records.session_id->sessions.id")
        self.assertEqual(findings[0]["child_id"], "src-1")
        self.assertEqual(findings[0]["missing_parent_id"], "missing-session")

    def test_audit_ignores_existing_session_reference(self) -> None:
        with db_base.connect() as conn:
            now = db_base.now_iso()
            conn.execute(
                """
                INSERT INTO sessions (
                    id, agent_name, source_type, started_at, status
                ) VALUES (?, ?, ?, ?, ?)
                """,
                ("session-1", "agent", "manual", now, "active"),
            )
            conn.execute(
                """
                INSERT INTO source_records (
                    id, source_type, source_name, session_id, content, created_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                ("src-1", "manual", "tester", "session-1", "hello", now),
            )
            self.assertEqual(audit_orphan_references(conn), [])

    def test_audit_detects_missing_plan_item_for_quest(self) -> None:
        with db_base.connect() as conn:
            now = db_base.now_iso()
            conn.execute("PRAGMA foreign_keys = OFF")
            conn.execute(
                """
                INSERT INTO quests (
                    id, plan_item_id, title, completion_criteria, status, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                ("quest-1", "missing-plan", "Quest", "Done", "active", now, now),
            )
            conn.execute("PRAGMA foreign_keys = ON")
            findings = audit_orphan_references(conn)

        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["relationship"], "quests.plan_item_id->plan_items.id")
        self.assertEqual(findings[0]["child_id"], "quest-1")


if __name__ == "__main__":
    unittest.main()
