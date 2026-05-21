from __future__ import annotations

from scripts.cli.telegram_cli import *  # noqa: F401,F403
from scripts.cli.telegram_cli import (
    backfill_chat,
    fill_missing_attachments,
    get_core_sources_sync_status,
    get_db,
    get_telegram_status,
    import_chat,
    import_message_ids,
    init_db,
    list_sources,
    run_sync_core,
    show_attachment_status,
    show_sync_status,
    sync_core,
)


if __name__ == "__main__":
    from scripts.cli.telegram_cli_main import run_cli

    run_cli()
