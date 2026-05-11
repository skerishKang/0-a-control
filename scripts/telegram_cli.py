# Enable both `python scripts/foo.py` and `python -m scripts.foo`
import sys
from pathlib import Path
_root = str(Path(__file__).resolve().parents[1])
if _root not in sys.path:
    sys.path.insert(0, _root)

import sqlite3
import json
import argparse
from datetime import datetime, timezone
from scripts.telegram_db import get_db_connection, init_db
from scripts.telegram_service import (
    TelegramSessionBusyError,
    fetch_messages,
    get_telegram_session_lock_status,
    get_telegram_status,
)
from scripts.telegram_helpers import (
    _normalize_message_timestamp,
    _format_bytes,
    _metadata_file_size,
)
from scripts.telegram_progress import AttachmentProgressReporter


def get_db():
    return get_db_connection()


def get_core_sources_sync_status() -> list[dict]:
    conn = get_db()
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

def run_sync_core() -> dict:
    status = {"ok": True, "details": [], "synced_count": 0, "success_count": 0, "failed_count": 0}
    sources = get_core_sources_sync_status()
    
    if not sources:
        status["ok"] = False
        status["error"] = "No core telegram sources found."
        return status

    for source in sources:
        res = import_chat(source['source_id'])
        status["details"].append({
            "source_id": source["source_id"],
            "source_name": source["source_name"],
            "count": res.get("count", 0) if isinstance(res, dict) else 0,
            "error": res.get("error") if isinstance(res, dict) else None
        })
        if isinstance(res, dict):
            status["synced_count"] += res.get("count", 0)
            if res.get("error"):
                status["failed_count"] += 1
            else:
                status["success_count"] += 1

    if status["failed_count"] and status["success_count"] == 0:
        status["ok"] = False
        status["error"] = "핵심4개 동기화에 모두 실패했습니다. Telegram 설정 또는 세션 상태를 확인하세요."
    
    return status

def list_sources():
    conn = get_db()
    sources = conn.execute("SELECT * FROM telegram_sources").fetchall()
    conn.close()
    
    print(f"{'ID':<15} | {'Name':<20} | {'Class':<15} | {'Core':<5}")
    print("-" * 60)
    for s in sources:
        print(f"{s['source_id']:<15} | {s['source_name']:<20} | {s['chat_class']:<15} | {bool(s['is_core']):<5}")

def sync_core():
    res = run_sync_core()
    if not res["ok"]:
        print(res.get("error", "Sync failed"))
        return
    
    print(f"Synced {len(res['details'])} sources. Total new messages: {res['synced_count']}")
    for d in res["details"]:
        if d["error"]:
            print(f"  - {d['source_name']}: FAILED ({d['error']})")
        else:
            print(f"  - {d['source_name']}: {d['count']} new messages")

def show_sync_status():
    rows = get_core_sources_sync_status()
    if not rows:
        print("No core telegram sources configured.")
        return

    print(f"{'Name':<24} | {'Class':<22} | {'Last Sync':<25} | {'Last ID':<10}")
    print("-" * 92)
    for row in rows:
        print(
            f"{row['source_name'][:24]:<24} | "
            f"{row['chat_class'][:22]:<22} | "
            f"{str(row['last_synced_at'] or '-')[:25]:<25} | "
            f"{str(row['last_message_id']):<10}"
        )

