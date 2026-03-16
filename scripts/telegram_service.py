from __future__ import annotations

import asyncio
import atexit
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
else:
    from .telegram_db import DATA_DIR


RUNTIME_DIR = Path(DATA_DIR) / "runtime"
TELEGRAM_BLOBS_DIR = Path(DATA_DIR) / "blobs" / "telegram"
STATUS_FILE = RUNTIME_DIR / "telegram_status.json"
CHATS_CACHE_FILE = RUNTIME_DIR / "telegram_chats.json"
DEFAULT_SESSION_PATH = RUNTIME_DIR / "telegram_userbot.session"
SESSION_LOCK_FILE = RUNTIME_DIR / "telegram_userbot.lock"
TELEGRAM_HEARTBEAT_TTL_SECONDS = 1800
TELEGRAM_SESSION_LOCK_TTL_SECONDS = 7200
TELEGRAM_SESSION_LOCK_WAIT_SECONDS = 5
LOCAL_TIMEZONE = ZoneInfo("Asia/Seoul")

_SESSION_LOCK_HELD = False


class TelegramSessionBusyError(RuntimeError):
    pass

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


def _runtime_dir() -> Path:
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    return RUNTIME_DIR


def _read_session_lock() -> dict | None:
    try:
        raw = SESSION_LOCK_FILE.read_text(encoding="utf-8")
        data = json.loads(raw)
        if isinstance(data, dict):
            return data
    except FileNotFoundError:
        return None
    except Exception:
        return None
    return None


def _pid_alive(pid: int | None) -> bool:
    if not pid or pid <= 0:
        return False
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def get_telegram_session_lock_status() -> dict:
    payload = _read_session_lock()
    if not payload:
        return {"locked": False, "lock_file": str(SESSION_LOCK_FILE)}

    acquired_at = payload.get("acquired_at")
    age_seconds = None
    if acquired_at:
        try:
            age_seconds = int((datetime.now(timezone.utc) - datetime.fromisoformat(acquired_at)).total_seconds())
        except Exception:
            age_seconds = None

    return {
        "locked": True,
        "lock_file": str(SESSION_LOCK_FILE),
        "pid": payload.get("pid"),
        "command": payload.get("command"),
        "acquired_at": acquired_at,
        "age_seconds": age_seconds,
        "pid_alive": _pid_alive(payload.get("pid")),
    }


def _clear_session_lock() -> None:
    global _SESSION_LOCK_HELD
    if not _SESSION_LOCK_HELD:
        return
    try:
        payload = _read_session_lock()
        if payload and payload.get("pid") not in (None, os.getpid()):
            return
        SESSION_LOCK_FILE.unlink(missing_ok=True)
    finally:
        _SESSION_LOCK_HELD = False


atexit.register(_clear_session_lock)


def acquire_telegram_session_lock(wait_seconds: int = TELEGRAM_SESSION_LOCK_WAIT_SECONDS) -> None:
    global _SESSION_LOCK_HELD
    _runtime_dir()
    deadline = time.monotonic() + max(0, wait_seconds)
    payload = {
        "pid": os.getpid(),
        "command": " ".join(os.sys.argv),
        "acquired_at": datetime.now(timezone.utc).isoformat(),
    }

    while True:
        try:
            fd = os.open(str(SESSION_LOCK_FILE), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(payload, handle, ensure_ascii=False, indent=2)
            _SESSION_LOCK_HELD = True
            return
        except FileExistsError:
            current = _read_session_lock() or {}
            acquired_at = current.get("acquired_at")
            is_stale = False
            if acquired_at:
                try:
                    age = (datetime.now(timezone.utc) - datetime.fromisoformat(acquired_at)).total_seconds()
                    is_stale = age > TELEGRAM_SESSION_LOCK_TTL_SECONDS
                except Exception:
                    is_stale = True
            current_pid = current.get("pid")
            if is_stale or not _pid_alive(current_pid):
                try:
                    SESSION_LOCK_FILE.unlink(missing_ok=True)
                except OSError:
                    pass
                continue

            if time.monotonic() >= deadline:
                detail = f"pid={current_pid}"
                if current.get("command"):
                    detail += f", command={current['command']}"
                raise TelegramSessionBusyError(
                    f"Telegram 세션이 다른 작업에서 사용 중입니다 ({detail})."
                )
            time.sleep(1)


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
            "첫 연결이 성공하면 이 경로에 세션 파일이 생성됩니다."
        )
    else:
        setup_message = "Telegram API 설정과 세션 파일이 준비되어 있습니다."

    return {
        "configured": configured,
        "missing_config": missing,
        "session_path": str(session_path),
        "session_dir": str(session_path.parent),
        "session_exists": session_exists,
        "first_session_required": configured and not session_exists,
        "connected": False,
        "auth_required": False,
        "user": None,
        "setup_message": setup_message,
    }


def _write_status(payload: dict) -> None:
    _runtime_dir()
    STATUS_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


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
    sender_id = getattr(message, "sender_id", None)
    return str(sender_id) if sender_id is not None else "Unknown"


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
