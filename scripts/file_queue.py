from __future__ import annotations

from datetime import datetime
from pathlib import Path

from scripts.queue_runtime import file_queue as _impl

ROOT_DIR = _impl.ROOT_DIR
QUEUE_DIR = _impl.QUEUE_DIR
REPORTS_DIR = _impl.REPORTS_DIR
VERDICTS_DIR = _impl.VERDICTS_DIR
PROCESSED_DIR = _impl.PROCESSED_DIR
SAFE_SUFFIXES = _impl.SAFE_SUFFIXES


def _sync_impl_handles() -> None:
    _impl.QUEUE_DIR = QUEUE_DIR
    _impl.REPORTS_DIR = REPORTS_DIR
    _impl.VERDICTS_DIR = VERDICTS_DIR
    _impl.PROCESSED_DIR = PROCESSED_DIR


def get_iso8601_basic(dt: datetime) -> str:
    return _impl.get_iso8601_basic(dt)


def _safe_token(value: str, placeholder: str = "_") -> str:
    return _impl._safe_token(value, placeholder)


def generate_report_id(quest_id: str, session_id: str = "") -> str:
    return _impl.generate_report_id(quest_id, session_id)


def generate_filename(report_id: str, suffix: str) -> str:
    return _impl.generate_filename(report_id, suffix)


def save_json(directory: Path, filename: str, data: dict) -> Path:
    return _impl.save_json(directory, filename, data)


def move_to_processed(file_path: Path):
    _sync_impl_handles()
    return _impl.move_to_processed(file_path)


def move_to_failed(file_path: Path):
    _sync_impl_handles()
    return _impl.move_to_failed(file_path)


def move_to_duplicate(file_path: Path):
    _sync_impl_handles()
    return _impl.move_to_duplicate(file_path)


def move_to_archive_revision(file_path: Path):
    _sync_impl_handles()
    return _impl.move_to_archive_revision(file_path)
