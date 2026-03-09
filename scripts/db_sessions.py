from __future__ import annotations

import json
import uuid

from agent_registry import canonical_agent_name
from db_base import connect, now_iso, row_to_dict, rows_to_dicts
from db_state import refresh_current_state


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
        return row_to_dict(row) if row else {}


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


def _load_current_state(conn) -> dict:
    refresh_current_state(conn)
    rows = conn.execute(
        "SELECT state_key, state_value FROM current_state ORDER BY state_key ASC"
    ).fetchall()
    state: dict = {}
    for row in rows:
        value = row["state_value"]
        try:
            state[row["state_key"]] = json.loads(value)
        except (TypeError, json.JSONDecodeError):
            state[row["state_key"]] = value
    return state


def _compact_text(content: str, limit: int = 300) -> str:
    text = " ".join((content or "").split())
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def _format_resume_prompt(
    project_key: str,
    title: str,
    state: dict,
    previous_sessions: list[dict],
    recent_turns: list[dict],
) -> str:
    lines = [
        f"Resume work in project `{project_key or 'unknown-project'}`.",
        f"Session title: {title or 'untitled session'}",
        "",
        "Use this stored memory as a starting brief, not as ground truth.",
        "If the repository or SQLite state disagrees, trust the live state and note the mismatch.",
        "",
        "Current control state:",
        f"- Main mission: {state.get('main_mission_title') or '-'}",
        f"- Current quest: {state.get('current_quest_title') or '-'}",
        f"- Restart point: {state.get('restart_point') or '-'}",
        f"- Recommended next quest: {state.get('recommended_next_quest') or '-'}",
    ]

    if previous_sessions:
        lines.extend(["", "Recent sessions:"])
        for session in previous_sessions:
            lines.append(
                f"- {session.get('started_at') or '-'} | {session.get('agent_name') or '-'} | {session.get('title') or '(untitled)'}"
            )
            lines.append(f"  summary: {session.get('summary_md') or '-'}")

    if recent_turns:
        lines.extend(["", "Recent key turns from the latest prior session:"])
        for turn in recent_turns:
            lines.append(f"- {turn['role']}: {turn['content']}")

    lines.extend(
        [
            "",
            "Start by validating the restart point against the current codebase, then continue with the next concrete quest.",
        ]
    )
    return "\n".join(lines).strip()


def get_resume_context(
    project_key: str = "",
    working_dir: str = "",
    title: str = "",
    session_id: str = "",
    session_limit: int = 2,
    turn_limit: int = 3,
) -> dict:
    clauses = ["status != 'active'"]
    params: list[object] = []

    if session_id:
        clauses.append("id != ?")
        params.append(session_id)
    if project_key:
        clauses.append("project_key = ?")
        params.append(project_key)
    elif working_dir:
        clauses.append("working_dir = ?")
        params.append(working_dir)

    where_sql = " AND ".join(clauses)

    with connect() as conn:
        state = _load_current_state(conn)
        rows = conn.execute(
            f"""
            SELECT *
            FROM sessions
            WHERE {where_sql}
            ORDER BY COALESCE(ended_at, started_at) DESC
            LIMIT ?
            """,
            (*params, max(session_limit, 1)),
        ).fetchall()
        previous_sessions = rows_to_dicts(rows)

        recent_turns: list[dict] = []
        source_session_id = previous_sessions[0]["id"] if previous_sessions else ""
        if source_session_id:
            turn_rows = conn.execute(
                """
                SELECT role, content, created_at
                FROM source_records
                WHERE session_id = ?
                  AND source_type = 'agent_turn'
                  AND role IN ('user', 'assistant', 'system')
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (source_session_id, max(turn_limit, 1)),
            ).fetchall()
            recent_turns = [
                {
                    "role": row["role"],
                    "content": _compact_text(row["content"]),
                    "created_at": row["created_at"],
                }
                for row in reversed(turn_rows)
            ]

        prompt = _format_resume_prompt(
            project_key=project_key,
            title=title,
            state=state,
            previous_sessions=previous_sessions,
            recent_turns=recent_turns,
        )
        return {
            "generated_at": now_iso(),
            "project_key": project_key,
            "working_dir": working_dir,
            "source_session_id": source_session_id,
            "current_state": {
                "main_mission_title": state.get("main_mission_title", ""),
                "current_quest_title": state.get("current_quest_title", ""),
                "restart_point": state.get("restart_point", ""),
                "recommended_next_quest": state.get("recommended_next_quest", ""),
            },
            "prior_sessions": [
                {
                    "id": session.get("id"),
                    "agent_name": session.get("agent_name"),
                    "title": session.get("title"),
                    "started_at": session.get("started_at"),
                    "ended_at": session.get("ended_at"),
                    "summary_md": session.get("summary_md"),
                    "status": session.get("status"),
                }
                for session in previous_sessions
            ],
            "recent_turns": recent_turns,
            "prompt": prompt,
        }
