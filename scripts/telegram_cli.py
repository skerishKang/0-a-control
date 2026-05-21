from __future__ import annotations

from scripts.cli import telegram_cli as _impl
from scripts.cli.telegram_cli import *  # noqa: F401,F403
from scripts.cli.telegram_cli import (
    TelegramSessionBusyError,
    fetch_messages,
    get_telegram_session_lock_status,
    get_telegram_status,
    init_db,
)


def _sync_patchable_dependencies() -> None:
    _impl.fetch_messages = fetch_messages


def get_db():
    return _impl.get_db()


def get_core_sources_sync_status() -> list[dict]:
    return _impl.get_core_sources_sync_status()


def run_sync_core() -> dict:
    _sync_patchable_dependencies()
    return _impl.run_sync_core()


def list_sources():
    return _impl.list_sources()


def sync_core():
    _sync_patchable_dependencies()
    return _impl.sync_core()


def show_sync_status():
    return _impl.show_sync_status()


def import_chat(*args, **kwargs):
    _sync_patchable_dependencies()
    return _impl.import_chat(*args, **kwargs)


def backfill_chat(*args, **kwargs):
    _sync_patchable_dependencies()
    return _impl.backfill_chat(*args, **kwargs)


def fill_missing_attachments(*args, **kwargs):
    _sync_patchable_dependencies()
    return _impl.fill_missing_attachments(*args, **kwargs)


def import_message_ids(*args, **kwargs):
    _sync_patchable_dependencies()
    return _impl.import_message_ids(*args, **kwargs)


def show_attachment_status(*args, **kwargs):
    return _impl.show_attachment_status(*args, **kwargs)


if __name__ == "__main__":
    from scripts.cli.telegram_cli_main import run_cli

    run_cli()
