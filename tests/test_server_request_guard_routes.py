import sys
import unittest
from email.message import Message
from http import HTTPStatus
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.server import ControlTowerHandler


class _CapturingControlTowerHandler(ControlTowerHandler):
    def __init__(self, method_path, client_host, host_header="127.0.0.1:4310"):
        self.path = method_path
        self.client_address = (client_host, 12345)
        self.headers = Message()
        self.headers["Host"] = host_header
        self.json_response = None
        self.dispatched = False
        self.parsed_body = False

    def send_json(self, payload, status=HTTPStatus.OK):
        self.json_response = {"payload": payload, "status": status}

    def handle_api_get_dispatch(self, path, query):
        self.dispatched = True
        self.send_json({"ok": True, "path": path})

    def handle_api_post_dispatch(self, path, body):
        self.dispatched = True
        self.send_json({"ok": True, "path": path})

    def _parse_and_validate_request(self):
        self.parsed_body = True
        return {}


class ApiRouteGuardDispatchTests(unittest.TestCase):
    def test_get_api_route_rejects_nonlocal_before_dispatch(self):
        handler = _CapturingControlTowerHandler(
            "/api/current-state",
            "192.168.0.20",
            host_header="127.0.0.1:4310",
        )
        handler.do_GET()
        self.assertFalse(handler.dispatched)
        self.assertEqual(handler.json_response["status"], HTTPStatus.FORBIDDEN)
        self.assertEqual(handler.json_response["payload"]["error"], "read requests are restricted to local clients")

    def test_get_health_route_remains_public_safe(self):
        handler = _CapturingControlTowerHandler(
            "/api/health",
            "192.168.0.20",
            host_header="remote.example",
        )
        handler.do_GET()
        self.assertTrue(handler.dispatched)
        self.assertEqual(handler.json_response["status"], HTTPStatus.OK)
        self.assertEqual(handler.json_response["payload"], {"ok": True, "path": "/api/health"})

    def test_post_api_route_rejects_nonlocal_before_body_parse(self):
        handler = _CapturingControlTowerHandler(
            "/api/sessions/start",
            "192.168.0.20",
            host_header="127.0.0.1:4310",
        )
        handler.do_POST()
        self.assertFalse(handler.dispatched)
        self.assertFalse(handler.parsed_body)
        self.assertEqual(handler.json_response["status"], HTTPStatus.FORBIDDEN)
        self.assertEqual(handler.json_response["payload"]["error"], "mutation requests are restricted to local clients")


if __name__ == "__main__":
    unittest.main()
