from __future__ import annotations

import json
import re

from scripts.db_base import connect, now_iso, record_event, row_to_dict, rows_to_dicts
from scripts.db_sessions import append_source_record
from scripts.db_state import refresh_current_state


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


def get_plans() -> list[dict]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT * FROM plan_items
            ORDER BY
                CASE bucket
                    WHEN 'today' THEN 1
                    WHEN 'dated' THEN 2
                    WHEN 'short_term' THEN 3
                    WHEN 'long_term' THEN 4
                    WHEN 'recurring' THEN 5
                    ELSE 6
                END,
                priority_score DESC,
                updated_at DESC
            """
        ).fetchall()
        return rows_to_dicts(rows)


def get_quests() -> list[dict]:
    with connect() as conn:
        return rows_to_dicts(conn.execute("SELECT * FROM quests ORDER BY updated_at DESC").fetchall())


def approve_plan_candidates(candidates: list[dict], session_id: str = "") -> list[dict]:
    """
    Takes a list of plan candidates (from AI summary) and creates plan_items in the database.
    Each candidate should have: 'title', 'bucket', and optionally 'description', 'priority_score', 'related_source_id'.
    """
    created_items = []
    updated_at = now_iso()
    
    with connect() as conn:
        for cand in candidates:
            item_id = str(uuid.uuid4())
            bucket = cand.get("bucket", "short_term")
            title = cand.get("title", "Untitled Plan")
            description = cand.get("description", "")
            status = "pending"
            priority_score = cand.get("priority_score", 50)
            related_source_id = cand.get("related_source_id")
            
            conn.execute(
                """
                INSERT INTO plan_items (
                    id, bucket, title, description, status, 
                    priority_score, related_session_id, related_source_id,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item_id, bucket, title, description, status,
                    priority_score, session_id or None, related_source_id,
                    updated_at, updated_at
                )
            )
            
            # If related to an inbox item, mark it as accepted
            if related_source_id:
                conn.execute(
                    "UPDATE external_inbox SET status = 'accepted', processed_at = ? WHERE id = ?",
                    (updated_at, related_source_id)
                )
            
            row = conn.execute("SELECT * FROM plan_items WHERE id = ?", (item_id,)).fetchone()
            created_items.append(row_to_dict(row))
            record_event(
                conn,
                event_type="plan_item_created",
                entity_id=item_id,
                entity_type="plan_item",
                detail=title,
                metadata={
                    "bucket": bucket,
                    "priority_score": priority_score,
                    "related_source_id": related_source_id,
                },
                created_at=updated_at,
            )

        if session_id:
            # Log the action to the session
            log_lines = [f"Approved {len(created_items)} plan items:"]
            for item in created_items:
                log_lines.append(f"- [{item['bucket']}] {item['title']}")
            
            append_source_record(
                session_id=session_id,
                source_name="inbox_cli",
                source_type="plan_update",
                content="\n".join(log_lines),
                role="system"
            )
            
        refresh_current_state(conn)
        
    return created_items


def get_latest_briefs(limit: int = 10) -> list[dict]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM brief_records
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return rows_to_dicts(rows)


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

