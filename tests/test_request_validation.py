from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.request_validation import ROUTE_SCHEMAS, validate_mutation_body


class RequestValidationTests(unittest.TestCase):
    def test_sessions_start_valid(self) -> None:
        self.assertIsNone(validate_mutation_body(
            "/api/sessions/start",
            {"agent_name": "agent", "source_type": "manual"},
        ))

    def test_sessions_start_requires_source_type(self) -> None:
        result = validate_mutation_body("/api/sessions/start", {"agent_name": "agent"})
        self.assertIsNotNone(result)

    def test_sessions_start_allows_future_fields(self) -> None:
        self.assertIsNone(validate_mutation_body(
            "/api/sessions/start",
            {"agent_name": "agent", "source_type": "manual", "future_field": "ok"},
        ))

    def test_sessions_log_valid(self) -> None:
        self.assertIsNone(validate_mutation_body(
            "/api/sessions/log",
            {
                "session_id": "s1",
                "source_name": "kilo",
                "source_type": "agent_turn",
                "content": "hello",
            },
        ))

    def test_sessions_log_requires_content(self) -> None:
        result = validate_mutation_body(
            "/api/sessions/log",
            {"session_id": "s1", "source_name": "kilo", "source_type": "agent_turn"},
        )
        self.assertIsNotNone(result)

    def test_sessions_log_limits_content_length(self) -> None:
        result = validate_mutation_body(
            "/api/sessions/log",
            {
                "session_id": "s1",
                "source_name": "kilo",
                "source_type": "agent_turn",
                "content": "x" * 300000,
            },
        )
        self.assertIsNotNone(result)

    def test_sessions_log_metadata_must_be_object(self) -> None:
        result = validate_mutation_body(
            "/api/sessions/log",
            {
                "session_id": "s1",
                "source_name": "kilo",
                "source_type": "agent_turn",
                "content": "hello",
                "metadata": "text",
            },
        )
        self.assertIsNotNone(result)

    def test_sessions_end_valid(self) -> None:
        self.assertIsNone(validate_mutation_body(
            "/api/sessions/end",
            {"session_id": "s1", "summary_md": "done", "files_touched": ["a.py"]},
        ))

    def test_sessions_end_default_status_applied(self) -> None:
        body = {"session_id": "s1"}
        self.assertIsNone(validate_mutation_body("/api/sessions/end", body))
        self.assertEqual(body["status"], "closed")

    def test_sessions_end_rejects_wrong_status_type(self) -> None:
        self.assertIsNotNone(validate_mutation_body("/api/sessions/end", {"session_id": "s1", "status": 42}))

    def test_quests_evaluate_valid(self) -> None:
        self.assertIsNone(validate_mutation_body(
            "/api/quests/evaluate",
            {"quest_id": "q1", "verdict": "done", "reason": "ok"},
        ))

    def test_quests_evaluate_rejects_unknown_verdict(self) -> None:
        self.assertIsNotNone(validate_mutation_body(
            "/api/quests/evaluate",
            {"quest_id": "q1", "verdict": "unknown"},
        ))

    def test_quests_evaluate_requires_verdict(self) -> None:
        self.assertIsNotNone(validate_mutation_body("/api/quests/evaluate", {"quest_id": "q1"}))

    def test_quests_report_valid(self) -> None:
        self.assertIsNone(validate_mutation_body(
            "/api/quests/report",
            {"quest_id": "q1", "work_summary": "work", "session_id": "s1"},
        ))

    def test_quests_report_requires_quest_id(self) -> None:
        self.assertIsNotNone(validate_mutation_body("/api/quests/report", {"work_summary": "work"}))

    def test_unregistered_route_allowed(self) -> None:
        self.assertIsNone(validate_mutation_body("/api/other", {"anything": "goes"}))

    def test_non_object_body_rejected_for_registered_route(self) -> None:
        result = validate_mutation_body("/api/sessions/start", [])
        self.assertIsNotNone(result)

    def test_registered_routes(self) -> None:
        self.assertEqual(
            set(ROUTE_SCHEMAS),
            {
                "/api/sessions/start",
                "/api/sessions/log",
                "/api/sessions/end",
                "/api/quests/evaluate",
                "/api/quests/report",
                "/api/bridge/parse",
                "/api/bridge/quick-input",
                "/api/bridge/create-plan",
                "/api/tomorrow-first-quest/confirm",
                "/api/tomorrow-first-quest/promote",
                "/api/tomorrow-first-quest/clear",
                "/api/agents/cleanup-stale",
                "/api/executor-prompts/generate",
            },
        )

    def test_bridge_parse_valid(self) -> None:
        self.assertIsNone(validate_mutation_body("/api/bridge/parse", {"text": "hello"}))

    def test_bridge_parse_requires_text(self) -> None:
        self.assertIsNotNone(validate_mutation_body("/api/bridge/parse", {}))

    def test_bridge_parse_rejects_non_string_text(self) -> None:
        self.assertIsNotNone(validate_mutation_body("/api/bridge/parse", {"text": 123}))

    def test_bridge_quick_input_valid(self) -> None:
        self.assertIsNone(validate_mutation_body(
            "/api/bridge/quick-input",
            {"text": "add task to short term"},
        ))

    def test_bridge_quick_input_requires_text(self) -> None:
        self.assertIsNotNone(validate_mutation_body("/api/bridge/quick-input", {}))

    def test_bridge_create_plan_valid(self) -> None:
        self.assertIsNone(validate_mutation_body(
            "/api/bridge/create-plan",
            {"candidates": [{"title": "Plan A", "reason": "important"}]},
        ))

    def test_bridge_create_plan_requires_candidates(self) -> None:
        self.assertIsNotNone(validate_mutation_body("/api/bridge/create-plan", {}))

    def test_bridge_create_plan_rejects_empty_array(self) -> None:
        self.assertIsNotNone(validate_mutation_body("/api/bridge/create-plan", {"candidates": []}))

    def test_bridge_create_plan_rejects_non_array(self) -> None:
        self.assertIsNotNone(validate_mutation_body("/api/bridge/create-plan", {"candidates": "string"}))

    def test_tomorrow_first_quest_confirm_valid(self) -> None:
        self.assertIsNone(validate_mutation_body(
            "/api/tomorrow-first-quest/confirm",
            {"title": "Investigate X"},
        ))

    def test_tomorrow_first_quest_confirm_requires_title(self) -> None:
        self.assertIsNotNone(validate_mutation_body("/api/tomorrow-first-quest/confirm", {}))

    def test_tomorrow_first_quest_confirm_source_default(self) -> None:
        body = {"title": "Task"}
        self.assertIsNone(validate_mutation_body("/api/tomorrow-first-quest/confirm", body))
        self.assertEqual(body["source"], "manual")

    def test_tomorrow_first_quest_promote_valid_empty_body(self) -> None:
        self.assertIsNone(validate_mutation_body("/api/tomorrow-first-quest/promote", {}))

    def test_tomorrow_first_quest_promote_valid_with_extra(self) -> None:
        self.assertIsNone(validate_mutation_body(
            "/api/tomorrow-first-quest/promote",
            {"unexpected": "field"},
        ))

    def test_tomorrow_first_quest_clear_valid_empty_body(self) -> None:
        self.assertIsNone(validate_mutation_body("/api/tomorrow-first-quest/clear", {}))

    def test_agents_cleanup_stale_valid(self) -> None:
        self.assertIsNone(validate_mutation_body(
            "/api/agents/cleanup-stale",
            {"agent_name": "kilo"},
        ))

    def test_agents_cleanup_stale_requires_agent_name(self) -> None:
        self.assertIsNotNone(validate_mutation_body("/api/agents/cleanup-stale", {}))

    def test_executor_prompt_generate_valid(self) -> None:
        self.assertIsNone(validate_mutation_body(
            "/api/executor-prompts/generate",
            {"prompt_type": "code_review"},
        ))

    def test_executor_prompt_generate_requires_prompt_type(self) -> None:
        self.assertIsNotNone(validate_mutation_body("/api/executor-prompts/generate", {}))


if __name__ == "__main__":
    unittest.main()
