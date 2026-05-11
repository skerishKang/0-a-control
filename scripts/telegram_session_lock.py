from __future__ import annotations

import atexit
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

if __package__ in (None, ""):
    from scripts.telegram_db import DATA_DIR
else:
    from .telegram_db import DATA_DIR


RUNTIME_DIR = Path(DATA_DIR) / "runtime"
SESSION_LOCK_FILE = RUNTIME_DIR / "telegram_userbot.lock"
TELEGRAM_SESSION_LOCK_TTL_SECONDS = 7200
TELEGRAM_SESSION_LOCK_WAIT_SECONDS = 5

_SESSION_LOCK_HELD = False


def _runtime_dir() -> Path:
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    return RUNTIME_DIR


class TelegramSessionBusyError(RuntimeError):
    pass


def _read_session_lock() -> dict | None:
    try:
        raw = SESSION_LOCK_FILE.read_text(encoding="utf-8")
        data = json.loads(raw)
        if isinstance(data, dict):
            return data
    except FileNotFoundError:
        return None
    except Exception:
        return None
    return None


def _pid_alive(pid: int | None) -> bool:
    if not pid or pid <= 0:
        return False
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def get_telegram_session_lock_status() -> dict:
    payload = _read_session_lock()
    if not payload:
        return {"locked": False, "lock_file": str(SESSION_LOCK_FILE)}

    acquired_at = payload.get("acquired_at")
    age_seconds = None
    if acquired_at:
        try:
            age_seconds = int((datetime.now(timezone.utc) - datetime.fromisoformat(acquired_at)).total_seconds())
        except Exception:
            age_seconds = None

    return {
        "locked": True,
        "lock_file": str(SESSION_LOCK_FILE),
        "pid": payload.get("pid"),
        "command": payload.get("command"),
        "acquired_at": acquired_at,
        "age_seconds": age_seconds,
        "pid_alive": _pid_alive(payload.get("pid")),
    }


def _clear_session_lock() -> None:
    global _SESSION_LOCK_HELD
    if not _SESSION_LOCK_HELD:
        return
    try:
        payload = _read_session_lock()
        if payload and payload.get("pid") not in (None, os.getpid()):
            return
        SESSION_LOCK_FILE.unlink(missing_ok=True)
    finally:
        _SESSION_LOCK_HELD = False


atexit.register(_clear_session_lock)


def acquire_telegram_session_lock(wait_seconds: int = TELEGRAM_SESSION_LOCK_WAIT_SECONDS) -> None:
    global _SESSION_LOCK_HELD
    _runtime_dir()
    deadline = time.monotonic() + max(0, wait_seconds)
    payload = {
        "pid": os.getpid(),
        "command": " ".join(os.sys.argv),
        "acquired_at": datetime.now(timezone.utc).isoformat(),
    }

    while True:
        try:
            fd = os.open(str(SESSION_LOCK_FILE), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(payload, handle, ensure_ascii=False, indent=2)
            _SESSION_LOCK_HELD = True
            return
        except FileExistsError:
            current = _read_session_lock() or {}
            acquired_at = current.get("acquired_at")
            is_stale = False
            if acquired_at:
                try:
                    age = (datetime.now(timezone.utc) - datetime.fromisoformat(acquired_at)).total_seconds()
                    is_stale = age > TELEGRAM_SESSION_LOCK_TTL_SECONDS
                except Exception:
                    is_stale = True
            current_pid = current.get("pid")
            if is_stale or not _pid_alive(current_pid):
                try:
                    SESSION_LOCK_FILE.unlink(missing_ok=True)
                except OSError:
                    pass
                continue

            if time.monotonic() >= deadline:
                detail = f"pid={current_pid}"
                if current.get("command"):
                    detail += f", command={current['command']}"
                raise TelegramSessionBusyError(
                    f"Telegram 세션이 다른 작업에서 사용 중입니다 ({detail})."
                )
            time.sleep(1)