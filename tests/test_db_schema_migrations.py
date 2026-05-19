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

    def test_init_db_records_schema_versions(self) -> None:
        db_base.init_db()
        with db_base.connect() as conn:
            versions = db_base.get_applied_schema_versions(conn)
            baseline_row = conn.execute(
                "SELECT name FROM schema_migrations WHERE version = ?",
                (db_base.BASELINE_SCHEMA_VERSION,),
            ).fetchone()
            cleanup_row = conn.execute(
                "SELECT name FROM schema_migrations WHERE version = ?",
                (db_base.ORPHAN_REFERENCE_CLEANUP_VERSION,),
            ).fetchone()

        self.assertEqual(versions, [db_base.BASELINE_SCHEMA_VERSION, db_base.ORPHAN_REFERENCE_CLEANUP_VERSION])
        self.assertEqual(baseline_row["name"], db_base.BASELINE_SCHEMA_NAME)
        self.assertEqual(cleanup_row["name"], db_base.ORPHAN_REFERENCE_CLEANUP_NAME)

    def test_init_db_is_idempotent_for_baseline_migration(self) -> None:
        db_base.init_db()
        db_base.init_db()
        with db_base.connect() as conn:
            count = conn.execute(
                "SELECT COUNT(*) FROM schema_migrations WHERE version = ?",
                (db_base.BASELINE_SCHEMA_VERSION,),
            ).fetchone()[0]

        self.assertEqual(count, 1)

    def test_apply_schema_migrations_creates_bookkeeping_table(self) -> None:
        with db_base.connect() as conn:
            db_base.apply_schema_migrations(conn)
            versions = db_base.get_applied_schema_versions(conn)

        self.assertEqual(versions, [db_base.BASELINE_SCHEMA_VERSION, db_base.ORPHAN_REFERENCE_CLEANUP_VERSION])


if __name__ == "__main__":
    unittest.main()
