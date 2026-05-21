"""Workdiary read services for dashboard GET handlers."""

from __future__ import annotations

from scripts import db as _db


def get_top_level_payload(limit: int) -> dict:
    return {"items": _db.get_workdiary_top_level(limit)}


def get_priority_candidates_payload(limit: int) -> dict:
    return {"items": _db.get_workdiary_priority_candidates(limit)}
