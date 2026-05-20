from __future__ import annotations

from pathlib import Path
from typing import Any

from scripts.queue_runtime import verdict_import as _impl

REPORTS_DIR = _impl.REPORTS_DIR
VERDICTS_DIR = _impl.VERDICTS_DIR
PLAN_BUCKETS = _impl.PLAN_BUCKETS
DuplicateVerdict = _impl.DuplicateVerdict
apply_verdict = _impl.apply_verdict
clear_current_state_cache = _impl.clear_current_state_cache
move_to_processed = _impl.move_to_processed
move_to_failed = _impl.move_to_failed
move_to_duplicate = _impl.move_to_duplicate
move_to_archive_revision = _impl.move_to_archive_revision


def _sync_impl_handles() -> None:
    _impl.REPORTS_DIR = REPORTS_DIR
    _impl.VERDICTS_DIR = VERDICTS_DIR
    _impl.apply_verdict = apply_verdict
    _impl.clear_current_state_cache = clear_current_state_cache
    _impl.move_to_processed = move_to_processed
    _impl.move_to_failed = move_to_failed
    _impl.move_to_duplicate = move_to_duplicate
    _impl.move_to_archive_revision = move_to_archive_revision


def _read_json(path: Path) -> dict[str, Any]:
    return _impl._read_json(path)


def _load_report_payload(report_ref: str) -> dict[str, Any] | None:
    _sync_impl_handles()
    return _impl._load_report_payload(report_ref)


def _merge_correlations(*payloads: dict[str, Any] | None) -> dict[str, Any]:
    return _impl._merge_correlations(*payloads)


def _first_non_empty(*candidates: Any) -> str:
    return _impl._first_non_empty(*candidates)


def _resolve_quest_id(verdict_data: dict[str, Any], report_payload: dict[str, Any] | None) -> str:
    return _impl._resolve_quest_id(verdict_data, report_payload)


def _resolve_session_id(verdict_data: dict[str, Any], report_payload: dict[str, Any] | None) -> str:
    return _impl._resolve_session_id(verdict_data, report_payload)


def _extract_plan_links(verdict_data: dict[str, Any], report_payload: dict[str, Any] | None) -> list[dict[str, Any]]:
    return _impl._extract_plan_links(verdict_data, report_payload)


def _extract_attachments(verdict_data: dict[str, Any], report_payload: dict[str, Any] | None) -> list[dict[str, Any]]:
    return _impl._extract_attachments(verdict_data, report_payload)


def _normalize_plan_impact(raw: Any) -> dict[str, str]:
    return _impl._normalize_plan_impact(raw)


def _validate_required_fields(
    report_ref: str,
    quest_id: str,
    plan_impact: dict[str, str],
    has_raw_plan_impact: bool,
) -> None:
    return _impl._validate_required_fields(report_ref, quest_id, plan_impact, has_raw_plan_impact)


def import_verdicts() -> None:
    _sync_impl_handles()
    return _impl.import_verdicts()


if __name__ == "__main__":
    import_verdicts()
