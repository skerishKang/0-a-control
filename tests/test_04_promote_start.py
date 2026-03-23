import sys
from pathlib import Path
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import pytest
import uuid
from scripts.db_base import connect, upsert_state, now_iso
from scripts.current_quest_ops import promote_confirmed_starting_point_to_quest
from scripts.db_ops import get_current_state

def test_promote_failure_no_starting_point():
    with connect() as conn:
        conn.execute("DELETE FROM current_state WHERE state_key = 'confirmed_starting_point'")
        conn.execute("DELETE FROM quests")
        conn.commit()
    
    with pytest.raises(ValueError):
        promote_confirmed_starting_point_to_quest()

def test_promote_failure_current_quest_exists():
    with connect() as conn:
        upsert_state(conn, "confirmed_starting_point", {"title": "테스트", "reason": "이유"})
        
        active_id = str(uuid.uuid4())
        ts = now_iso()
        conn.execute(
            "INSERT INTO quests (id, title, status, completion_criteria, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
            (active_id, "진행 중인 퀘스트", "active", "완료 기준", ts, ts)
        )
        conn.commit()
    
    with pytest.raises(ValueError):
        promote_confirmed_starting_point_to_quest()

def test_promote_success():
    title = "내일의 첫 단추"
    reason = "오늘의 연결 고리"
    
    with connect() as conn:
        conn.execute("DELETE FROM quests")
        conn.execute("DELETE FROM current_state WHERE state_key LIKE 'current_quest_%'")
        upsert_state(conn, "confirmed_starting_point", {"title": title, "reason": reason, "source": "manual"})
        conn.commit()
    
    result = promote_confirmed_starting_point_to_quest()
    
    assert result["ok"] is True
    assert result["quest"]["title"] == title
    
    state = get_current_state()
    assert state.get("confirmed_starting_point") is None

def test_clear_starting_point_success():
    with connect() as conn:
        upsert_state(conn, "confirmed_starting_point", {"title": "비울 제목", "reason": "이유"})
        conn.commit()
    
    from scripts.confirmed_starting_point import clear_confirmed_starting_point
    result = clear_confirmed_starting_point()
    
    assert result["ok"] is True
    state = get_current_state()
    assert state.get("confirmed_starting_point") is None

def test_clear_starting_point_no_op():
    with connect() as conn:
        conn.execute("DELETE FROM current_state WHERE state_key = 'confirmed_starting_point'")
        conn.commit()
    
    from scripts.confirmed_starting_point import clear_confirmed_starting_point
    result = clear_confirmed_starting_point()
    
    assert result["ok"] is True
    state = get_current_state()
    assert state.get("confirmed_starting_point") is None
