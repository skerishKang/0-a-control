#!/usr/bin/env python3
import sys
import sqlite3
from pathlib import Path
from datetime import datetime

ROOT_DIR = Path(__file__).parent.parent
DATA_DIR = ROOT_DIR / "data"
DB_PATH = DATA_DIR / "db" / "notices.sqlite3"


def update_notice(
    notice_id: str = None,
    id: int = None,
    status: str = None,
    note: str = None,
    summary: str = None
) -> int:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if id is not None:
        target_id = id
    elif notice_id:
        cursor.execute("SELECT id FROM notices WHERE source_notice_id = ?", (notice_id,))
        row = cursor.fetchone()
        if not row:
            print(f"Error: Notice with source_notice_id '{notice_id}' not found")
            conn.close()
            return -1
        target_id = row[0]
    else:
        print("Error: Must provide --notice-id or --id")
        conn.close()
        return -1
    
    updates = []
    params = []
    
    if status is not None:
        updates.append("status = ?")
        params.append(status)
    if note is not None:
        updates.append("manual_note = ?")
        params.append(note)
    if summary is not None:
        updates.append("one_line_summary = ?")
        params.append(summary)
    
    if not updates:
        print("Error: No fields to update")
        conn.close()
        return -1
    
    updates.append("updated_at = ?")
    params.append(datetime.now().isoformat())
    params.append(target_id)
    
    sql = f"UPDATE notices SET {', '.join(updates)} WHERE id = ?"
    cursor.execute(sql, params)
    conn.commit()
    
    cursor.execute("SELECT id, source_notice_id, status, manual_note, one_line_summary FROM notices WHERE id = ?", (target_id,))
    row = cursor.fetchone()
    print(f"Updated notice {target_id}:")
    print(f"  source_notice_id: {row[1]}")
    print(f"  status: {row[2]}")
    print(f"  manual_note: {row[3]}")
    print(f"  one_line_summary: {row[4]}")
    
    conn.close()
    return target_id


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Update notice status, note, or summary")
    parser.add_argument("--notice-id", type=str, help="Source notice ID (e.g., PBLN_000000000119288)")
    parser.add_argument("--id", type=int, help="Internal notice ID")
    parser.add_argument("--status", type=str, help="Status: new, reviewing, writing, submitted, pass, hold")
    parser.add_argument("--note", type=str, help="Manual note text")
    parser.add_argument("--summary", type=str, help="One-line summary")
    
    args = parser.parse_args()
    
    if not args.notice_id and not args.id:
        print("Usage:")
        print("  python update_notice.py --notice-id PBLN_000000000119288 --status reviewing")
        print("  python update_notice.py --notice-id PBLN_000000000119288 --note 'NIPA형, 컨소시엄 필요'")
        print("  python update_notice.py --notice-id PBLN_000000000119288 --summary 'SW기업-수요기업 컨소시엄형 XaaS 과제'")
        print("  python update_notice.py --notice-id PBLN_000000000119288 --status reviewing --note '메모' --summary '한줄요약'")
        sys.exit(1)
    
    update_notice(
        notice_id=args.notice_id,
        id=args.id,
        status=args.status,
        note=args.note,
        summary=args.summary
    )


if __name__ == "__main__":
    main()