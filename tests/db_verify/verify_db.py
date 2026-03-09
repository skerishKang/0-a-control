import sqlite3
from pathlib import Path

DB_PATH = Path("data/control_tower.db")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("--- [검증] external_inbox 스키마 ---")
cursor.execute("PRAGMA table_info(external_inbox)")
for row in cursor.fetchall():
    print(row[1])

print("\n--- [검증] external_inbox 레코드 개수 ---")
cursor.execute("SELECT count(*) FROM external_inbox")
print(f"개수: {cursor.fetchone()[0]}")

conn.close()