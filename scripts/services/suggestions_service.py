"""Suggestion read services for dashboard GET handlers."""

from __future__ import annotations

import json
import logging

from scripts import db as _db


def get_suggestions_payload(limit: int) -> dict:
    suggestions_path = _db.ROOT_DIR / "data" / "runtime" / "quest_suggestions.json"
    if not suggestions_path.exists():
        return {"suggestions": []}
    try:
        data = json.loads(suggestions_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        logging.warning("quest_suggestions.json is corrupted, returning empty: %s", exc)
        return {"suggestions": []}
    return {"suggestions": data.get("suggestions", [])[:limit]}
