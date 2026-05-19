from __future__ import annotations

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import scripts.db_base as db_base
from scripts.db_integrity_cli import main


class RelationalIntegrityCliTests(unittest.TestCase):
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

    def test_main_returns_zero_when_no_orphans(self) -> None:
        output = io.StringIO()
        with redirect_stdout(output):
            status = main([])

        self.assertEqual(status, 0)
        self.assertIn("RESULT: PASS", output.getvalue())

    def test_json_output_reports_success(self) -> None:
        output = io.StringIO()
        with redirect_stdout(output):
            status = main(["--json"])

        payload = json.loads(output.getvalue())
        self.assertEqual(status, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["findings"], [])

    def test_main_returns_one_when_orphans_exist(self) -> None:
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

        output = io.StringIO()
        with redirect_stdout(output):
            status = main([])

        self.assertEqual(status, 1)
        self.assertIn("RESULT: FAIL", output.getvalue())
        self.assertIn("source_records.session_id->sessions.id", output.getvalue())


if __name__ == "__main__":
    unittest.main()
