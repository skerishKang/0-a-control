from __future__ import annotations

import re


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
