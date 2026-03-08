from __future__ import annotations

import argparse
import os
import re
from pathlib import Path

from db_sessions import append_source_record
from db_sessions import update_session_summary
from session_summary import summarize_transcript


ANSI_RE = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")


def strip_ansi(text: str) -> str:
    return ANSI_RE.sub("", text)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Import terminal transcript into source_records")
    parser.add_argument("--session-id", required=True)
    parser.add_argument("--source-name", required=True)
    parser.add_argument("--project", default="")
    parser.add_argument("--cwd", default="")
    parser.add_argument("--file", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    transcript_path = Path(args.file)
    if not transcript_path.exists():
        raise SystemExit(f"transcript file not found: {transcript_path}")

    raw = transcript_path.read_text(errors="replace")
    content = strip_ansi(raw).strip()
    if not content:
      raise SystemExit(0)

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
        },
    )
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
