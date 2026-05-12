from __future__ import annotations

import asyncio
import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable
from zoneinfo import ZoneInfo

if __package__ in (None, ""):
    from scripts.telegram_db import DATA_DIR
    from scripts.telegram_helpers import (
        _mask_phone,
        _safe_path_part,
        _classify_message_type,
        _message_sender_label,
    )
    from scripts.telegram_service_helpers import (
        _runtime_dir,
        _write_status,
        _original_attachment_name,
        _build_attachment_path,
        _inspect_attachment,
    )
    from scripts.telegram_session_lock import (
        TelegramSessionBusyError,
        acquire_telegram_session_lock,
        get_telegram_session_lock_status,
        _clear_session_lock,
    )
else:
    from .telegram_db import DATA_DIR
    from .telegram_helpers import (
        _mask_phone,
        _safe_path_part,
        _classify_message_type,
        _message_sender_label,
    )
    from .telegram_service_helpers import (
        _runtime_dir,
        _write_status,
        _original_attachment_name,
        _build_attachment_path,
        _inspect_attachment,
    )
    from .telegram_session_lock import (
        TelegramSessionBusyError,
        acquire_telegram_session_lock,
        get_telegram_session_lock_status,
        _clear_session_lock,
    )


RUNTIME_DIR = Path(DATA_DIR) / "runtime"
TELEGRAM_BLOBS_DIR = Path(DATA_DIR) / "blobs" / "telegram"
STATUS_FILE = RUNTIME_DIR / "telegram_status.json"
CHATS_CACHE_FILE = RUNTIME_DIR / "telegram_chats.json"
DEFAULT_SESSION_PATH = RUNTIME_DIR / "telegram_userbot.session"
TELEGRAM_HEARTBEAT_TTL_SECONDS = 1800
LOCAL_TIMEZONE = ZoneInfo("Asia/Seoul")


def _load_local_env() -> None:
    if os.environ.get("CONTROL_TOWER_IGNORE_DOTENV") == "1":
        return
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if key and key not in os.environ:
            os.environ[key] = value.strip()


def _telegram_env() -> dict:
    _load_local_env()
    return {
        "api_id": os.environ.get("TELEGRAM_API_ID"),
        "api_hash": os.environ.get("TELEGRAM_API_HASH"),
        "phone": os.environ.get("TELEGRAM_PHONE_NUMBER"),
        "password": os.environ.get("TELEGRAM_2FA_PASSWORD"),
        "session_path": os.environ.get("CONTROL_TOWER_TELEGRAM_SESSION_PATH", str(DEFAULT_SESSION_PATH)),
    }


def _missing_config_items(env: dict) -> list[str]:
    missing: list[str] = []
    if not env.get("api_id"):
        missing.append("TELEGRAM_API_ID")
    if not env.get("api_hash"):
        missing.append("TELEGRAM_API_HASH")
    return missing


def _session_path_label(session_path: Path) -> str:
    return session_path.name or "telegram_userbot.session"


def _session_dir_label(session_path: Path) -> str:
    parent_name = session_path.parent.name
    return parent_name if parent_name else "[redacted]"


def _build_status_payload() -> dict:
    env = _telegram_env()
    session_path = Path(env["session_path"])
    missing = _missing_config_items(env)
    configured = not missing
    session_exists = session_path.exists()

    if missing:
        setup_message = f"Telegram API 설정이 부족합니다: {', '.join(missing)}"
    elif not session_exists:
        setup_message = (
            "Telegram API 설정은 준비됐지만 첫 인증 세션 파일이 아직 없습니다. "
            "첫 연결이 성공하면 세션 파일이 생성됩니다."
        )
    else:
        setup_message = "Telegram API 설정과 세션 파일이 준비되어 있습니다."

    return {
        "configured": configured,
        "missing_config": missing,
        "session_path": _session_path_label(session_path),
        "session_dir": _session_dir_label(session_path),
        "session_exists": session_exists,
        "first_session_required": configured and not session_exists,
        "connected": False,
        "auth_required": False,
        "user": None,
        "setup_message": setup_message,
    }


