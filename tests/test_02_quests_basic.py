import os
import tempfile
import unittest
from pathlib import Path
import sys

# Setup path and environment isolation
temp_dir = tempfile.mkdtemp()
os.environ["CONTROL_TOWER_DATA_DIR"] = str(Path(temp_dir) / "data")
os.environ["CONTROL_TOWER_DB_PATH"] = str(Path(temp_dir) / "data" / "control_tower.db")

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.db_base import connect, init_db

class QuestsBasicTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    def test_db_connectivity_and_quests_table(self):
        with connect() as conn:
            # Check if quests table exists and is readable
            try:
                row = conn.execute("SELECT COUNT(*) as count FROM quests").fetchone()
                self.assertIsNotNone(row)
                print(f"Total quests in DB: {row['count']}")
            except Exception as e:
                self.fail(f"Failed to query quests table: {e}")

    def test_plan_items_table(self):
        with connect() as conn:
            try:
                row = conn.execute("SELECT COUNT(*) as count FROM plan_items").fetchone()
                self.assertIsNotNone(row)
                print(f"Total plan_items in DB: {row['count']}")
            except Exception as e:
                self.fail(f"Failed to query plan_items table: {e}")

if __name__ == "__main__":
    unittest.main()
