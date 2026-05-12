"""Validation checklist runtime storage and API.

Stores checklists as JSON at data/runtime/validation_checklists.json.
Not committed to Git.
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STORAGE_REL = Path("data") / "runtime" / "validation_checklists.json"

# ---- helpers ----

def _storage_path() -> Path:
    """Resolve storage path relative to project root."""
    from scripts.server import ROOT_DIR
    return ROOT_DIR / STORAGE_REL


def _read_all() -> dict[str, Any]:
    path = _storage_path()
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        logging.warning("validation_checklists.json corrupted, returning empty")
        return {}


def _write_all(data: dict[str, Any]) -> None:
    path = _storage_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---- item definitions ----

STANDARD_ITEMS: dict[str, dict[str, Any]] = {
    "install": {"label": "Install dependencies", "is_local_needed": True, "default_status": "not_started"},
    "lint": {"label": "Lint / static analysis", "is_local_needed": True, "default_status": "not_started"},
    "typecheck": {"label": "Type check", "is_local_needed": True, "default_status": "not_started"},
    "unit_test": {"label": "Unit tests", "is_local_needed": True, "default_status": "not_started"},
    "integration_test": {"label": "Integration tests", "is_local_needed": True, "default_status": "not_started"},
    "build": {"label": "Build", "is_local_needed": True, "default_status": "not_started"},
    "server_start": {"label": "Server startup", "is_local_needed": True, "default_status": "not_started"},
    "api_smoke": {"label": "API smoke test", "is_local_needed": True, "default_status": "not_started"},
    "browser_smoke": {"label": "Browser smoke test", "is_local_needed": True, "default_status": "not_started"},
    "manual_review": {"label": "Manual review", "is_local_needed": False, "default_status": "not_started"},
    "security_review": {"label": "Security review", "is_local_needed": False, "default_status": "not_started"},
    "docs_review": {"label": "Docs review", "is_local_needed": False, "default_status": "not_started"},
}


def _build_items(required_keys: list[str]) -> list[dict[str, Any]]:
    items = []
    for key in required_keys:
        template = STANDARD_ITEMS.get(key, {
            "label": key.replace("_", " ").title(),
            "is_local_needed": False,
            "default_status": "not_started",
        })
        items.append({
            "key": key,
            "label": template["label"],
            "status": template["default_status"],
            "is_local_needed": template["is_local_needed"],
            "command": None,
            "environment": None,
            "summary": None,
            "log_excerpt": None,
            "evidence_url": None,
            "run_at": None,
            "runner": None,
            "skip_reason": None,
        })
    return items


# ---- public API ----

def recompute_overall_status(checklist: dict[str, Any]) -> str:
    """Determine overall_status based on required items.

    Rules (from docs/21-validation-checklist-results.md):
      - Any required item 'failed'       → 'failed'
      - Any required item 'blocked'      → 'blocked'
      - Any required item 'not_started'  → 'not_started'
      - All required items 'passed' or 'not_applicable' → 'passed'
      - All required items 'skipped' with reasons → 'skipped'
    """
    items = checklist.get("items", [])
    if not items:
        return "not_started"

    has_failed = False
    has_blocked = False
    has_not_started = False
    all_skipped = True

    for item in items:
        status = item.get("status", "not_started")
        if status == "failed":
            has_failed = True
        elif status == "blocked":
            has_blocked = True
        elif status == "not_started":
            has_not_started = True

        if status != "skipped":
            all_skipped = False

    if has_failed:
        return "failed"
    if has_blocked:
        return "blocked"
    if has_not_started:
        return "not_started"
    if all_skipped:
        return "skipped"
    return "passed"


def create_checklist(body: dict) -> dict[str, Any]:
    """Create a new validation checklist.

    Body fields:
      - target_type (required): pr, issue, quest, plan, global, deploy
      - target_id (required): target identifier
      - required_items (optional): list of item keys; defaults to standard set
    """
    target_type = body.get("target_type", "").strip()
    target_id = body.get("target_id", "").strip()
    if not target_type or not target_id:
        raise ValueError("target_type and target_id are required")

    required_keys = body.get("required_items")
    if not required_keys or not isinstance(required_keys, list):
        # Default: provide a sensible set based on target_type
        if target_type in ("docs",):
            required_keys = ["docs_review", "manual_review"]
        elif target_type in ("deploy",):
            required_keys = ["security_review", "docs_review", "manual_review"]
        else:
            required_keys = ["unit_test", "api_smoke", "manual_review"]

    now = _now_iso()
    checklist_id = str(uuid.uuid4())
    items = _build_items(required_keys)
    checklist: dict[str, Any] = {
        "id": checklist_id,
        "target_type": target_type,
        "target_id": target_id,
        "required_items": required_keys,
        "items": items,
        "overall_status": recompute_overall_status({"items": items}),
        "created_at": now,
        "updated_at": now,
    }

    data = _read_all()
    data[checklist_id] = checklist
    _write_all(data)
    return checklist


def list_checklists() -> list[dict[str, Any]]:
    """Return all validation checklists."""
    data = _read_all()
    return list(data.values())


def get_checklist(checklist_id: str) -> dict[str, Any] | None:
    """Return a single checklist by id, or None."""
    data = _read_all()
    return data.get(checklist_id)


def update_result_item(checklist_id: str, item_key: str, body: dict) -> dict[str, Any]:
    """Update a single item in a checklist and recompute overall_status.

    Body can include any item fields: status, command, summary, etc.
    """
    data = _read_all()
    checklist = data.get(checklist_id)
    if checklist is None:
        raise ValueError(f"Checklist {checklist_id} not found")

    items = checklist.get("items", [])
    found = None
    for item in items:
        if item["key"] == item_key:
            found = item
            break

    if found is None:
        raise ValueError(f"Item {item_key} not found in checklist {checklist_id}")

    # Update allowed fields
    allowed_fields = {
        "status", "command", "environment", "summary",
        "log_excerpt", "evidence_url", "runner", "skip_reason",
    }
    for field in allowed_fields:
        if field in body:
            found[field] = body[field]

    if body.get("status") in ("passed", "failed"):
        found["run_at"] = _now_iso()

    # Recompute overall status
    checklist["overall_status"] = recompute_overall_status(checklist)
    checklist["updated_at"] = _now_iso()

    data[checklist_id] = checklist
    _write_all(data)
    return checklist
