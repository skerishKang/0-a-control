from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

if __package__ is None:
    project_root = Path(__file__).resolve().parents[1]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from scripts.db import append_source_record, end_session, get_resume_context, get_source_records, start_session
else:
    from .db import append_source_record, end_session, get_resume_context, get_source_records, start_session


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Control Tower session helper")
    sub = parser.add_subparsers(dest="command", required=True)

    start = sub.add_parser("start")
    start.add_argument("--agent", required=True)
    start.add_argument("--source-type", required=True)
    start.add_argument("--model", default="")
    start.add_argument("--project", default="")
    start.add_argument("--cwd", default="")
    start.add_argument("--title", default="")
    start.add_argument("--metadata-json", default="")
    start.add_argument("--with-resume-context", action="store_true")
    start.add_argument("--resume-session-limit", type=int, default=3)
    start.add_argument("--resume-turn-limit", type=int, default=6)

    log = sub.add_parser("log")
    log.add_argument("--session-id", required=True)
    log.add_argument("--source-name", required=True)
    log.add_argument("--source-type", required=True)
    log.add_argument("--role", default="user")
    log.add_argument("--project", default="")
    log.add_argument("--cwd", default="")
    log.add_argument("--content", default="")

    end = sub.add_parser("end")
    end.add_argument("--session-id", required=True)
    end.add_argument("--summary", default="")
    end.add_argument("--status", default="closed")
    end.add_argument("--actions", nargs="*", default=[])
    end.add_argument("--files", nargs="*", default=[])

    show = sub.add_parser("show")
    show.add_argument("--session-id", required=True)
    show.add_argument("--limit", type=int, default=50)

    resume = sub.add_parser("resume")
    resume.add_argument("--project", default="")
    resume.add_argument("--cwd", default="")
    resume.add_argument("--title", default="")
    resume.add_argument("--session-id", default="")
    resume.add_argument("--session-limit", type=int, default=3)
    resume.add_argument("--turn-limit", type=int, default=6)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cwd = getattr(args, "cwd", "") or os.getcwd()
    if args.command == "start":
        meta = None
        if args.metadata_json:
            try:
                meta = json.loads(args.metadata_json)
            except Exception as e:
                meta = {"raw_metadata": args.metadata_json, "parse_error": str(e)}

        result = start_session(
            agent_name=args.agent,
            source_type=args.source_type,
            model_name=args.model,
            project_key=args.project,
            working_dir=cwd,
            title=args.title,
            metadata=meta,
            include_resume_context=args.with_resume_context,
            resume_session_limit=args.resume_session_limit,
            resume_turn_limit=args.resume_turn_limit,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    if args.command == "log":
        result = append_source_record(
            session_id=args.session_id,
            source_name=args.source_name,
            source_type=args.source_type,
            content=args.content,
            role=args.role,
            project_key=args.project,
            working_dir=cwd,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    if args.command == "end":
        result = end_session(
            session_id=args.session_id,
            summary_md=args.summary,
            status=args.status,
            files_touched=args.files,
            actions=args.actions,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    if args.command == "show":
        result = get_source_records(args.session_id, args.limit)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    if args.command == "resume":
        result = get_resume_context(
            project_key=args.project,
            working_dir=cwd,
            title=args.title,
            session_id=args.session_id,
            session_limit=args.session_limit,
            turn_limit=args.turn_limit,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
