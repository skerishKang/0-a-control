import sys
import tempfile
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts import settings_guardrails


class SettingsGuardrailsTests(unittest.TestCase):
    def test_build_settings_status_uses_safe_defaults(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = settings_guardrails.build_settings_status(env={}, project_root=Path(tmp))

        self.assertEqual(result["host"], "127.0.0.1")
        self.assertEqual(result["port"], "4310")
        self.assertFalse(result["debug_enabled"])
        self.assertFalse(result["telegram"]["configured"])
        self.assertIn("python_version", result)

    def test_build_settings_status_reports_booleans_not_secret_values(self):
        with tempfile.TemporaryDirectory() as tmp:
            session_path = Path(tmp) / "telegram.session"
            session_path.write_text("sensitive-session-placeholder")
            env = {
                "HOST": "0.0.0.0",
                "PORT": "9999",
                "DEBUG": "1",
                "TELEGRAM_API_ID": "12345",
                "TELEGRAM_API_HASH": "secret-hash-value",
                "CONTROL_TOWER_TELEGRAM_SESSION_PATH": str(session_path),
            }

            result = settings_guardrails.build_settings_status(env=env, project_root=Path(tmp))

        rendered = repr(result)
        self.assertEqual(result["host"], "0.0.0.0")
        self.assertEqual(result["port"], "9999")
        self.assertTrue(result["debug_enabled"])
        self.assertTrue(result["telegram"]["api_id_configured"])
        self.assertTrue(result["telegram"]["api_hash_configured"])
        self.assertTrue(result["telegram"]["configured"])
        self.assertTrue(result["telegram"]["session_path_configured"])
        self.assertTrue(result["telegram"]["session_path_present"])
        self.assertNotIn("secret-hash-value", rendered)
        self.assertNotIn("sensitive-session-placeholder", rendered)

    def test_guardrails_classifies_local_host_as_ok(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = settings_guardrails.build_guardrails_status(
                env={"HOST": "127.0.0.1"},
                project_root=Path(tmp),
            )

        codes = {check["code"] for check in result["checks"]}
        self.assertIn("LOCAL_ONLY_SAFE", codes)
        self.assertIn("TELEGRAM_NOT_CONFIGURED", codes)
        self.assertIn("BACKUP_NOT_CONFIRMED", codes)

    def test_guardrails_warns_for_lan_and_debug(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = settings_guardrails.build_guardrails_status(
                env={"HOST": "0.0.0.0", "DEBUG": "true"},
                project_root=Path(tmp),
            )

        checks = {check["code"]: check["level"] for check in result["checks"]}
        self.assertEqual(checks["LAN_EXPOSED"], "warning")
        self.assertEqual(checks["DEBUG_ENABLED"], "warning")
        self.assertEqual(result["overall_level"], "warning")


if __name__ == "__main__":
    unittest.main()