def import_chat(
    source_id,
    limit: int = 200,
    max_id: int | None = None,
    download_attachments: bool = True,
    attachment_progress_callback=None,
) -> dict:
    conn = get_db()
    source = conn.execute("SELECT * FROM telegram_sources WHERE source_id = ?", (source_id,)).fetchone()
    if not source:
        conn.close()
        return {"ok": False, "error": f"Source {source_id} not found"}
    
    result = {"ok": True, "count": 0}
    try:
        fetch_kwargs = {
            "limit": limit,
            "max_id": max_id,
            "download_attachments": download_attachments,
        }
        if attachment_progress_callback is not None:
            fetch_kwargs["attachment_progress_callback"] = attachment_progress_callback

        messages = fetch_messages(
            source_id,
            **fetch_kwargs,
        )
        if not isinstance(messages, list):
            raise ValueError("Invalid telegram messages response: 'messages' must be a list")
        
        count = 0
        total_changes_before = conn.total_changes
        last_id = source['last_message_id']
        new_last_id = last_id
        
        now_iso = datetime.now(timezone.utc).isoformat()
        for msg in messages:
            author = msg.get("sender", "Unknown")
            item_timestamp = _normalize_message_timestamp(msg.get("date"), now_iso)
            is_new = msg["id"] > last_id

            conn.execute(
                """
                INSERT INTO external_inbox
                (
                    source_type, source_id, source_name, external_message_id,
                    author, item_type, title, raw_content, attachment_path, attachment_ref,
                    item_timestamp, imported_at, status, metadata_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(source_id, external_message_id) DO UPDATE SET
                    source_name = excluded.source_name,
                    author = excluded.author,
                    item_type = excluded.item_type,
                    title = excluded.title,
                    raw_content = excluded.raw_content,
                    attachment_path = COALESCE(excluded.attachment_path, external_inbox.attachment_path),
                    attachment_ref = COALESCE(excluded.attachment_ref, external_inbox.attachment_ref),
                    item_timestamp = excluded.item_timestamp,
                    metadata_json = excluded.metadata_json
                """,
                (
                    "telegram",
                    source_id,
                    source["source_name"],
                    str(msg["id"]),
                    author,
                    msg.get("item_type", "text"),
                    source["source_name"],
                    msg.get("text", ""),
                    msg.get("attachment_path"),
                    msg.get("attachment_name") or str(msg["id"]),
                    item_timestamp,
                    now_iso,
                    "new",
                    json.dumps({
                        "date": msg.get("date"),
                        "sender": msg.get("sender"),
                        "from_me": msg.get("from_me"),
                        "chat_id": source_id,
                        "attachment_name": msg.get("attachment_name"),
                        "mime_type": msg.get("mime_type"),
                        "file_size": msg.get("file_size"),
                    }, ensure_ascii=False),
                ),
            )
            if msg["id"] > new_last_id:
                new_last_id = msg["id"]
            if is_new:
                count += 1
        
        conn.execute("UPDATE telegram_sources SET last_message_id = ?, last_synced_at = ? WHERE source_id = ?",
                     (new_last_id, datetime.now(timezone.utc).isoformat(), source_id))
        conn.commit()
        result["count"] = count
        result["processed_count"] = len(messages)
        result["changed_rows"] = conn.total_changes - total_changes_before
        result["oldest_message_id"] = min((msg["id"] for msg in messages), default=None)
        
    except ValueError as e:
        result = {"ok": False, "error": str(e), "count": 0}
    except Exception as e:
        result = {"ok": False, "error": f"Unexpected error: {e}", "count": 0}
    finally:
        conn.close()
    return result


def backfill_chat(
    source_id: str,
    batch_limit: int = 200,
    max_batches: int | None = None,
    download_attachments: bool = True,
) -> dict:
    conn = get_db()
    source = conn.execute(
        "SELECT source_id, source_name, MIN(CAST(external_message_id AS INTEGER)) AS oldest_id "
        "FROM external_inbox WHERE source_type = 'telegram' AND source_id = ? GROUP BY source_id, source_name",
        (source_id,),
    ).fetchone()
    conn.close()

    if not source:
        return {"ok": False, "error": f"No existing telegram history found for source {source_id}"}

    before_id = source["oldest_id"]
    batches = 0
    total_processed = 0
    total_changed = 0
    last_oldest = before_id

    while before_id and before_id > 1:
        if max_batches is not None and batches >= max_batches:
            break
        res = import_chat(
            source_id,
            limit=batch_limit,
            max_id=before_id,
            download_attachments=download_attachments,
        )
        if not res.get("ok"):
            return {
                "ok": False,
                "error": res.get("error", "Backfill failed"),
                "batches": batches,
                "processed_count": total_processed,
                "changed_rows": total_changed,
                "oldest_message_id": last_oldest,
            }

        processed = res.get("processed_count", 0)
        oldest = res.get("oldest_message_id")
        total_processed += processed
        total_changed += res.get("changed_rows", 0)
        batches += 1

        if not processed or oldest is None or oldest >= before_id:
            break

        before_id = oldest
        last_oldest = oldest

    return {
        "ok": True,
        "source_id": source_id,
        "source_name": source["source_name"],
        "batches": batches,
        "processed_count": total_processed,
        "changed_rows": total_changed,
        "oldest_message_id": last_oldest,
    }


