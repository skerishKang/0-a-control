from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from zoneinfo import ZoneInfo

try:
    from scripts.db_base import connect, rows_to_dicts
    from scripts.inbox_parse import resolve_source_aliases
except ModuleNotFoundError:
    from db_base import connect, rows_to_dicts
    from inbox_parse import resolve_source_aliases


def get_external_inbox_overview(limit: int = 8, status: str | None = None, category: str | None = None) -> dict:
    """
    Returns classified items and a summary of the external inbox.
    """
    try:
        from scripts.inbox_parse import resolve_source_aliases
    except ModuleNotFoundError:
        from inbox_parse import resolve_source_aliases

    with connect() as conn:
        table_exists = conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'external_inbox'"
        ).fetchone()
        if not table_exists:
            return {
                "summary": {"new": 0, "reviewing": 0, "accepted": 0, "rejected": 0, "archived": 0, "total": 0},
                "items": [],
                "categories": {},
            }

        params: list[Any] = []
        where_clauses = [
            "COALESCE(ei.source_id, '') NOT GLOB 'test_*'",
            "COALESCE(ei.source_name, '') NOT GLOB 'test_*'",
        ]

        if status:
            where_clauses.append("ei.status = ?")
            params.append(status)

        if category:
            resolved_sources = resolve_source_aliases([category])
            if resolved_sources:
                placeholders = ", ".join(["?"] * len(resolved_sources))
                where_clauses.append(f"COALESCE(ts.chat_class, '') IN ({placeholders})")
                params.extend(resolved_sources)

        where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
        params.append(limit)

        rows = rows_to_dicts(
            conn.execute(
                f"""
                SELECT
                    ei.id,
                    ei.source_type,
                    ei.source_id,
                    ei.source_name,
                    ei.author,
                    ei.item_type,
                    ei.title,
                    ei.raw_content,
                    ei.item_timestamp,
                    ei.imported_at,
                    ei.status,
                    COALESCE(ts.chat_class, '') AS chat_class,
                    COALESCE(ts.is_core, 0) AS is_core
                FROM external_inbox ei
                LEFT JOIN telegram_sources ts
                  ON ts.source_id = ei.source_id
                {where_sql}
                ORDER BY
                    CASE ei.status
                        WHEN 'new' THEN 1
                        WHEN 'reviewing' THEN 2
                        WHEN 'accepted' THEN 3
                        WHEN 'rejected' THEN 4
                        WHEN 'archived' THEN 5
                        ELSE 6
                    END,
                    COALESCE(NULLIF(ei.item_timestamp, ''), ei.imported_at) DESC,
                    ei.imported_at DESC,
                    ei.id DESC
                LIMIT ?
                """,
                tuple(params),
            ).fetchall()
        )

        core_four = {"local_chat", "kilo_chat", "self_chat", "kang_hyerim_chat"}
        for row in rows:
            c_class = row.get("chat_class", "")
            if row.get("is_core") or c_class in core_four:
                row["category"] = "핵심4개"
            elif c_class == "stock_curator_channel":
                row["category"] = "주식큐레이터"
            elif c_class == "news_channel":
                row["category"] = "뉴스"
            elif c_class == "general_chat" or c_class.startswith("chat_"):
                row["category"] = "일반대화"
            else:
                row["category"] = "기타"

            row["actions"] = ["save", "discard"]
            if row["status"] in ("new", "reviewing"):
                row["actions"].append("ai_ingest")

        counts = {
            row["status"]: row["count"]
            for row in conn.execute(
                """
                SELECT status, COUNT(*) AS count
                FROM external_inbox
                WHERE COALESCE(source_id, '') NOT GLOB 'test_*'
                  AND COALESCE(source_name, '') NOT GLOB 'test_*'
                GROUP BY status
                """
            ).fetchall()
        }

    return {
        "summary": {
            "new": counts.get("new", 0),
            "reviewing": counts.get("reviewing", 0),
            "accepted": counts.get("accepted", 0),
            "rejected": counts.get("rejected", 0),
            "archived": counts.get("archived", 0),
            "total": sum(counts.values()),
        },
        "items": rows,
    }


def get_external_inbox_source_messages(
    source_id: str,
    day: str = "today",
    limit: int = 500,
    before: str | None = None,
) -> dict:
    if not source_id:
        return {
            "source_id": "",
            "source_name": "",
            "day": day,
            "messages": [],
            "loaded_days": [],
            "has_more_before": False,
            "previous_day": None,
        }

    local_tz = ZoneInfo("Asia/Seoul")
    now_local = datetime.now(local_tz)

    with connect() as conn:
        rows = rows_to_dicts(
            conn.execute(
                """
                SELECT
                    ei.id,
                    ei.source_id,
                    ei.source_name,
                    ei.external_message_id,
                    ei.author,
                    ei.item_type,
                    ei.raw_content,
                    ei.attachment_path,
                    ei.item_timestamp,
                    ei.imported_at,
                    ei.status,
                    COALESCE(ts.chat_class, '') AS chat_class
                FROM external_inbox ei
                LEFT JOIN telegram_sources ts
                  ON ts.source_id = ei.source_id
                WHERE ei.source_id = ?
                  AND COALESCE(ei.source_id, '') NOT GLOB 'test_*'
                  AND COALESCE(ei.source_name, '') NOT GLOB 'test_*'
                ORDER BY COALESCE(NULLIF(ei.item_timestamp, ''), ei.imported_at) ASC,
                         ei.imported_at ASC,
                         ei.id ASC
                LIMIT ?
                """,
                (source_id, limit),
            ).fetchall()
        )

    def parse_dt(row: dict) -> datetime | None:
        raw = row.get("item_timestamp") or row.get("imported_at")
        if not raw:
            return None
        try:
            dt = datetime.fromisoformat(raw)
        except ValueError:
            return None
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(local_tz)

    dated_rows: list[tuple[dict, datetime]] = []
    for row in rows:
        dt = parse_dt(row)
        if dt:
            row["display_timestamp"] = dt.isoformat()
            row["display_day"] = dt.date().isoformat()
            dated_rows.append((row, dt))

    available_days = sorted({dt.date() for _, dt in dated_rows})
    if before:
        before_date = datetime.fromisoformat(before).date()
        candidate_days = [candidate for candidate in available_days if candidate < before_date]
        target_date = candidate_days[-1] if candidate_days else before_date
    elif day == "today":
        today_date = now_local.date()
        if today_date in available_days:
            target_date = today_date
        elif available_days:
            target_date = available_days[-1]
        else:
            target_date = today_date
    else:
        target_date = datetime.fromisoformat(day).date()

    filtered = [row for row, dt in dated_rows if dt.date() == target_date]
    previous_days = [candidate for candidate in available_days if candidate < target_date]

    source_name = filtered[0]["source_name"] if filtered else (rows[0]["source_name"] if rows else source_id)
    chat_class = filtered[0]["chat_class"] if filtered else (rows[0]["chat_class"] if rows else "")
    return {
        "source_id": source_id,
        "source_name": source_name,
        "chat_class": chat_class,
        "day": target_date.isoformat(),
        "loaded_days": [target_date.isoformat()],
        "has_more_before": bool(previous_days),
        "previous_day": previous_days[-1].isoformat() if previous_days else None,
        "messages": filtered,
    }
