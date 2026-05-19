from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

import scripts.db_base as db_base
from scripts.db_integrity import audit_orphan_references, clear_orphan_references


class OrphanReferenceCleanupMigrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.orig_db_path = os.environ.get("CONTROL_TOWER_DB_PATH")
        os.environ["CONTROL_TOWER_DB_PATH"] = str(Path(self.temp_dir.name) / "control_tower.db")

    def tearDown(self) -> None:
        if self.orig_db_path is None:
            os.environ.pop("CONTROL_TOWER_DB_PATH", None)
        else:
            os.environ["CONTROL_TOWER_DB_PATH"] = self.orig_db_path
        self.temp_dir.cleanup()

    def test_clear_orphan_references_sets_missing_parents_to_null(self) -> None:
        db_base.init_db()
        with db_base.connect() as conn:
            now = db_base.now_iso()
            conn.execute("PRAGMA foreign_keys = OFF")
            conn.execute(
                """
                INSERT INTO decision_records (
                    id, decision_type, title, related_quest_id, related_session_id, created_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                ("decision-1", "test", "Decision", "missing-quest", "_", now),
            )
            conn.execute("PRAGMA foreign_keys = ON")
            self.assertEqual(len(audit_orphan_references(conn)), 2)
            updates = clear_orphan_references(conn)
            row = conn.execute(
                "SELECT related_quest_id, related_session_id FROM decision_records WHERE id = ?",
                ("decision-1",),
            ).fetchone()

        self.assertEqual(updates["decision_records.related_quest_id->quests.id"], 1)
        self.assertEqual(updates["decision_records.related_session_id->sessions.id"], 1)
        self.assertIsNone(row["related_quest_id"])
        self.assertIsNone(row["related_session_id"])

    def test_init_db_records_cleanup_migration_version(self) -> None:
        db_base.init_db()
        with db_base.connect() as conn:
            versions = db_base.get_applied_schema_versions(conn)

        self.assertIn(db_base.BASELINE_SCHEMA_VERSION, versions)
        self.assertIn(db_base.ORPHAN_REFERENCE_CLEANUP_VERSION, versions)

    def test_cleanup_migration_is_idempotent(self) -> None:
        db_base.init_db()
        db_base.init_db()
        with db_base.connect() as conn:
            count = conn.execute(
                "SELECT COUNT(*) FROM schema_migrations WHERE version = ?",
                (db_base.ORPHAN_REFERENCE_CLEANUP_VERSION,),
            ).fetchone()[0]

        self.assertEqual(count, 1)


if __name__ == "__main__":
    unittest.main()
