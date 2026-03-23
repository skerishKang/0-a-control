from __future__ import annotations

import json
import uuid

from scripts.db_base import connect, now_iso, record_event, row_to_dict
from scripts.db_state import extract_completion_criteria_for_plan, refresh_current_state


def _read_current_state_from_conn(conn) -> dict:
    state_rows = conn.execute(
        "SELECT state_key, state_value, updated_at, metadata_json FROM current_state ORDER BY state_key ASC"
    ).fetchall()
    state_out: dict = {}
    for row in state_rows:
        value = row["state_value"]
        try:
            state_out[row["state_key"]] = json.loads(value)
        except (TypeError, json.JSONDecodeError):
            state_out[row["state_key"]] = value
    return state_out


def defer_current_quest_to_short_term() -> dict:
    with connect() as conn:
        refresh_current_state(conn)
        state_rows = conn.execute(
            "SELECT state_key, state_value FROM current_state WHERE state_key IN ('current_quest_id', 'main_mission_id')"
        ).fetchall()
        state_map = {row["state_key"]: row["state_value"] for row in state_rows}
        quest_id = state_map.get("current_quest_id") or ""
        plan_item_id = state_map.get("main_mission_id") or ""
        if not quest_id:
            raise ValueError("current quest not found")

        quest_row = conn.execute("SELECT * FROM quests WHERE id = ?", (quest_id,)).fetchone()
        if quest_row is None:
            raise ValueError("current quest not found")

        quest = dict(quest_row)
        updated_at = now_iso()
        restart_point = quest.get("restart_point") or "현재 멈춘 지점부터 다시 시작합니다."
        next_hint = quest.get("next_quest_hint") or "단기 플랜에서 다시 꺼낼 시작점을 정리합니다."
        metadata = json.loads(quest.get("metadata_json") or "{}")
        metadata["deferred_from_today"] = {
            "at": updated_at,
            "reason": "moved from today to short_term",
        }

        conn.execute(
            """
            UPDATE quests
            SET status = ?, restart_point = ?, next_quest_hint = ?, updated_at = ?, metadata_json = ?
            WHERE id = ?
            """,
            (
                "hold",
                restart_point,
                next_hint,
                updated_at,
                json.dumps(metadata, ensure_ascii=False),
                quest_id,
            ),
        )

        if plan_item_id:
            conn.execute(
                """
                UPDATE plan_items
                SET bucket = 'short_term', status = ?, updated_at = ?
                WHERE id = ?
                """,
                ("hold", updated_at, plan_item_id),
            )

        conn.execute(
            """
            INSERT INTO decision_records (
                id, decision_type, title, reason, impact_summary,
                related_plan_item_id, related_quest_id, related_session_id, created_at, metadata_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(uuid.uuid4()),
                "scope_cut",
                f"단기 플랜으로 이동: {quest['title']}",
                "오늘판에서는 내리고, 단기 플랜으로 다시 이어갈 항목으로 정리했습니다.",
                "오늘판에서 내리고 단기 플랜으로 넘김",
                plan_item_id or None,
                quest_id,
                None,
                updated_at,
                None,
            ),
        )

        record_event(
            conn,
            event_type="plan_item_deferred",
            entity_id=plan_item_id or quest_id,
            entity_type="plan_item" if plan_item_id else "quest",
            detail=quest["title"],
            metadata={
                "quest_id": quest_id,
                "plan_item_id": plan_item_id,
                "from_bucket": "today",
                "to_bucket": "short_term",
                "status": "hold",
            },
            created_at=updated_at,
        )
        refresh_current_state(conn)

        quest_out = conn.execute("SELECT * FROM quests WHERE id = ?", (quest_id,)).fetchone()
        plan_out = conn.execute("SELECT * FROM plan_items WHERE id = ?", (plan_item_id,)).fetchone() if plan_item_id else None
        return {
            "quest": row_to_dict(quest_out) if quest_out else {},
            "plan_item": row_to_dict(plan_out) if plan_out else {},
            "current_state": _read_current_state_from_conn(conn),
        }


def mark_current_quest_unfinished() -> dict:
    with connect() as conn:
        refresh_current_state(conn)
        state_rows = conn.execute(
            "SELECT state_key, state_value FROM current_state WHERE state_key IN ('current_quest_id', 'main_mission_id')"
        ).fetchall()
        state_map = {row["state_key"]: row["state_value"] for row in state_rows}
        quest_id = state_map.get("current_quest_id") or ""
        plan_item_id = state_map.get("main_mission_id") or ""
        if not quest_id:
            raise ValueError("current quest not found")

        quest_row = conn.execute("SELECT * FROM quests WHERE id = ?", (quest_id,)).fetchone()
        if quest_row is None:
            raise ValueError("current quest not found")

        quest = dict(quest_row)
        updated_at = now_iso()
        restart_point = quest.get("restart_point") or "현재 멈춘 지점부터 다시 시작합니다."
        next_hint = quest.get("next_quest_hint") or "오늘 안에 다시 붙잡을 수 있는 다음 행동을 정리합니다."
        metadata = json.loads(quest.get("metadata_json") or "{}")
        metadata["marked_unfinished"] = {
            "at": updated_at,
            "reason": "today_unfinished",
        }

        conn.execute(
            """
            UPDATE quests
            SET status = ?, restart_point = ?, next_quest_hint = ?, updated_at = ?, metadata_json = ?
            WHERE id = ?
            """,
            (
                "hold",
                restart_point,
                next_hint,
                updated_at,
                json.dumps(metadata, ensure_ascii=False),
                quest_id,
            ),
        )

        if plan_item_id:
            conn.execute(
                """
                UPDATE plan_items
                SET status = ?, updated_at = ?
                WHERE id = ?
                """,
                ("hold", updated_at, plan_item_id),
            )

        conn.execute(
            """
            INSERT INTO decision_records (
                id, decision_type, title, reason, impact_summary,
                related_plan_item_id, related_quest_id, related_session_id, created_at, metadata_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(uuid.uuid4()),
                "scope_cut",
                f"미완료로 남김: {quest['title']}",
                "오늘판에 남겨 두고, 미완료 상태로 다시 이어갈 수 있게 정리했습니다.",
                "오늘 미완료로 남김",
                plan_item_id or None,
                quest_id,
                None,
                updated_at,
                None,
            ),
        )

        record_event(
            conn,
            event_type="quest_marked_unfinished",
            entity_id=plan_item_id or quest_id,
            entity_type="plan_item" if plan_item_id else "quest",
            detail=quest["title"],
            metadata={
                "quest_id": quest_id,
                "plan_item_id": plan_item_id,
                "bucket": "today",
                "status": "hold",
            },
            created_at=updated_at,
        )
        refresh_current_state(conn)

        quest_out = conn.execute("SELECT * FROM quests WHERE id = ?", (quest_id,)).fetchone()
        plan_out = conn.execute("SELECT * FROM plan_items WHERE id = ?", (plan_item_id,)).fetchone() if plan_item_id else None
        return {
            "quest": row_to_dict(quest_out) if quest_out else {},
            "plan_item": row_to_dict(plan_out) if plan_out else {},
            "current_state": _read_current_state_from_conn(conn),
        }


