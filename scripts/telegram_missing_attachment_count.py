import sqlite3
import sys


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: python scripts/telegram_missing_attachment_count.py <source_id> [max_file_size_mb]")
        return 1

    source_id = sys.argv[1]
    max_file_size_bytes = None
    if len(sys.argv) >= 3:
        try:
            max_file_size_bytes = int(float(sys.argv[2]) * 1024 * 1024)
        except ValueError:
            print("invalid max_file_size_mb")
            return 1

    conn = sqlite3.connect("data/control_tower.db")
    try:
        rows = conn.execute(
            """
            SELECT metadata_json
            FROM external_inbox
            WHERE source_id = ?
              AND COALESCE(item_type, 'text') != 'text'
              AND COALESCE(attachment_path, '') = ''
            """,
            (source_id,),
        ).fetchall()
        count = 0
        for row in rows:
            if max_file_size_bytes is None:
                count += 1
                continue
            raw = row[0]
            file_size = None
            if raw:
                try:
                    import json
                    metadata = json.loads(raw)
                    value = metadata.get("file_size")
                    file_size = int(value) if value is not None else None
                except Exception:
                    file_size = None
            if file_size is None or file_size <= max_file_size_bytes:
                count += 1
        print(count)
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
