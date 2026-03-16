# Enable both `python scripts/foo.py` and `python -m scripts.foo`
import sys
from pathlib import Path
_root = str(Path(__file__).resolve().parents[1])
if _root not in sys.path:
    sys.path.insert(0, _root)

"""
Actual implementation of the CLI for interacting with the external_inbox.
"""
import argparse
import json
import re
from datetime import datetime, timedelta, timezone

from scripts.db_base import connect, rows_to_dicts, ROOT_DIR
from scripts import db_ops
from scripts.inbox_parse import parse_time_range, resolve_source_aliases

CANDIDATES_CACHE_FILE = ROOT_DIR / "data" / "runtime" / "last_inbox_candidates.json"

def summarize_inbox(args):
    try:
        start_time, end_time = parse_time_range(args.time_range)
    except ValueError as e:
        print(f"Time range error: {e}")
        return

    sources = resolve_source_aliases(args.sources) if args.sources else None
    status = args.status
    limit = args.limit
    
    with connect() as conn:
        query = (
            "SELECT * FROM external_inbox "
            "WHERE COALESCE(NULLIF(item_timestamp, ''), imported_at) >= ? "
            "AND COALESCE(NULLIF(item_timestamp, ''), imported_at) <= ?"
        )
        params = [start_time.isoformat(), end_time.isoformat()]
        
        if sources:
            placeholders = ",".join("?" * len(sources))
            query += f" AND source_id IN ({placeholders})"
            params.extend(sources)
        
        if status and status.lower() != 'all':
            query += " AND status = ?"
            params.append(status.lower())
            
        query += " ORDER BY COALESCE(NULLIF(item_timestamp, ''), imported_at) ASC, imported_at ASC, id ASC"
        
        if limit:
            query += " LIMIT ?"
            params.append(limit)
            
        items = rows_to_dicts(conn.execute(query, params).fetchall())

    if not items:
        print(f"No inbox items found with criteria: range={args.time_range}, sources={sources}, status={status}.")
        return

    # Deterministic summary: one candidate per item for now
    candidates = []
    for i, item in enumerate(items, 1):
        candidates.append({
            "id": i,
            "inbox_id": item["id"],
            "title": item["raw_content"][:60].strip() + "..." if len(item["raw_content"]) > 60 else item["raw_content"],
            "description": f"Source: {item.get('source_name') or item['source_id']} | Type: {item.get('item_type', 'text')}",
            "related_source_id": item["id"],
            "bucket": "short_term"  # Default suggestion
        })

    # Save to cache
    CANDIDATES_CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CANDIDATES_CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(candidates, f, ensure_ascii=False, indent=2)

    print(f"--- Inbox Summary ({len(items)} items) ---")
    print(f"Range: {start_time.isoformat()} to {end_time.isoformat()}")
    if status: print(f"Status Filter: {status}")
    print("-" * 40)
    for cand in candidates:
        print(f"[Candidate ID: {cand['id']}] (Inbox ID: {cand['inbox_id']}) {cand['title']}")
        print(f"    {cand['description']}")
    print("-" * 40)
    print(f"Run 'python scripts/inbox_cli.py approve \"<id> <bucket>, ...\"' to create plan items.")
    print("Example: 1 today, 2 short_term")

def generate_digest(args):
    """
    Generate a derived digest JSON product from inbox items.
    """
    try:
        start_time, end_time = parse_time_range(args.time_range)
    except ValueError as e:
        print(f"Time range error: {e}")
        return

    sources = resolve_source_aliases(args.sources) if args.sources else None
    
    with connect() as conn:
        query = (
            "SELECT * FROM external_inbox "
            "WHERE COALESCE(NULLIF(item_timestamp, ''), imported_at) >= ? "
            "AND COALESCE(NULLIF(item_timestamp, ''), imported_at) <= ?"
        )
        params = [start_time.isoformat(), end_time.isoformat()]
        
        if sources:
            placeholders = ",".join("?" * len(sources))
            query += f" AND source_id IN ({placeholders})"
            params.extend(sources)
            
        query += " ORDER BY COALESCE(NULLIF(item_timestamp, ''), imported_at) ASC, imported_at ASC, id ASC"
        items = rows_to_dicts(conn.execute(query, params).fetchall())

    if not items:
        print("No items found for digest.")
        return

    digest_id = datetime.now().strftime("%H%M%S")
    date_str = datetime.now().strftime("%Y%m%d")
    digest_dir = ROOT_DIR / "data" / "runtime" / "digests" / date_str
    digest_dir.mkdir(parents=True, exist_ok=True)
    
    digest_file = digest_dir / f"digest_{digest_id}.json"
    
    # Simple deterministic summary logic
    digest_data = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "query_context": {
            "time_range": args.time_range,
            "sources": sources,
            "start": start_time.isoformat(),
            "end": end_time.isoformat()
        },
        "item_count": len(items),
        "sources_involved": list(set(item["source_id"] for item in items)),
        "summary": f"Collected {len(items)} items from {len(set(item['source_id'] for item in items))} sources.",
        "candidates": [
            {"title": item["raw_content"][:50], "source": item.get("source_name") or item["source_id"], "ref_id": item["id"]} 
            for item in items if len(item["raw_content"]) > 10
        ],
        "reply_needed": [],
        "reference_only": [
             {"title": item["title"] or "No Title", "content_preview": item["raw_content"][:100]} 
             for item in items if "공시" in (item["title"] or "") or "뉴스" in (item["title"] or "")
        ]
    }
    
    with open(digest_file, "w", encoding="utf-8") as f:
        json.dump(digest_data, f, ensure_ascii=False, indent=2)
        
    print(f"Digest generated: {digest_file}")
    print(f"Summary: {digest_data['summary']}")

