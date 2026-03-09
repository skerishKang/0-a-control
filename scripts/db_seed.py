from __future__ import annotations

# Enable both `python scripts/foo.py` and `python -m scripts.foo`
import sys
from pathlib import Path
_root = str(Path(__file__).resolve().parents[1])
if _root not in sys.path:
    sys.path.insert(0, _root)

import json
import uuid
from datetime import datetime

from scripts.db_base import UTC, connect, init_db, now_iso
from scripts.db_state import get_workdiary_priority_candidates
from scripts.db_state import refresh_current_state


def create_sample_data_if_empty() -> None:
    init_db()
    with connect() as conn:
        existing = conn.execute("SELECT COUNT(*) AS count FROM plan_items").fetchone()["count"]
        if existing:
            sync_seed_data(conn)
            refresh_current_state(conn)
            return

        created_at = now_iso()
        profile = build_seed_profile()

        main_plan_id = str(uuid.uuid4())
        short_plan_id = str(uuid.uuid4())
        long_plan_id = str(uuid.uuid4())
        recurring_plan_id = str(uuid.uuid4())

        conn.executemany(
            """
            INSERT INTO plan_items (
                id, bucket, title, description, status, priority_score, priority_reason, due_at,
                project_key, related_session_id, related_source_id, created_at, updated_at, metadata_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    main_plan_id,
                    "today",
                    profile["main_title"],
                    profile["main_description"],
                    "active",
                    100,
                    profile["main_reason"],
                    None,
                    "portfolio-review",
                    None,
                    None,
                    created_at,
                    created_at,
                    json.dumps({"is_main_mission": True}, ensure_ascii=False),
                ),
                (
                    short_plan_id,
                    "short_term",
                    profile["short_title"],
                    profile["short_description"],
                    "pending",
                    70,
                    profile["short_reason"],
                    None,
                    profile["short_project_key"],
                    None,
                    None,
                    created_at,
                    created_at,
                    None,
                ),
                (
                    long_plan_id,
                    "long_term",
                    profile["long_title"],
                    profile["long_description"],
                    "pending",
                    50,
                    profile["long_reason"],
                    None,
                    "portfolio-strategy",
                    None,
                    None,
                    created_at,
                    created_at,
                    None,
                ),
                (
                    recurring_plan_id,
                    "recurring",
                    "workdiary 일일 점검",
                    "매일 workdiary의 흐름을 확인하고 다음 행동을 정리",
                    "active",
                    40,
                    "반복 운영 루틴",
                    None,
                    "ops",
                    None,
                    None,
                    created_at,
                    created_at,
                    None,
                ),
            ],
        )

        conn.execute(
            """
            INSERT INTO quests (
                id, plan_item_id, parent_quest_id, title, why_now, completion_criteria, status,
                verdict_reason, restart_point, next_quest_hint, created_at, updated_at, metadata_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(uuid.uuid4()),
                main_plan_id,
                None,
                profile["quest_title"],
                profile["quest_why_now"],
                "프로젝트 후보 5개와 선정 이유 1줄씩 정리",
                "active",
                None,
                profile["quest_restart"],
                profile["quest_next_hint"],
                created_at,
                created_at,
                None,
            ),
        )

        sync_seed_data(conn)
        refresh_current_state(conn)


def build_seed_profile() -> dict[str, str]:
    candidates = get_workdiary_priority_candidates(5)
    primary = candidates[0]["name"] if candidates else "workdiary 핵심 프로젝트"
    secondary = candidates[1]["name"] if len(candidates) > 1 else primary
    tertiary = candidates[2]["name"] if len(candidates) > 2 else secondary
    joined = ", ".join(item["name"] for item in candidates[:3]) if candidates else "상위 프로젝트 후보"

    return {
        "main_title": f"{primary} 포함 핵심 프로젝트 흐름 파악",
        "main_description": f"{joined}를 중심으로 지금 계속 진행할 후보와 바로 착수할 프로젝트 흐름을 정리한다.",
        "main_reason": f"급하고, 미루기 쉽지만, 반드시 해야 하는 핵심 정리 작업. 우선 추천 후보는 {primary}",
        "short_title": f"{secondary} 다음 단계 점검",
        "short_description": f"{secondary}를 단기 실행 후보로 둘지 바로 이어서 검토한다.",
        "short_reason": f"주 임무 다음에 이어야 할 단기 계획. 현재 후보는 {secondary}",
        "short_project_key": secondary,
        "long_title": f"{primary}, {secondary}, {tertiary} 장기 전략 정리",
        "long_description": "상위 프로젝트 후보를 사업화, 계속 진행, 보류 축으로 나눌 장기 판단 기준을 만든다.",
        "long_reason": "장기 전략과 포트폴리오 판단 축 정리",
        "quest_title": f"{primary} 포함 우선 검토 후보 5개 좁히기",
        "quest_why_now": f"{primary}를 포함해 실제로 볼 프로젝트 후보 5개를 먼저 확정해야 주 임무가 앞으로 진행된다.",
        "quest_restart": "후보 5개 목록과 선정 이유 초안 다시 보기",
        "quest_next_hint": f"{primary}를 포함한 후보 5개와 선정 이유를 문장으로 정리",
    }


def sync_seed_data(conn) -> None:
    profile = build_seed_profile()
    now = now_iso()
    conn.execute(
        """
        UPDATE plan_items
        SET title = ?, description = ?, priority_reason = ?, updated_at = ?
        WHERE project_key = 'portfolio-review'
        """,
        (profile["main_title"], profile["main_description"], profile["main_reason"], now),
    )
    conn.execute(
        """
        UPDATE plan_items
        SET title = ?, description = ?, priority_reason = ?, project_key = ?, updated_at = ?
        WHERE bucket = 'short_term' AND (
            project_key = '0-a-control' OR
            title = '0-a-control 운영 구조 초안 점검'
        )
        """,
        (profile["short_title"], profile["short_description"], profile["short_reason"], profile["short_project_key"], now),
    )
    conn.execute(
        """
        UPDATE plan_items
        SET title = ?, description = ?, priority_reason = ?, project_key = 'portfolio-strategy', updated_at = ?
        WHERE bucket = 'long_term' AND (
            project_key = 'control-tower' OR
            title = '전자료 기반 참모 시스템 완성'
        )
        """,
        (profile["long_title"], profile["long_description"], profile["long_reason"], now),
    )
    conn.execute(
        """
        DELETE FROM plan_items
        WHERE bucket = 'dated' AND title = '기한 임박 샘플 항목 점검'
        """
    )
    conn.execute(
        """
        UPDATE quests
        SET title = ?, why_now = ?, restart_point = ?, next_quest_hint = ?, updated_at = ?
        WHERE plan_item_id IN (
            SELECT id FROM plan_items WHERE project_key = 'portfolio-review'
        )
        """,
        (profile["quest_title"], profile["quest_why_now"], profile["quest_restart"], profile["quest_next_hint"], now),
    )
