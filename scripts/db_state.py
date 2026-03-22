from __future__ import annotations

import json
import sqlite3
import uuid
from typing import Any
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
from pathlib import Path

try:
    from scripts.db_base import UTC, ROOT_DIR, WORKDIARY_DIR, connect, now_iso, row_to_dict, rows_to_dicts, upsert_state
except ModuleNotFoundError:
    from db_base import UTC, ROOT_DIR, WORKDIARY_DIR, connect, now_iso, row_to_dict, rows_to_dicts, upsert_state


def extract_completion_criteria_for_plan(conn: sqlite3.Connection, plan_item_id: str | None) -> str:
    if not plan_item_id:
        return ""
    row = conn.execute(
        "SELECT completion_criteria FROM quests WHERE plan_item_id = ? ORDER BY created_at ASC LIMIT 1",
        (plan_item_id,),
    ).fetchone()
    return row["completion_criteria"] if row else ""


def latest_decision_summary(conn: sqlite3.Connection) -> dict:
    row = conn.execute(
        """
        SELECT decision_type, title, reason, impact_summary, created_at,
               related_plan_item_id, related_quest_id
        FROM decision_records
        ORDER BY created_at DESC
        LIMIT 1
        """
    ).fetchone()
    if not row:
        return {}

    data = row_to_dict(row)
    if data.get("decision_type") != "scope_cut":
        data.pop("decision_type", None)
        data.pop("related_plan_item_id", None)
        data.pop("related_quest_id", None)
        return data

    title = str(data.get("title") or "")
    impact = str(data.get("impact_summary") or "")
    created_at = data.get("created_at")
    related_plan_item_id = data.get("related_plan_item_id")
    related_quest_id = data.get("related_quest_id")

    mode = None
    if "단기 플랜으로 이동" in title or "Move current quest out of today" in title or "short_term" in impact:
        mode = "defer"
    elif "미완료로 남김" in title or "Keep current quest unfinished" in title or "unfinished" in impact:
        mode = "hold"
    else:
        event = conn.execute(
            """
            SELECT event_type
            FROM event_log
            WHERE created_at <= ?
              AND (
                entity_id = COALESCE(?, '')
                OR entity_id = COALESCE(?, '')
              )
              AND event_type IN ('plan_item_deferred', 'quest_marked_unfinished')
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (created_at, related_plan_item_id or "", related_quest_id or ""),
        ).fetchone()
        if event:
            if event["event_type"] == "plan_item_deferred":
                mode = "defer"
            elif event["event_type"] == "quest_marked_unfinished":
                mode = "hold"

    quest_title = title.split(":", 1)[1].strip() if ":" in title else title.strip()
    if mode == "defer":
        data["title"] = f"단기 플랜으로 이동: {quest_title}"
        data["reason"] = "오늘판에서는 내리고, 단기 플랜으로 다시 이어갈 항목으로 정리했습니다."
        data["impact_summary"] = "오늘판에서 내리고 단기 플랜으로 넘김"
    elif mode == "hold":
        data["title"] = f"미완료로 남김: {quest_title}"
        data["reason"] = "오늘판에 남겨 두고, 미완료 상태로 다시 이어갈 수 있게 정리했습니다."
        data["impact_summary"] = "오늘 미완료로 남김"

    data.pop("decision_type", None)
    data.pop("related_plan_item_id", None)
    data.pop("related_quest_id", None)
    return data


def build_day_progress_summary(conn: sqlite3.Connection) -> dict:
    rows = conn.execute("SELECT status, COUNT(*) AS count FROM quests GROUP BY status").fetchall()
    counts = {row["status"]: row["count"] for row in rows}
    return {
        "done": counts.get("done", 0),
        "partial": counts.get("partial", 0),
        "hold": counts.get("hold", 0),
        "active": counts.get("active", 0) + counts.get("queued", 0) + counts.get("pending", 0),
    }


def get_workdiary_top_level(limit: int = 30) -> list[dict]:
    items: list[dict] = []
    for path in sorted(WORKDIARY_DIR.iterdir(), key=lambda p: p.name.lower()):
        if not path.is_dir() or path.name.startswith(".") or path.name == ROOT_DIR.name:
            continue
        try:
            stat = path.stat()
        except OSError:
            continue
        item = build_workdiary_item(path.name, str(path), stat.st_mtime)
        items.append(item)
    return items[:limit]


def build_workdiary_item(name: str, path: str, modified_ts: float) -> dict:
    modified_at = datetime.fromtimestamp(modified_ts, UTC).replace(microsecond=0).isoformat()
    path_obj = Path(path)
    lowered = name.lower()
    system_names = {
        "node_modules",
        "logs",
        "log",
        "test-results",
        "dist",
        "build",
        "coverage",
        "__pycache__",
        "tmp",
        "temp",
        "tools",
        "flutter",
        "summaries",
        "uploads",
        "upload",
        "cache",
        "arxiv_cache",
        "assets",
        "references",
        "archive",
        "archives",
        "prompts",
    }
    archive_keywords = ("백업", "backup", "archive", "deleted", "trash", "보관")
    document_keywords = ("문서", "계획", "정리", "proposal", "ppt", "노션", "회의", "notes")
    project_boost_keywords = ("control", "plan", "auto", "browser", "edu", "dashboard", "api", "cli", "agent")
    manifest_names = ("package.json", "pyproject.toml", "requirements.txt", "go.mod", "Cargo.toml")
    source_markers = ("src", "app", "pages", "server", "scripts", "main.py", "index.html")

    readme_exists = (path_obj / "README.md").exists() or (path_obj / "readme.md").exists()
    git_exists = (path_obj / ".git").exists()
    manifest_hits = [marker for marker in manifest_names if (path_obj / marker).exists()]
    source_hits = [marker for marker in source_markers if (path_obj / marker).exists()]

    is_backup = any(keyword in lowered for keyword in archive_keywords)
    is_docs = any(keyword in lowered for keyword in document_keywords)
    is_numbered_project = lowered[:1].isdigit()
    is_control = "control" in lowered or "cmd" in lowered
    is_plan = "plan" in lowered
    is_system = lowered in system_names
    has_project_keyword = any(keyword in lowered for keyword in project_boost_keywords)

    item_type = "project"
    if is_backup:
        item_type = "archive"
    elif is_docs and not is_plan:
        item_type = "document"
    elif is_system:
        item_type = "system"

    score = 0
    reasons: list[str] = []
    if item_type == "project":
        score += 30
        reasons.append("프로젝트 후보")
    if is_numbered_project:
        score += 10
        reasons.append("번호 체계")
    if is_control or is_plan:
        score += 15
        reasons.append("운영/플랜 연관")
    if has_project_keyword:
        score += 8
        reasons.append("프로젝트 키워드")
    if readme_exists:
        score += 12
        reasons.append("README 존재")
    if git_exists:
        score += 12
        reasons.append("Git 저장소")
    if manifest_hits:
        score += 10 + min(len(manifest_hits), 2) * 3
        reasons.append("구성 파일")
    if source_hits:
        score += 8
        reasons.append("소스 구조")

    days_old = max((datetime.now(UTC).timestamp() - modified_ts) / 86400, 0)
    if days_old <= 7:
        score += 16
        reasons.append("최근 수정")
    elif days_old <= 30:
        score += 10
        reasons.append("비교적 최근 수정")
    elif days_old <= 90:
        score += 4

    if item_type == "archive":
        score -= 40
        reasons.append("보관/백업 성격")
    elif item_type == "document":
        score -= 18
        reasons.append("문서 중심")
    elif item_type == "system":
        score -= 35
        reasons.append("시스템/보조 폴더")

    return {
        "name": name,
        "path": path,
        "modified_at": modified_at,
        "item_type": item_type,
        "priority_score": score,
        "priority_reason": ", ".join(reasons[:4]) if reasons else "추가 신호 없음",
    }


def get_workdiary_priority_candidates(limit: int = 8) -> list[dict]:
    items = get_workdiary_top_level(200)
    project_items = [
        item
        for item in items
        if item["item_type"] == "project"
        and item["name"] != ROOT_DIR.name
        and item["priority_score"] >= 60
    ]
    project_items.sort(
        key=lambda item: (
            item["priority_score"],
            item["modified_at"],
        ),
        reverse=True,
    )
    return project_items[:limit]


def get_external_inbox_overview(limit: int = 8, status: str | None = None, category: str | None = None) -> dict:
    """
    Returns classified items and a summary of the external inbox.
    """
    try:
        from scripts.inbox_parse import resolve_source_aliases
    except ModuleNotFoundError:
        from inbox_parse import resolve_source_aliases
    
    with connect() as conn:
        table_exists = conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'external_inbox'"
        ).fetchone()
        if not table_exists:
            return {
                "summary": {"new": 0, "reviewing": 0, "accepted": 0, "rejected": 0, "archived": 0, "total": 0},
                "items": [],
                "categories": {}
            }

        params: list[Any] = []
        where_clauses = [
            "COALESCE(ei.source_id, '') NOT GLOB 'test_*'",
            "COALESCE(ei.source_name, '') NOT GLOB 'test_*'",
        ]
        
        if status:
            where_clauses.append("ei.status = ?")
            params.append(status)
        
        if category:
            resolved_sources = resolve_source_aliases([category])
            if resolved_sources:
                placeholders = ", ".join(["?"] * len(resolved_sources))
                where_clauses.append(f"COALESCE(ts.chat_class, '') IN ({placeholders})")
                params.extend(resolved_sources)

        where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
        params.append(limit)

        rows = rows_to_dicts(
            conn.execute(
                f"""
                SELECT
                    ei.id,
                    ei.source_type,
                    ei.source_id,
                    ei.source_name,
                    ei.author,
                    ei.item_type,
                    ei.title,
                    ei.raw_content,
                    ei.item_timestamp,
                    ei.imported_at,
                    ei.status,
                    COALESCE(ts.chat_class, '') AS chat_class,
                    COALESCE(ts.is_core, 0) AS is_core
                FROM external_inbox ei
                LEFT JOIN telegram_sources ts
                  ON ts.source_id = ei.source_id
                {where_sql}
                ORDER BY
                    CASE ei.status
                        WHEN 'new' THEN 1
                        WHEN 'reviewing' THEN 2
                        WHEN 'accepted' THEN 3
                        WHEN 'rejected' THEN 4
                        WHEN 'archived' THEN 5
                        ELSE 6
                    END,
                    COALESCE(NULLIF(ei.item_timestamp, ''), ei.imported_at) DESC,
                    ei.imported_at DESC,
                    ei.id DESC
                LIMIT ?
                """,
                tuple(params),
            ).fetchall()
        )
        
        # Add classification/category to each item
        core_four = {'local_chat', 'kilo_chat', 'self_chat', 'kang_hyerim_chat'}
        for row in rows:
            c_class = row.get("chat_class", "")
            if row.get("is_core") or c_class in core_four:
                row["category"] = "핵심4개"
            elif c_class == "stock_curator_channel":
                row["category"] = "주식큐레이터"
            elif c_class == "news_channel":
                row["category"] = "뉴스"
            elif c_class == "general_chat" or c_class.startswith("chat_"):
                row["category"] = "일반대화"
            else:
                row["category"] = "기타"
            
            # Action hints for frontend
            row["actions"] = ["save", "discard"]
            if row["status"] in ("new", "reviewing"):
                row["actions"].append("ai_ingest")

        counts = {
            row["status"]: row["count"]
            for row in conn.execute(
                """
                SELECT status, COUNT(*) AS count
                FROM external_inbox
                WHERE COALESCE(source_id, '') NOT GLOB 'test_*'
                  AND COALESCE(source_name, '') NOT GLOB 'test_*'
                GROUP BY status
                """
            ).fetchall()
        }
        
        # Category summary
        cat_counts = {
            "핵심4개": 0,
            "주식큐레이터": 0,
            "뉴스": 0,
            "일반대화": 0,
            "기타": 0
        }
        # For simplicity, we calculate cat counts from all data (or just items shown? Usually all in status).
        # But doing a full query for cat counts might be slow if data is huge. 
        # For now, let's keep it simple.
        
    return {
        "summary": {
            "new": counts.get("new", 0),
            "reviewing": counts.get("reviewing", 0),
            "accepted": counts.get("accepted", 0),
            "rejected": counts.get("rejected", 0),
            "archived": counts.get("archived", 0),
            "total": sum(counts.values()),
        },
        "items": rows,
    }


def get_external_inbox_source_messages(
    source_id: str,
    day: str = "today",
    limit: int = 500,
    before: str | None = None,
) -> dict:
    if not source_id:
        return {
            "source_id": "",
            "source_name": "",
            "day": day,
            "messages": [],
            "loaded_days": [],
            "has_more_before": False,
            "previous_day": None,
        }

    local_tz = ZoneInfo("Asia/Seoul")
    now_local = datetime.now(local_tz)

    with connect() as conn:
        rows = rows_to_dicts(
            conn.execute(
                """
                SELECT
                    ei.id,
                    ei.source_id,
                    ei.source_name,
                    ei.external_message_id,
                    ei.author,
                    ei.item_type,
                    ei.raw_content,
                    ei.attachment_path,
                    ei.item_timestamp,
                    ei.imported_at,
                    ei.status,
                    COALESCE(ts.chat_class, '') AS chat_class
                FROM external_inbox ei
                LEFT JOIN telegram_sources ts
                  ON ts.source_id = ei.source_id
                WHERE ei.source_id = ?
                  AND COALESCE(ei.source_id, '') NOT GLOB 'test_*'
                  AND COALESCE(ei.source_name, '') NOT GLOB 'test_*'
                ORDER BY COALESCE(NULLIF(ei.item_timestamp, ''), ei.imported_at) ASC,
                         ei.imported_at ASC,
                         ei.id ASC
                LIMIT ?
                """,
                (source_id, limit),
            ).fetchall()
        )

    def parse_dt(row: dict) -> datetime | None:
        raw = row.get("item_timestamp") or row.get("imported_at")
        if not raw:
            return None
        try:
            dt = datetime.fromisoformat(raw)
        except ValueError:
            return None
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(local_tz)

    dated_rows: list[tuple[dict, datetime]] = []
    for row in rows:
        dt = parse_dt(row)
        if dt:
            row["display_timestamp"] = dt.isoformat()
            row["display_day"] = dt.date().isoformat()
            dated_rows.append((row, dt))

    available_days = sorted({dt.date() for _, dt in dated_rows})
    if before:
        before_date = datetime.fromisoformat(before).date()
        candidate_days = [candidate for candidate in available_days if candidate < before_date]
        target_date = candidate_days[-1] if candidate_days else before_date
    elif day == "today":
        today_date = now_local.date()
        if today_date in available_days:
            target_date = today_date
        elif available_days:
            target_date = available_days[-1]
        else:
            target_date = today_date
    else:
        target_date = datetime.fromisoformat(day).date()

    filtered = [row for row, dt in dated_rows if dt.date() == target_date]
    previous_days = [candidate for candidate in available_days if candidate < target_date]

    source_name = filtered[0]["source_name"] if filtered else (rows[0]["source_name"] if rows else source_id)
    chat_class = filtered[0]["chat_class"] if filtered else (rows[0]["chat_class"] if rows else "")
    return {
        "source_id": source_id,
        "source_name": source_name,
        "chat_class": chat_class,
        "day": target_date.isoformat(),
        "loaded_days": [target_date.isoformat()],
        "has_more_before": bool(previous_days),
        "previous_day": previous_days[-1].isoformat() if previous_days else None,
        "messages": filtered,
    }


def build_today_done_quests(conn: sqlite3.Connection) -> list[dict]:
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


def build_tomorrow_first_quest(conn: sqlite3.Connection) -> dict | None:
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


def generate_morning_brief(conn: sqlite3.Connection, state: dict) -> dict:
    main = state["main_mission"] or {}
    quest = state["current_quest"] or {}
    confirmed = state.get("confirmed_starting_point")
    due_items = state["due_items"][:3]
    unfinished = state["unfinished_items"][:3]
    recommendation = generate_priority_recommendation(state)
    candidates = recommendation["candidates"]
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
    if candidates:
        names = ", ".join(item["name"] for item in candidates[:3])
        lines.append(f"- 우선 검토 후보: {names}")
        lines.append(f"- 자동 추천 후보: {recommendation['title']}")

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
