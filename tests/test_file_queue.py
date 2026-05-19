"""Tests for file_queue module — filename token hardening."""

from __future__ import annotations

import unittest

from scripts.file_queue import (
    SAFE_SUFFIXES,
    _safe_token,
    generate_filename,
    generate_report_id,
)


class TestSafeToken(unittest.TestCase):
    """_safe_token() normalizes arbitrary strings to filesystem-safe tokens."""

    def test_normal_id_preserved(self):
        uuid_like = "123e4567-e89b-12d3-a456-426614174000"
        self.assertEqual(_safe_token(uuid_like), uuid_like)

    def test_strips_control_chars(self):
        self.assertEqual(_safe_token("abc\n\t\rdef\x00"), "abcdef")

    def test_strips_path_separators(self):
        self.assertEqual(_safe_token("../../etc/passwd"), "etcpasswd")

    def test_strips_leading_trailing_dots(self):
        self.assertEqual(_safe_token("..hidden.."), "hidden")

    def test_returns_placeholder_for_empty(self):
        self.assertEqual(_safe_token(""), "_")

    def test_returns_placeholder_for_all_dots(self):
        self.assertEqual(_safe_token("..."), "_")

    def test_custom_placeholder(self):
        self.assertEqual(_safe_token("\x00\x01\x02", "empty"), "empty")

    def test_preserves_underscore_hyphen_dot(self):
        self.assertEqual(
            _safe_token("my-quest_123.rev"),
            "my-quest_123.rev",
        )

    def test_replaces_spaces(self):
        self.assertEqual(_safe_token("quest 123"), "quest123")


class TestGenerateReportId(unittest.TestCase):
    """generate_report_id() produces safe tokens from any input."""

    def test_normal_uuid_quest_id(self):
        qid = "123e4567-e89b-12d3-a456-426614174000"
        result = generate_report_id(qid, "sess-001")
        self.assertIn(qid, result)

    def test_malformed_quest_id_sanitized(self):
        result = generate_report_id("../malicious")
        self.assertNotIn("../", result)
        self.assertNotIn("..", result)

    def test_malformed_session_id_sanitized(self):
        result = generate_report_id("q-1", "../../etc")
        self.assertNotIn("..", result)

    def test_empty_session_uses_underscore(self):
        result = generate_report_id("q-1")
        self.assertIn("q-1", result)
        self.assertTrue(result.endswith("-_"), f"Expected suffix '-_', got: {result}")

    def test_control_chars_in_quest_id(self):
        result = generate_report_id("q\n\t\r\x00id")
        self.assertNotIn("\n", result)
        self.assertNotIn("\t", result)

    def test_report_id_format(self):
        result = generate_report_id("quest-42", "sess-1")
        parts = result.split("-")
        self.assertGreaterEqual(len(parts), 3)
        self.assertTrue(
            parts[0].startswith("202") or parts[0].isdigit(),
            f"First part should be timestamp, got: {parts[0]}",
        )


class TestGenerateFilename(unittest.TestCase):
    """generate_filename() produces safe filenames."""

    def test_normal_suffix_preserved(self):
        result = generate_filename("report-123", "quest-report")
        self.assertEqual(result, "report-123.quest-report.json")

    def test_unknown_suffix_normalized(self):
        result = generate_filename("r", "../../malicious")
        self.assertNotIn("..", result)
        self.assertTrue(result.endswith(".json"))

    def test_allowed_suffixes(self):
        for suffix in SAFE_SUFFIXES:
            result = generate_filename("test", suffix)
            self.assertEqual(result, f"test.{suffix}.json")

    def test_report_id_with_path_traversal(self):
        result = generate_filename("../../etc/passwd", "quest-report")
        self.assertNotIn("/", result)
        self.assertNotIn("..", result)
        self.assertTrue(result.count(".") >= 2)

    def test_report_id_leading_dots(self):
        result = generate_filename("..hidden", "summary")
        self.assertFalse(result.startswith("."))

    def test_suffix_with_control_chars(self):
        result = generate_filename("r", "bad\nsuffix\x00")
        self.assertNotIn("\n", result)


if __name__ == "__main__":
    unittest.main()
