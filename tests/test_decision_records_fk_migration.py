"""Tests for migration v5: decision_records plan and quest foreign keys."""

from __future__ import annotations

import os
import sqlite3
import tempfile
import unittest
from pathlib import Path

import scripts.db_base as db_base


class DecisionRecordsFKMigrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.data_dir = self.root / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.orig_env = {
            "CONTROL_TOWER_DATA_DIR": os.environ.get("CONTROL_TOWER_DATA_DIR"),
            "CONTROL_TOWER_DB_PATH": os.environ.get("CONTROL_TOWER_DB_PATH"),
        }
        os.environ["CONTROL_TOWER_DATA_DIR"] = str(self.data_dir)
        os.environ["CONTROL_TOWER_DB_PATH"] = str(self.data_dir / "control_tower.db")

        self.orig_data_dir = db_base.DATA_DIR
        self.orig_db_path = db_base.DB_PATH
        db_base.DATA_DIR = self.data_dir
        db_base.DB_PATH = self.data_dir / "control_tower.db"

    def tearDown(self) -> None:
        db_base.DATA_DIR = self.orig_data_dir
        db_base.DB_PATH = self.orig_db_path
        for key, value in self.orig_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        self.temp_dir.cleanup()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.data_dir / "control_tower.db"), timeout=10)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _insert_session(self, conn: sqlite3.Connection, session_id: str = "sess-1") -> None:
        conn.execute(
            """INSERT INTO sessions
               (id, agent_name, source_type, started_at, status)
               VALUES (?, 'agent', 'test', '2026-01-01', 'active')""",
            (session_id,),
        )

    def _insert_plan(self, conn: sqlite3.Connection, plan_id: str = "plan-1") -> None:
        conn.execute(
            """INSERT INTO plan_items
               (id, bucket, title, status, created_at, updated_at)
               VALUES (?, 'today', 'Plan', 'pending', '2026-01-01', '2026-01-01')""",
            (plan_id,),
        )

    def _insert_quest(self, conn: sqlite3.Connection, quest_id: str = "quest-1") -> None:
        conn.execute(
            """INSERT INTO quests
               (id, title, completion_criteria, status, created_at, updated_at)
               VALUES (?, 'Quest', 'Done', 'pending', '2026-01-01', '2026-01-01')""",
            (quest_id,),
        )

    def _insert_decision(
        self,
        conn: sqlite3.Connection,
        decision_id: str,
        plan_id: str | None = None,
        quest_id: str | None = None,
        session_id: str | None = None,
    ) -> None:
        conn.execute(
            """INSERT INTO decision_records
               (id, decision_type, title, related_plan_item_id,
                related_quest_id, related_session_id, created_at)
               VALUES (?, 'test', 'Decision', ?, ?, ?, '2026-01-01')""",
            (decision_id, plan_id, quest_id, session_id),
        )

    def test_schema_migrations_records_v1_to_v5(self) -> None:
        db_base.init_db()
        conn = self._connect()
        try:
            versions = conn.execute(
                "SELECT version, name FROM schema_migrations ORDER BY version"
            ).fetchall()
            result = {int(r["version"]): r["name"] for r in versions}
            self.assertEqual(result[5], "decision-records-reference-fks")
            self.assertGreaterEqual(max(result), 5)
        finally:
            conn.close()

    def test_foreign_key_list_has_plan_and_quest_fks(self) -> None:
        db_base.init_db()
        conn = self._connect()
        try:
            fk_list = conn.execute("PRAGMA foreign_key_list(decision_records)").fetchall()
            expected = {
                ("plan_items", "related_plan_item_id"),
                ("quests", "related_quest_id"),
            }
            actual = {(r[2], r[3]) for r in fk_list}
            self.assertTrue(expected.issubset(actual))
            self.assertNotIn(("sessions", "related_session_id"), actual)
            for row in fk_list:
                if (row[2], row[3]) in expected:
                    self.assertEqual(row[6], "SET NULL")
        finally:
            conn.close()

    def test_invalid_plan_and_quest_references_raise(self) -> None:
        db_base.init_db()
        conn = self._connect()
        try:
            cases = [
                ("decision-bad-plan", "missing-plan", None, None),
                ("decision-bad-quest", None, "missing-quest", None),
            ]
            for decision_id, plan_id, quest_id, session_id in cases:
                with self.assertRaises(sqlite3.IntegrityError):
                    self._insert_decision(conn, decision_id, plan_id, quest_id, session_id)
                    conn.commit()
                conn.rollback()
        finally:
            conn.close()

    def test_legacy_session_reference_remains_unconstrained_for_now(self) -> None:
        db_base.init_db()
        conn = self._connect()
        try:
            self._insert_decision(conn, "decision-legacy-session", None, None, "missing-session")
            conn.commit()
            row = conn.execute(
                "SELECT related_session_id FROM decision_records WHERE id = 'decision-legacy-session'"
            ).fetchone()
            self.assertEqual(row["related_session_id"], "missing-session")
        finally:
            conn.close()

    def test_valid_references_succeed(self) -> None:
        db_base.init_db()
        conn = self._connect()
        try:
            self._insert_plan(conn, "plan-valid")
            self._insert_quest(conn, "quest-valid")
            self._insert_session(conn, "sess-valid")
            self._insert_decision(conn, "decision-valid", "plan-valid", "quest-valid", "sess-valid")
            conn.commit()
            row = conn.execute(
                """SELECT related_plan_item_id, related_quest_id, related_session_id
                   FROM decision_records WHERE id = 'decision-valid'"""
            ).fetchone()
            self.assertEqual(row["related_plan_item_id"], "plan-valid")
            self.assertEqual(row["related_quest_id"], "quest-valid")
            self.assertEqual(row["related_session_id"], "sess-valid")
        finally:
            conn.close()

    def test_delete_plan_and_quest_sets_reference_columns_null(self) -> None:
        db_base.init_db()
        conn = self._connect()
        try:
            self._insert_plan(conn, "plan-del")
            self._insert_quest(conn, "quest-del")
            self._insert_session(conn, "sess-del")
            self._insert_decision(conn, "decision-null", "plan-del", "quest-del", "sess-del")
            conn.commit()

            conn.execute("DELETE FROM plan_items WHERE id = 'plan-del'")
            conn.execute("DELETE FROM quests WHERE id = 'quest-del'")
            conn.execute("DELETE FROM sessions WHERE id = 'sess-del'")
            conn.commit()

            row = conn.execute(
                """SELECT related_plan_item_id, related_quest_id, related_session_id
                   FROM decision_records WHERE id = 'decision-null'"""
            ).fetchone()
            self.assertIsNone(row["related_plan_item_id"])
            self.assertIsNone(row["related_quest_id"])
            self.assertEqual(row["related_session_id"], "sess-del")
        finally:
            conn.close()

    def test_init_db_idempotent_for_v5(self) -> None:
        db_base.init_db()
        db_base.init_db()
        conn = self._connect()
        try:
            count = conn.execute(
                "SELECT COUNT(*) as cnt FROM schema_migrations WHERE version = 5"
            ).fetchone()
            self.assertEqual(count["cnt"], 1)
        finally:
            conn.close()

    def test_foreign_key_check_clean(self) -> None:
        db_base.init_db()
        conn = self._connect()
        try:
            errors = conn.execute("PRAGMA foreign_key_check").fetchall()
            self.assertEqual(errors, [])
        finally:
            conn.close()

    def test_fts_trigger_survives_migration(self) -> None:
        db_base.init_db()
        conn = self._connect()
        try:
            self._insert_decision(conn, "decision-fts")
            conn.commit()
            fts_row = conn.execute(
                "SELECT id FROM decision_records_fts WHERE id = 'decision-fts'"
            ).fetchone()
            self.assertIsNotNone(fts_row)
            self.assertEqual(fts_row["id"], "decision-fts")
        finally:
            conn.close()


if __name__ == "__main__":
    unittest.main()
