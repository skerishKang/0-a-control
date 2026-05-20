from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import requests


DEFAULT_REPOSITORY = "skerishKang/0-a-control"
GITHUB_API_BASE_URL = "https://api.github.com"
REQUEST_TIMEOUT_SECONDS = 10
MAX_ITEMS = 50


@dataclass(frozen=True)
class GitHubConfig:
    repository: str
    token_configured: bool


def get_github_config() -> GitHubConfig:
    repository = os.getenv("CONTROL_TOWER_GITHUB_REPOSITORY", DEFAULT_REPOSITORY).strip()
    if not repository or "/" not in repository:
        repository = DEFAULT_REPOSITORY
    return GitHubConfig(
        repository=repository,
        token_configured=bool(os.getenv("GITHUB_TOKEN") or os.getenv("CONTROL_TOWER_GITHUB_TOKEN")),
    )


def _get_token() -> str | None:
    return os.getenv("CONTROL_TOWER_GITHUB_TOKEN") or os.getenv("GITHUB_TOKEN")


def _headers() -> dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "0-a-control-local-dashboard",
    }
    token = _get_token()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _safe_json(response: requests.Response) -> Any:
    try:
        return response.json()
    except ValueError:
        return {"message": response.text[:500]}


def _github_get(path: str, params: dict[str, Any] | None = None) -> tuple[Any, dict[str, Any]]:
    url = f"{GITHUB_API_BASE_URL}{path}"
    response = requests.get(url, headers=_headers(), params=params, timeout=REQUEST_TIMEOUT_SECONDS)
    rate_limit = {
        "limit": response.headers.get("X-RateLimit-Limit"),
        "remaining": response.headers.get("X-RateLimit-Remaining"),
        "reset": response.headers.get("X-RateLimit-Reset"),
    }
    data = _safe_json(response)
    if response.status_code >= 400:
        message = data.get("message") if isinstance(data, dict) else str(data)
        raise RuntimeError(f"GitHub API error {response.status_code}: {message}")
    return data, rate_limit


def _normalize_user(user: dict[str, Any] | None) -> dict[str, Any]:
    if not user:
        return {}
    return {
        "login": user.get("login"),
        "avatar_url": user.get("avatar_url"),
        "html_url": user.get("html_url"),
    }


def _normalize_label(label: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": label.get("name"),
        "color": label.get("color"),
        "description": label.get("description"),
    }


def _normalize_issue(issue: dict[str, Any]) -> dict[str, Any]:
    return {
        "number": issue.get("number"),
        "title": issue.get("title"),
        "state": issue.get("state"),
        "html_url": issue.get("html_url"),
        "created_at": issue.get("created_at"),
        "updated_at": issue.get("updated_at"),
        "closed_at": issue.get("closed_at"),
        "comments": issue.get("comments"),
        "labels": [_normalize_label(label) for label in issue.get("labels", [])],
        "user": _normalize_user(issue.get("user")),
        "is_pull_request": "pull_request" in issue,
    }


def _normalize_pull_request(pr: dict[str, Any]) -> dict[str, Any]:
    return {
        "number": pr.get("number"),
        "title": pr.get("title"),
        "state": pr.get("state"),
        "draft": pr.get("draft"),
        "html_url": pr.get("html_url"),
        "created_at": pr.get("created_at"),
        "updated_at": pr.get("updated_at"),
        "closed_at": pr.get("closed_at"),
        "merged_at": pr.get("merged_at"),
        "base": {
            "ref": (pr.get("base") or {}).get("ref"),
            "sha": (pr.get("base") or {}).get("sha"),
        },
        "head": {
            "ref": (pr.get("head") or {}).get("ref"),
            "sha": (pr.get("head") or {}).get("sha"),
        },
        "user": _normalize_user(pr.get("user")),
    }


def get_github_summary() -> dict[str, Any]:
    config = get_github_config()
    repo_path = f"/repos/{config.repository}"

    repo, repo_rate = _github_get(repo_path)
    open_issues_raw, issue_rate = _github_get(
        f"{repo_path}/issues",
        {"state": "open", "per_page": MAX_ITEMS, "sort": "updated", "direction": "desc"},
    )
    open_prs_raw, pr_rate = _github_get(
        f"{repo_path}/pulls",
        {"state": "open", "per_page": MAX_ITEMS, "sort": "updated", "direction": "desc"},
    )
    recent_closed_prs_raw, closed_pr_rate = _github_get(
        f"{repo_path}/pulls",
        {"state": "closed", "per_page": 10, "sort": "updated", "direction": "desc"},
    )

    open_issues = [_normalize_issue(item) for item in open_issues_raw if "pull_request" not in item]
    open_prs = [_normalize_pull_request(item) for item in open_prs_raw]
    recent_closed_prs = [_normalize_pull_request(item) for item in recent_closed_prs_raw]

    return {
        "repository": {
            "full_name": repo.get("full_name"),
            "default_branch": repo.get("default_branch"),
            "html_url": repo.get("html_url"),
            "private": repo.get("private"),
            "updated_at": repo.get("updated_at"),
            "pushed_at": repo.get("pushed_at"),
        },
        "config": {
            "repository": config.repository,
            "token_configured": config.token_configured,
            "max_items": MAX_ITEMS,
        },
        "counts": {
            "open_issues": len(open_issues),
            "open_pull_requests": len(open_prs),
            "draft_pull_requests": sum(1 for pr in open_prs if pr.get("draft")),
            "recent_closed_pull_requests": len(recent_closed_prs),
        },
        "open_issues": open_issues,
        "open_pull_requests": open_prs,
        "recent_closed_pull_requests": recent_closed_prs,
        "rate_limit": {
            "repo": repo_rate,
            "issues": issue_rate,
            "pulls": pr_rate,
            "closed_pulls": closed_pr_rate,
        },
    }
