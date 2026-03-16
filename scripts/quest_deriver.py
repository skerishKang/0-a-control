from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[1]
CONTEXT_PATH = ROOT_DIR / "data" / "runtime" / "project_context.json"
OUTPUT_PATH = ROOT_DIR / "data" / "runtime" / "quest_suggestions.json"


def load_context() -> dict:
    if not CONTEXT_PATH.exists():
        return {"scanned_at": None, "projects": []}
    with open(CONTEXT_PATH, encoding="utf-8") as f:
        return json.load(f)


def rule_git_uncommitted(ctx: dict) -> list[dict]:
    suggestions = []
    git = ctx.get("git", {})
    uncommitted = git.get("uncommitted_count", 0)

    if uncommitted > 0:
        suggestions.append({
            "signal": "git_uncommitted",
            "title": f"{ctx['name']}: {uncommitted}개의 커밋되지 않은 변경사항 처리",
            "parent_mission": f"{ctx['name']} 유지보수",
            "why_now": f"커밋되지 않은 변경 {uncommitted}건이 있습니다. 미루기 쉽지만 프로젝트 위생상 필수입니다.",
            "completion_criteria": "변경사항을 확인하고, 의미있는 단위로 commit 하거나 임시 저장(stash)합니다.",
            "next_candidates": ["이어서 세션 진행", "PR 리뷰 요청", "브랜치 병합"],
        })
    return suggestions


def rule_session_resume(ctx: dict) -> list[dict]:
    suggestions = []
    ep = ctx.get("entry_point", {})

    if ep.get("exists") and ep.get("entry_text"):
        suggestions.append({
            "signal": "session_resume",
            "title": f"{ctx['name']}: {ep['entry_text']}",
            "parent_mission": f"{ctx['name']} 세션 재개",
            "why_now": "이전 세션의 재진입 포인트를 발견했습니다. 빠르게 컨텍스트를 회복할 수 있습니다.",
            "completion_criteria": "이전 작업 내용을 확인하고, 진행 중이던 작업을 이어서 완료합니다.",
            "next_candidates": ["다음 작업 선정", "코드 리뷰", "문서 업데이트"],
        })
    return suggestions


def rule_stale_branch(ctx: dict) -> list[dict]:
    suggestions = []
    git = ctx.get("git", {})
    branch = git.get("branch")

    if branch and branch not in ("main", "master", "develop"):
        commits = git.get("recent_commits", [])
        if commits:
            try:
                last_commit_date = datetime.fromisoformat(commits[0]["date"].replace("+00:00", ""))
                days_since = (datetime.now() - last_commit_date).days
                if days_since > 14:
                    suggestions.append({
                        "signal": "stale_branch",
                        "title": f"{ctx['name']}: '{branch}' 브랜치 검토",
                        "parent_mission": f"{ctx['name']} 브랜치 정리",
                        "why_now": f"'{branch}' 브랜치에 {days_since}일간 활동이 없습니다. 병합하거나 닫아야 합니다.",
                        "completion_criteria": "브랜치 내용을 main/develop에 병합하거나, 더 이상 필요하지 않으면 삭제합니다.",
                        "next_candidates": ["병합 후 삭제", "해당 브랜치에서繼續作業", "브랜치 유지"],
                    })
            except Exception:
                pass
    return suggestions


def rule_recent_activity_no_commit(ctx: dict) -> list[dict]:
    suggestions = []
    recent_files = ctx.get("recent_files", [])
    git = ctx.get("git", {})
    commits = git.get("recent_commits", [])

    if recent_files and not commits:
        suggestions.append({
            "signal": "recent_activity_no_commit",
            "title": f"{ctx['name']}: 최근 수정파일 확인",
            "parent_mission": f"{ctx['name']} 작업 정리",
            "why_now": "최근 수정된 파일이 있지만 commit 기록이 없습니다. 작업 내용을 기록해야 합니다.",
            "completion_criteria": "수정된 파일을 확인하고, 적절한 단위로 commit 합니다.",
            "next_candidates": ["commit 실행", "stash", "파일 복원"],
        })
    return suggestions


DERIVE_RULES = [
    rule_session_resume,     # Highest: immediate restart possible
    rule_git_uncommitted,     # High: active work detected
    rule_recent_activity_no_commit,  # Medium: has activity but no commit
    rule_stale_branch,       # Low: maintenance task
]

SIGNAL_PRIORITY = {
    "session_resume": 100,
    "git_uncommitted": 80,
    "recent_activity_no_commit": 50,
    "stale_branch": 20,
}


def derive_suggestions() -> dict:
    context = load_context()
    result = {
        "generated_at": datetime.now().isoformat(),
        "source_scan_at": context.get("scanned_at"),
        "suggestions": [],
    }

    for proj in context.get("projects", []):
        if not proj.get("exists"):
            continue

        for rule in DERIVE_RULES:
            try:
                suggestions = rule(proj)
                for s in suggestions:
                    s["id"] = f"suggest-{len(result['suggestions']) + 1:03d}"
                    s["source_project"] = proj["id"]
                    s["_sort_priority"] = SIGNAL_PRIORITY.get(s["signal"], 0)
                    result["suggestions"].append(s)
            except Exception as e:
                continue

    result["suggestions"].sort(key=lambda x: x.get("_sort_priority", 0), reverse=True)

    # Remove internal metadata before output
    for s in result["suggestions"]:
        s.pop("_sort_priority", None)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    return result


def main() -> None:
    result = derive_suggestions()
    print(f"Generated {len(result['suggestions'])} suggestions")
    print(f"Output: {OUTPUT_PATH}")
    for s in result["suggestions"]:
        print(f"  [{s['id']}] {s['title']}")


if __name__ == "__main__":
    main()
