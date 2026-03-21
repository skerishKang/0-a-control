from __future__ import annotations

import re
from typing import Any


ANSI_ESCAPE_RE = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
LITERAL_ESCAPE_RE = re.compile(r"\\x1b\[[0-9;?]*[ -/]*[@-~]", re.IGNORECASE)

TRANSCRIPT_META_PATTERNS = (
    re.compile(r"^Script started on\b", re.IGNORECASE),
    re.compile(r"^Script done on\b", re.IGNORECASE),
)

COMMON_NOISE_PATTERNS = (
    re.compile(r"^\s*Conversation interrupted\b", re.IGNORECASE),
    re.compile(r"^Something went wrong", re.IGNORECASE),
    re.compile(r"^Hit `/feedback` to report\b", re.IGNORECASE),
    re.compile(r"^Tip:\s*(?:NEW|New):", re.IGNORECASE),
    re.compile(r"^Enable in /experimental and restart Codex!?$", re.IGNORECASE),
    re.compile(r"^계속하려면 아무 키나 누르십시오", re.IGNORECASE),
    re.compile(r"\bgpt-[\w.]+\s+\w+\s+[·•]\s+\d+%\s+left", re.IGNORECASE),
    re.compile(r"^Token usage:\s*", re.IGNORECASE),
)

CODEX_NOISE_PATTERNS = (
    re.compile(r"^OpenAI Codex\b", re.IGNORECASE),
    re.compile(r"^model:\s*", re.IGNORECASE),
    re.compile(r"^directory:\s*", re.IGNORECASE),
    re.compile(r"^To continue this session, run codex resume\b", re.IGNORECASE),
)

GEMINI_NOISE_PATTERNS = (
    re.compile(r"^Usage:\s*gemini\b", re.IGNORECASE),
    re.compile(r"^Gemini CLI\b", re.IGNORECASE),
    re.compile(r"^Commands:\s*$", re.IGNORECASE),
    re.compile(r"^Options:\s*$", re.IGNORECASE),
    re.compile(r"^\s+gemini\s", re.IGNORECASE),
)

WINDSURF_NOISE_PATTERNS = (
    re.compile(r"^Windsurf\b", re.IGNORECASE),
    re.compile(r"^Cascade\b", re.IGNORECASE),
    re.compile(r"^Continue with\b", re.IGNORECASE),
)

ACTION_PREFIXES = ("- ", "* ", "• ", "1. ", "2. ", "3. ")
DECISION_PATTERNS = (
    "완료",
    "종료",
    "결정",
    "정리",
    "done",
    "complete",
    "completed",
    "finished",
    "ended",
    "updated",
    "created",
    "fixed",
)
NEXT_PATTERNS = (
    "다음",
    "next",
    "continue",
    "restart",
    "resume",
    "follow-up",
)


def strip_ansi(content: str) -> str:
    cleaned = ANSI_ESCAPE_RE.sub("", content or "")
    cleaned = LITERAL_ESCAPE_RE.sub("", cleaned)
    cleaned = cleaned.replace("\r", "\n")
    cleaned = re.sub(r"[\x00-\x08\x0b-\x1f\x7f]", "", cleaned)
    return cleaned