def fill_missing_attachments(
    source_id: str,
    limit: int = 50,
    show_progress: bool = False,
    max_file_size_mb: float | None = None,
) -> dict:
    conn = get_db()
    source = conn.execute("SELECT * FROM telegram_sources WHERE source_id = ?", (source_id,)).fetchone()
    if not source:
        conn.close()
        return {"ok": False, "error": f"Source {source_id} not found"}

    query_limit = limit if max_file_size_mb is None else 1000000
    rows = conn.execute(
        """
        SELECT external_message_id, metadata_json
        FROM external_inbox
        WHERE source_type = 'telegram'
          AND source_id = ?
          AND COALESCE(item_type, 'text') != 'text'
          AND COALESCE(attachment_path, '') = ''
        ORDER BY COALESCE(NULLIF(item_timestamp, ''), imported_at) ASC,
                 CAST(external_message_id AS INTEGER) ASC
        LIMIT ?
        """,
        (source_id, query_limit),
    ).fetchall()
    conn.close()

    max_file_size_bytes = None
    if max_file_size_mb is not None:
        max_file_size_bytes = int(max_file_size_mb * 1024 * 1024)

    message_ids = []
    skipped_too_large = 0
    for row in rows:
        if not row["external_message_id"]:
            continue
        if max_file_size_bytes is not None:
            file_size = _metadata_file_size(row)
            if file_size is not None and file_size > max_file_size_bytes:
                skipped_too_large += 1
                continue
        message_ids.append(int(row["external_message_id"]))
        if len(message_ids) >= limit:
            break

    if not message_ids:
        conn = get_db()
        remaining_missing = conn.execute(
            """
            SELECT COUNT(*) AS count
            FROM external_inbox
            WHERE source_type = 'telegram'
              AND source_id = ?
              AND COALESCE(item_type, 'text') != 'text'
              AND COALESCE(attachment_path, '') = ''
            """,
            (source_id,),
        ).fetchone()["count"]
        conn.close()
        return {
            "ok": True,
            "source_id": source_id,
            "source_name": source["source_name"],
            "processed_count": 0,
            "changed_rows": 0,
            "remaining_missing": remaining_missing,
            "skipped_too_large": skipped_too_large,
        }

    result = import_message_ids(
        source_id,
        message_ids,
        download_attachments=True,
        show_progress=show_progress,
    )
    if not result.get("ok"):
        return result

    conn = get_db()
    remaining_missing = conn.execute(
        """
        SELECT COUNT(*) AS count
        FROM external_inbox
        WHERE source_type = 'telegram'
          AND source_id = ?
          AND COALESCE(item_type, 'text') != 'text'
          AND COALESCE(attachment_path, '') = ''
        """,
        (source_id,),
    ).fetchone()["count"]
    conn.close()
    result["remaining_missing"] = remaining_missing
    result["skipped_too_large"] = skipped_too_large
    return result