def start_current_quest_from_main_mission() -> dict:
    with connect() as conn:
        refresh_current_state(conn)
        state_rows = conn.execute(
            "SELECT state_key, state_value FROM current_state WHERE state_key IN ('current_quest_id', 'main_mission_id')"
        ).fetchall()
        state_map = {row["state_key"]: row["state_value"] for row in state_rows}
        current_quest_id = state_map.get("current_quest_id") or ""
        main_mission_id = state_map.get("main_mission_id") or ""

        if current_quest_id:
            quest_row = conn.execute("SELECT * FROM quests WHERE id = ?", (current_quest_id,)).fetchone()
            return {
                "quest": row_to_dict(quest_row) if quest_row else {},
                "reused": True,
                "current_state": _read_current_state_from_conn(conn),
            }

        if not main_mission_id:
            raise ValueError("main mission not found")

        plan_row = conn.execute("SELECT * FROM plan_items WHERE id = ?", (main_mission_id,)).fetchone()
        if plan_row is None:
            raise ValueError("main mission not found")

        plan = dict(plan_row)
        updated_at = now_iso()

        existing_quest = conn.execute(
            """
            SELECT * FROM quests
            WHERE plan_item_id = ? AND status IN ('hold', 'pending', 'partial', 'queued')
            ORDER BY updated_at DESC, created_at DESC
            LIMIT 1
            """,
            (main_mission_id,),
        ).fetchone()

        if existing_quest is not None:
            quest_id = existing_quest["id"]
            conn.execute(
                """
                UPDATE quests
                SET status = 'active', updated_at = ?
                WHERE id = ?
                """,
                (updated_at, quest_id),
            )
            conn.execute(
                "UPDATE plan_items SET status = 'active', updated_at = ? WHERE id = ?",
                (updated_at, main_mission_id),
            )
            record_event(
                conn,
                event_type="quest_resumed",
                entity_id=quest_id,
                entity_type="quest",
                detail=existing_quest["title"],
                metadata={"plan_item_id": main_mission_id},
                created_at=updated_at,
            )
        else:
            quest_id = str(uuid.uuid4())
            title = plan.get("title") or "현재 퀘스트"
            why_now = plan.get("priority_reason") or "오늘 주 임무를 실제 실행으로 전환해야 하는 시점입니다."
            completion_criteria = extract_completion_criteria_for_plan(conn, main_mission_id)
            if not completion_criteria:
                completion_criteria = "주 임무를 다음 단계로 진행시키는 구체적 결과를 남긴다."
            restart_point = plan.get("description") or f"{title}부터 바로 시작"
            next_quest_hint = ""
            conn.execute(
                """
                INSERT INTO quests (
                    id, plan_item_id, parent_quest_id, title, why_now, completion_criteria, status,
                    verdict_reason, restart_point, next_quest_hint, created_at, updated_at, metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    quest_id,
                    main_mission_id,
                    None,
                    title,
                    why_now,
                    completion_criteria,
                    "active",
                    None,
                    restart_point,
                    next_quest_hint,
                    updated_at,
                    updated_at,
                    None,
                ),
            )
            conn.execute(
                "UPDATE plan_items SET status = 'active', updated_at = ? WHERE id = ?",
                (updated_at, main_mission_id),
            )
            record_event(
                conn,
                event_type="quest_started",
                entity_id=quest_id,
                entity_type="quest",
                detail=title,
                metadata={"plan_item_id": main_mission_id},
                created_at=updated_at,
            )

        refresh_current_state(conn)
        quest_out = conn.execute("SELECT * FROM quests WHERE id = ?", (quest_id,)).fetchone()
        return {
            "quest": row_to_dict(quest_out) if quest_out else {},
            "current_state": _read_current_state_from_conn(conn),
        }


def promote_confirmed_starting_point_to_quest() -> dict:
    with connect() as conn:
        refresh_current_state(conn)
        state = _read_current_state_from_conn(conn)
        
        # 1. active 퀘스트가 이미 있으면 승격 금지 (quests 테이블 직접 조회)
        active_quest = conn.execute(
            "SELECT id FROM quests WHERE status = 'active' LIMIT 1"
        ).fetchone()
        if active_quest:
            raise ValueError("이미 진행 중인 퀘스트가 있습니다. 먼저 종료하거나 보류(hold)하세요.")
        
        # 2. confirmed_starting_point가 없으면 승격 금지
        confirmed = state.get("confirmed_starting_point")
        if not confirmed or not confirmed.get("title"):
            raise ValueError("승격할 확정된 시작점이 없습니다.")
            
        updated_at = now_iso()
        quest_id = str(uuid.uuid4())
        title = confirmed["title"]
        why_now = confirmed.get("reason") or "어제 확정한 시작점입니다."
        
        # 3. 새 quest 생성 (plan_item_id 없이도 생성 가능해야 함)
        conn.execute(
            """
            INSERT INTO quests (
                id, plan_item_id, parent_quest_id, title, why_now, completion_criteria, status,
                verdict_reason, restart_point, next_quest_hint, created_at, updated_at, metadata_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                quest_id,
                None,
                None,
                title,
                why_now,
                "확정된 시작점의 목표를 달성한다.",
                "active",
                None,
                f"{title} 시작",
                "",
                updated_at,
                updated_at,
                json.dumps({"promoted_from_confirmed_start": True}, ensure_ascii=False),
            ),
        )
        
        # 4. 성공 후 confirmed_starting_point 제거
        conn.execute("DELETE FROM current_state WHERE state_key = 'confirmed_starting_point'")
        
        record_event(
            conn,
            event_type="quest_promoted",
            entity_id=quest_id,
            entity_type="quest",
            detail=title,
            metadata={"source": confirmed.get("source")},
            created_at=updated_at,
        )
        
        refresh_current_state(conn)
        quest_out = conn.execute("SELECT * FROM quests WHERE id = ?", (quest_id,)).fetchone()
        return {
            "ok": True,
            "quest": row_to_dict(quest_out) if quest_out else {},
            "current_state": _read_current_state_from_conn(conn),
        }
