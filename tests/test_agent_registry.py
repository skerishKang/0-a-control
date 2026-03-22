import os
import sys
import tempfile
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import scripts.db_base as db_base
from unittest.mock import patch

from scripts.agent_registry import canonical_agent_name, get_agent_statuses, list_registered_agents


class AgentRegistryTests(unittest.TestCase):
    def test_canonical_aliases(self) -> None:
        self.assertEqual(canonical_agent_name("gemini"), "gemini-cli")
        self.assertEqual(canonical_agent_name("kilocode"), "kilo")
        self.assertEqual(canonical_agent_name("open-code"), "opencode")

    def test_registered_agents_have_expected_fields(self) -> None:
        items = list_registered_agents()
        self.assertTrue(any(item["canonical_name"] == "codex" for item in items))
        for item in items:
            self.assertIn("canonical_name", item)
            self.assertIn("label", item)
            self.assertIn("aliases", item)
            self.assertIn("executable", item)
            self.assertIn("available", item)

    @patch("scripts.agent_registry.get_running_agent_names", return_value={"codex"})
    def test_agent_status_prefers_running_processes(self, _mock_running) -> None:
        temp_dir = tempfile.TemporaryDirectory()
        data_dir = Path(temp_dir.name) / "data"
        db_path = data_dir / "control_tower.db"

        original_env = {
            key: os.environ.get(key)
            for key in ("CONTROL_TOWER_DATA_DIR", "CONTROL_TOWER_DB_PATH")
        }
        original_paths = {
            "data_dir": db_base.DATA_DIR,
            "db_path": db_base.DB_PATH,
        }

        os.environ["CONTROL_TOWER_DATA_DIR"] = str(data_dir)
        os.environ["CONTROL_TOWER_DB_PATH"] = str(db_path)
        db_base.DATA_DIR = data_dir
        db_base.DB_PATH = db_path

        try:
            db_base.init_db()
            with db_base.connect() as conn:
                conn.execute(
                    """
                    INSERT INTO sessions (
                        id, agent_name, source_type, started_at, status
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    ("s-1", "codex", "interactive", "2026-03-22T00:00:00Z", "active"),
                )
                conn.execute(
                    """
                    INSERT INTO sessions (
                        id, agent_name, source_type, started_at, status
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    ("s-2", "gemini-cli", "interactive", "2026-03-22T01:00:00Z", "closed"),
                )
                conn.execute(
                    """
                    INSERT INTO sessions (
                        id, agent_name, source_type, started_at, status
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    ("s-3", "opencode", "interactive", "2026-03-22T02:00:00Z", "active"),
                )

            statuses = {item["canonical_name"]: item for item in get_agent_statuses()}
            self.assertEqual(statuses["codex"]["status"], "working")
            self.assertTrue(statuses["codex"]["process_running"])
            self.assertEqual(statuses["gemini-cli"]["status"], "idle")
            self.assertFalse(statuses["gemini-cli"]["process_running"])
            self.assertEqual(statuses["opencode"]["status"], "stale")
            self.assertFalse(statuses["opencode"]["process_running"])
            self.assertTrue(statuses["opencode"]["has_stale_session"])
            self.assertIsNotNone(statuses["codex"]["last_session"])
        finally:
            db_base.DATA_DIR = original_paths["data_dir"]
            db_base.DB_PATH = original_paths["db_path"]
            for key, value in original_env.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value
            temp_dir.cleanup()


if __name__ == "__main__":
    unittest.main()
