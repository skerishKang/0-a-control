from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

try:
    from scripts.db_base import UTC, ROOT_DIR, WORKDIARY_DIR, connect, now_iso, row_to_dict, rows_to_dicts, upsert_state
except ModuleNotFoundError:
    from db_base import UTC, ROOT_DIR, WORKDIARY_DIR, connect, now_iso, row_to_dict, rows_to_dicts, upsert_state



try:
    from scripts.db_workdiary_helpers import (
        build_day_progress_summary,
        build_workdiary_item,
        extract_completion_criteria_for_plan,
        get_workdiary_priority_candidates,
        get_workdiary_top_level,
        latest_decision_summary,
    )
except ModuleNotFoundError:
    from db_workdiary_helpers import (
        build_day_progress_summary,
        build_workdiary_item,
        extract_completion_criteria_for_plan,
        get_workdiary_priority_candidates,
        get_workdiary_top_level,
        latest_decision_summary,
    )


try:
    from scripts.db_inbox import get_external_inbox_overview, get_external_inbox_source_messages  # noqa: F401
except ModuleNotFoundError:
    from db_inbox import get_external_inbox_overview, get_external_inbox_source_messages  # noqa: F401



try:
    from scripts.db_briefing import (
        build_today_done_quests,
        build_tomorrow_first_quest,
        generate_morning_brief,
        generate_priority_recommendation,
    )
except ModuleNotFoundError:
    from db_briefing import (
        build_today_done_quests,
        build_tomorrow_first_quest,
        generate_morning_brief,
        generate_priority_recommendation,
    )


def refresh_current_state(conn: sqlite3.Connection | None = None) -> dict:
    if conn is None:
        with connect() as conn:
            return _refresh_current_state_impl(conn)
    return _refresh_current_state_impl(conn)


