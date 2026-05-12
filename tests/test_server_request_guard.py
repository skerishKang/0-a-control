import os
import sys
import unittest
from email.message import Message
from pathlib import Path
from unittest.mock import patch


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.server_request_guard import mutation_request_allowed, read_request_allowed


class _DummyHandler:
    def __init__(self, client_host, host_header="127.0.0.1:4310", origin_header=None):
        self.client_address = (client_host, 12345)
        self.headers = Message()
        if host_header is not None:
            self.headers["Host"] = host_header
        if origin_header is not None:
            self.headers["Origin"] = origin_header


class ServerRequestGuardTests(unittest.TestCase):
    def test_allows_loopback_client_with_local_host(self):
        handler = _DummyHandler("127.0.0.1", host_header="localhost:4310")
        self.assertTrue(mutation_request_allowed(handler))

    def test_allows_ipv6_loopback_client(self):
        handler = _DummyHandler("::1", host_header="[::1]:4310")
        self.assertTrue(mutation_request_allowed(handler))

    def test_rejects_non_loopback_client_by_default(self):
        handler = _DummyHandler("192.168.0.20", host_header="127.0.0.1:4310")
        self.assertFalse(mutation_request_allowed(handler))

    def test_rejects_non_local_host_header(self):
        handler = _DummyHandler("127.0.0.1", host_header="example.com")
        self.assertFalse(mutation_request_allowed(handler))

    def test_rejects_non_local_origin_header(self):
        handler = _DummyHandler(
            "127.0.0.1",
            host_header="127.0.0.1:4310",
            origin_header="https://example.com",
        )
        self.assertFalse(mutation_request_allowed(handler))

    def test_explicit_env_override_allows_nonlocal_client(self):
        handler = _DummyHandler("192.168.0.20", host_header="example.com")
        with patch.dict(os.environ, {"CONTROL_TOWER_ALLOW_NONLOCAL_MUTATIONS": "1"}):
            self.assertTrue(mutation_request_allowed(handler))


class ReadRequestGuardTests(unittest.TestCase):
    def test_health_endpoint_always_allowed(self):
        handler = _DummyHandler("192.168.0.20", host_header="example.com")
        self.assertTrue(read_request_allowed(handler, "/api/health"))

    def test_sensitive_get_rejects_non_loopback_by_default(self):
        handler = _DummyHandler("192.168.0.20", host_header="127.0.0.1:4310")
        self.assertFalse(read_request_allowed(handler, "/api/current-state"))

    def test_sensitive_get_allows_loopback_with_local_host(self):
        handler = _DummyHandler("127.0.0.1", host_header="localhost:4310")
        self.assertTrue(read_request_allowed(handler, "/api/current-state"))

    def test_sensitive_get_rejects_non_local_host_header(self):
        handler = _DummyHandler("127.0.0.1", host_header="example.com")
        self.assertFalse(read_request_allowed(handler, "/api/current-state"))

    def test_sensitive_get_rejects_non_local_origin(self):
        handler = _DummyHandler(
            "127.0.0.1",
            host_header="127.0.0.1:4310",
            origin_header="https://attacker.com",
        )
        self.assertFalse(read_request_allowed(handler, "/api/current-state"))

    def test_sensitive_get_allows_ipv6_loopback(self):
        handler = _DummyHandler("::1", host_header="[::1]:4310")
        self.assertTrue(read_request_allowed(handler, "/api/plans"))

    def test_env_override_allows_nonlocal_sensitive_read(self):
        handler = _DummyHandler("192.168.0.20", host_header="example.com")
        with patch.dict(os.environ, {"CONTROL_TOWER_ALLOW_NONLOCAL_READS": "1"}):
            self.assertTrue(read_request_allowed(handler, "/api/current-state"))


if __name__ == "__main__":
    unittest.main()