async def _download_attachment(
    client,
    source_name: str,
    message,
    progress_callback: Callable[[dict], None] | None = None,
) -> dict:
    attachment_info = _inspect_attachment(message)
    item_type = attachment_info["item_type"]
    if item_type == "text":
        return attachment_info

    target_path = _build_attachment_path(source_name, message, item_type)
    if target_path is None:
        return attachment_info

    base_event = {
        "message_id": getattr(message, "id", None),
        "item_type": item_type,
        "attachment_name": attachment_info["attachment_name"],
        "file_size": attachment_info["file_size"],
        "target_path": str(target_path),
    }

    if not target_path.exists():
        if progress_callback:
            progress_callback({**base_event, "stage": "start"})

        last_percent = {"value": -1}

        def on_progress(current: int, total: int) -> None:
            if not progress_callback or total <= 0:
                return
            percent = int((current / total) * 100)
            if percent // 10 == last_percent["value"] // 10 and percent not in {0, 100}:
                return
            last_percent["value"] = percent
            progress_callback(
                {
                    **base_event,
                    "stage": "progress",
                    "current_bytes": current,
                    "total_bytes": total,
                    "percent": percent,
                }
            )

        downloaded = await client.download_media(
            message,
            file=str(target_path),
            progress_callback=on_progress,
        )
        if downloaded and downloaded != str(target_path):
            target_path = Path(downloaded)
        if progress_callback:
            progress_callback(
                {
                    **base_event,
                    "stage": "done",
                    "target_path": str(target_path),
                    "current_bytes": attachment_info["file_size"],
                    "total_bytes": attachment_info["file_size"],
                    "percent": 100,
                }
            )
    elif progress_callback:
        progress_callback({**base_event, "stage": "exists"})

    return {
        "item_type": item_type,
        "attachment_path": str(target_path),
        "attachment_name": target_path.name,
        "mime_type": attachment_info["mime_type"],
        "file_size": attachment_info["file_size"],
    }


def _get_telegram_client():
    env = _telegram_env()
    missing = _missing_config_items(env)
    if missing:
        raise RuntimeError(f"Telegram API 설정이 부족합니다: {', '.join(missing)}")

    from telethon import TelegramClient

    session_path = Path(env["session_path"])
    session_path.parent.mkdir(parents=True, exist_ok=True)
    return TelegramClient(str(session_path), int(env["api_id"]), env["api_hash"])


async def _connect_client():
    client = _get_telegram_client()

    env = _telegram_env()
    try:
        if not client.is_connected():
            if env["phone"]:
                await client.start(phone=env["phone"], password=env["password"])
            else:
                await client.connect()
        if not client.is_connected():
            await client.connect()
        return client
    except Exception as exc:
        _write_status(
            {
                "connected": False,
                "last_seen": datetime.now(timezone.utc).isoformat(),
                "error": str(exc),
                "auth_required": True,
                "setup_message": "Telegram 인증 또는 첫 세션 생성이 필요합니다.",
            }
        )
        raise


async def _disconnect_client(client) -> None:
    if client and client.is_connected():
        await client.disconnect()


async def _get_me_safe(client):
    try:
        return await client.get_me()
    except Exception:
        return None


def get_telegram_status() -> dict:
    payload = _build_status_payload()

    if STATUS_FILE.exists():
        try:
            status_data = json.loads(STATUS_FILE.read_text(encoding="utf-8"))
            payload.update(
                {
                    "connected": bool(status_data.get("connected")),
                    "auth_required": bool(status_data.get("auth_required")),
                    "user": status_data.get("user"),
                    "last_seen": status_data.get("last_seen"),
                    "error": status_data.get("error"),
                    "setup_message": status_data.get("setup_message") or payload.get("setup_message"),
                }
            )
            last_seen = status_data.get("last_seen")
            if last_seen:
                seen_dt = datetime.fromisoformat(last_seen)
                if (datetime.now(timezone.utc) - seen_dt).total_seconds() > TELEGRAM_HEARTBEAT_TTL_SECONDS:
                    payload["connected"] = False
        except Exception as exc:
            payload["error"] = str(exc)

    return payload


