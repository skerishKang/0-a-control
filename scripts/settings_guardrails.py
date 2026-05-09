from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any, Mapping


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = "4310"

STATUS_OK = "ok"
STATUS_INFO = "info"
STATUS_WARNING = "warning"
STATUS_BLOCKED = "blocked"


def _truthy(value: str | None) -> bool:
    if value is None:
        return False
    return value.strip().lower() in {"1", "true", "yes", "on", "debug"}


def _configured(env: Mapping[str, str], key: str) -> bool:
    return bool((env.get(key) or "").strip())


def _host_status(host: str) -> dict[str, str]:
    normalized = (host or DEFAULT_HOST).strip()
    if normalized in {"127.0.0.1", "localhost", "::1"}:
        return {
            "code": "LOCAL_ONLY_SAFE",
            "level": STATUS_OK,
            "message": "Server is configured for local-only access.",
        }
    if normalized == "0.0.0.0":
        return {
            "code": "LAN_EXPOSED",
            "level": STATUS_WARNING,
            "message": "Server is bound to all interfaces; use only with network controls.",
        }
    return {
        "code": "CUSTOM_HOST",
        "level": STATUS_INFO,
        "message": "Server uses a custom host binding.",
    }


def build_settings_status(
    env: Mapping[str, str] | None = None,
    project_root: Path | None = None,
) -> dict[str, Any]:
    env = env or os.environ
    root = project_root or Path.cwd()

    host = (env.get("HOST") or DEFAULT_HOST).strip() or DEFAULT_HOST
    port = (env.get("PORT") or DEFAULT_PORT).strip() or DEFAULT_PORT
    debug_enabled = _truthy(env.get("DEBUG"))

    telegram_api_id_configured = _configured(env, "TELEGRAM_API_ID")
    telegram_api_hash_configured = _configured(env, "TELEGRAM_API_HASH")
    telegram_configured = telegram_api_id_configured and telegram_api_hash_configured

    session_path_raw = (env.get("CONTROL_TOWER_TELEGRAM_SESSION_PATH") or "").strip()
    session_path_present = False
    if session_path_raw:
        session_path_present = Path(session_path_raw).expanduser().exists()

    data_dir = root / "data"
    runtime_dir = data_dir / "runtime"

    return {
        "host": host,
        "port": port,
        "debug_enabled": debug_enabled,
        "python_version": sys.version.split()[0],
        "project_root": str(root),
        "data_dir": str(data_dir),
        "runtime_dir": str(runtime_dir),
        "telegram": {
            "api_id_configured": telegram_api_id_configured,
            "api_hash_configured": telegram_api_hash_configured,
            "configured": telegram_configured,
            "session_path_configured": bool(session_path_raw),
            "session_path_present": session_path_present,
        },
    }


def build_guardrails_status(
    env: Mapping[str, str] | None = None,
    project_root: Path | None = None,
) -> dict[str, Any]:
    settings = build_settings_status(env=env, project_root=project_root)
    checks: list[dict[str, str]] = []

    checks.append(_host_status(settings["host"]))

    if settings["debug_enabled"]:
        checks.append({
            "code": "DEBUG_ENABLED",
            "level": STATUS_WARNING,
            "message": "DEBUG is enabled; use only for temporary diagnostics.",
        })

    if not settings["telegram"]["configured"]:
        checks.append({
            "code": "TELEGRAM_NOT_CONFIGURED",
            "level": STATUS_INFO,
            "message": "Telegram sync is optional and not fully configured.",
        })

    if settings["telegram"]["session_path_present"]:
        checks.append({
            "code": "TELEGRAM_SESSION_PRESENT",
            "level": STATUS_INFO,
            "message": "Telegram session file is present; treat it as sensitive.",
        })

    checks.append({
        "code": "BACKUP_NOT_CONFIRMED",
        "level": STATUS_INFO,
        "message": "Backup status is not yet automatically verified.",
    })

    highest_level = STATUS_OK
    if any(check["level"] == STATUS_BLOCKED for check in checks):
        highest_level = STATUS_BLOCKED
    elif any(check["level"] == STATUS_WARNING for check in checks):
        highest_level = STATUS_WARNING
    elif any(check["level"] == STATUS_INFO for check in checks):
        highest_level = STATUS_INFO

    return {
        "overall_level": highest_level,
        "checks": checks,
        "settings": settings,
    }
