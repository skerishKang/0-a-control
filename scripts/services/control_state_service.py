"""Control state read services for dashboard GET handlers."""

from __future__ import annotations

from scripts import db as _db


def get_current_state_payload() -> dict:
    return {"current_state": _db.get_current_state(refresh=False)}


def get_plans_payload() -> dict:
    return {"plans": _db.get_plans()}


def get_quests_payload() -> dict:
    return {"quests": _db.get_quests()}