def approve_candidates(args):
    if not CANDIDATES_CACHE_FILE.exists():
        print("No summary found. Please run 'summarize' first.")
        return

    with open(CANDIDATES_CACHE_FILE, "r", encoding="utf-8") as f:
        all_candidates = {str(c["id"]): c for c in json.load(f)}

    # Parse approval string: e.g. "1 today, 2 short_term"
    commands = [c.strip() for c in args.approval_string.split(",")]
    to_approve = []
    
    valid_buckets = {"today", "dated", "short_term", "long_term", "recurring"}
    
    for cmd in commands:
        parts = cmd.split()
        if len(parts) != 2:
            print(f"Skipping invalid command part: '{cmd}' (Expected: '<id> <bucket>')")
            continue
        
        cid, bucket = parts[0], parts[1].lower()
        if cid not in all_candidates:
            print(f"Skipping unknown candidate ID: {cid}")
            continue
        
        if bucket not in valid_buckets:
            print(f"Skipping invalid bucket: {bucket}. (Valid: {', '.join(valid_buckets)})")
            continue
        
        cand = all_candidates[cid]
        cand["bucket"] = bucket
        to_approve.append(cand)

    if not to_approve:
        print("No valid candidates to approve.")
        return

    created = db_ops.approve_plan_candidates(to_approve)
    print(f"Successfully created {len(created)} plan items and updated external_inbox status.")
    for item in created:
        print(f"- [{item['bucket']}] {item['title']} (ID: {item['id']})")

def update_status(args):
    """
    Update the status of multiple inbox items.
    """
    if not args.ids:
        print("No IDs provided.")
        return

    new_status = args.status_val
    reason = getattr(args, 'reason', None)
    updated_at = datetime.now(timezone.utc).isoformat()

    with connect() as conn:
        for item_id in args.ids:
            # Fetch existing metadata
            row = conn.execute("SELECT metadata_json FROM external_inbox WHERE id = ?", (item_id,)).fetchone()
            if not row:
                print(f"ID {item_id} not found. Skipping.")
                continue
                
            metadata = json.loads(row["metadata_json"] or "{}")
            if reason:
                if "status_history" not in metadata:
                    metadata["status_history"] = []
                metadata["status_history"].append({
                    "status": new_status,
                    "reason": reason,
                    "updated_at": updated_at
                })

            conn.execute(
                """
                UPDATE external_inbox 
                SET status = ?, processed_at = ?, metadata_json = ? 
                WHERE id = ?
                """,
                (new_status, updated_at, json.dumps(metadata, ensure_ascii=False), item_id)
            )
            print(f"Updated ID {item_id} -> {new_status}")

