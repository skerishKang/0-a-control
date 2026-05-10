from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path


UTC = timezone.utc


def build_workdiary_item(name: str, path: str, modified_ts: float) -> dict:
    modified_at = datetime.fromtimestamp(modified_ts, UTC).replace(microsecond=0).isoformat()
    path_obj = Path(path)
    lowered = name.lower()
    system_names = {
        "node_modules",
        "logs",
        "log",
        "test-results",
        "dist",
        "build",
        "coverage",
        "__pycache__",
        "tmp",
        "temp",
        "tools",
        "flutter",
        "summaries",
        "uploads",
        "upload",
        "cache",
        "arxiv_cache",
        "assets",
        "references",
        "archive",
        "archives",
        "prompts",
    }
    archive_keywords = ("백업", "backup", "archive", "deleted", "trash", "보관")
    document_keywords = ("문서", "계획", "정리", "proposal", "ppt", "노션", "회의", "notes")
    project_boost_keywords = ("control", "plan", "auto", "browser", "edu", "dashboard", "api", "cli", "agent")
    manifest_names = ("package.json", "pyproject.toml", "requirements.txt", "go.mod", "Cargo.toml")
    source_markers = ("src", "app", "pages", "server", "scripts", "main.py", "index.html")

    readme_exists = (path_obj / "README.md").exists() or (path_obj / "readme.md").exists()
    git_exists = (path_obj / ".git").exists()
    manifest_hits = [marker for marker in manifest_names if (path_obj / marker).exists()]
    source_hits = [marker for marker in source_markers if (path_obj / marker).exists()]

    is_backup = any(keyword in lowered for keyword in archive_keywords)
    is_docs = any(keyword in lowered for keyword in document_keywords)
    is_numbered_project = lowered[:1].isdigit()
    is_control = "control" in lowered or "cmd" in lowered
    is_plan = "plan" in lowered
    is_system = lowered in system_names
    has_project_keyword = any(keyword in lowered for keyword in project_boost_keywords)

    item_type = "project"
    if is_backup:
        item_type = "archive"
    elif is_docs and not is_plan:
        item_type = "document"
    elif is_system:
        item_type = "system"

    score = 0
    reasons: list[str] = []
    if item_type == "project":
        score += 30
        reasons.append("프로젝트 후보")
    if is_numbered_project:
        score += 10
        reasons.append("번호 체계")
    if is_control or is_plan:
        score += 15
        reasons.append("운영/플랜 연관")
    if has_project_keyword:
        score += 8
        reasons.append("프로젝트 키워드")
    if readme_exists:
        score += 12
        reasons.append("README 존재")
    if git_exists:
        score += 12
        reasons.append("Git 저장소")
    if manifest_hits:
        score += 10 + min(len(manifest_hits), 2) * 3
        reasons.append("구성 파일")
    if source_hits:
        score += 8
        reasons.append("소스 구조")

    days_old = max((datetime.now(UTC).timestamp() - modified_ts) / 86400, 0)
    if days_old <= 7:
        score += 16
        reasons.append("최근 수정")
    elif days_old <= 30:
        score += 10
        reasons.append("비교적 최근 수정")
    elif days_old <= 90:
        score += 4

    if item_type == "archive":
        score -= 40
        reasons.append("보관/백업 성격")
    elif item_type == "document":
        score -= 18
        reasons.append("문서 중심")
    elif item_type == "system":
        score -= 35
        reasons.append("시스템/보조 폴더")

    return {
        "name": name,
        "path": path,
        "modified_at": modified_at,
        "item_type": item_type,
        "priority_score": score,
        "priority_reason": ", ".join(reasons[:4]) if reasons else "추가 신호 없음",
    }