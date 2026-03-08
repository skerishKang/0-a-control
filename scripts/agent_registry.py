from __future__ import annotations

import os
from pathlib import Path


CANONICAL_AGENTS = {
    "codex": "codex",
    "gemini": "gemini-cli",
    "gemini-cli": "gemini-cli",
    "antigravity": "antigravity",
    "windsurf": "windsurf",
    "kilo": "kilo",
    "kilocode": "kilo",
    "opencode": "opencode",
    "open-code": "opencode",
}


EXECUTABLES = {
    "codex": "codex",
    "gemini-cli": "gemini",
    "antigravity": os.environ.get("ANTIGRAVITY_BIN", "antigravity"),
    "windsurf": os.environ.get("WINDSURF_BIN", "windsurf"),
    "kilo": os.environ.get("KILO_BIN", "kilo"),
    "opencode": os.environ.get("OPENCODE_BIN", "opencode"),
}


def canonical_agent_name(name: str) -> str:
    raw = (name or "").strip().lower()
    lowered = Path(raw).name if raw else ""
    return CANONICAL_AGENTS.get(lowered, lowered or "unknown-agent")


def resolve_executable(name: str) -> str:
    canonical = canonical_agent_name(name)
    return EXECUTABLES.get(canonical, canonical)
