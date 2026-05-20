from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

import scripts.db_base as db_base


class SchemaMigrationTests(unittest.TestCase):
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

    def _expected_versions(self) -> list[int]:
        return [
            db_base.BASELINE_SCHEMA_VERSION,
            db_base.ORPHAN_REFERENCE_CLEANUP_VERSION,
            db_base.SOURCE_RECORDS_SESSION_FK_VERSION,
            db_base.QUESTS_PLAN_PARENT_FK_VERSION,
            db_base.DECISION_RECORDS_REFERENCE_FK_VERSION,
            db_base.BRIEF_RECORDS_REFERENCE_FK_VERSION,
            db_base.DECISION_RECORDS_SESSION_FK_VERSION,
            db_base.BRIEF_RECORDS_SESSION_FK_VERSION,
            db_base.PLAN_ITEMS_SESSION_FK_VERSION,
        ]

    def test_init_db_records_schema_versions(self) -> None:
        db_base.init_db()
        with db_base.connect() as conn:
            versions = db_base.get_applied_schema_versions(conn)
            names = {
                int(row["version"]): row["name"]
                for row in conn.execute(
                    "SELECT version, name FROM schema_migrations ORDER BY version"
                ).fetchall()
            }

        self.assertEqual(versions, self._expected_versions())
        self.assertEqual(names[db_base.BASELINE_SCHEMA_VERSION], db_base.BASELINE_SCHEMA_NAME)
        self.assertEqual(
            names[db_base.ORPHAN_REFERENCE_CLEANUP_VERSION],
            db_base.ORPHAN_REFERENCE_CLEANUP_NAME,
        )
        self.assertEqual(
            names[db_base.QUESTS_PLAN_PARENT_FK_VERSION],
            db_base.QUESTS_PLAN_PARENT_FK_NAME,
        )
        self.assertEqual(
            names[db_base.DECISION_RECORDS_REFERENCE_FK_VERSION],
            db_base.DECISION_RECORDS_REFERENCE_FK_NAME,
        )
        self.assertEqual(
            names[db_base.BRIEF_RECORDS_REFERENCE_FK_VERSION],
            db_base.BRIEF_RECORDS_REFERENCE_FK_NAME,
        )
        self.assertEqual(
            names[db_base.DECISION_RECORDS_SESSION_FK_VERSION],
            db_base.DECISION_RECORDS_SESSION_FK_NAME,
        )
        self.assertEqual(
            names[db_base.BRIEF_RECORDS_SESSION_FK_VERSION],
            db_base.BRIEF_RECORDS_SESSION_FK_NAME,
        )
        self.assertEqual(
            names[db_base.PLAN_ITEMS_SESSION_FK_VERSION],
            db_base.PLAN_ITEMS_SESSION_FK_NAME,
        )

    def test_init_db_is_idempotent_for_baseline_migration(self) -> None:
        db_base.init_db()
        db_base.init_db()
        with db_base.connect() as conn:
            count = conn.execute(
                "SELECT COUNT(version) FROM schema_migrations WHERE version = ?",
                (db_base.BASELINE_SCHEMA_VERSION,),
            ).fetchone()[0]

        self.assertEqual(count, 1)

    def test_apply_schema_migrations_creates_bookkeeping_table(self) -> None:
        with db_base.connect() as conn:
            db_base.apply_schema_migrations(conn)
            versions = db_base.get_applied_schema_versions(conn)

        self.assertEqual(versions, self._expected_versions())


if __name__ == "__main__":
    unittest.main()
