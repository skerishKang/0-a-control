from __future__ import annotations

import os
import sqlite3
import tempfile
import unittest
from pathlib import Path

import scripts.db_base as db_base


class ConnectionPragmaTests(unittest.TestCase):
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

    def test_foreign_keys_enabled(self) -> None:
        with db_base.connect() as conn:
            result = conn.execute("PRAGMA foreign_keys").fetchone()
            self.assertEqual(result[0], 1, "foreign_keys must be ON")

    def test_journal_mode_is_wal(self) -> None:
        with db_base.connect() as conn:
            result = conn.execute("PRAGMA journal_mode").fetchone()
            mode = str(result[0]).lower()
            self.assertEqual(mode, "wal", f"journal_mode should be wal, got {mode}")

    def test_synchronous_normal_when_wal(self) -> None:
        with db_base.connect() as conn:
            journal = conn.execute("PRAGMA journal_mode").fetchone()
            if str(journal[0]).lower() == "wal":
                sync = conn.execute("PRAGMA synchronous").fetchone()
                # NORMAL = 1
                self.assertEqual(
                    sync[0], 1, f"synchronous should be 1 (NORMAL) when WAL, got {sync[0]}"
                )

    def test_busy_timeout_set(self) -> None:
        with db_base.connect() as conn:
            result = conn.execute("PRAGMA busy_timeout").fetchone()
            self.assertEqual(result[0], 10000, f"busy_timeout should be 10000, got {result[0]}")

    def test_pragmas_apply_to_new_connections(self) -> None:
        """Each new connection from connect() must have pragmas configured."""
        with db_base.connect() as conn1:
            fk1 = conn1.execute("PRAGMA foreign_keys").fetchone()
        with db_base.connect() as conn2:
            fk2 = conn2.execute("PRAGMA foreign_keys").fetchone()
        self.assertEqual(fk1[0], 1)
        self.assertEqual(fk2[0], 1)

    def test_configure_connection_sets_pragmas(self) -> None:
        """configure_connection() directly on a raw connection sets all pragmas."""
        db_path = self.data_dir / "direct_test.db"
        conn = sqlite3.connect(str(db_path))
        try:
            db_base.configure_connection(conn)
            fk = conn.execute("PRAGMA foreign_keys").fetchone()
            journal = conn.execute("PRAGMA journal_mode").fetchone()
            busy = conn.execute("PRAGMA busy_timeout").fetchone()
            self.assertEqual(fk[0], 1)
            self.assertEqual(str(journal[0]).lower(), "wal")
            self.assertEqual(busy[0], 10000)
        finally:
            conn.close()


if __name__ == "__main__":
    unittest.main()
