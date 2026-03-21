from __future__ import annotations

import argparse
import os
import re
from pathlib import Path

from db_sessions import append_source_record, update_session_summary
from session_summary import clean_transcript_content, infer_transcript_profile, strip_ansi, summarize_transcript


USER_RE = re.compile(r"^(?:> |(?:You|User|Human|사용자):\s*)", re.IGNORECASE)
ASSISTANT_RE = re.compile(
    r"^(?:(?:Codex|Gemini|Assistant|AI|Response|Bot|Windsurf):\s*|[-*]\s)",
    re.IGNORECASE,
)
TOOL_RE = re.compile(
    r"^(?:(?:Tool|System|Executing|Error|Warning|Info):\s*|\$\s+|\[\d{4}-\d{2}-\d{2}|Script started on|Script done on)",
    re.IGNORECASE,
)

NOISE_RE = re.compile(
    r"^(?:Tip:|model:\s|directory:\s|gpt-[\w.-]+|OpenAI Codex|Token usage:|To continue this session, run codex resume)",
    re.IGNORECASE,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Import terminal transcript into source_records")
    parser.add_argument("--session-id", required=True)
    parser.add_argument("--source-name", required=True)
    parser.add_argument("--project", default="")
    parser.add_argument("--cwd", default="")
    parser.add_argument("--file", required=True)
    return parser.parse_args()


def normalize_line(line: str) -> str:
    line = line.replace("\ufeff", "").rstrip()
    line = re.sub(r"\s+", " ", line).strip()
    return line


def is_noise_line(line: str) -> bool:
    if not line:
        return True
    if NOISE_RE.match(line):
        return True
    return False


def chunk_transcript(content: str, profile: str = "default") -> list[dict[str, str]]:
    chunks: list[dict[str, str]] = []
    current_role = "tool"
    current_lines: list[str] = []

    for raw_line in clean_transcript_content(content, profile=profile).splitlines():
        line = normalize_line(raw_line)
        if is_noise_line(line):
            continue

        if USER_RE.match(line):
            if current_lines:
                chunks.append({"role": current_role, "text": "\n".join(current_lines)})
                current_lines = []
            current_role = "user"
            current_lines.append(line)
        elif ASSISTANT_RE.match(line):
            if current_lines:
                chunks.append({"role": current_role, "text": "\n".join(current_lines)})
                current_lines = []
            current_role = "assistant"
            current_lines.append(line)
        elif TOOL_RE.match(line):
            if current_lines:
                chunks.append({"role": current_role, "text": "\n".join(current_lines)})
                current_lines = []
            current_role = "tool"
            current_lines.append(line)
        else:
            current_lines.append(line)

    if current_lines:
        chunks.append({"role": current_role, "text": "\n".join(current_lines)})

    filtered: list[dict[str, str]] = []
    for chunk in chunks:
        text = chunk["text"].strip()
        if not text:
            continue
        if text in {"Working", "Explored"}:
            continue
        filtered.append({"role": chunk["role"], "text": text})
    return filtered


def main() -> None:
    args = parse_args()
    transcript_path = Path(args.file)
    if not transcript_path.exists():
        raise SystemExit(f"transcript file not found: {transcript_path}")

    raw = transcript_path.read_text(errors="replace")
    content = strip_ansi(raw).strip()
    if not content:
        raise SystemExit(0)
    profile = infer_transcript_profile(source_name=args.source_name)

    append_source_record(
        session_id=args.session_id,
        source_name=args.source_name,
        source_type="terminal_transcript",
        content=content,
        role="tool",
        project_key=args.project,
        working_dir=args.cwd,
        metadata={
            "transcript_path": str(transcript_path),
            "bytes": os.path.getsize(transcript_path),
            "parse_type": "raw_dump",
            "transcript_profile": profile,
        },
    )

    chunks = chunk_transcript(content, profile=profile)
    for i, chunk in enumerate(chunks):
        text = chunk["text"].strip()
        if not text:
            continue
        append_source_record(
            session_id=args.session_id,
            source_name=args.source_name,
            source_type="agent_turn",
            content=text,
            role=chunk["role"],
            project_key=args.project,
            working_dir=args.cwd,
            metadata={
                "chunk_index": i,
                "total_chunks": len(chunks),
            },
        )

    update_session_summary(
        session_id=args.session_id,
        summary_md=summarize_transcript(content, project_key=args.project, profile=profile),
        metadata={
            "summary_source": "terminal_transcript",
            "transcript_path": str(transcript_path),
            "transcript_profile": profile,
        },
    )


if __name__ == "__main__":
    main()
