from __future__ import annotations

import os
import shutil
import subprocess
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


def _agent_match_tokens(spec: AgentSpec) -> set[str]:
    tokens = {spec.canonical_name.lower(), spec.executable.lower(), Path(spec.executable).name.lower()}
    tokens.update(alias.lower() for alias in spec.aliases)
    return {token for token in tokens if token}


def get_running_agent_names() -> set[str]:
    if os.name != "nt":
        return set()

    command = (
        "Get-CimInstance Win32_Process | "
        "Select-Object Name,CommandLine | "
        "ConvertTo-Json -Compress"
    )

    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", command],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=10,
            check=True,
        )
    except Exception:
        return set()

    raw = (result.stdout or "").strip()
    if not raw:
        return set()

    try:
        import json

        records = json.loads(raw)
    except Exception:
        return set()

    if isinstance(records, dict):
        records = [records]

    running: set[str] = set()
    for spec in AGENT_SPECS:
        match_tokens = _agent_match_tokens(spec)
        for record in records:
            name = str(record.get("Name") or "").lower()
            commandline = str(record.get("CommandLine") or "").lower()
            haystack = f"{name} {commandline}"
            if any(token in haystack for token in match_tokens):
                running.add(spec.canonical_name)
                break

    return running


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

    running_agents = get_running_agent_names()
    items: list[dict] = []
    for agent in list_registered_agents():
        canonical = agent["canonical_name"]
        latest = latest_sessions.get(canonical)
        status = "idle"
        has_stale_session = False
        if not agent["available"]:
            status = "unavailable"
        elif canonical in running_agents:
            status = "working"
        elif latest:
            latest_status = (latest.get("status") or "").lower()
            if latest_status in {"error", "failed"}:
                status = "error"
            elif latest_status == "active":
                status = "stale"
                has_stale_session = True

        items.append(
            {
                **agent,
                "status": status,
                "process_running": canonical in running_agents,
                "has_stale_session": has_stale_session,
                "last_session": latest,
            }
        )

    return items