def _looks_like_terminal_frame(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    frame_chars = set("╭╮╰╯│─┌┐└┘")
    return len(stripped) >= 3 and all(ch in frame_chars for ch in stripped)


def _get_noise_patterns(profile: str) -> tuple[re.Pattern[str], ...]:
    if profile == "codex":
        return COMMON_NOISE_PATTERNS + CODEX_NOISE_PATTERNS
    if profile == "gemini-cli":
        return COMMON_NOISE_PATTERNS + GEMINI_NOISE_PATTERNS
    if profile == "windsurf":
        return COMMON_NOISE_PATTERNS + WINDSURF_NOISE_PATTERNS
    return COMMON_NOISE_PATTERNS


def infer_transcript_profile(agent_name: str = "", source_name: str = "") -> str:
    value = f"{agent_name} {source_name}".lower()
    if "codex" in value:
        return "codex"
    if "gemini" in value:
        return "gemini-cli"
    if "windsurf" in value:
        return "windsurf"
    return "default"


def clean_transcript_content(content: str, profile: str = "default") -> str:
    cleaned_lines: list[str] = []
    skip_bootstrap = False
    noise_patterns = _get_noise_patterns(profile)

    for raw_line in strip_ansi(content).splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()

        if not stripped:
            cleaned_lines.append("")
            continue

        if profile == "codex" and "You are starting inside the 0-a-control workspace." in stripped:
            skip_bootstrap = True
            continue
        if skip_bootstrap:
            if "Keep that first reply to 1-3 short sentences." in stripped:
                skip_bootstrap = False
            continue

        if _looks_like_terminal_frame(stripped):
            continue
        if any(pattern.match(stripped) for pattern in TRANSCRIPT_META_PATTERNS):
            continue
        if any(pattern.search(stripped) for pattern in noise_patterns):
            continue
        if stripped in {"Working", "Explored"}:
            continue

        cleaned_lines.append(line)

    compacted: list[str] = []
    blank_run = 0
    for line in cleaned_lines:
        if not line.strip():
            blank_run += 1
            if blank_run > 1:
                continue
        else:
            blank_run = 0
        compacted.append(line)

    return "\n".join(compacted).strip()


def _clean_lines(content: str, profile: str = "default") -> list[str]:
    return [line.strip() for line in clean_transcript_content(content, profile=profile).splitlines() if line.strip()]


def summarize_transcript(
    content: str,
    title: str = "",
    project_key: str = "",
    profile: str = "default",
) -> str:
    lines = _clean_lines(content, profile=profile)
    if not lines:
        return title or (f"{project_key} 작업 세션" if project_key else "작업 세션")

    unique_lines: list[str] = []
    seen = set()
    for line in reversed(lines):
        if line in seen or len(line) < 4:
            continue
        seen.add(line)
        unique_lines.insert(0, line)
        if len(unique_lines) >= 3:
            break

    if not unique_lines and lines:
        unique_lines = lines[-1:]

    summary = " / ".join(unique_lines)
    if len(summary) > 220:
        summary = summary[:217].rstrip() + "..."
    return summary


def _dedupe(items: list[str], limit: int) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        normalized = item.strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        result.append(normalized)
        if len(result) >= limit:
            break
    return result


def parse_summary_md(summary_md: str) -> dict[str, Any]:
    text = (summary_md or "").strip()
    if not text:
        return {
            "raw": "",
            "intent": "",
            "actions": [],
            "decisions": [],
            "next_start": [],
            "has_structured_content": False,
        }

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    intent = lines[0] if lines else ""
    actions: list[str] = []
    decisions: list[str] = []
    next_start: list[str] = []

    for line in lines[1:]:
        lowered = line.lower()
        if any(token in lowered for token in NEXT_PATTERNS):
            next_start.append(line)
            continue
        if any(token in lowered for token in DECISION_PATTERNS):
            decisions.append(line)
            continue
        if any(line.startswith(prefix) for prefix in ACTION_PREFIXES):
            actions.append(line)
            continue
        if len(line) > 8:
            actions.append(line)

    return {
        "raw": text,
        "intent": intent,
        "actions": _dedupe(actions, 5),
        "decisions": _dedupe(decisions, 3),
        "next_start": _dedupe(next_start, 3),
        "has_structured_content": bool(actions or decisions or next_start),
    }


def build_session_badges(summary_md: str) -> dict[str, str]:
    summary = summary_md or ""
    content_length = len(summary)

    length_badge = "short"
    length_color = "#999999"
    if content_length >= 1500:
        length_badge = "medium"
        length_color = "#f39c12"
    if content_length >= 2500:
        length_badge = "long"
        length_color = "#27ae60"

    lowered = summary.lower()
    value_badge = "empty"
    value_label = "비어있음"
    value_color = "#e74c3c"

    if any(token in lowered for token in ("완료", "종료", "결정", "done", "complete", "ended")):
        value_badge = "decisions"
        value_label = "결정"
        value_color = "#27ae60"
    elif any(token in lowered for token in ("다음", "next", "continue", "resume")):
        value_badge = "next-action"
        value_label = "다음"
        value_color = "#3498db"
    elif any(summary.startswith(prefix) or f"\n{prefix}" in summary for prefix in ACTION_PREFIXES):
        value_badge = "actions"
        value_label = "행동"
        value_color = "#9b59b6"
    elif content_length > 30:
        value_badge = "transcript-only"
        value_label = "기록"
        value_color = "#f39c12"

    return {
        "length_badge": length_badge,
        "length_color": length_color,
        "value_badge": value_badge,
        "value_label": value_label,
        "value_color": value_color,
    }
