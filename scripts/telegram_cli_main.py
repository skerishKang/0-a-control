import sys
from pathlib import Path
_root = str(Path(__file__).resolve().parents[1])
if _root not in sys.path:
    sys.path.insert(0, _root)

import argparse
import json
from scripts.telegram_cli import (
    init_db,
    list_sources,
    sync_core,
    show_sync_status,
    get_telegram_status,
    import_chat,
    backfill_chat,
    fill_missing_attachments,
    show_attachment_status,
)


def run_cli():
    init_db()
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("list-sources")
    subparsers.add_parser("sync-core")
    subparsers.add_parser("sync-status")
    subparsers.add_parser("telegram-status")

    import_parser = subparsers.add_parser("import-chat")
    import_parser.add_argument("source_id")
    import_parser.add_argument("--limit", type=int, default=200)
    import_parser.add_argument("--max-id", type=int, default=None)
    import_parser.add_argument("--skip-attachments", action="store_true")

    backfill_parser = subparsers.add_parser("backfill-chat")
    backfill_parser.add_argument("source_id")
    backfill_parser.add_argument("--batch-limit", type=int, default=200)
    backfill_parser.add_argument("--max-batches", type=int, default=None)
    backfill_parser.add_argument("--skip-attachments", action="store_true")

    fill_parser = subparsers.add_parser("fill-missing-attachments")
    fill_parser.add_argument("source_id")
    fill_parser.add_argument("--limit", type=int, default=50)
    fill_parser.add_argument("--max-file-size-mb", type=float, default=None)

    attachment_status_parser = subparsers.add_parser("attachment-status")
    attachment_status_parser.add_argument("source_id")
    attachment_status_parser.add_argument("--max-file-size-mb", type=float, default=None)

    args = parser.parse_args()

    if args.command == "list-sources":
        list_sources()
    elif args.command == "sync-core":
        sync_core()
    elif args.command == "sync-status":
        show_sync_status()
    elif args.command == "telegram-status":
        print(json.dumps(get_telegram_status(), ensure_ascii=False, indent=2))
    elif args.command == "import-chat":
        print(
            json.dumps(
                import_chat(
                    args.source_id,
                    limit=args.limit,
                    max_id=args.max_id,
                    download_attachments=not args.skip_attachments,
                ),
                ensure_ascii=False,
                indent=2,
            )
        )
    elif args.command == "backfill-chat":
        print(
            json.dumps(
                backfill_chat(
                    args.source_id,
                    batch_limit=args.batch_limit,
                    max_batches=args.max_batches,
                    download_attachments=not args.skip_attachments,
                ),
                ensure_ascii=False,
                indent=2,
            )
        )
    elif args.command == "fill-missing-attachments":
        print(
            json.dumps(
                fill_missing_attachments(
                    args.source_id,
                    limit=args.limit,
                    show_progress=True,
                    max_file_size_mb=args.max_file_size_mb,
                ),
                ensure_ascii=False,
                indent=2,
            )
        )
    elif args.command == "attachment-status":
        show_attachment_status(args.source_id, args.max_file_size_mb)


if __name__ == "__main__":
    run_cli()
