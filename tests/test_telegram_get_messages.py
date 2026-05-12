import os
import sys
import unittest
from email.message import Message
from http import HTTPStatus
from pathlib import Path
from unittest.mock import MagicMock, patch


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.server_handlers.server_get_routes import handle_get_telegram_messages


class _DummyHandler:
    def __init__(self):
        self.sent = None
        self.status = None

    def send_json(self, data, status=HTTPStatus.OK):
        self.sent = data
        self.status = status


class TelegramGetMessagesSideEffectTests(unittest.TestCase):
    """GET /api/telegram/messages must not trigger attachment downloads."""

    def test_fetch_messages_called_with_download_attachments_false(self):
        """Verify handle_get_telegram_messages passes download_attachments=False."""
        handler = _DummyHandler()
        query = {"chat_id": ["test_chat"], "limit": ["10"]}

        with patch(
            "scripts.server_handlers.server_get_routes._get_db",
            return_value={
                "parse_limit": lambda q, k, d, m: int(q.get(k, [str(d)])[0]),
                "fetch_messages": MagicMock(return_value=[]),
            },
        ) as mock_get_db:
            handle_get_telegram_messages(handler, query)

            fetch_messages_fn = mock_get_db.return_value["fetch_messages"]
            fetch_messages_fn.assert_called_once_with(
                "test_chat", limit=10, download_attachments=False
            )

    def test_missing_chat_id_returns_bad_request(self):
        """Verify missing chat_id yields 400 without calling fetch_messages."""
        handler = _DummyHandler()
        query = {}

        with patch(
            "scripts.server_handlers.server_get_routes._get_db",
            return_value={
                "fetch_messages": MagicMock(),
            },
        ):
            handle_get_telegram_messages(handler, query)

        self.assertEqual(handler.status, HTTPStatus.BAD_REQUEST)
        self.assertIn("error", handler.sent)

    def test_response_contains_messages(self):
        """Verify the response includes the fetched messages."""
        handler = _DummyHandler()
        query = {"chat_id": ["chat_1"], "limit": ["5"]}

        with patch(
            "scripts.server_handlers.server_get_routes._get_db",
            return_value={
                "parse_limit": lambda q, k, d, m: int(q.get(k, [str(d)])[0]),
                "fetch_messages": MagicMock(return_value=[{"id": 1}]),
            },
        ):
            handle_get_telegram_messages(handler, query)

        self.assertEqual(handler.status, HTTPStatus.OK)
        self.assertEqual(handler.sent["messages"], [{"id": 1}])
        self.assertEqual(handler.sent["chat_id"], "chat_1")
