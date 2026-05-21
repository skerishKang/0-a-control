"""Compatibility wrapper for validation checklist runtime storage and API."""

from __future__ import annotations

try:
    from scripts.services import validation_checklist as _impl
except ModuleNotFoundError:
    from services import validation_checklist as _impl

STORAGE_REL = _impl.STORAGE_REL
STANDARD_ITEMS = _impl.STANDARD_ITEMS


def _storage_path():
    return _impl._storage_path()


def _sync_test_hooks() -> None:
    _impl._storage_path = _storage_path


def _read_all():
    _sync_test_hooks()
    return _impl._read_all()


def _write_all(data):
    _sync_test_hooks()
    return _impl._write_all(data)


def _now_iso():
    return _impl._now_iso()


def _build_items(required_keys):
    return _impl._build_items(required_keys)


def recompute_overall_status(checklist):
    return _impl.recompute_overall_status(checklist)


def create_checklist(body):
    _sync_test_hooks()
    return _impl.create_checklist(body)


def list_checklists():
    _sync_test_hooks()
    return _impl.list_checklists()


def get_checklist(checklist_id):
    _sync_test_hooks()
    return _impl.get_checklist(checklist_id)


def update_result_item(checklist_id, item_key, body):
    _sync_test_hooks()
    return _impl.update_result_item(checklist_id, item_key, body)
