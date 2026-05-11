from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

if __package__ in (None, ""):
    from scripts.telegram_db import DATA_DIR
    from scripts.telegram_helpers import (
        _mask_phone,
        _safe_path_part,
        _classify_message_type,
    )
else:
    from .telegram_db import DATA_DIR
    from .telegram_helpers import (
        _mask_phone,
        _safe_path_part,
        _classify_message_type,
    )


RUNTIME_DIR = Path(DATA_DIR) / "runtime"
TELEGRAM_BLOBS_DIR = Path(DATA_DIR) / "blobs" / "telegram"
STATUS_FILE = RUNTIME_DIR / "telegram_status.json"
LOCAL_TIMEZONE = ZoneInfo("Asia/Seoul")


def _runtime_dir() -> Path:
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    return RUNTIME_DIR


def _write_status(payload: dict) -> None:
    _runtime_dir()
    STATUS_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _original_attachment_name(message, item_type: str) -> str | None:
    file_obj = getattr(message, "file", None)
    original_name = getattr(file_obj, "name", None) if file_obj else None
    if original_name:
        return original_name

    ext = getattr(file_obj, "ext", None) if file_obj else None
    ext = ext or ""
    base = {
        "image": "image",
        "audio": "audio",
        "video": "video",
        "file": "file",
    }.get(item_type, "attachment")
    return f"{base}{ext}" if item_type != "text" else None


def _build_attachment_path(source_name: str, message, item_type: str) -> Path | None:
    if item_type == "text":
        return None

    message_dt = message.date.astimezone(LOCAL_TIMEZONE) if message.date else datetime.now(LOCAL_TIMEZONE)
    day_part = message_dt.strftime("%Y-%m-%d")
    safe_source = _safe_path_part(source_name or "telegram")
    original_name = _safe_path_part(_original_attachment_name(message, item_type), f"{item_type}")
    filename = f"{safe_source}_{day_part}_{message.id}_{original_name}"
    target_dir = TELEGRAM_BLOBS_DIR / safe_source / day_part
    target_dir.mkdir(parents=True, exist_ok=True)
    return target_dir / filename


def _inspect_attachment(message) -> dict:
    item_type = _classify_message_type(message)
    file_obj = getattr(message, "file", None)
    original_name = _original_attachment_name(message, item_type)
    return {
        "item_type": item_type,
        "attachment_path": None,
        "attachment_name": original_name,
        "mime_type": getattr(file_obj, "mime_type", None) if file_obj else None,
        "file_size": getattr(file_obj, "size", None) if file_obj else None,
    }
