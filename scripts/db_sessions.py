from __future__ import annotations

import json
import uuid

try:
    from scripts.agent_registry import canonical_agent_name
    from scripts.db_base import connect, merge_metadata, now_iso, record_event, row_to_dict, rows_to_dicts
    from scripts.session_summary import build_session_badges, clean_transcript_content, infer_transcript_profile, parse_summary_md
except ModuleNotFoundError:
    from agent_registry import canonical_agent_name
    from db_base import connect, merge_metadata, now_iso, record_event, row_to_dict, rows_to_dicts
    from session_summary import build_session_badges, clean_transcript_content, infer_transcript_profile, parse_summary_md


def start_session(
    agent_name: str,
    source_type: str,
    model_name: str = "",
    project_key: str = "",
    working_dir: str = "",
    title: str = "",
    metadata: dict | None = None,
    include_resume_context: bool = False,
    resume_session_limit: int = 2,
    resume_turn_limit: int = 3,
) -> dict:
    agent_name = canonical_agent_name(agent_name)
    session_id = str(uuid.uuid4())
    started_at = now_iso()
    result: dict = {}
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO sessions (
                id, agent_name, model_name, source_type, project_key, working_dir, title,
                started_at, ended_at, summary_md, status, files_touched_json, actions_json, metadata_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                session_id,
                agent_name,
                model_name or None,
                source_type,
                project_key or None,
                working_dir or None,
                title or None,
                started_at,
                None,
                None,
                "active",
                None,
                None,
                json.dumps(metadata, ensure_ascii=False) if metadata else None,
            ),
        )
        record_event(
            conn,
            event_type="session_start",
            entity_id=session_id,
            entity_type="session",
            detail=title or f"{agent_name} session started",
            metadata={
                "agent_name": agent_name,
                "source_type": source_type,
                "model_name": model_name or "",
                "project_key": project_key or "",
                "working_dir": working_dir or "",
            },
            created_at=started_at,
        )
        row = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
        result = row_to_dict(row) if row else {}
    if include_resume_context and result:
        result["resume_context"] = get_resume_context(
            project_key=project_key,
            working_dir=working_dir,
            title=title,
            session_id=session_id,
            session_limit=resume_session_limit,
            turn_limit=resume_turn_limit,
        )
    return result


def append_source_record(
    session_id: str,
    source_name: str,
    source_type: str,
    content: str,
    role: str = "user",
    project_key: str = "",
    working_dir: str = "",
    metadata: dict | None = None,
) -> dict:
    source_name = canonical_agent_name(source_name)
    record_id = str(uuid.uuid4())
    created_at = now_iso()
    with connect() as conn:
        session = conn.execute("SELECT id FROM sessions WHERE id = ?", (session_id,)).fetchone()
        if session is None:
            raise ValueError("session not found")
        conn.execute(
            """
            INSERT INTO source_records (
                id, source_type, source_name, session_id, project_key, working_dir,
                role, content, created_at, metadata_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record_id,
                source_type,
                source_name,
                session_id,
                project_key or None,
                working_dir or None,
                role,
                content,
                created_at,
                json.dumps(metadata, ensure_ascii=False) if metadata else None,
            ),
        )
        row = conn.execute("SELECT * FROM source_records WHERE id = ?", (record_id,)).fetchone()
        return row_to_dict(row) if row else {}


def end_session(
    session_id: str,
    summary_md: str = "",
    status: str = "closed",
    files_touched: list[str] | None = None,
    actions: list[str] | None = None,
    metadata: dict | None = None,
) -> dict:
    ended_at = now_iso()
    with connect() as conn:
        session = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
        if session is None:
            raise ValueError("session not found")
        merged_metadata = merge_metadata(session["metadata_json"], metadata)
        summary_value = summary_md or session["summary_md"]
        conn.execute(
            """
            UPDATE sessions
            SET ended_at = ?, summary_md = ?, status = ?, files_touched_json = ?, actions_json = ?, metadata_json = ?
            WHERE id = ?
            """,
            (
                ended_at,
                summary_value or None,
                status,
                json.dumps(files_touched, ensure_ascii=False) if files_touched else None,
                json.dumps(actions, ensure_ascii=False) if actions else None,
                json.dumps(merged_metadata, ensure_ascii=False) if merged_metadata else None,
                session_id,
            ),
        )
        record_event(
            conn,
            event_type="session_end",
            entity_id=session_id,
            entity_type="session",
            detail=summary_value or session["title"] or "session ended",
            metadata={
                "status": status,
                "files_touched_count": len(files_touched or []),
                "actions_count": len(actions or []),
            },
            created_at=ended_at,
        )
        row = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
        return row_to_dict(row) if row else {}


def close_latest_active_session_for_agent(
    agent_name: str,
    summary_md: str = "stale active session closed from dashboard",
    metadata: dict | None = None,
) -> dict:
    agent_key = str(agent_name or "").strip()
    if not agent_key:
        raise ValueError("agent_name is required")

    with connect() as conn:
        row = conn.execute(
            """
            SELECT id
            FROM sessions
            WHERE agent_name = ? AND status = 'active'
            ORDER BY started_at DESC, rowid DESC
            LIMIT 1
            """,
            (agent_key,),
        ).fetchone()
        if row is None:
            raise ValueError("no active session found for agent")
        session_id = row["id"]

    merged_metadata = {"cleanup_source": "dashboard_agent_status"}
    if metadata:
        merged_metadata.update(metadata)
    return end_session(
        session_id=session_id,
        summary_md=summary_md,
        status="closed",
        metadata=merged_metadata,
    )


def update_session_summary(session_id: str, summary_md: str, metadata: dict | None = None) -> dict:
    with connect() as conn:
        session = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
        if session is None:
            raise ValueError("session not found")

        merged_metadata = merge_metadata(session["metadata_json"], metadata)

        conn.execute(
            """
            UPDATE sessions
            SET summary_md = ?, metadata_json = ?
            WHERE id = ?
            """,
            (
                summary_md or None,
                json.dumps(merged_metadata, ensure_ascii=False) if merged_metadata else None,
                session_id,
            ),
        )
        record_event(
            conn,
            event_type="session_summary_updated",
            entity_id=session_id,
            entity_type="session",
            detail=(summary_md or "")[:100],
            metadata={"has_summary": bool(summary_md)},
        )
        row = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
        return row_to_dict(row) if row else {}


def get_source_records(session_id: str, limit: int = 200) -> list[dict]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT * FROM source_records
            WHERE session_id = ?
            ORDER BY created_at ASC
            LIMIT ?
            """,
            (session_id, limit),
        ).fetchall()
        return rows_to_dicts(rows)


def get_session(session_id: str) -> dict:
    with connect() as conn:
        row = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
        if row is None:
            raise ValueError("session not found")
        return row_to_dict(row)



try:
    from scripts.db_session_view import get_session_view_model  # noqa: F401
except ModuleNotFoundError:
    from db_session_view import get_session_view_model  # noqa: F401


try:
    from scripts.db_session_resume import get_resume_context  # noqa: F401
except ModuleNotFoundError:
    from db_session_resume import get_resume_context  # noqa: F401

