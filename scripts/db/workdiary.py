from __future__ import annotations

import sqlite3
from datetime import datetime
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
