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
        conn.execute("DELETE FROM current_state WHERE state_key = 'current_quest_id'")
        conn.commit()
    
    with pytest.raises(ValueError):
        promote_confirmed_starting_point_to_quest()

def test_promote_failure_current_quest_exists():
    with connect() as conn:
        upsert_state(conn, "confirmed_starting_point", {"title": "테스트", "reason": "이유"})
        upsert_state(conn, "current_quest_id", "some-active-quest-id")
        conn.commit()
    
    with pytest.raises(ValueError):
        promote_confirmed_starting_point_to_quest()

def test_promote_success():
    title = "내일의 첫 단추"
    reason = "오늘의 연결 고리"
    
    # 퀘스트 테이블 비우기 (테스트 환경)
    with connect() as conn:
        conn.execute("DELETE FROM quests")
        conn.execute("DELETE FROM current_state WHERE state_key = 'current_quest_id'")
        upsert_state(conn, "confirmed_starting_point", {"title": title, "reason": reason, "source": "manual"})
        conn.commit()
    
    # 여기서 강제로 refresh_current_state를 호출하지 않고 promote만 실행
    # 내부적으로 refresh를 호출하므로 current_quest_id가 없는 상태여야 함
    result = promote_confirmed_starting_point_to_quest()
    
    assert result["ok"] is True
    assert result["quest"]["title"] == title
    
    state = get_current_state()
    assert state.get("confirmed_starting_point") is None
