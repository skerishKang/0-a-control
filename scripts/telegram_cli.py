import sqlite3
import requests
import json
import argparse
from pathlib import Path
from datetime import datetime, timezone
from telegram_db import init_db

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "control_tower.db"
BASE_URL = "http://localhost:4300"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def list_sources():
    conn = get_db()
    sources = conn.execute("SELECT * FROM telegram_sources").fetchall()
    conn.close()
    
    print(f"{'ID':<15} | {'Name':<20} | {'Class':<15} | {'Core':<5}")
    print("-" * 60)
    for s in sources:
        print(f"{s['source_id']:<15} | {s['source_name']:<20} | {s['chat_class']:<15} | {bool(s['is_core']):<5}")

def sync_core():
    conn = get_db()
    core_sources = conn.execute("SELECT * FROM telegram_sources WHERE is_core = 1").fetchall()
    conn.close()
    
    for source in core_sources:
        print(f"Syncing core source: {source['source_name']}")
        import_chat(source['source_id'])

def import_chat(source_id):
    conn = get_db()
    source = conn.execute("SELECT * FROM telegram_sources WHERE source_id = ?", (source_id,)).fetchone()
    if not source:
        print(f"Source {source_id} not found in DB.")
        conn.close()
        return
    
    try:
        resp = requests.get(f"{BASE_URL}/api/telegram/messages?chat_id={source_id}", timeout=10)
        resp.raise_for_status()
        payload = resp.json()
        messages = payload.get("messages", [])
        if not isinstance(messages, list):
            raise ValueError("Invalid telegram messages response: 'messages' must be a list")
        
        count = 0
        last_id = source['last_message_id']
        new_last_id = last_id
        
        now_iso = datetime.now(timezone.utc).isoformat()
        for msg in messages:
            if msg['id'] > last_id:
                author = msg.get("sender", "Unknown")
                item_timestamp = msg.get("date") or now_iso
                
                conn.execute(
                    """
                    INSERT OR IGNORE INTO external_inbox
                    (
                        source_type, source_id, source_name, external_message_id, 
                        author, item_type, title, raw_content, 
                        item_timestamp, imported_at, status, metadata_json
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        "telegram",
                        source_id,
                        source["source_name"],
                        str(msg["id"]),
                        author,
                        "text",
                        source["source_name"],
                        msg.get("text", ""),
                        item_timestamp,
                        now_iso,
                        "new",
                        json.dumps({
                            "date": msg.get("date"),
                            "sender": msg.get("sender"),
                            "from_me": msg.get("from_me"),
                            "chat_id": source_id
                        }, ensure_ascii=False),
                    ),
                )
                if msg['id'] > new_last_id:
                    new_last_id = msg['id']
                count += 1
        
        conn.execute("UPDATE telegram_sources SET last_message_id = ?, last_synced_at = ? WHERE source_id = ?", 
                     (new_last_id, datetime.now(timezone.utc).isoformat(), source_id))
        conn.commit()
        print(f"Imported {count} new messages for {source['source_name']}.")
        
    except requests.HTTPError as e:
        print(f"Failed to sync {source['source_name']}: HTTP {e.response.status_code}")
    except requests.RequestException as e:
        print(f"Failed to sync {source['source_name']}: request error: {e}")
    except ValueError as e:
        print(f"Failed to sync {source['source_name']}: {e}")
    except Exception as e:
        print(f"Failed to sync {source['source_name']}: unexpected error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")
    
    subparsers.add_parser("list-sources")
    subparsers.add_parser("sync-core")
    
    import_parser = subparsers.add_parser("import-chat")
    import_parser.add_argument("source_id")
    
    args = parser.parse_args()
    
    if args.command == "list-sources":
        list_sources()
    elif args.command == "sync-core":
        sync_core()
    elif args.command == "import-chat":
        import_chat(args.source_id)
