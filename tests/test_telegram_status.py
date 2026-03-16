import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import scripts.telegram_service as telegram_service


class TelegramStatusTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.session_path = self.root / "runtime" / "telegram_userbot.session"
        self.status_path = self.root / "runtime" / "telegram_status.json"

        self.original_env = {
            key: os.environ.get(key)
            for key in (
                "TELEGRAM_API_ID",
                "TELEGRAM_API_HASH",
                "CONTROL_TOWER_TELEGRAM_SESSION_PATH",
                "CONTROL_TOWER_IGNORE_DOTENV",
            )
        }
        self.original_status_file = telegram_service.STATUS_FILE

        telegram_service.STATUS_FILE = self.status_path
        os.environ["CONTROL_TOWER_TELEGRAM_SESSION_PATH"] = str(self.session_path)
        os.environ["CONTROL_TOWER_IGNORE_DOTENV"] = "1"
        os.environ.pop("TELEGRAM_API_ID", None)
        os.environ.pop("TELEGRAM_API_HASH", None)

    def tearDown(self) -> None:
        telegram_service.STATUS_FILE = self.original_status_file
        for key, value in self.original_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        self.temp_dir.cleanup()

    def test_status_reports_missing_required_settings(self) -> None:
        status = telegram_service.get_telegram_status()
        self.assertFalse(status["configured"])
        self.assertEqual(status["missing_config"], ["TELEGRAM_API_ID", "TELEGRAM_API_HASH"])
        self.assertEqual(status["session_path"], str(self.session_path))
        self.assertFalse(status["session_exists"])
        self.assertIn("TELEGRAM_API_ID", status["setup_message"])

    def test_status_reports_first_session_required_when_configured(self) -> None:
        os.environ["TELEGRAM_API_ID"] = "12345"
        os.environ["TELEGRAM_API_HASH"] = "hash-value"

        status = telegram_service.get_telegram_status()
        self.assertTrue(status["configured"])
        self.assertEqual(status["missing_config"], [])
        self.assertTrue(status["first_session_required"])
        self.assertIn("세션 파일", status["setup_message"])


if __name__ == "__main__":
    unittest.main()
