from __future__ import annotations

from scripts.db_base import connect, now_iso, upsert_state
from scripts.db_state import refresh_current_state


def confirm_starting_point(title: str, reason: str, source: str = "manual") -> dict:
    """사용자가 내일 첫 퀘스트를 확정하는 함수."""
    if not title:
        raise ValueError("title is required")
    with connect() as conn:
        confirmed = {
            "title": title,
            "reason": reason or "사용자가 직접 확정",
            "source": source,
            "confirmed_at": now_iso(),
        }
        upsert_state(conn, "confirmed_starting_point", confirmed)
        refresh_current_state(conn)
        return {"ok": True, "confirmed_starting_point": confirmed}
