from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone, timedelta

try:
    from scripts.db_base import UTC, connect, now_iso, rows_to_dicts
except ModuleNotFoundError:
    from db_base import UTC, connect, now_iso, rows_to_dicts


def build_today_done_quests(conn) -> list[dict]:
    # 오늘(KST 기준) 완료된 퀘스트 목록
    now_kst = datetime.now(timezone.utc) + timedelta(hours=9)
    today_str = now_kst.date().isoformat()
    rows = conn.execute(
        """
        SELECT * FROM quests
        WHERE status IN ('done', 'partial')
          AND updated_at >= ?
        ORDER BY updated_at DESC
        """,
        (today_str,),
    ).fetchall()
    return rows_to_dicts(rows)


def build_tomorrow_first_quest(conn) -> dict | None:
    # 1순위: 오늘 hold 상태로 남은 항목
    hold_item = conn.execute(
        """
        SELECT * FROM plan_items
        WHERE bucket = 'today' AND status = 'hold'
        ORDER BY priority_score DESC, updated_at DESC
        LIMIT 1
        """
    ).fetchone()
    if hold_item:
        return {
            "source": "today_hold",
            "id": hold_item["id"],
            "title": hold_item["title"],
            "reason": "오늘 미완료로 남긴 항목. 이어서 진행하면 됨",
        }

    # 2순위: short_term 버킷의 우선순위 높은 항목
    short_term = conn.execute(
        """
        SELECT * FROM plan_items
        WHERE bucket = 'short_term' AND status IN ('pending', 'active', 'partial', 'hold')
        ORDER BY priority_score DESC, updated_at DESC
        LIMIT 1
        """
    ).fetchone()
    if short_term:
        return {
            "source": "short_term",
            "id": short_term["id"],
            "title": short_term["title"],
            "reason": "단기 플랜 중 가장 우선순위가 높은 다음 목표",
        }

    return None


def generate_priority_recommendation(state: dict) -> dict:
    from scripts.db_state import get_workdiary_priority_candidates  # lazy import

    candidates = get_workdiary_priority_candidates(5)
    recommended = candidates[0] if candidates else None
    if not recommended:
        return {
            "title": "우선 검토 후보 없음",
            "reason": "workdiary 상위 폴더에서 즉시 추천 가능한 프로젝트 후보를 찾지 못함",
            "candidates": [],
        }

    return {
        "title": recommended["name"],
        "reason": f"{recommended['name']}이(가) 최근성, 프로젝트 구조, 운영 연관성 기준에서 가장 먼저 검토할 후보로 올라옴",
        "candidates": candidates,
    }


def generate_morning_brief(conn, state: dict) -> dict:
    # 하루에 한 번만 생성 (이미 오늘 생성된 게 있으면 기존 반환)
    today = datetime.now(UTC).date().isoformat()
    existing = conn.execute(
        "SELECT title, content_md FROM brief_records WHERE brief_type = 'morning_auto' AND DATE(created_at) = ? ORDER BY created_at DESC LIMIT 1",
        (today,)
    ).fetchone()
    if existing:
        return {"title": existing["title"], "content_md": existing["content_md"]}

    main = state["main_mission"] or {}
    quest = state["current_quest"] or {}
    confirmed = state.get("confirmed_starting_point")
    due_items = state["due_items"][:3]
    unfinished = state["unfinished_items"][:3]
    main_title = main.get("title", "미정")
    main_reason = main.get("priority_reason", "우선순위 이유 없음")
    quest_title = quest.get("title", "미정")

    lines = [
        "## 오늘 브리핑",
        "",
        f"- 주 임무: {main_title}",
        f"- 이유: {main_reason}",
    ]

    # 어제 확정한 시작점이 있으면 추가
    if confirmed and confirmed.get("title"):
        lines.append(f"- 어제 확정한 첫 시작: {confirmed['title']}")
        if confirmed.get("reason"):
            lines.append(f"  (이유: {confirmed['reason']})")

    lines.append(f"- 현재 퀘스트: {quest_title}")

    if due_items:
        lines.append(f"- 기한 압박: {due_items[0]['title']}")
    if unfinished:
        lines.append(f"- 가장 큰 미완료: {unfinished[0]['title']}")
    
    content_md = "\n".join(lines) + "\n"
    title = f"자동 아침 브리프 {datetime.now(UTC).date().isoformat()}"
    conn.execute("DELETE FROM brief_records WHERE brief_type = 'morning_auto'")
    conn.execute(
        """
        INSERT INTO brief_records (
            id, brief_type, title, content_md, related_plan_item_id, related_quest_id,
            related_session_id, created_at, metadata_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            str(uuid.uuid4()),
            "morning_auto",
            title,
            content_md,
            main.get("id"),
            quest.get("id"),
            None,
            now_iso(),
            json.dumps({"generated": True}, ensure_ascii=False),
        ),
    )
    return {"title": title, "content_md": content_md}
