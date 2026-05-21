"""External inbox read services for dashboard GET handlers."""

from __future__ import annotations

from scripts import db as _db


def get_overview_payload(limit: int, status: str | None, category: str | None) -> dict:
    return _db.get_external_inbox_overview(limit, status, category)


def get_source_messages_payload(source_id: str, day: str, limit: int, before: str | None) -> dict:
    return _db.get_external_inbox_source_messages(source_id, day, limit, before)
