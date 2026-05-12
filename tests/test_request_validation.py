"""Tests for route-level JSON schema validation on mutation APIs."""

import json
import os
import sys
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.request_validation import (
    ROUTE_SCHEMAS,
    validate_mutation_body,
)


class RequestValidationTests(unittest.TestCase):
    """Tests for request body validation against JSON schemas."""

    def test_sessions_start_valid(self):
        result = validate_mutation_body("/api/sessions/start", {
            "agent_name": "test-agent",
            "source_type": "manual",
        })
        self.assertIsNone(result)

    def test_sessions_start_missing_required(self):
        result = validate_mutation_body("/api/sessions/start", {
            "agent_name": "test-agent",
        })
        self.assertIsNotNone(result)
        self.assertEqual(result["error"], "invalid request body")
        self.assertTrue(any("source_type" in d for d in result["detail"]))

    def test_sessions_start_extra_property(self):
        result = validate_mutation_body("/api/sessions/start", {
            "agent_name": "test-agent",
            "source_type": "manual",
            "unknown_field": "should not be here",
        })
        self.assertIsNotNone(result)

    def test_sessions_log_valid(self):
        result = validate_mutation_body("/api/sessions/log", {
            "session_id": "abc-123",
            "source_name": "kilo",
            "source_type": "agent_turn",
            "content": "Hello world",
        })
        self.assertIsNone(result)

    def test_sessions_log_missing_content(self):
        result = validate_mutation_body("/api/sessions/log", {
            "session_id": "abc-123",
            "source_name": "kilo",
            "source_type": "agent_turn",
        })
        self.assertIsNotNone(result)

    def test_sessions_log_oversized_content(self):
        result = validate_mutation_body("/api/sessions/log", {
            "session_id": "abc-123",
            "source_name": "kilo",
            "source_type": "agent_turn",
            "content": "x" * 300000,  # exceeds maxLength 200000
        })
        self.assertIsNotNone(result)

    def test_sessions_end_valid(self):
        result = validate_mutation_body("/api/sessions/end", {
            "session_id": "abc-123",
            "summary_md": "Session complete",
            "status": "closed",
            "files_touched": ["file1.py", "file2.js"],
        })
        self.assertIsNone(result)

    def test_sessions_end_default_status_applied(self):
        result = validate_mutation_body("/api/sessions/end", {
            "session_id": "abc-123",
        })
        self.assertIsNone(result)

    def test_sessions_end_invalid_status_type(self):
        result = validate_mutation_body("/api/sessions/end", {
            "session_id": "abc-123",
            "status": 42,
        })
        self.assertIsNotNone(result)

    def test_quests_evaluate_valid(self):
        result = validate_mutation_body("/api/quests/evaluate", {
            "quest_id": "q-1",
            "verdict": "done",
            "reason": "Completed successfully",
        })
        self.assertIsNone(result)

    def test_quests_evaluate_invalid_verdict(self):
        result = validate_mutation_body("/api/quests/evaluate", {
            "quest_id": "q-1",
            "verdict": "invalid_verdict",
        })
        self.assertIsNotNone(result)

    def test_quests_evaluate_missing_verdict(self):
        result = validate_mutation_body("/api/quests/evaluate", {
            "quest_id": "q-1",
        })
        self.assertIsNotNone(result)

    def test_quests_report_valid(self):
        result = validate_mutation_body("/api/quests/report", {
            "quest_id": "q-1",
            "work_summary": "Did some work",
            "session_id": "s-1",
        })
        self.assertIsNone(result)

    def test_quests_report_missing_quest_id(self):
        result = validate_mutation_body("/api/quests/report", {
            "work_summary": "Did some work",
        })
        self.assertIsNotNone(result)

    def test_unregistered_route_allowed(self):
        """Routes without a registered schema should pass through."""
        result = validate_mutation_body("/api/unknown-route", {"anything": "goes"})
        self.assertIsNone(result)

    def test_all_registered_routes_exist(self):
        """Verify expected routes have schemas."""
        expected = {
            "/api/sessions/start",
            "/api/sessions/log",
            "/api/sessions/end",
            "/api/quests/evaluate",
            "/api/quests/report",
        }
        self.assertEqual(set(ROUTE_SCHEMAS.keys()), expected)


if __name__ == "__main__":
    unittest.main()
