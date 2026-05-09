from __future__ import annotations

import sys
import time
import subprocess
import signal
import os
import json
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

# Enable both `python scripts/foo.py` and `python -m scripts.foo`
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Configuration
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "4310"))
BASE_URL = f"http://{HOST}:{PORT}"
HEALTH_ENDPOINT = "/api/health"
BOARD_V2_HTML = "/board-v2.html"
API_ENDPOINTS = [
    "/api/current-state",
    "/api/briefs/latest?limit=3",
    "/api/sessions/recent?limit=50",
    "/api/quests",
    "/api/plans",
]

OPS_OVERRIDES_ENDPOINT = "/api/ops-overrides"

# Timeouts
SERVER_START_TIMEOUT = 10  # seconds to wait for server to start
REQUEST_TIMEOUT = 5        # seconds per request


def log_status(label: str, status: str) -> None:
    """Print sanitized PASS/FAIL status line."""
    print(f"{label}: {status}")


def start_server_subprocess() -> subprocess.Popen | None:
    """Start the server as a subprocess using the existing entrypoint."""
    server_script = Path(__file__).parent / "server.py"
    if not server_script.exists():
        log_status("SERVER_START", "FAIL — scripts/server.py not found")
        return None

    try:
        # Windows: use CREATE_NEW_PROCESS_GROUP to enable CTRL_BREAK_EVENT
        CreationFlags = 0
        if os.name == "nt":
            CreationFlags = subprocess.CREATE_NEW_PROCESS_GROUP

        proc = subprocess.Popen(
            [sys.executable, str(server_script)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            cwd=project_root,
            creationflags=CreationFlags,
        )
        return proc
    except Exception as exc:
        log_status("SERVER_START", f"FAIL — {type(exc).__name__}: {exc}")
        return None


def wait_for_health(timeout: int = SERVER_START_TIMEOUT) -> bool:
    """Poll health endpoint until it responds OK or timeout."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            req = Request(f"{BASE_URL}{HEALTH_ENDPOINT}", method="GET")
            resp = urlopen(req, timeout=REQUEST_TIMEOUT)
            if resp.status == 200:
                data = resp.read()
                payload = json.loads(data.decode("utf-8"))
                if payload.get("ok") is True:
                    return True
        except (URLError, HTTPError, json.JSONDecodeError, ValueError):
            pass
        time.sleep(0.5)
    return False


def check_url(path: str, expect_json: bool = True) -> bool:
    """Request a URL path and verify it returns 200 (and valid JSON if expect_json)."""
    try:
        req = Request(f"{BASE_URL}{path}", method="GET")
        resp = urlopen(req, timeout=REQUEST_TIMEOUT)
        if resp.status != 200:
            return False
        if expect_json:
            data = resp.read()
            json.loads(data.decode("utf-8"))
        return True
    except (URLError, HTTPError, json.JSONDecodeError, ValueError):
        return False


def main() -> int:
    server_proc = None
    try:
        # Step 1: Start server subprocess
        server_proc = start_server_subprocess()
        if server_proc is None:
            return 1

        log_status("SERVER_START", "PASS — subprocess launched")

        # Step 2: Wait for health endpoint
        if not wait_for_health():
            log_status("HEALTH_ENDPOINT", "FAIL — timeout or invalid response")
            return 1
        log_status("HEALTH_ENDPOINT", "PASS")

        # Step 3: Check board-v2.html is served
        if not check_url(BOARD_V2_HTML, expect_json=False):
            log_status("BOARD_V2_HTML", "FAIL — not reachable or invalid")
            return 1
        log_status("BOARD_V2_HTML", "PASS")

        # Step 4: Check required API endpoints
        all_ok = True
        for path in API_ENDPOINTS:
            if not check_url(path, expect_json=True):
                log_status("API_ENDPOINT", f"FAIL — {path}")
                all_ok = False
            else:
                log_status("API_ENDPOINT", f"PASS — {path}")

        if not all_ok:
            log_status("BOARD_V2_REQUIRED_API_ENDPOINTS", "FAIL")
            return 1

        log_status("BOARD_V2_REQUIRED_API_ENDPOINTS", "PASS")

        # Step 5: Sanitized ops-overrides availability check (fatal)
        try:
            req = Request(f"{BASE_URL}{OPS_OVERRIDES_ENDPOINT}", method="GET")
            resp = urlopen(req, timeout=REQUEST_TIMEOUT)
            if resp.status == 200:
                data = resp.read()
                payload = json.loads(data.decode("utf-8"))
                if isinstance(payload, dict) and "overrides" in payload:
                    log_status("OPS_OVERRIDES_ENDPOINT", "PASS")
                else:
                    log_status("OPS_OVERRIDES_ENDPOINT", "FAIL — missing overrides key")
                    log_status("FINAL", "FAIL")
                    return 1
            else:
                log_status("OPS_OVERRIDES_ENDPOINT", f"FAIL — HTTP {resp.status}")
                log_status("FINAL", "FAIL")
                return 1
        except Exception as exc:
            log_status("OPS_OVERRIDES_ENDPOINT", f"FAIL — {type(exc).__name__}: {exc}")
            log_status("FINAL", "FAIL")
            return 1

        log_status("FINAL", "PASS")
        return 0

    except KeyboardInterrupt:
        print("\n[INFO] Interrupted by user", file=sys.stderr)
        return 130
    finally:
        # Always terminate server subprocess
        if server_proc is not None:
            try:
                if os.name == "nt":
                    # Windows: CTRL_BREAK_EVENT requires CREATE_NEW_PROCESS_GROUP
                    server_proc.send_signal(signal.CTRL_BREAK_EVENT)
                    try:
                        server_proc.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        server_proc.kill()
                else:
                    server_proc.terminate()
                    try:
                        server_proc.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        server_proc.kill()
            except Exception:
                try:
                    server_proc.kill()
                except Exception:
                    pass


if __name__ == "__main__":
    sys.exit(main())
