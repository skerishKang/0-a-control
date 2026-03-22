from __future__ import annotations

import json
import re

from scripts.db_base import connect, rows_to_dicts
from scripts.db_state import refresh_current_state
from scripts.plan_ops import approve_plan_candidates, get_latest_briefs, get_plans
from scripts.verdict_ops import DuplicateVerdict, apply_verdict, report_quest_progress


VERDICT_STATUS_RE = re.compile(r"^AI 판정:\s*(done|partial|hold|pending)\b", re.MULTILINE)


def get_current_state() -> dict:
    with connect() as conn:
        refresh_current_state(conn)
        rows = conn.execute(
            "SELECT state_key, state_value, updated_at, metadata_json FROM current_state ORDER BY state_key ASC"
        ).fetchall()
        state: dict = {}
        for row in rows:
            value = row["state_value"]
            try:
                state[row["state_key"]] = json.loads(value)
            except (TypeError, json.JSONDecodeError):
                state[row["state_key"]] = value
        return state

def get_quests() -> list[dict]:
    with connect() as conn:
        return rows_to_dicts(conn.execute("SELECT * FROM quests ORDER BY updated_at DESC").fetchall())


def get_recent_sessions(limit: int = 10) -> list[dict]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT
                s.*,
                EXISTS(
                    SELECT 1
                    FROM source_records sr
                    WHERE sr.session_id = s.id
                      AND sr.source_type = 'quest_verdict'
                ) AS has_quest_verdict
            FROM sessions s
            ORDER BY s.started_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        sessions = rows_to_dicts(rows)
        for session in sessions:
            verdict_row = conn.execute(
                """
                SELECT content
                FROM source_records
                WHERE session_id = ?
                  AND source_type = 'quest_verdict'
                ORDER BY created_at DESC
                LIMIT 1
                """,
                (session["id"],),
            ).fetchone()
            status = ""
            if verdict_row and verdict_row["content"]:
                match = VERDICT_STATUS_RE.search(verdict_row["content"])
                if match:
                    status = match.group(1)
            session["quest_verdict_status"] = status
        return sessions
