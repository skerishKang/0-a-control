from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AgentSpec:
    canonical_name: str
    aliases: tuple[str, ...]
    executable: str
    label: str


AGENT_SPECS: tuple[AgentSpec, ...] = (
    AgentSpec("codex", ("codex",), "codex", "Codex"),
    AgentSpec("gemini-cli", ("gemini", "gemini-cli"), "gemini", "Gemini CLI"),
    AgentSpec("antigravity", ("antigravity",), os.environ.get("ANTIGRAVITY_BIN", "antigravity"), "Antigravity"),
    AgentSpec("windsurf", ("windsurf",), os.environ.get("WINDSURF_BIN", "windsurf"), "Windsurf"),
    AgentSpec("kilo", ("kilo", "kilocode"), os.environ.get("KILO_BIN", "kilo"), "Kilo"),
    AgentSpec("opencode", ("opencode", "open-code"), os.environ.get("OPENCODE_BIN", "opencode"), "OpenCode"),
)

CANONICAL_AGENTS = {
    alias: spec.canonical_name
    for spec in AGENT_SPECS
    for alias in spec.aliases
}

EXECUTABLES = {spec.canonical_name: spec.executable for spec in AGENT_SPECS}
SPEC_BY_NAME = {spec.canonical_name: spec for spec in AGENT_SPECS}


def canonical_agent_name(name: str) -> str:
    raw = (name or "").strip().lower()
    lowered = Path(raw).name if raw else ""
    return CANONICAL_AGENTS.get(lowered, lowered or "unknown-agent")


def resolve_executable(name: str) -> str:
    canonical = canonical_agent_name(name)
    return EXECUTABLES.get(canonical, canonical)


def get_agent_spec(name: str) -> AgentSpec | None:
    canonical = canonical_agent_name(name)
    return SPEC_BY_NAME.get(canonical)


def list_registered_agents() -> list[dict]:
    items: list[dict] = []
    for spec in AGENT_SPECS:
        resolved = shutil.which(spec.executable)
        items.append(
            {
                "canonical_name": spec.canonical_name,
                "label": spec.label,
                "aliases": list(spec.aliases),
                "executable": spec.executable,
                "resolved_path": resolved,
                "available": bool(resolved),
            }
        )
    return items


def get_agent_statuses() -> list[dict]:
    try:
        if __package__ in (None, ""):
            from scripts.db_base import connect
        else:
            from .db_base import connect
    except Exception:
        connect = None

    latest_sessions: dict[str, dict] = {}
    if connect is not None:
        with connect() as conn:
            rows = conn.execute(
                """
                SELECT s1.agent_name, s1.id, s1.status, s1.title, s1.started_at, s1.ended_at, s1.model_name
                FROM sessions s1
                INNER JOIN (
                    SELECT agent_name, MAX(started_at) AS max_started_at
                    FROM sessions
                    GROUP BY agent_name
                ) s2
                  ON s1.agent_name = s2.agent_name
                 AND s1.started_at = s2.max_started_at
                """
            ).fetchall()
            for row in rows:
                latest_sessions[row["agent_name"]] = dict(row)

    items: list[dict] = []
    for agent in list_registered_agents():
        canonical = agent["canonical_name"]
        latest = latest_sessions.get(canonical)
        status = "idle"
        if not agent["available"]:
            status = "unavailable"
        elif latest:
            latest_status = (latest.get("status") or "").lower()
            if latest_status == "active":
                status = "working"
            elif latest_status in {"error", "failed"}:
                status = "error"

        items.append(
            {
                **agent,
                "status": status,
                "last_session": latest,
            }
        )

    return items
