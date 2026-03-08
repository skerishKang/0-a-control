import json
import os
import shutil
from pathlib import Path
from pprint import pprint

from scripts.db_base import connect
from scripts.db_ops import get_current_state, report_quest_progress
from scripts.db_state import refresh_current_state
from scripts.file_queue import REPORTS_DIR, VERDICTS_DIR
from scripts.verdict_import import import_verdicts

def print_box(msg):
    print("\n" + "=" * 60)
    print(f"[{msg}]")
    print("=" * 60)

def main():
    print_box("1. Check current main mission and quest")
    with connect() as conn:
        refresh_current_state(conn)
    state_before = get_current_state()
    quest_id = None
    if state_before.get("current_quest"):
        quest_id = state_before["current_quest"]["id"]
        print(f"Current Quest: {state_before['current_quest']['title']} (ID: {quest_id})")
        print(f"Status: {state_before['current_quest']['status']}")
    else:
        print("No current quest. Trying to find one.")
        with connect() as conn:
            row = conn.execute("SELECT id, title FROM quests LIMIT 1").fetchone()
            if row:
                quest_id = row["id"]
                print(f"Selected Quest: {row['title']} (ID: {quest_id})")
            else:
                print("DB is entirely empty. Aborting.")
                return

    print(f"Status Summary Before: {state_before.get('quest_status_summary')}")
    
    # 2. quest report
    print_box("2. Generate quest report")
    report_quest_progress(
        quest_id=quest_id,
        work_summary="진행 상태 점검 자동화 루프 테스트",
        remaining_work="에지 케이스 확인",
        blocker="없음",
        self_assessment="partial",
        session_id=""
    )
    
    state_pending = get_current_state()
    
    with connect() as conn:
        q_row = conn.execute("SELECT status FROM quests WHERE id = ?", (quest_id,)).fetchone()
        print(f"Quest Status Now DB: {q_row['status'] if q_row else None}")
        
    print(f"Status Summary Now: {state_pending.get('quest_status_summary')}")
    
    # 3. check quest reports
    print_box("3. Check generated report file")
    report_dir = REPORTS_DIR
    reports = list(report_dir.glob("*.report.json"))
    if not reports:
        print("Error: No report generated.")
        return
    
    reports.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    latest_report = reports[0]
    print(f"Found latest report: {latest_report.name}")
    
    with open(latest_report, "r", encoding="utf-8") as f:
        report_data = json.load(f)
    print(f"Report ID: {report_data.get('report_id')}")
    
    # 4. Create dummy external verdict
    print_box("4. Create dummy external verdict JSON")
    verdict_dir = VERDICTS_DIR
    report_id = report_data.get('report_id')
    verdict_path = verdict_dir / f"{report_id}.verdict.json"
    
    dummy_verdict = {
        "schema_version": "1.0",
        "report_ref": report_id,
        "verdict": {
            "status": "partial",
            "reason": "자동루프 테스트를 통한 partial 검증. 흐름 통과.",
            "restart_point": "다음 스테이지 검증",
            "next_hint": "DB 리셋 후 테스트",
            "plan_impact": {
                "today": "유지",
                "short_term": "--",
                "long_term": "--",
                "recurring": "--",
                "dated": "--"
            },
            "ai_tags": ["test", "e2e"],
            "confidence": 0.99
        },
        "judge": {
            "provider": "e2e-tester",
            "model": "auto-script",
            "prompt_hash": "sha256:dummy",
            "latency_ms": 100
        }
    }
    
    with open(verdict_path, "w", encoding="utf-8") as f:
        json.dump(dummy_verdict, f, ensure_ascii=False, indent=2)
    print(f"Created dummy verdict: {verdict_path.name}")
    
    # 5. ingest
    print_box("5. Import verdicts (queue_worker logic)")
    import_verdicts()
    
    # 6. check DB state
    print_box("6. Check final DB State & UI fields")
    with connect() as conn:
        refresh_current_state(conn)
    state_final = get_current_state()
    
    with connect() as conn:
        q_row = conn.execute("SELECT status FROM quests WHERE id = ?", (quest_id,)).fetchone()
        print(f"Quest Status Final DB: {q_row['status'] if q_row else None}")
    print(f"Status Summary Final:")
    pprint(state_final.get("quest_status_summary"))
    
    print("\n[UI Fields Simulation]")
    print(f"- 최근 판정 제목: {state_final.get('recent_verdict', {}).get('title')}")
    print(f"- 다음 퀘스트: {state_final.get('recommended_next_quest')}")
    print(f"- 진행 상황 요약: {state_final.get('day_progress_summary')}")
    print(f"- pending 해제 여부: is_pending={state_final.get('quest_status_summary', {}).get('is_pending')}, is_awaiting_external={state_final.get('quest_status_summary', {}).get('is_awaiting_external_verdict')}")
    
if __name__ == "__main__":
    main()
