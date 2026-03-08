from __future__ import annotations

import re


TRANSCRIPT_META_PATTERNS = (
    re.compile(r"^Script started on\b", re.IGNORECASE),
    re.compile(r"^Script done on\b", re.IGNORECASE),
)


def _clean_lines(content: str) -> list[str]:
    lines: list[str] = []
    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if any(pattern.match(line) for pattern in TRANSCRIPT_META_PATTERNS):
            continue
        lines.append(line)
    return lines


def summarize_transcript(content: str, title: str = "", project_key: str = "") -> str:
    lines = _clean_lines(content)
    if not lines:
        return title or (f"{project_key} 작업 세션" if project_key else "작업 세션")

    unique_lines: list[str] = []
    seen = set()
    for line in lines:
        if line in seen:
            continue
        seen.add(line)
        unique_lines.append(line)
        if len(unique_lines) >= 3:
            break

    summary = " / ".join(unique_lines)
    if len(summary) > 220:
        summary = summary[:217].rstrip() + "..."
    return summary
