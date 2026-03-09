import sqlite3
from datetime import datetime, timedelta, timezone
import json
import uuid
from pathlib import Path

DB_PATH = Path("data/control_tower.db")
conn = sqlite3.connect(DB_PATH)

def insert_inbox_item(source_id, external_message_id, content, status, item_type='text', author='TestUser', session_id=None, attachment_path=None):
    current_time = datetime.now(timezone.utc)
    imported_at = current_time.isoformat()
    item_timestamp = (current_time - timedelta(hours=1)).isoformat() # 1 hour ago
    
    conn.execute("""
        INSERT INTO external_inbox 
        (source_type, source_id, source_name, external_message_id, 
         author, item_type, title, raw_content, attachment_path, attachment_ref, 
         item_timestamp, imported_at, processed_at, status, session_id, metadata_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        'telegram', source_id, source_id, external_message_id,
        author, item_type, content[:30], content, attachment_path, None,
        item_timestamp, imported_at, None, status, session_id, json.dumps({})
    ))

# Clear existing dummy data first if any
conn.execute("DELETE FROM external_inbox WHERE source_id LIKE 'test_%'")
conn.execute("DELETE FROM plan_items WHERE title LIKE 'Test Message%'")

# Insert diverse dummy data
insert_inbox_item('test_self_chat', 101, 'Test Message Content - 핵심 판단 A (new)', 'new')
insert_inbox_item('test_kang_hyerim_chat', 102, 'Test Message Content - 프로젝트 B 제안 (new)', 'new')
insert_inbox_item('test_news_channel', 103, 'Test Message Content - 시장 동향 분석 (reviewing)', 'reviewing')
insert_inbox_item('test_self_chat', 104, 'Test Message Content - 아이디어 스케치 (reviewing)', 'reviewing')
insert_inbox_item('test_self_chat', 105, 'Test Message Content - 이미지 파일 (new)', 'new', item_type='image', attachment_path='/data/blobs/test_self_chat/image_105.jpg')
insert_inbox_item('test_kang_hyerim_chat', 106, 'Test Message Content - 완료된 작업 보고 (accepted)', 'accepted')
insert_inbox_item('test_self_chat', 107, 'Test Message Content - 거절된 아이디어 (rejected)', 'rejected')

conn.commit()
conn.close()
print("Diverse dummy data inserted.")