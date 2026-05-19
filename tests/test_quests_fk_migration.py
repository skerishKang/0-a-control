"""Tests for migration v4: quests plan and parent foreign keys."""

from __future__ import annotations

import os
import sqlite3
import tempfile
import unittest
from pathlib import Path

import scripts.db_base as db_base


class QuestsFKMigrationTests(unittest.TestCase):
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

    def _insert_plan(self, conn: sqlite3.Connection, plan_id: str = "plan-1") -> None:
        conn.execute(
            """INSERT INTO plan_items
               (id, bucket, title, status, created_at, updated_at)
               VALUES (?, 'today', 'Plan', 'pending', '2026-01-01', '2026-01-01')""",
            (plan_id,),
        )

    def _insert_quest(
        self,
        conn: sqlite3.Connection,
        quest_id: str,
        plan_item_id: str | None = None,
        parent_quest_id: str | None = None,
    ) -> None:
        conn.execute(
            """INSERT INTO quests
               (id, plan_item_id, parent_quest_id, title, completion_criteria,
                status, created_at, updated_at)
               VALUES (?, ?, ?, 'Quest', 'Done', 'pending', '2026-01-01', '2026-01-01')""",
            (quest_id, plan_item_id, parent_quest_id),
        )

    def test_schema_migrations_records_v1_to_v4(self) -> None:
        db_base.init_db()
        conn = self._connect()
        try:
            versions = conn.execute(
                "SELECT version, name FROM schema_migrations ORDER BY version"
            ).fetchall()
            result = {int(r["version"]): r["name"] for r in versions}
            self.assertEqual(
                result,
                {
                    1: "baseline-current-schema",
                    2: "null-orphan-relational-references",
                    3: "source-records-session-fk",
                    4: "quests-plan-parent-fks",
                },
            )
        finally:
            conn.close()

    def test_foreign_key_list_has_plan_and_parent_fks(self) -> None:
        db_base.init_db()
        conn = self._connect()
        try:
            fk_list = conn.execute("PRAGMA foreign_key_list(quests)").fetchall()
            plan_fk = [r for r in fk_list if r[2] == "plan_items" and r[3] == "plan_item_id"]
            parent_fk = [r for r in fk_list if r[2] == "quests" and r[3] == "parent_quest_id"]
            self.assertEqual(len(plan_fk), 1)
            self.assertEqual(len(parent_fk), 1)
            self.assertEqual(plan_fk[0][6], "SET NULL")
            self.assertEqual(parent_fk[0][6], "SET NULL")
        finally:
            conn.close()

    def test_insert_invalid_plan_item_id_raises(self) -> None:
        db_base.init_db()
        conn = self._connect()
        try:
            with self.assertRaises(sqlite3.IntegrityError):
                self._insert_quest(conn, "quest-bad-plan", plan_item_id="missing-plan")
                conn.commit()
        finally:
            conn.close()

    def test_insert_invalid_parent_quest_id_raises(self) -> None:
        db_base.init_db()
        conn = self._connect()
        try:
            with self.assertRaises(sqlite3.IntegrityError):
                self._insert_quest(conn, "quest-bad-parent", parent_quest_id="missing-parent")
                conn.commit()
        finally:
            conn.close()

    def test_insert_valid_plan_and_parent_succeeds(self) -> None:
        db_base.init_db()
        conn = self._connect()
        try:
            self._insert_plan(conn, "plan-valid")
            self._insert_quest(conn, "quest-parent", plan_item_id="plan-valid")
            self._insert_quest(conn, "quest-child", plan_item_id="plan-valid", parent_quest_id="quest-parent")
            conn.commit()
            row = conn.execute(
                "SELECT plan_item_id, parent_quest_id FROM quests WHERE id = 'quest-child'"
            ).fetchone()
            self.assertEqual(row["plan_item_id"], "plan-valid")
            self.assertEqual(row["parent_quest_id"], "quest-parent")
        finally:
            conn.close()

    def test_delete_plan_sets_quest_plan_item_null(self) -> None:
        db_base.init_db()
        conn = self._connect()
        try:
            self._insert_plan(conn, "plan-del")
            self._insert_quest(conn, "quest-plan-null", plan_item_id="plan-del")
            conn.commit()
            conn.execute("DELETE FROM plan_items WHERE id = 'plan-del'")
            conn.commit()
            row = conn.execute(
                "SELECT plan_item_id FROM quests WHERE id = 'quest-plan-null'"
            ).fetchone()
            self.assertIsNone(row["plan_item_id"])
        finally:
            conn.close()

    def test_delete_parent_sets_child_parent_null(self) -> None:
        db_base.init_db()
        conn = self._connect()
        try:
            self._insert_quest(conn, "quest-parent-del")
            self._insert_quest(conn, "quest-child-null", parent_quest_id="quest-parent-del")
            conn.commit()
            conn.execute("DELETE FROM quests WHERE id = 'quest-parent-del'")
            conn.commit()
            row = conn.execute(
                "SELECT parent_quest_id FROM quests WHERE id = 'quest-child-null'"
            ).fetchone()
            self.assertIsNone(row["parent_quest_id"])
        finally:
            conn.close()

    def test_init_db_idempotent_for_v4(self) -> None:
        db_base.init_db()
        db_base.init_db()
        conn = self._connect()
        try:
            count = conn.execute(
                "SELECT COUNT(*) as cnt FROM schema_migrations WHERE version = 4"
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


if __name__ == "__main__":
    unittest.main()