async def _fetch_chats_async(limit: int = 50) -> list[dict]:
    client = await _connect_client()

    try:
        me = await _get_me_safe(client)
        if me:
            _write_status(
                {
                    "connected": True,
                    "last_seen": datetime.now(timezone.utc).isoformat(),
                    "auth_required": False,
                    "user": {
                        "id": me.id,
                        "first_name": getattr(me, "first_name", None),
                        "username": getattr(me, "username", None),
                        "phone": _mask_phone(getattr(me, "phone", None)),
                    },
                }
            )

        dialogs = await client.get_dialogs(limit=limit)
        chats = []
        for dialog in dialogs:
            entity = dialog.entity
            chats.append(
                {
                    "id": entity.id,
                    "title": getattr(entity, "title", None) or getattr(entity, "first_name", "Unknown"),
                    "type": "channel" if getattr(entity, "broadcast", False) else ("group" if getattr(entity, "megagroup", False) else "user"),
                    "unread_count": dialog.unread_count,
                    "last_message_date": dialog.message.date.isoformat() if dialog.message and dialog.message.date else None,
                }
            )

        _runtime_dir()
        CHATS_CACHE_FILE.write_text(
            json.dumps({"chats": chats, "updated": datetime.now(timezone.utc).isoformat()}, ensure_ascii=False),
            encoding="utf-8",
        )
        return chats
    finally:
        await _disconnect_client(client)


async def _fetch_messages_async(
    chat_id: str,
    limit: int = 200,
    max_id: int | None = None,
    download_attachments: bool = True,
    message_ids: list[int] | None = None,
    attachment_progress_callback: Callable[[dict], None] | None = None,
) -> list[dict]:
    client = await _connect_client()
    if not chat_id:
        return []

    try:
        me = await _get_me_safe(client)
        if me:
            _write_status(
                {
                    "connected": True,
                    "last_seen": datetime.now(timezone.utc).isoformat(),
                    "auth_required": False,
                    "user": {
                        "id": me.id,
                        "first_name": getattr(me, "first_name", None),
                        "username": getattr(me, "username", None),
                        "phone": _mask_phone(getattr(me, "phone", None)),
                    },
                }
            )

        entity = await client.get_entity(int(chat_id))
        if message_ids is not None:
            messages = await client.get_messages(entity, ids=message_ids)
            messages = [message for message in messages if message is not None]
        else:
            kwargs = {"limit": limit}
            if max_id is not None:
                kwargs["max_id"] = max_id
            messages = await client.get_messages(entity, **kwargs)
        source_name = getattr(entity, "title", None) or getattr(entity, "first_name", None) or str(chat_id)
        result = []
        for message in reversed(list(messages)):
            if download_attachments:
                attachment = await _download_attachment(
                    client,
                    source_name,
                    message,
                    progress_callback=attachment_progress_callback,
                )
            else:
                attachment = _inspect_attachment(message)
            result.append(
                {
                    "id": message.id,
                    "text": message.message or "",
                    "sender": _message_sender_label(message),
                    "from_me": bool(message.out),
                    "date": message.date.astimezone(timezone.utc).isoformat() if message.date else None,
                    "time": message.date.strftime("%H:%M") if message.date else "",
                    "item_type": attachment["item_type"],
                    "attachment_path": attachment["attachment_path"],
                    "attachment_name": attachment["attachment_name"],
                    "mime_type": attachment["mime_type"],
                    "file_size": attachment["file_size"],
                }
            )
        return result
    finally:
        await _disconnect_client(client)


def fetch_chats(limit: int = 50) -> list[dict]:
    acquire_telegram_session_lock()
    try:
        return asyncio.run(_fetch_chats_async(limit=limit))
    finally:
        _clear_session_lock()


def fetch_messages(
    chat_id: str,
    limit: int = 200,
    max_id: int | None = None,
    download_attachments: bool = True,
    message_ids: list[int] | None = None,
    attachment_progress_callback: Callable[[dict], None] | None = None,
) -> list[dict]:
    acquire_telegram_session_lock()
    try:
        return asyncio.run(
            _fetch_messages_async(
                chat_id=chat_id,
                limit=limit,
                max_id=max_id,
                download_attachments=download_attachments,
                message_ids=message_ids,
                attachment_progress_callback=attachment_progress_callback,
            )
        )
    finally:
        _clear_session_lock()
