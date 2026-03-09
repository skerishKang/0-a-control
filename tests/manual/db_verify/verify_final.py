import sqlite3
from pathlib import Path

DB_PATH = Path("data/control_tower.db")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("--- [검증] plan_items 확인 ---")
cursor.execute("SELECT id, title, bucket FROM plan_items")
for row in cursor.fetchall():
    print(row)

print("\n--- [검증] external_inbox 상태 확인 ---")
cursor.execute("SELECT id, status FROM external_inbox WHERE id = 1")
print(f"Inbox 1 상태: {cursor.fetchone()}")

conn.close()