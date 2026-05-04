from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


STATUS_READY = "READY"
STATUS_IN_PROGRESS = "IN_PROGRESS"
STATUS_BLOCKED = "BLOCKED"
STATUS_NEEDS_IMPLEMENTATION = "NEEDS_IMPLEMENTATION"
STATUS_NEEDS_REVIEW = "NEEDS_REVIEW"
STATUS_NEEDS_VALIDATION = "NEEDS_VALIDATION"
STATUS_DONE = "DONE"
STATUS_NO_ACTION = "NO_ACTION"

GUARD_DESTRUCTIVE_ACTION_CAUTION = "DESTRUCTIVE_ACTION_CAUTION"
GUARD_CLOSE_CAUTION = "CLOSE_CAUTION"
GUARD_CONFIGURATION_MISSING = "CONFIGURATION_MISSING"
GUARD_VALIDATION_REQUIRED = "VALIDATION_REQUIRED"
GUARD_REVIEW_REQUIRED = "REVIEW_REQUIRED"

STALE_DAYS = 14


@dataclass(frozen=True)
class Classification:
    status: str
    reason: str
    next_action: str
    guards: tuple[str, ...] = ()
    priority: str = "P2"

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "reason": self.reason,
            "nextAction": self.next_action,
            "guards": list(self.guards),
            "priority": self.priority,
        }


def _lower_values(item: dict[str, Any]) -> list[str]:
    values: list[str] = []
    title = item.get("title")
    if title:
        values.append(str(title).lower())
    for label in item.get("labels", []) or []:
        if isinstance(label, dict):
            name = label.get("name")
        else:
            name = label
        if name:
            values.append(str(name).lower())
    return values


def _has_any(values: list[str], needles: tuple[str, ...]) -> bool:
    return any(needle in value for value in values for needle in needles)


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        if value.endswith("Z"):
            value = value[:-1] + "+00:00"
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def _is_stale(item: dict[str, Any], now: datetime | None = None) -> bool:
    updated = _parse_datetime(item.get("updated_at"))
    if not updated:
        return False
    if now is None:
        now = datetime.now(timezone.utc)
    if updated.tzinfo is None:
        updated = updated.replace(tzinfo=timezone.utc)
    return (now - updated).days >= STALE_DAYS


def classify_issue(issue: dict[str, Any], now: datetime | None = None) -> Classification:
    values = _lower_values(issue)
    state = issue.get("state")

    if state == "closed":
        return Classification(
            status=STATUS_DONE,
            reason="Issue is closed.",
            next_action="No action required unless it should be reopened.",
            priority="P3",
        )

    if _has_any(values, ("blocked", "blocker", "waiting", "hold")):
        return Classification(
            status=STATUS_BLOCKED,
            reason="Issue appears blocked or waiting based on title/labels.",
            next_action="Record the blocker and the condition required to resume.",
            guards=(GUARD_CONFIGURATION_MISSING,),
            priority="P1",
        )

    if _has_any(values, ("review", "needs review", "검토")):
        return Classification(
            status=STATUS_NEEDS_REVIEW,
            reason="Issue is marked for review.",
            next_action="Review the issue scope and decide whether implementation or validation is next.",
            guards=(GUARD_REVIEW_REQUIRED,),
            priority="P1",
        )

    if _has_any(values, ("validation", "test", "verify", "검증")):
        return Classification(
            status=STATUS_NEEDS_VALIDATION,
            reason="Issue title/labels indicate validation is needed.",
            next_action="Run the required checks and attach the result.",
            guards=(GUARD_VALIDATION_REQUIRED,),
            priority="P1",
        )

    if _is_stale(issue, now):
        return Classification(
            status=STATUS_NEEDS_REVIEW,
            reason=f"Issue has not been updated for at least {STALE_DAYS} days.",
            next_action="Review whether this is still actionable, blocked, or obsolete.",
            guards=(GUARD_REVIEW_REQUIRED,),
            priority="P2",
        )

    return Classification(
        status=STATUS_NEEDS_IMPLEMENTATION,
        reason="Open issue has no blocking, review, or validation marker.",
        next_action="Define implementation scope or mark as no-action if not actionable.",
        priority="P2",
    )


