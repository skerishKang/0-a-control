from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT_DIR / "data" / "config" / "tracked_projects.json"
OUTPUT_PATH = ROOT_DIR / "data" / "runtime" / "project_context.json"


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        return {"version": 1, "projects": []}
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


def get_git_state(project_path: Path) -> dict[str, Any]:
    result = {"branch": None, "has_uncommitted": False, "uncommitted_count": 0, "recent_commits": [], "error": None}
    try:
        branch_result = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=str(project_path),
            capture_output=True,
            text=True,
            timeout=10,
        )
        result["branch"] = branch_result.stdout.strip() or "unknown"

        status_result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=str(project_path),
            capture_output=True,
            text=True,
            timeout=10,
        )
        lines = status_result.stdout.strip().splitlines() if status_result.stdout.strip() else []
        result["uncommitted_count"] = len(lines)
        result["has_uncommitted"] = len(lines) > 0

        log_result = subprocess.run(
            ["git", "log", "-3", "--oneline", "--format=%H %ci %s"],
            cwd=str(project_path),
            capture_output=True,
            text=True,
            timeout=10,
        )
        if log_result.stdout.strip():
            for line in log_result.stdout.strip().splitlines():
                parts = line.split(" ", 2)
                if len(parts) >= 3:
                    result["recent_commits"].append({
                        "hash": parts[0][:7],
                        "date": parts[1],
                        "msg": parts[2],
                    })
    except subprocess.TimeoutExpired:
        result["error"] = "git command timeout"
    except Exception as e:
        result["error"] = str(e)
    return result


def get_recent_files(project_path: Path, scan_rules: dict) -> list[dict[str, str]]:
    recent_files = []
    recent_days = scan_rules.get("recent_days", 7)
    max_files = scan_rules.get("max_recent_files", 10)
    ignore_patterns = scan_rules.get("ignore_patterns", [])

    cutoff = datetime.now() - timedelta(days=recent_days)

    def should_ignore(path_str: str) -> bool:
        for pattern in ignore_patterns:
            if pattern.endswith("/"):
                if pattern.rstrip("/") in path_str.split("/"):
                    return True
            else:
                if pattern in path_str:
                    return True
        return False

    try:
        for item in project_path.rglob("*"):
            if not item.is_file():
                continue
            if should_ignore(str(item)):
                continue
            try:
                mtime = datetime.fromtimestamp(item.stat().st_mtime)
                if mtime >= cutoff:
                    recent_files.append({
                        "path": str(item.relative_to(project_path)),
                        "modified": mtime.isoformat(),
                    })
            except OSError:
                continue
    except Exception:
        pass

    recent_files.sort(key=lambda x: x["modified"], reverse=True)
    return recent_files[:max_files]


def get_entry_point(project_path: Path, entry_points: dict) -> dict[str, Any]:
    result = {"exists": False, "entry_text": None, "type": None}

    session_file = entry_points.get("session_file")
    if session_file:
        session_path = project_path / session_file
        if session_path.exists():
            result["exists"] = True
            result["type"] = "session"
            try:
                content = session_path.read_text(encoding="utf-8", errors="ignore")
                lines = [l.strip() for l in content.splitlines() if l.strip()]
                result["entry_text"] = lines[0] if lines else "Continue from session"
            except Exception:
                result["entry_text"] = "Continue from session"
            return result

    state_marker = entry_points.get("state_marker")
    if state_marker:
        state_path = project_path / state_marker
        if state_path.exists():
            result["exists"] = True
            result["type"] = "state_marker"
            try:
                with open(state_path, encoding="utf-8") as f:
                    data = json.load(f)
                    result["entry_text"] = data.get("current_task", data.get("entry", "Resume work"))
            except Exception:
                result["entry_text"] = "Resume from workstate"
            return result

    return result


def scan_project(project: dict) -> dict[str, Any]:
    project_path = Path(project["path"])
    ctx = {
        "id": project["id"],
        "name": project["name"],
        "path": str(project_path),
        "exists": project_path.is_dir(),
        "git": {"branch": None, "has_uncommitted": False, "uncommitted_count": 0, "recent_commits": [], "error": None},
        "recent_files": [],
        "entry_point": {"exists": False, "entry_text": None, "type": None},
        "scan_error": None,
    }

    if not ctx["exists"]:
        ctx["scan_error"] = f"Project path does not exist: {project_path}"
        return ctx

    try:
        ctx["git"] = get_git_state(project_path)
    except Exception as e:
        ctx["git"]["error"] = str(e)

    scan_rules = project.get("scan_rules", {})
    try:
        ctx["recent_files"] = get_recent_files(project_path, scan_rules)
    except Exception as e:
        ctx["scan_error"] = f"Failed to scan recent files: {e}"

    entry_points = project.get("entry_points", {})
    try:
        ctx["entry_point"] = get_entry_point(project_path, entry_points)
    except Exception as e:
        ctx["entry_point"] = {"exists": False, "entry_text": None, "type": None, "error": str(e)}

    return ctx


def scan_projects() -> dict:
    config = load_config()
    result = {
        "scanned_at": datetime.now().isoformat(),
        "projects": [],
    }

    for proj in config.get("projects", []):
        if not proj.get("enabled", True):
            continue
        try:
            ctx = scan_project(proj)
            result["projects"].append(ctx)
        except Exception as e:
            result["projects"].append({
                "id": proj.get("id", "unknown"),
                "name": proj.get("name", "Unknown"),
                "path": proj.get("path", ""),
                "exists": False,
                "scan_error": str(e),
            })

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    return result


def main() -> None:
    result = scan_projects()
    print(f"Scanned {len(result['projects'])} projects")
    print(f"Output: {OUTPUT_PATH}")
    for proj in result["projects"]:
        status = "OK" if proj.get("exists") else "NOT FOUND"
        uncommitted = proj.get("git", {}).get("uncommitted_count", 0)
        print(f"  [{status}] {proj['name']}: {uncommitted} uncommitted")


if __name__ == "__main__":
    main()
