import sqlite3
from datetime import datetime, timezone
import json

conn = sqlite3.connect("data/control_tower.db")
conn.execute("""
    INSERT INTO external_inbox 
    (source_id, external_message_id, title, content, imported_at, author, item_timestamp)
    VALUES (?, ?, ?, ?, ?, ?, ?)
""", ("test_source", 1, "Test Title", "Test Message Content - 핵심 판단 A", datetime.now(timezone.utc).isoformat(), "Tester", datetime.now(timezone.utc).isoformat()))
conn.commit()
conn.close()
print("Dummy data inserted.")