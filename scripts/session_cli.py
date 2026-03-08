from __future__ import annotations

import argparse
import json
import os

from db import append_source_record, end_session, get_source_records, start_session


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
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cwd = getattr(args, "cwd", "") or os.getcwd()
    if args.command == "start":
        result = start_session(
            agent_name=args.agent,
            source_type=args.source_type,
            model_name=args.model,
            project_key=args.project,
            working_dir=cwd,
            title=args.title,
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


if __name__ == "__main__":
    main()
