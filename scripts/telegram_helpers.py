from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from scripts.telegram_db import get_db_connection


def _get_core_sources_sync_status() -> list[dict]:
    conn = get_db_connection()
    rows = conn.execute(
        """
        SELECT 
            ts.source_id, ts.source_name, ts.chat_class, ts.is_core, ts.sync_mode, ts.last_synced_at, ts.last_message_id,
            COUNT(CASE WHEN ei.status = 'new' THEN 1 END) as new_count,
            COUNT(CASE WHEN ei.status = 'reviewing' THEN 1 END) as reviewing_count
        FROM telegram_sources ts
        LEFT JOIN external_inbox ei ON ts.source_id = ei.source_id
        WHERE ts.is_core = 1
        GROUP BY ts.source_id
        ORDER BY ts.source_name COLLATE NOCASE ASC
        """
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def _normalize_message_timestamp(raw_value, fallback_iso: str) -> str:
    if raw_value is None:
        return fallback_iso
    if isinstance(raw_value, (int, float)):
        return datetime.fromtimestamp(raw_value, timezone.utc).isoformat()
    if isinstance(raw_value, str):
        cleaned = raw_value.strip()
        if not cleaned:
            return fallback_iso
        return cleaned
    return fallback_iso


def _format_bytes(num_bytes: int | None) -> str:
    value = int(num_bytes or 0)
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(value)
    for unit in units:
        if size < 1024 or unit == units[-1]:
            if unit == "B":
                return f"{int(size)}{unit}"
            return f"{size:.1f}{unit}"
        size /= 1024
    return f"{value}B"


def _metadata_file_size(row) -> int | None:
    raw = row["metadata_json"] if "metadata_json" in row.keys() else None
    if not raw:
        return None
    try:
        metadata = json.loads(raw)
    except Exception:
        return None
    try:
        value = metadata.get("file_size")
        return int(value) if value is not None else None
    except Exception:
        return None


def _mask_phone(phone: str | None) -> str | None:
    if not phone:
        return None
    if len(phone) <= 7:
        return "****"
    return f"{phone[:4]}****{phone[-4:]}"


def _safe_path_part(value: str | None, fallback: str = "unknown") -> str:
    raw = (value or "").strip()
    if not raw:
        return fallback
    cleaned = re.sub(r'[\\/:*?"<>|\r\n\t]+', "_", raw)
    cleaned = re.sub(r"\s+", "_", cleaned).strip("._ ")
    return cleaned or fallback


def _classify_message_type(message) -> str:
    if getattr(message, "photo", None):
        return "image"
    if getattr(message, "voice", None):
        return "audio"
    if getattr(message, "video", None):
        return "video"
    if getattr(message, "audio", None):
        return "audio"
    if getattr(message, "document", None):
        return "file"
    return "text"


def _message_sender_label(message) -> str:
    if getattr(message, "out", False):
        return "me"
    sender = getattr(message, "sender", None)
    if sender is not None:
        if getattr(sender, "username", None):
            return sender.username
        if getattr(sender, "first_name", None):
            return sender.first_name
        if getattr(sender, "title", None):
            return sender.title
    return str(getattr(message, "sender_id", None) or "Unknown")


def _count_missing_attachments(source_id: str) -> int:
    conn = get_db_connection()
    result = conn.execute(
        """
        SELECT COUNT(*) AS count
        FROM external_inbox
        WHERE source_type = 'telegram'
          AND source_id = ?
          AND COALESCE(item_type, 'text') != 'text'
          AND COALESCE(attachment_path, '') = ''
        """,
        (source_id,),
    ).fetchone()
    conn.close()
    return result["count"]
