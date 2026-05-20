from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Callable

from scripts.github_service import get_github_summary
from scripts.services.operational_state import classify_github_summary


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _error_payload(message: str, generated_at: str | None = None) -> dict[str, Any]:
    return {
        "ok": False,
        "source_status": {
            "github": "error",
            "classifier": "not_run",
            "message": message,
        },
        "repository": {},
        "counts": {},
        "open_issues": [],
        "open_pull_requests": [],
        "recent_closed_pull_requests": [],
        "rate_limit": {},
        "generated_at": generated_at or _utc_now_iso(),
    }


def build_operations_summary(
    github_summary_loader: Callable[[], dict[str, Any]] = get_github_summary,
    classifier: Callable[[dict[str, Any]], dict[str, Any]] = classify_github_summary,
) -> dict[str, Any]:
    generated_at = _utc_now_iso()
    try:
        github_summary = github_summary_loader()
    except Exception as exc:
        return _error_payload(str(exc), generated_at)

    try:
        classified = classifier(github_summary)
    except Exception as exc:
        return {
            "ok": False,
            "source_status": {
                "github": "ok",
                "classifier": "error",
                "message": str(exc),
            },
            "repository": github_summary.get("repository", {}),
            "counts": github_summary.get("counts", {}),
            "open_issues": github_summary.get("open_issues", []),
            "open_pull_requests": github_summary.get("open_pull_requests", []),
            "recent_closed_pull_requests": github_summary.get("recent_closed_pull_requests", []),
            "rate_limit": github_summary.get("rate_limit", {}),
            "generated_at": generated_at,
        }

    return {
        "ok": True,
        "source_status": {
            "github": "ok",
            "classifier": "ok",
        },
        "repository": classified.get("repository", {}),
        "counts": classified.get("counts", {}),
        "open_issues": classified.get("open_issues", []),
        "open_pull_requests": classified.get("open_pull_requests", []),
        "recent_closed_pull_requests": classified.get("recent_closed_pull_requests", []),
        "rate_limit": github_summary.get("rate_limit", {}),
        "generated_at": generated_at,
    }
