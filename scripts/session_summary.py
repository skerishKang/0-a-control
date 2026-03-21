from __future__ import annotations

import re
from typing import Any


TRANSCRIPT_META_PATTERNS = (
    re.compile(r"^Script started on\b", re.IGNORECASE),
    re.compile(r"^Script done on\b", re.IGNORECASE),
)

NOISE_PATTERNS = (
    re.compile(r"^■ Conversation interrupted\b", re.IGNORECASE),
    re.compile(r"^Something went wrong\?", re.IGNORECASE),
    re.compile(r"^Hit `/feedback` to report\b", re.IGNORECASE),
    re.compile(r"^Tip:\s*NEW:\s*Use ChatGPT Apps\b", re.IGNORECASE),
    re.compile(r"^Enable in /experimental and restart Codex!?$", re.IGNORECASE),
    re.compile(r"^계속하려면 아무 키나 누르십시오", re.IGNORECASE),
    re.compile(r"\bgpt-[\w.]+\s+medium\s+·\s+\d+%\s+left\s+·", re.IGNORECASE),
)


def _clean_lines(content: str) -> list[str]:
    lines: list[str] = []
    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if any(pattern.match(line) for pattern in TRANSCRIPT_META_PATTERNS):
            continue
        if any(pattern.search(line) for pattern in NOISE_PATTERNS):
            continue
        lines.append(line)
    return lines


def summarize_transcript(content: str, title: str = "", project_key: str = "") -> str:
    lines = _clean_lines(content)
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

    actions = _dedupe(actions, 5)
    decisions = _dedupe(decisions, 3)
    next_start = _dedupe(next_start, 3)

    return {
        "raw": text,
        "intent": intent,
        "actions": actions,
        "decisions": decisions,
        "next_start": next_start,
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
