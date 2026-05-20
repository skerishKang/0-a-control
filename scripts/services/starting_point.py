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


def clear_confirmed_starting_point() -> dict:
    """사용자가 확정한 내일 첫 퀘스트를 명시적으로 비우는 함수."""
    with connect() as conn:
        conn.execute("DELETE FROM current_state WHERE state_key = 'confirmed_starting_point'")
        refresh_current_state(conn)
        return {"ok": True, "message": "확정된 시작점을 비웠습니다."}