def classify_pull_request(pr: dict[str, Any], now: datetime | None = None) -> Classification:
    values = _lower_values(pr)
    state = pr.get("state")

    if state == "closed":
        if pr.get("merged_at"):
            return Classification(
                status=STATUS_DONE,
                reason="Pull request is merged.",
                next_action="No action required unless follow-up documentation is needed.",
                priority="P3",
            )
        return Classification(
            status=STATUS_NO_ACTION,
            reason="Pull request is closed without merge.",
            next_action="No action required unless it should be reopened.",
            priority="P3",
        )

    if pr.get("draft"):
        return Classification(
            status=STATUS_IN_PROGRESS,
            reason="Pull request is still draft.",
            next_action="Continue implementation or request local validation before marking ready.",
            guards=(GUARD_VALIDATION_REQUIRED,),
            priority="P1",
        )

    if _has_any(values, ("blocked", "hold", "waiting")):
        return Classification(
            status=STATUS_BLOCKED,
            reason="Pull request appears blocked or waiting based on title/labels.",
            next_action="Identify the blocker before review or merge.",
            guards=(GUARD_REVIEW_REQUIRED,),
            priority="P1",
        )

    if _has_any(values, ("docs", "documentation")):
        return Classification(
            status=STATUS_NEEDS_REVIEW,
            reason="Open non-draft documentation PR is ready for review.",
            next_action="Review documentation scope and merge readiness.",
            guards=(GUARD_REVIEW_REQUIRED,),
            priority="P2",
        )

    if _has_any(values, ("test", "validation", "verify")):
        return Classification(
            status=STATUS_NEEDS_VALIDATION,
            reason="Pull request title/labels indicate validation is needed.",
            next_action="Run targeted and relevant full checks before review.",
            guards=(GUARD_VALIDATION_REQUIRED,),
            priority="P1",
        )

    if _is_stale(pr, now):
        return Classification(
            status=STATUS_NEEDS_REVIEW,
            reason=f"Pull request has not been updated for at least {STALE_DAYS} days.",
            next_action="Review current relevance and decide whether to continue or close.",
            guards=(GUARD_REVIEW_REQUIRED,),
            priority="P2",
        )

    return Classification(
        status=STATUS_READY,
        reason="Open non-draft pull request has no blocking marker.",
        next_action="Review changed files and validation evidence.",
        guards=(GUARD_REVIEW_REQUIRED,),
        priority="P2",
    )


def classify_github_summary(summary: dict[str, Any], now: datetime | None = None) -> dict[str, Any]:
    issues = summary.get("open_issues", []) or []
    open_prs = summary.get("open_pull_requests", []) or []
    closed_prs = summary.get("recent_closed_pull_requests", []) or []

    classified_issues = [
        {**issue, "classification": classify_issue(issue, now).to_dict()}
        for issue in issues
    ]
    classified_open_prs = [
        {**pr, "classification": classify_pull_request(pr, now).to_dict()}
        for pr in open_prs
    ]
    classified_closed_prs = [
        {**pr, "classification": classify_pull_request(pr, now).to_dict()}
        for pr in closed_prs
    ]

    status_counts: dict[str, int] = {}
    for item in [*classified_issues, *classified_open_prs, *classified_closed_prs]:
        status = item["classification"]["status"]
        status_counts[status] = status_counts.get(status, 0) + 1

    return {
        "repository": summary.get("repository", {}),
        "counts": {
            **(summary.get("counts", {}) or {}),
            "classified_statuses": status_counts,
        },
        "open_issues": classified_issues,
        "open_pull_requests": classified_open_prs,
        "recent_closed_pull_requests": classified_closed_prs,
    }
