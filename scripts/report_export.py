from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from .file_queue import REPORTS_DIR, generate_report_id, generate_filename, save_json
from .db_base import connect


def export_quest_report(
    quest_id: str,
    quest_title: str,
    completion_criteria: str,
    work_summary: str,
    remaining_work: str,
    blocker: str,
    self_assessment: str,
    session_id: str = "",
) -> Path:
    report_id = generate_report_id(quest_id, session_id)
    now_iso = datetime.now(timezone.utc).isoformat()

    plan_links: list[dict] = []
    plan_item_id = ""
    plan_bucket = ""
    with connect() as conn:
        quest = conn.execute(
            "SELECT plan_item_id FROM quests WHERE id = ?",
            (quest_id,),
        ).fetchone()
        if quest and quest["plan_item_id"]:
            plan_item_id = quest["plan_item_id"]
            plan_item = conn.execute(
                "SELECT bucket FROM plan_items WHERE id = ?",
                (plan_item_id,),
            ).fetchone()
            if plan_item:
                plan_bucket = plan_item["bucket"]
                plan_links.append({"bucket": plan_bucket, "plan_item_id": plan_item_id})

    data = {
        "report_id": report_id,
        "quest_id": quest_id,
        "session_id": session_id or "_",
        "generated_at": now_iso,
        "timezone": "Asia/Seoul",
        "agent_name": "control-tower-ui",
        "schema_version": "1.0",
        "correlation": {
            "quest_id": quest_id,
            "plan_item_id": plan_item_id,
            "plan_bucket": plan_bucket,
            "session_id": session_id or "_",
            "report_id": report_id,
        },
        "report": {
            "quest_id": quest_id,
            "quest_title": quest_title,
            "completion_criteria": completion_criteria,
            "work_summary": work_summary,
            "remaining_work": remaining_work,
            "blocker": blocker,
            "self_assessment": self_assessment,
            "plan_links": plan_links,
            "attachments": [],
        },
    }
    filename = generate_filename(report_id, suffix="report")
    return save_json(REPORTS_DIR, filename, data)
