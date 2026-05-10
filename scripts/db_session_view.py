from __future__ import annotations

import json
from collections import Counter

try:
    from scripts.db_base import connect, row_to_dict, rows_to_dicts
    from scripts.session_summary import (
        build_session_badges,
        clean_transcript_content,
        infer_transcript_profile,
        parse_summary_md,
    )
except ModuleNotFoundError:
    from db_base import connect, row_to_dict, rows_to_dicts
    from session_summary import (
        build_session_badges,
        clean_transcript_content,
        infer_transcript_profile,
        parse_summary_md,
    )


def get_session_view_model(session_id: str, record_limit: int = 500) -> dict:
    with connect() as conn:
        session_row = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
        if session_row is None:
            raise ValueError("session not found")

        session = row_to_dict(session_row)
        record_rows = conn.execute(
            """
            SELECT *
            FROM source_records
            WHERE session_id = ?
            ORDER BY created_at ASC
            LIMIT ?
            """,
            (session_id, max(record_limit, 1)),
        ).fetchall()
        records = rows_to_dicts(record_rows)

    summary = parse_summary_md(session.get("summary_md") or "")
    badges = build_session_badges(session.get("summary_md") or "")

    dialogue_records = [
        record
        for record in records
        if record.get("source_type") == "agent_turn"
    ]
    transcript_records = [
        record
        for record in records
        if record.get("source_type") == "terminal_transcript"
    ]
    quest_report_record = next(
        (record for record in reversed(records) if record.get("source_type") == "quest_report"),
        None,
    )
    quest_verdict_record = next(
        (record for record in reversed(records) if record.get("source_type") == "quest_verdict"),
        None,
    )

    transcript_raw_content = "\n\n".join(
        record.get("content", "").strip() for record in transcript_records if record.get("content")
    ).strip()
    transcript_profile = infer_transcript_profile(agent_name=session.get("agent_name") or "")
    transcript_cleaned_content = clean_transcript_content(
        transcript_raw_content,
        profile=transcript_profile,
    )

    metadata_value = session.get("metadata_json")
    if isinstance(metadata_value, dict):
        metadata = metadata_value
    else:
        try:
            metadata = json.loads(metadata_value or "{}")
        except (TypeError, json.JSONDecodeError):
            metadata = {}

    files_touched_value = session.get("files_touched_json")
    if isinstance(files_touched_value, list):
        files_touched = files_touched_value
    else:
        try:
            files_touched = json.loads(files_touched_value or "[]")
        except (TypeError, json.JSONDecodeError):
            files_touched = []

    actions_value = session.get("actions_json")
    if isinstance(actions_value, list):
        actions_json = actions_value
    else:
        try:
            actions_json = json.loads(actions_value or "[]")
        except (TypeError, json.JSONDecodeError):
            actions_json = []

    role_counts = Counter(record.get("role") or "tool" for record in dialogue_records)

    return {
        "session_id": session["id"],
        "header": {
            "title": session.get("title") or session.get("project_key") or "세션",
            "started_at": session.get("started_at"),
            "ended_at": session.get("ended_at"),
            "status": session.get("status"),
        },
        "meta": {
            "agent_name": session.get("agent_name"),
            "model_name": session.get("model_name"),
            "project_key": session.get("project_key"),
            "working_dir": session.get("working_dir"),
            "source_type": session.get("source_type"),
        },
        "summary": summary,
        "badges": badges,
        "artifacts": {
            "files_touched": files_touched,
            "actions": actions_json,
        },
        "quest": {
            "report": quest_report_record.get("content") if quest_report_record else "",
            "verdict": quest_verdict_record.get("content") if quest_verdict_record else "",
        },
        "dialogue": dialogue_records,
        "transcript": {
            "available": bool(transcript_raw_content or transcript_cleaned_content),
            "record_count": len(transcript_records),
            "profile": transcript_profile,
            "raw_content": transcript_raw_content,
            "cleaned_content": transcript_cleaned_content,
            "content": transcript_cleaned_content,
        },
        "records": {
            "all": records,
            "counts": {
                "total": len(records),
                "dialogue": len(dialogue_records),
                "transcript": len(transcript_records),
                "user": role_counts.get("user", 0),
                "assistant": role_counts.get("assistant", 0),
                "tool": role_counts.get("tool", 0),
            },
        },
        "metadata": metadata,
    }
