from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RUNTIME_TRANSCRIPT_DIR = PROJECT_ROOT / "data" / "runtime" / "transcripts"
IMPORT_SCRIPT = PROJECT_ROOT / "scripts" / "import_transcript.py"


def build_parser(default_source_name: str = "") -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Import an agent transcript file into a control tower session"
    )
    parser.add_argument("--session-id", required=True)
    parser.add_argument("--source-name", default=default_source_name)
    parser.add_argument("--project", default="")
    parser.add_argument("--cwd", default="")
    parser.add_argument(
        "--file",
        default="",
        help="Transcript file path. Defaults to data/runtime/transcripts/<session-id>.log",
    )
    return parser


def resolve_transcript_file(session_id: str, explicit_path: str) -> Path:
    if explicit_path:
        return Path(explicit_path)
    return RUNTIME_TRANSCRIPT_DIR / f"{session_id}.log"


def run_import(
    session_id: str,
    source_name: str,
    project: str,
    cwd: str,
    transcript_file: Path,
) -> int:
    if not transcript_file.exists():
        raise SystemExit(f"transcript file not found: {transcript_file}")

    cmd = [
        sys.executable,
        str(IMPORT_SCRIPT),
        "--session-id",
        session_id,
        "--source-name",
        source_name,
        "--project",
        project,
        "--cwd",
        cwd,
        "--file",
        str(transcript_file),
    ]
    return subprocess.call(cmd, cwd=str(PROJECT_ROOT))


def main(default_source_name: str = "") -> None:
    parser = build_parser(default_source_name=default_source_name)
    args = parser.parse_args()
    source_name = args.source_name or default_source_name
    if not source_name:
        raise SystemExit("--source-name is required")

    transcript_file = resolve_transcript_file(args.session_id, args.file)
    raise SystemExit(
        run_import(
            session_id=args.session_id,
            source_name=source_name,
            project=args.project,
            cwd=args.cwd,
            transcript_file=transcript_file,
        )
    )


if __name__ == "__main__":
    main()
