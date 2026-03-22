import sys
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.server import ControlTowerHandler


class _DummyHandler:
    def __init__(self):
        self.called = None
        self.called_path = None
        self.called_query = None
        self.payload = None
        self.error = None

    def __getattr__(self, name):
        if name.startswith("_get_") or name.startswith("_post_"):
            return lambda *args, **kwargs: None
        raise AttributeError(name)

    def _get_agents_status(self, query):
        self.called = "agents"
        self.called_query = query

    def _post_agents_cleanup_stale(self, body):
        self.called = "cleanup_stale"
        self.called_query = body

    def _get_sessions_view(self, path, query):
        self.called = "session_view"
        self.called_path = path
        self.called_query = query

    def send_error(self, status, message):
        self.error = (status, message)

    def send_json(self, payload, status=None):
        self.payload = (payload, status)


class ServerRouteTests(unittest.TestCase):
    def test_exact_route_dispatches_agents_status(self):
        handler = _DummyHandler()
        ControlTowerHandler.handle_api_get_dispatch(handler, "/api/agents/status", {})
        self.assertEqual(handler.called, "agents")
        self.assertIsNone(handler.error)

    def test_prefix_route_dispatches_session_view(self):
        handler = _DummyHandler()
        ControlTowerHandler.handle_api_get_dispatch(handler, "/api/sessions/view/session-123", {"limit": ["10"]})
        self.assertEqual(handler.called, "session_view")
        self.assertEqual(handler.called_path, "/api/sessions/view/session-123")
        self.assertEqual(handler.called_query, {"limit": ["10"]})

    def test_unknown_route_returns_404(self):
        handler = _DummyHandler()
        ControlTowerHandler.handle_api_get_dispatch(handler, "/api/does-not-exist", {})
        self.assertIsNone(handler.called)
        self.assertIsNotNone(handler.error)

    def test_get_agents_status_returns_payload(self):
        handler = _DummyHandler()
        with patch("scripts.server.get_agent_statuses", return_value=[{"canonical_name": "codex", "status": "idle"}]):
            ControlTowerHandler._get_agents_status(handler, {})
        self.assertEqual(handler.payload[0]["agents"][0]["canonical_name"], "codex")

    def test_post_route_dispatches_cleanup_stale(self):
        handler = _DummyHandler()
        ControlTowerHandler.handle_api_post_dispatch(handler, "/api/agents/cleanup-stale", {"agent_name": "codex"})
        self.assertEqual(handler.called, "cleanup_stale")
        self.assertEqual(handler.called_query, {"agent_name": "codex"})


if __name__ == "__main__":
    unittest.main()
