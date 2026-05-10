from __future__ import annotations

import json

try:
    from scripts.db_base import connect, now_iso, rows_to_dicts
    from scripts.db_state import refresh_current_state
except ModuleNotFoundError:
    from db_base import connect, now_iso, rows_to_dicts
    from db_state import refresh_current_state


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


def _load_transcript_excerpt(conn, session_id: str, limit: int = 8) -> list[str]:
    row = conn.execute(
        """
        SELECT content
        FROM source_records
        WHERE session_id = ?
          AND source_type = 'terminal_transcript'
        ORDER BY created_at DESC
        LIMIT 1
        """,
        (session_id,),
    ).fetchone()
    if row is None or not row["content"]:
        return []

    lines: list[str] = []
    for raw_line in row["content"].splitlines():
        line = " ".join((raw_line or "").split()).strip()
        if not line:
            continue
        if line.startswith("Script started on"):
            continue
        if line.startswith("Script done on"):
            continue
        if line.startswith("Windows PowerShell 기록"):
            continue
        if line in {"Working", "Explored"}:
            continue
        if len(line) >= 20 and set(line) <= {"│", "•", "─", " ", "╭", "╮", "╰", "╯"}:
            continue
        if line.startswith("│ directory:") or line.startswith("directory:"):
            continue
        if line.startswith("│ model:") or line.startswith("model:"):
            continue
        if "OpenAI Codex" in line and "directory:" in line:
            continue
        lines.append(_compact_text(line, 220))
        if len(lines) >= limit:
            break
    return lines


def _format_resume_prompt(
    project_key: str,
    title: str,
    state: dict,
    previous_sessions: list[dict],
    recent_turns: list[dict],
    compact: bool = False,
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

    if compact and previous_sessions:
        latest = previous_sessions[0]
        lines.extend(
            [
                "",
                "Latest prior session:",
                f"- {latest.get('started_at') or '-'} | {latest.get('agent_name') or '-'} | {latest.get('title') or '(untitled)'}",
                f"- Summary: {latest.get('summary_md') or '-'}",
            ]
        )
    elif previous_sessions:
        lines.extend(["", "Recent sessions:"])
        for session in previous_sessions:
            lines.append(
                f"- {session.get('started_at') or '-'} | {session.get('agent_name') or '-'} | {session.get('title') or '(untitled)'}"
            )
            lines.append(f"  summary: {session.get('summary_md') or '-'}")

    if recent_turns and not compact:
        lines.extend(["", "Recent key turns from the latest prior session:"])
        for turn in recent_turns:
            lines.append(f"- {turn['role']}: {turn['content']}")
    elif state.get("_transcript_excerpt"):
        lines.extend(["", "Recent transcript excerpt from the latest prior session:"])
        for line in state["_transcript_excerpt"]:
            lines.append(f"- {line}")

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
            if not recent_turns:
                state["_transcript_excerpt"] = _load_transcript_excerpt(conn, source_session_id)

        prompt = _format_resume_prompt(
            project_key=project_key,
            title=title,
            state=state,
            previous_sessions=previous_sessions,
            recent_turns=recent_turns,
        )
        compact_prompt = _format_resume_prompt(
            project_key=project_key,
            title=title,
            state=state,
            previous_sessions=previous_sessions,
            recent_turns=recent_turns,
            compact=True,
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
            "compact_prompt": compact_prompt,
        }
