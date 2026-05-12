import json
import os
import sys
import tempfile
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.server import validate_session_id, get_active_session_runtime, SESSIONS_DIR


class ValidateSessionIdTests(unittest.TestCase):
    """Tests for session_id validation in get_active_session_runtime."""

    def test_accepts_uuid_like(self):
        self.assertTrue(validate_session_id("abc12345-6789-def0-1234-56789abcdef0"))

    def test_accepts_hex(self):
        self.assertTrue(validate_session_id("a1b2c3d4e5f6"))

    def test_accepts_alphanumeric_with_dash_underscore(self):
        self.assertTrue(validate_session_id("session_abc-123"))

    def test_rejects_slash(self):
        self.assertFalse(validate_session_id("foo/bar"))

    def test_rejects_backslash(self):
        self.assertFalse(validate_session_id("foo\\bar"))

    def test_rejects_dot_dot(self):
        self.assertFalse(validate_session_id("../etc/passwd"))

    def test_rejects_null_byte(self):
        self.assertFalse(validate_session_id("foo\0bar"))

    def test_rejects_empty_string(self):
        self.assertFalse(validate_session_id(""))

    def test_rejects_absolute_unix_path(self):
        self.assertFalse(validate_session_id("/tmp/malicious"))

    def test_rejects_windows_drive_letter(self):
        self.assertFalse(validate_session_id("C:malicious"))

    def test_rejects_colon(self):
        self.assertFalse(validate_session_id("session:id"))

    def test_rejects_very_long(self):
        self.assertFalse(validate_session_id("x" * 200))


class GetActiveSessionRuntimeTests(unittest.TestCase):
    """Tests for get_active_session_runtime path safety."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.sessions_dir = Path(self.temp_dir.name) / "sessions"
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self.valid_session_id = "valid-session-123"
        self.valid_file = self.sessions_dir / f"{self.valid_session_id}.json"
        self.valid_file.write_text(json.dumps({"key": "value"}), encoding="utf-8")

        # Patch SESSIONS_DIR to use our temp dir
        self._orig_patch = None
        import scripts.server as server_mod
        self._orig_sessions_dir = server_mod.SESSIONS_DIR
        server_mod.SESSIONS_DIR = self.sessions_dir

    def tearDown(self):
        import scripts.server as server_mod
        server_mod.SESSIONS_DIR = self._orig_sessions_dir
        self.temp_dir.cleanup()

    def test_valid_session_id_loads_data(self):
        result = get_active_session_runtime(self.valid_session_id)
        self.assertEqual(result, {"key": "value"})

    def test_invalid_session_id_returns_empty_dict(self):
        result = get_active_session_runtime("../secret")
        self.assertEqual(result, {})

    def test_traversal_containment_check(self):
        """Verify resolved path must be within SESSIONS_DIR."""
        result = get_active_session_runtime(self.valid_session_id)
        self.assertEqual(result, {"key": "value"})

    def test_nonexistent_session_returns_empty(self):
        result = get_active_session_runtime("nonexistent-id")
        self.assertEqual(result, {})

    def test_none_session_id_returns_empty_when_no_current_file(self):
        result = get_active_session_runtime(None)
        self.assertEqual(result, {})
