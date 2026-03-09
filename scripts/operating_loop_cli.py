from __future__ import annotations

import argparse
import json

from db import get_current_state
from db_base import connect


PHASE_GUIDE = {
    "morning": {
        "title": "Morning Loop",
        "goal": "오늘 주 임무 확정",
        "prompt": "Codex, 브리핑해 줘. 오늘 주 임무와 첫 퀘스트 정하자.",
        "checklist": ["주 임무 1개 확정", "첫 퀘스트 확정", "진행 전략 수립"],
    },
    "midday": {
        "title": "Midday Re-entry",
        "goal": "작업 정렬",
        "prompt": "Codex, 흐름 정리해 줘. 다음 퀘스트 하나만 잡자.",
        "checklist": ["주 임무 확인", "재시작 포인트 확인", "다음 퀘스트 재지정"],
    },
    "in-progress": {
        "title": "In-Progress Loop",
        "goal": "현재 퀘스트 집중",
        "prompt": "Codex, 진행 상황 보고할게. 다음 걸음 정리해 줘.",
        "checklist": ["완료 기준 확인", "진척 보고", "막힘 요소 제거"],
    },
    "verdict-pending": {
        "title": "Verdict Pending",
        "goal": "판정 및 후속 조치",
        "prompt": "Codex, 방금 한 보고 판정해 줘. 다음 퀘스트도 정하자.",
        "checklist": ["완료/보류 판정", "이유 기록", "재시작 포인트 확정"],
    },
    "end-of-day": {
        "title": "End-of-Day",
        "goal": "마감 및 내일 준비",
        "prompt": "Codex, 오늘 마감하자. 한 일과 미완료, 내일 첫 퀘스트 정리해 줘.",
        "checklist": ["오늘 성과 요약", "미완료 항목 정리", "내일 첫 퀘스트 준비"],
    },
}


def _external_inbox_summary() -> dict:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT status, COUNT(*) AS count
            FROM external_inbox
            GROUP BY status
            """
        ).fetchall()
    counts = {row["status"]: row["count"] for row in rows}
    return {
        "new": counts.get("new", 0),
        "reviewing": counts.get("reviewing", 0),
        "accepted": counts.get("accepted", 0),
        "rejected": counts.get("rejected", 0),
        "archived": counts.get("archived", 0),
    }


def _infer_phase(state: dict, explicit_phase: str | None) -> str:
    if explicit_phase:
        return explicit_phase
    phase = state.get("day_phase") or "morning"
    if phase in PHASE_GUIDE:
        return phase
    return "morning"


def _build_snapshot(state: dict, phase: str) -> dict:
    return {
        "phase": phase,
        "phase_title": PHASE_GUIDE[phase]["title"],
        "phase_reason": state.get("day_phase_reason", ""),
        "main_mission_title": state.get("main_mission_title", ""),
        "main_mission_reason": state.get("main_mission_reason", ""),
        "current_quest_title": state.get("current_quest_title", ""),
        "current_quest_completion_criteria": state.get("current_quest_completion_criteria", ""),
        "restart_point": state.get("restart_point", ""),
        "recommended_next_quest": state.get("recommended_next_quest", ""),
        "recent_verdict": state.get("recent_verdict", {}),
        "external_inbox": _external_inbox_summary(),
        "prompt": PHASE_GUIDE[phase]["prompt"],
        "goal": PHASE_GUIDE[phase]["goal"],
        "checklist": PHASE_GUIDE[phase]["checklist"],
    }


def print_status(explicit_phase: str | None, as_json: bool) -> None:
    state = get_current_state()
    phase = _infer_phase(state, explicit_phase)
    snapshot = _build_snapshot(state, phase)

    if as_json:
        print(json.dumps(snapshot, ensure_ascii=False, indent=2))
        return

    print(f"[{snapshot['phase_title']}]")
    if snapshot["phase_reason"]:
        print(f"상태 판단 이유: {snapshot['phase_reason']}")
    print(f"목표: {snapshot['goal']}")
    print()
    print(f"주 임무: {snapshot['main_mission_title'] or '미정'}")
    if snapshot["main_mission_reason"]:
        print(f"이유: {snapshot['main_mission_reason']}")
    print(f"현재 퀘스트: {snapshot['current_quest_title'] or '미정'}")
    if snapshot["current_quest_completion_criteria"]:
        print(f"완료 기준: {snapshot['current_quest_completion_criteria']}")
    if snapshot["restart_point"]:
        print(f"재시작 포인트: {snapshot['restart_point']}")
    if snapshot["recommended_next_quest"]:
        print(f"추천 다음 퀘스트: {snapshot['recommended_next_quest']}")

    verdict = snapshot["recent_verdict"] or {}
    if verdict.get("verdict"):
        print(f"최근 판정: {verdict.get('verdict')} / {verdict.get('reason', '')}".strip())

    inbox = snapshot["external_inbox"]
    print(
        "외부 입력: "
        f"new={inbox['new']}, reviewing={inbox['reviewing']}, "
        f"accepted={inbox['accepted']}, archived={inbox['archived']}"
    )
    print()
    print("지금 이렇게 말하면 됩니다:")
    print(snapshot["prompt"])
    print()
    print("체크리스트:")
    for item in snapshot["checklist"]:
        print(f"- {item}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Daily operating loop helper")
    sub = parser.add_subparsers(dest="command", required=True)

    status = sub.add_parser("status", help="Show current operating-loop guidance")
    status.add_argument(
        "--phase",
        choices=sorted(PHASE_GUIDE.keys()),
        help="Override inferred phase",
    )
    status.add_argument("--json", action="store_true", help="Output JSON snapshot")

    prompt = sub.add_parser("prompt", help="Show only the recommended user utterance")
    prompt.add_argument(
        "--phase",
        choices=sorted(PHASE_GUIDE.keys()),
        help="Override inferred phase",
    )

    checklist = sub.add_parser("checklist", help="Show only the current checklist")
    checklist.add_argument(
        "--phase",
        choices=sorted(PHASE_GUIDE.keys()),
        help="Override inferred phase",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    state = get_current_state()
    phase = _infer_phase(state, getattr(args, "phase", None))

    if args.command == "status":
        print_status(args.phase, args.json)
        return
    if args.command == "prompt":
        print(PHASE_GUIDE[phase]["prompt"])
        return
    if args.command == "checklist":
        for item in PHASE_GUIDE[phase]["checklist"]:
            print(f"- {item}")


if __name__ == "__main__":
    main()
