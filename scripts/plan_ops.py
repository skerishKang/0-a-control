from __future__ import annotations

import uuid

from scripts.db_base import connect, now_iso, record_event, row_to_dict, rows_to_dicts
from scripts.db_sessions import append_source_record
from scripts.db_state import refresh_current_state


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


def approve_plan_candidates(candidates: list[dict], session_id: str = "") -> list[dict]:
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
                    item_id,
                    bucket,
                    title,
                    description,
                    status,
                    priority_score,
                    session_id or None,
                    related_source_id,
                    updated_at,
                    updated_at,
                ),
            )

            if related_source_id:
                conn.execute(
                    "UPDATE external_inbox SET status = 'accepted', processed_at = ? WHERE id = ?",
                    (updated_at, related_source_id),
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
            log_lines = [f"Approved {len(created_items)} plan items:"]
            for item in created_items:
                log_lines.append(f"- [{item['bucket']}] {item['title']}")

            append_source_record(
                session_id=session_id,
                source_name="inbox_cli",
                source_type="plan_update",
                content="\n".join(log_lines),
                role="system",
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
