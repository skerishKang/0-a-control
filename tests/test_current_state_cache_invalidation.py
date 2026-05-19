from __future__ import annotations

import unittest
from http import HTTPStatus
from unittest.mock import patch

from scripts.server_handlers.server_post_routes import handle_post_dispatch


class _DummyHandler:
    def __init__(self) -> None:
        self.called = False
        self.response = None
        self.error = None

    def _post_sessions_start(self, body):
        self.called = True

    def send_json(self, payload, status=HTTPStatus.OK):
        self.response = {"payload": payload, "status": status}

    def send_error(self, status, message):
        self.error = {"status": status, "message": message}


class CurrentStateCacheInvalidationTests(unittest.TestCase):
    def test_registered_mutation_clears_cache_before_dispatch(self) -> None:
        handler = _DummyHandler()
        calls = []

        with patch("scripts.server_handlers.server_post_routes._clear_current_state_cache", side_effect=lambda: calls.append("clear")):
            handle_post_dispatch(
                handler,
                "/api/sessions/start",
                {"agent_name": "agent", "source_type": "manual"},
            )

        self.assertEqual(calls, ["clear"])
        self.assertTrue(handler.called)

    def test_invalid_registered_mutation_does_not_clear_cache(self) -> None:
        handler = _DummyHandler()
        calls = []

        with patch("scripts.server_handlers.server_post_routes._clear_current_state_cache", side_effect=lambda: calls.append("clear")):
            handle_post_dispatch(handler, "/api/sessions/start", {"agent_name": "agent"})

        self.assertEqual(calls, [])
        self.assertFalse(handler.called)
        self.assertEqual(handler.response["status"], HTTPStatus.BAD_REQUEST)


if __name__ == "__main__":
    unittest.main()