def import_message_ids(
    source_id: str,
    message_ids: list[int],
    download_attachments: bool = True,
    show_progress: bool = False,
) -> dict:
    if not message_ids:
        return {"ok": True, "count": 0, "processed_count": 0, "changed_rows": 0}

    conn = get_db()
    source = conn.execute("SELECT * FROM telegram_sources WHERE source_id = ?", (source_id,)).fetchone()
    if not source:
        conn.close()
        return {"ok": False, "error": f"Source {source_id} not found"}

    result = {"ok": True, "count": 0}
    try:
        progress_reporter = AttachmentProgressReporter(len(message_ids)) if download_attachments and show_progress else None
        fetch_kwargs = {
            "limit": len(message_ids),
            "download_attachments": download_attachments,
            "message_ids": message_ids,
        }
        if progress_reporter is not None:
            fetch_kwargs["attachment_progress_callback"] = progress_reporter

        messages = fetch_messages(
            source_id,
            **fetch_kwargs,
        )
        if not isinstance(messages, list):
            raise ValueError("Invalid telegram messages response: 'messages' must be a list")

        total_changes_before = conn.total_changes
        now_iso = datetime.now(timezone.utc).isoformat()
        for msg in messages:
            author = msg.get("sender", "Unknown")
            item_timestamp = _normalize_message_timestamp(msg.get("date"), now_iso)
            conn.execute(
                """
                INSERT INTO external_inbox
                (
                    source_type, source_id, source_name, external_message_id,
                    author, item_type, title, raw_content, attachment_path, attachment_ref,
                    item_timestamp, imported_at, status, metadata_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(source_id, external_message_id) DO UPDATE SET
                    source_name = excluded.source_name,
                    author = excluded.author,
                    item_type = excluded.item_type,
                    title = excluded.title,
                    raw_content = excluded.raw_content,
                    attachment_path = COALESCE(excluded.attachment_path, external_inbox.attachment_path),
                    attachment_ref = COALESCE(excluded.attachment_ref, external_inbox.attachment_ref),
                    item_timestamp = excluded.item_timestamp,
                    metadata_json = excluded.metadata_json
                """,
                (
                    "telegram",
                    source_id,
                    source["source_name"],
                    str(msg["id"]),
                    author,
                    msg.get("item_type", "text"),
                    source["source_name"],
                    msg.get("text", ""),
                    msg.get("attachment_path"),
                    msg.get("attachment_name") or str(msg["id"]),
                    item_timestamp,
                    now_iso,
                    "new",
                    json.dumps({
                        "date": msg.get("date"),
                        "sender": msg.get("sender"),
                        "from_me": msg.get("from_me"),
                        "chat_id": source_id,
                        "attachment_name": msg.get("attachment_name"),
                        "mime_type": msg.get("mime_type"),
                        "file_size": msg.get("file_size"),
                    }, ensure_ascii=False),
                ),
            )

        conn.commit()
        result["processed_count"] = len(messages)
        result["changed_rows"] = conn.total_changes - total_changes_before
        result["message_ids"] = [msg["id"] for msg in messages]
    except TelegramSessionBusyError as e:
        result = {
            "ok": False,
            "error": str(e),
            "error_code": "telegram_session_busy",
            "count": 0,
            "session_lock": get_telegram_session_lock_status(),
        }
    except ValueError as e:
        result = {"ok": False, "error": str(e), "count": 0}
    except Exception as e:
        result = {"ok": False, "error": f"Unexpected error: {e}", "count": 0}
    finally:
        conn.close()
    return result


def show_attachment_status(source_id: str, max_file_size_mb: float | None = None) -> None:
    conn = get_db()
    source = conn.execute(
        "SELECT source_id, source_name FROM telegram_sources WHERE source_id = ?",
        (source_id,),
    ).fetchone()
    if not source:
        conn.close()
        print(json.dumps({"ok": False, "error": f"Source {source_id} not found"}, ensure_ascii=False, indent=2))
        return

    rows = conn.execute(
        """
        SELECT attachment_path, imported_at, metadata_json
        FROM external_inbox
        WHERE source_type = 'telegram'
          AND source_id = ?
          AND COALESCE(item_type, 'text') != 'text'
        """,
        (source_id,),
    ).fetchall()
    conn.close()

    max_file_size_bytes = None
    if max_file_size_mb is not None:
        max_file_size_bytes = int(max_file_size_mb * 1024 * 1024)

    attachment_count = 0
    missing_attachment_count = 0
    filtered_missing_attachment_count = 0
    last_attachment_imported_at = None

    for row in rows:
        attachment_path = row["attachment_path"] or ""
        if attachment_path:
            attachment_count += 1
            imported_at = row["imported_at"]
            if imported_at and (last_attachment_imported_at is None or imported_at > last_attachment_imported_at):
                last_attachment_imported_at = imported_at
            continue

        missing_attachment_count += 1
        file_size = _metadata_file_size(row)
        if max_file_size_bytes is None or file_size is None or file_size <= max_file_size_bytes:
            filtered_missing_attachment_count += 1

    print(
        json.dumps(
            {
                "ok": True,
                "source_id": source["source_id"],
                "source_name": source["source_name"],
                "attachment_count": attachment_count,
                "missing_attachment_count": missing_attachment_count,
                "filtered_missing_attachment_count": filtered_missing_attachment_count,
                "last_attachment_imported_at": last_attachment_imported_at,
                "max_file_size_mb": max_file_size_mb,
                "session_lock": get_telegram_session_lock_status(),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    from scripts.telegram_cli_main import run_cli
    run_cli()
