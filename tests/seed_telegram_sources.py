import sqlite3
import json
from pathlib import Path
from telegram_db import init_db

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "control_tower.db"
CHATS_FILE = Path("G:/Ddrive/BatangD/task/workdiary/0-conmand-center/data/telegram_chats.json")

def seed():
    init_db()
    with open(CHATS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    chats = data.get("chats", [])
    conn = sqlite3.connect(DB_PATH)
    
    core_titles = {"로컬봇", "킬로봇", "내텔레", "강혜림"}
    
    for chat in chats:
        # Simplified mapping
        chat_class = "general_chat"
        if "로컬봇" in chat['title']: chat_class = "local_chat"
        elif "킬로봇" in chat['title']: chat_class = "kilo_chat"
        elif "내텔레" in chat['title']: chat_class = "self_chat"
        elif "강혜림" in chat['title']: chat_class = "kang_hyerim_chat"
        elif "주식큐레이터" in chat['title']: chat_class = "stock_curator_channel"
        elif "뉴스" in chat['title'] or "공시" in chat['title']: chat_class = "news_channel"
        
        is_core = 1 if chat['title'] in core_titles else 0
        
        conn.execute("""
            INSERT OR REPLACE INTO telegram_sources 
            (source_id, source_name, chat_class, is_core, sync_mode, metadata_json) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            str(chat['id']),
            chat['title'],
            chat_class,
            is_core,
            "core_sync" if is_core else "manual",
            json.dumps(chat, ensure_ascii=False),
        ))
        
    conn.commit()
    conn.close()
    print("Seeded telegram_sources successfully.")

if __name__ == "__main__":
    seed()
