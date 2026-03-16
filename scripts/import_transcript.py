from __future__ import annotations

import argparse
import os
import re
from pathlib import Path

from db_sessions import append_source_record, update_session_summary
from session_summary import summarize_transcript

ANSI_CSI_RE = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")
ANSI_OSC_RE = re.compile(r"\x1B\][^\x07\x1B]*(?:\x07|\x1B\\)")

# Common Prompts for heuristic splitting
USER_RE = re.compile(r"^(?:> |› |(?:You|User|Human):\s*)", re.IGNORECASE)
ASSISTANT_RE = re.compile(
    r"^(?:(?:Codex|Gemini|Assistant|AI|Response|Bot):\s*|•\s|[-*]\s)",
    re.IGNORECASE,
)
TOOL_RE = re.compile(
    r"^(?:(?:Tool|System|Executing|Error|Warning|Info):\s*|\$\s+|\[\d{4}-\d{2}-\d{2}|Script started on|Windows PowerShell 기록)",
    re.IGNORECASE,
)

NOISE_RE = re.compile(
    r"^(?:Tip:|model:\s|directory:\s|gpt-[\w.-]+|OpenAI Codex|Windows PowerShell 기록|PSVersion:|Host Application:|호스트 응용 프로그램:)",
    re.IGNORECASE,
)

def strip_ansi(text: str) -> str:
    text = ANSI_OSC_RE.sub("", text)
    text = ANSI_CSI_RE.sub("", text)
    text = text.replace("\r", "\n")
    text = re.sub(r"(?<!\n)([›•])\s", r"\n\1 ", text)
    text = re.sub(r"(?<!\n)(Script started on)", r"\n\1", text)
    text = re.sub(r"(?<!\n)(Script done on)", r"\n\1", text)
    return text


def normalize_line(line: str) -> str:
    line = line.replace("\ufeff", "").rstrip()
    line = re.sub(r"\s+", " ", line).strip()
    return line


def is_noise_line(line: str) -> bool:
    if not line:
        return True
    if NOISE_RE.match(line):
        return True
    if len(line) >= 20 and set(line) <= {"─", "│", "╭", "╮", "╰", "╯", " "}:
        return True
    return False

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Import terminal transcript into source_records")
    parser.add_argument("--session-id", required=True)
    parser.add_argument("--source-name", required=True)
    parser.add_argument("--project", default="")
    parser.add_argument("--cwd", default="")
    parser.add_argument("--file", required=True)
    return parser.parse_args()

def chunk_transcript(content: str) -> list[dict[str, str]]:
    chunks = []
    current_role = "tool"  # default fallback
    current_lines = []

    for raw_line in content.splitlines():
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
    # Drop low-signal chunks that are just transcript scaffolding.
    filtered = []
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

    # 1. Save the entire original transcript as a single immutable tool record
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
            "parse_type": "raw_dump"
        },
    )

    # 2. Chunk by roles and save sequentially
    chunks = chunk_transcript(content)
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
                "total_chunks": len(chunks)
            },
        )

    # 3. Update the summary
    update_session_summary(
        session_id=args.session_id,
        summary_md=summarize_transcript(content, project_key=args.project),
        metadata={
            "summary_source": "terminal_transcript",
            "transcript_path": str(transcript_path),
        },
    )

if __name__ == "__main__":
    main()
