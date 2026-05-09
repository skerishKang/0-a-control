from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from scripts import db as _db


DEFAULT_STORE_PATH = _db.ROOT_DIR / "data" / "runtime" / "ops_overrides.json"
MANUAL_STATUSES = {
    "READY",
    "IN_PROGRESS",
    "BLOCKED",
    "NEEDS_IMPLEMENTATION",
    "NEEDS_REVIEW",
    "NEEDS_VALIDATION",
    "DONE",
    "NO_ACTION",
    "PINNED",
    "WATCH",
    "IGNORE_UNTIL",
    "DO_NOT_MERGE",
    "DO_NOT_CLOSE",
}
TARGET_TYPES = {"issue", "pr", "quest", "plan", "session", "source", "global"}
PRIORITIES = {"P0", "P1", "P2", "P3"}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _read_store(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"version": 1, "overrides": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"override store is invalid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("override store root must be an object")
    overrides = data.get("overrides", [])
    if not isinstance(overrides, list):
        raise ValueError("override store overrides must be a list")
    return {"version": data.get("version", 1), "overrides": overrides}


def _write_store(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp_path.replace(path)


def _validate_payload(payload: dict[str, Any], partial: bool = False) -> None:
    required = ("target_type", "target_id", "manual_status", "reason")
    if not partial:
        for key in required:
            if not str(payload.get(key, "")).strip():
                raise ValueError(f"{key} is required")

    target_type = payload.get("target_type")
    if target_type is not None and target_type not in TARGET_TYPES:
        raise ValueError("target_type is invalid")

    manual_status = payload.get("manual_status")
    if manual_status is not None and manual_status not in MANUAL_STATUSES:
        raise ValueError("manual_status is invalid")

    priority = payload.get("priority")
    if priority not in (None, "") and priority not in PRIORITIES:
        raise ValueError("priority is invalid")

    if "reason" in payload and not str(payload.get("reason", "")).strip():
        raise ValueError("reason is required")


def list_manual_overrides(
    *,
    path: Path = DEFAULT_STORE_PATH,
    include_inactive: bool = False,
    target_type: str | None = None,
    target_id: str | None = None,
) -> list[dict[str, Any]]:
    data = _read_store(path)
    results: list[dict[str, Any]] = []
    for item in data["overrides"]:
        if not include_inactive and not item.get("is_active", True):
            continue
        if target_type and item.get("target_type") != target_type:
            continue
        if target_id and item.get("target_id") != target_id:
            continue
        results.append(dict(item))
    return results


def create_manual_override(payload: dict[str, Any], *, path: Path = DEFAULT_STORE_PATH) -> dict[str, Any]:
    _validate_payload(payload)
    data = _read_store(path)
    now = _utc_now()
    record = {
        "id": payload.get("id") or f"override-{uuid4().hex[:12]}",
        "target_type": str(payload["target_type"]).strip(),
        "target_id": str(payload["target_id"]).strip(),
        "manual_status": str(payload["manual_status"]).strip(),
        "reason": str(payload["reason"]).strip(),
        "note": str(payload.get("note", "")).strip(),
        "priority": payload.get("priority") or "",
        "expires_at": payload.get("expires_at") or "",
        "created_at": payload.get("created_at") or now,
        "updated_at": now,
        "created_by": payload.get("created_by") or "",
        "source": payload.get("source") or "manual",
        "is_active": bool(payload.get("is_active", True)),
    }
    data["overrides"].append(record)
    _write_store(path, data)
    return dict(record)


def update_manual_override(
    override_id: str,
    updates: dict[str, Any],
    *,
    path: Path = DEFAULT_STORE_PATH,
) -> dict[str, Any]:
    if not override_id:
        raise ValueError("override_id is required")
    if not updates:
        raise ValueError("updates are required")
    _validate_payload(updates, partial=True)

    data = _read_store(path)
    for item in data["overrides"]:
        if item.get("id") != override_id:
            continue
        for key in (
            "manual_status",
            "reason",
            "note",
            "priority",
            "expires_at",
            "created_by",
            "source",
            "is_active",
        ):
            if key in updates:
                value = updates[key]
                item[key] = value if isinstance(value, bool) else str(value).strip()
        item["updated_at"] = _utc_now()
        _write_store(path, data)
        return dict(item)
    raise ValueError("override not found")


def deactivate_manual_override(override_id: str, *, path: Path = DEFAULT_STORE_PATH) -> dict[str, Any]:
    return update_manual_override(override_id, {"is_active": False}, path=path)


def is_stale_manual_override(record: dict[str, Any], *, now: datetime | None = None) -> bool:
    now = now or datetime.now(timezone.utc)
    expires_at = str(record.get("expires_at", "")).strip()
    if expires_at:
        try:
            expires = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
            if expires < now:
                return True
        except ValueError:
            return True

    updated_at = str(record.get("updated_at", "")).strip()
    if not updated_at:
        return True
    try:
        updated = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
    except ValueError:
        return True
    return (now - updated).days >= 14
