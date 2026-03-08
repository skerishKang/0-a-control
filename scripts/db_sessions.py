from __future__ import annotations

import json
import uuid

from agent_registry import canonical_agent_name
from db_base import connect, now_iso, row_to_dict, rows_to_dicts


def start_session(
    agent_name: str,
    source_type: str,
    model_name: str = "",
    project_key: str = "",
    working_dir: str = "",
    title: str = "",
    metadata: dict | None = None,
) -> dict:
    agent_name = canonical_agent_name(agent_name)
    session_id = str(uuid.uuid4())
    started_at = now_iso()
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
        row = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
        return row_to_dict(row)


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
        return row_to_dict(row)


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
        merged_metadata = dict(session["metadata_json"] and json.loads(session["metadata_json"]) or {})
        if metadata:
            merged_metadata.update(metadata)
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
        row = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
        return row_to_dict(row)


def update_session_summary(session_id: str, summary_md: str, metadata: dict | None = None) -> dict:
    with connect() as conn:
        session = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
        if session is None:
            raise ValueError("session not found")

        merged_metadata = dict(session["metadata_json"] and json.loads(session["metadata_json"]) or {})
        if metadata:
            merged_metadata.update(metadata)

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
        row = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
        return row_to_dict(row)


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