def _refresh_current_state_impl(conn: sqlite3.Connection) -> dict:
    main_mission = conn.execute(
        """
        SELECT * FROM plan_items
        WHERE bucket = 'today'
          AND (
                status IN ('active', 'pending', 'partial', 'hold')
                OR EXISTS (
                    SELECT 1
                    FROM quests q
                    WHERE q.plan_item_id = plan_items.id
                      AND q.status IN ('active', 'queued', 'partial', 'pending', 'hold')
                )
          )
        ORDER BY priority_score DESC, updated_at DESC
        LIMIT 1
        """
    ).fetchone()
    current_quest = None
    if main_mission:
        current_quest = conn.execute(
            """
            SELECT * FROM quests
            WHERE plan_item_id = ? AND status IN ('active', 'queued', 'partial', 'pending', 'hold')
            ORDER BY updated_at DESC
            LIMIT 1
            """,
            (main_mission["id"],),
        ).fetchone()

    recent_verdict_row = conn.execute(
        """
        SELECT title, status, updated_at FROM quests
        WHERE status IN ('done', 'partial', 'hold')
        ORDER BY updated_at DESC
        LIMIT 1
        """
    ).fetchone()
    due_items = rows_to_dicts(
        conn.execute(
            """
            SELECT id, title, due_at, status FROM plan_items
            WHERE bucket = 'dated' AND status IN ('active', 'pending', 'partial')
            ORDER BY due_at ASC
            LIMIT 5
            """
        ).fetchall()
    )
    unfinished = rows_to_dicts(
        conn.execute(
            """
            SELECT id, title, bucket, status FROM plan_items
            WHERE status IN ('pending', 'active', 'partial', 'hold')
            ORDER BY priority_score DESC, updated_at DESC
            LIMIT 5
            """
        ).fetchall()
    )

    today_done_quests = build_today_done_quests(conn)
    tomorrow_first_quest = build_tomorrow_first_quest(conn)
    
    # confirmed_starting_point 읽기
    confirmed_row = conn.execute(
        "SELECT state_value FROM current_state WHERE state_key = 'confirmed_starting_point'"
    ).fetchone()
    confirmed_starting_point = None
    if confirmed_row and confirmed_row["state_value"]:
        try:
            confirmed_starting_point = json.loads(confirmed_row["state_value"])
        except json.JSONDecodeError:
            pass

    state = {
        "main_mission": row_to_dict(main_mission),
        "current_quest": row_to_dict(current_quest),
        "recent_verdict": row_to_dict(recent_verdict_row),
        "due_items": due_items,
        "unfinished_items": unfinished,
        "recommended_next_quest": current_quest["next_quest_hint"] if current_quest else None,
        "restart_point": current_quest["restart_point"] if current_quest else None,
        "day_progress_summary": build_day_progress_summary(conn),
        "today_done_quests": today_done_quests,
        "tomorrow_first_quest": tomorrow_first_quest,
        "confirmed_starting_point": confirmed_starting_point,
    }
    
    # Calculate structured quest_status_summary
    quest_status_summary = {
        "is_pending": False,
        "is_awaiting_external_verdict": False,
        "waiting_since": None,
        "latest_report_ref": None,
        "latest_verdict_provider": None,
        "latest_verdict_time": None,
        "preliminary_verdict": None,
        "preliminary_reason": None,
        "is_stale": False,
        "stale_reason": None,
    }
    
    if current_quest:
        qa_status = current_quest["status"]
        quest_status_summary["is_pending"] = qa_status == "pending"
        meta = json.loads(current_quest["metadata_json"] or "{}")
        
        report = meta.get("report")
        if report and qa_status == "pending":
            quest_status_summary["is_awaiting_external_verdict"] = True
            reported_at = report.get("reported_at")
            quest_status_summary["waiting_since"] = reported_at
            
            # Check for timeout (e.g., 10 minutes)
            if reported_at:
                try:
                    report_time = datetime.fromisoformat(reported_at)
                    if report_time.tzinfo is None:
                        report_time = report_time.replace(tzinfo=timezone.utc)
                    
                    diff = datetime.now(timezone.utc) - report_time
                    if diff > timedelta(minutes=10):
                        quest_status_summary["is_stale"] = True
                        quest_status_summary["stale_reason"] = f"판정이 {int(diff.total_seconds() / 60)}분째 지연되고 있습니다. 에이전트 구동을 확인하세요."
                except (ValueError, TypeError):
                    pass
        
        latest_report = meta.get("latest_report")
        if latest_report:
            quest_status_summary["latest_report_ref"] = latest_report.get("report_ref")
            
        ai_verdict = meta.get("ai_verdict")
        if ai_verdict:
            quest_status_summary["latest_verdict_provider"] = ai_verdict.get("provider")
            quest_status_summary["latest_verdict_time"] = ai_verdict.get("updated_at")
            
        preliminary = meta.get("preliminary_ai_verdict")
        if preliminary:
            quest_status_summary["preliminary_verdict"] = preliminary.get("verdict")
            quest_status_summary["preliminary_reason"] = preliminary.get("reason")

    if quest_status_summary["is_pending"]:
        state["recommended_next_quest"] = ""
        state["restart_point"] = state["restart_point"] or "판정 대기 중입니다."
    elif current_quest and current_quest["status"] == "hold":
        state["recommended_next_quest"] = state["recommended_next_quest"] or "대체 퀘스트를 권장합니다."

    state["quest_status_summary"] = quest_status_summary
    recommendation = generate_priority_recommendation(state)
    candidates = recommendation["candidates"]

    main = state["main_mission"] or {}
    quest = state["current_quest"] or {}
    main_title = main.get("title", "")
    main_reason = main.get("priority_reason", "")
    quest_title = quest.get("title", "")

    if candidates and "workdiary 핵심 프로젝트 흐름 파악" in main_title:
        main_title = f"{recommendation['title']} 포함 핵심 프로젝트 흐름 파악"
        main_reason = f"{main_reason} 우선 추천 후보는 {recommendation['title']}이며, {recommendation['reason']}"
        quest_title = f"{recommendation['title']} 포함 우선 검토 후보 5개 좁히기"

    upsert_state(conn, "main_mission_id", main.get("id", ""))
    upsert_state(conn, "main_mission_title", main_title)
    upsert_state(conn, "main_mission_reason", main_reason)
    upsert_state(conn, "main_mission_completion_criteria", extract_completion_criteria_for_plan(conn, main.get("id")))
    upsert_state(conn, "current_quest_id", quest.get("id", ""))
    upsert_state(conn, "current_quest_title", quest_title)
    upsert_state(conn, "current_quest_completion_criteria", quest.get("completion_criteria", ""))
    upsert_state(conn, "quest_status_summary", state["quest_status_summary"])
    upsert_state(conn, "recent_verdict", state["recent_verdict"] or {})
    upsert_state(conn, "recommended_next_quest", state["recommended_next_quest"] or "")
    upsert_state(conn, "top_unfinished_summary", unfinished)
    upsert_state(conn, "dated_pressure_summary", due_items)
    upsert_state(conn, "latest_decision_summary", latest_decision_summary(conn))
    upsert_state(conn, "restart_point", state["restart_point"] or "")
    upsert_state(conn, "day_progress_summary", state["day_progress_summary"])
    upsert_state(conn, "today_done_quests", today_done_quests)
    upsert_state(conn, "tomorrow_first_quest", tomorrow_first_quest or {})

    # Enhanced heuristic for Daily Operating Loop status
    now_kst = datetime.now(timezone.utc) + timedelta(hours=9)
    hour = now_kst.hour
    
    has_quest = bool(state["current_quest"])
    is_pending = state["quest_status_summary"]["is_pending"]
    
    # Check if any progress was made today
    has_progress_today = False
    recent_verdict = state["recent_verdict"]
    if recent_verdict and recent_verdict.get("updated_at"):
        try:
            verdict_time = datetime.fromisoformat(recent_verdict["updated_at"])
            if verdict_time.date() == datetime.now(timezone.utc).date():
                has_progress_today = True
        except ValueError:
            pass

    day_phase = "morning"
    day_phase_reason = "기본 아침 시작 상태입니다."

    if has_quest:
        if is_pending:
            day_phase = "verdict-pending"
            day_phase_reason = "현재 진행 중인 퀘스트의 보고가 제출되어 AI 판정을 기다리고 있습니다."
        else:
            day_phase = "in-progress"
            day_phase_reason = "주 임무에 속한 퀘스트가 현재 활성화되어 진행 중입니다."
    else:
        if has_progress_today:
            if hour >= 17:
                day_phase = "end-of-day"
                day_phase_reason = f"현재 시각이 늦었고({hour}시), 오늘 퀘스트를 완료한 이력이 있어 마감 루프를 권장합니다."
            else:
                day_phase = "midday"
                day_phase_reason = "오늘 이미 퀘스트를 수행했으나 현재 활성 퀘스트가 없어 다음 행동을 재정렬할 시점입니다."
        else:
            if hour >= 17:
                day_phase = "midday"
                day_phase_reason = f"시간이 늦었지만({hour}시) 오늘 기록된 완료 퀘스트가 없어, 중간 점검으로 흐름을 잡아야 합니다."
            else:
                day_phase = "morning"
                day_phase_reason = "오늘 진행된 퀘스트가 없고 활성 퀘스트도 없어, 하루를 계획하는 아침 상태입니다."
        
    upsert_state(conn, "day_phase", day_phase)
    upsert_state(conn, "day_phase_reason", day_phase_reason)
    
    upsert_state(conn, "workdiary_top_level", get_workdiary_top_level(12))
    upsert_state(conn, "workdiary_priority_candidates", get_workdiary_priority_candidates(8))
    upsert_state(conn, "priority_recommendation", recommendation)
    upsert_state(conn, "latest_morning_brief", generate_morning_brief(conn, state))
    return state