def main():
    parser = argparse.ArgumentParser(description="외부 입력 Inbox CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    summarize_parser = subparsers.add_parser("summarize", help="요약 및 계획 후보 추출")
    summarize_parser.add_argument("--time-range", default="6h", help="조회 시간 (예: 6h, 1d, 09:00-11:00)")
    summarize_parser.add_argument("--sources", nargs='+', help="소스 별칭 (예: 핵심4개, self)")
    summarize_parser.add_argument("--status", default="new", help="상태 필터 (new, reviewing, accepted, rejected, archived, all)")
    summarize_parser.add_argument("--limit", type=int, help="조회할 최대 항목 수")
    summarize_parser.set_defaults(func=summarize_inbox)

    fetch_parser = subparsers.add_parser("fetch", help="원본 데이터 조회")
    fetch_parser.add_argument("--time-range", default="6h", help="조회 시간")
    fetch_parser.add_argument("--sources", nargs='+', help="소스 별칭 또는 source_id 목록")
    fetch_parser.add_argument("--status", default="new", help="상태 필터 (new, reviewing, accepted, rejected, archived, all)")
    fetch_parser.add_argument("--limit", type=int, help="조회할 최대 항목 수")
    fetch_parser.add_argument("--json", action="store_true", help="JSON 출력")
    fetch_parser.set_defaults(func=fetch_inbox)

    digest_parser = subparsers.add_parser("digest", help="파생 결과물인 digest JSON 생성")
    digest_parser.add_argument("--time-range", default="24h", help="digest 생성 범위")
    digest_parser.add_argument("--sources", nargs='+', help="소스 별칭 또는 source_id 목록")
    digest_parser.set_defaults(func=generate_digest)

    approve_parser = subparsers.add_parser("approve", help="후보를 승인해 계획으로 반영")
    approve_parser.add_argument("approval_string", help="예: '1 today, 2 short_term'")
    approve_parser.set_defaults(func=approve_candidates)

    review_parser = subparsers.add_parser("mark-reviewing", help="항목을 reviewing 상태로 변경")
    review_parser.add_argument("ids", nargs='+', type=int)
    review_parser.set_defaults(func=update_status, status_val="reviewing")

    reject_parser = subparsers.add_parser("reject", help="항목을 rejected 상태로 변경")
    reject_parser.add_argument("ids", nargs='+', type=int)
    reject_parser.add_argument("--reason", help="거절 사유")
    reject_parser.set_defaults(func=update_status, status_val="rejected")

    archive_parser = subparsers.add_parser("archive", help="항목을 archived 상태로 변경")
    archive_parser.add_argument("ids", nargs='+', type=int)
    archive_parser.add_argument("--reason", help="보관 사유")
    archive_parser.set_defaults(func=update_status, status_val="archived")

    reopen_parser = subparsers.add_parser("reopen", help="항목을 다시 new 상태로 되돌림")
    reopen_parser.add_argument("ids", nargs='+', type=int)
    reopen_parser.set_defaults(func=update_status, status_val="new")

    args = parser.parse_args()
    args.func(args)

def fetch_inbox(args):
    """
    Fetch raw inbox items for Codex consumption.
    """
    try:
        start_time, end_time = parse_time_range(args.time_range)
    except ValueError as e:
        print(f"Time range error: {e}")
        return

    sources = resolve_source_aliases(args.sources) if args.sources else None
    
    with connect() as conn:
        query = (
            "SELECT * FROM external_inbox "
            "WHERE COALESCE(NULLIF(item_timestamp, ''), imported_at) >= ? "
            "AND COALESCE(NULLIF(item_timestamp, ''), imported_at) <= ?"
        )
        params = [start_time.isoformat(), end_time.isoformat()]
        
        if sources:
            placeholders = ",".join("?" * len(sources))
            query += f" AND source_id IN ({placeholders})"
            params.extend(sources)
        
        if args.status and args.status.lower() != 'all':
            query += " AND status = ?"
            params.append(args.status.lower())
            
        query += " ORDER BY COALESCE(NULLIF(item_timestamp, ''), imported_at) ASC, imported_at ASC, id ASC"
        
        if args.limit:
            query += " LIMIT ?"
            params.append(args.limit)
            
        items = rows_to_dicts(conn.execute(query, params).fetchall())

    # Map output strictly to the JSON contract
    contract_items = []
    for item in items:
        contract_items.append({
            "id": item.get("id"),
            "source_type": item.get("source_type"),
            "source_id": item.get("source_id"),
            "source_name": item.get("source_name"),
            "author": item.get("author"),
            "item_type": item.get("item_type"),
            "title": item.get("title"),
            "raw_content": item.get("raw_content"),
            "attachment_path": item.get("attachment_path"),
            "item_timestamp": item.get("item_timestamp"),
            "status": item.get("status"),
            "metadata_json": item.get("metadata_json")
        })

    if args.json:
        print(json.dumps(contract_items, indent=2, ensure_ascii=False))
        return

    if not contract_items:
        print(f"No items found.")
        return

    for item in contract_items:
        source_display = item.get('source_name') or item.get('source_id')
        print(f"--- [ID: {item['id']}] {source_display} ---")
        print(f"Author: {item.get('author')}")
        print(f"Type: {item.get('item_type')}")
        print(f"Timestamp: {item.get('item_timestamp')}")
        print(f"Status: {item.get('status')}")
        print(f"Content: {item.get('raw_content')}")
        if item.get('attachment_path'):
            print(f"Attachment: {item['attachment_path']}")
        print()


if __name__ == "__main__":
    main()
