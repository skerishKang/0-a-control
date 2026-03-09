from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from .db_ops import apply_verdict, DuplicateVerdict
from .file_queue import (
    REPORTS_DIR,
    VERDICTS_DIR,
    move_to_processed,
    move_to_failed,
    move_to_duplicate,
    move_to_archive_revision,
)

logger = logging.getLogger("verdict_import")

PLAN_BUCKETS = ("today", "short_term", "long_term", "recurring", "dated")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_report_payload(report_ref: str) -> dict[str, Any] | None:
    if not report_ref:
        return None
    report_path = REPORTS_DIR / f"{report_ref}.report.json"
    if not report_path.exists():
        return None
    try:
        return _read_json(report_path)
    except json.JSONDecodeError:
        logger.warning("Report JSON 손상: %s", report_path)
        return None


def _merge_correlations(*payloads: dict[str, Any] | None) -> dict[str, Any]:
    merged: dict[str, Any] = {}
    for payload in payloads:
        if not payload:
            continue
        correlation = payload.get("correlation") or {}
        for key, value in correlation.items():
            if value:
                merged[key] = value
    return merged


def _first_non_empty(*candidates: Any) -> str:
    for candidate in candidates:
        if isinstance(candidate, str) and candidate.strip():
            return candidate.strip()
    return ""


def _resolve_quest_id(verdict_data: dict[str, Any], report_payload: dict[str, Any] | None) -> str:
    quest_id = _first_non_empty(
        verdict_data.get("quest_id"),
        verdict_data.get("report", {}).get("quest_id"),
        (verdict_data.get("correlation") or {}).get("quest_id"),
        (verdict_data.get("metadata") or {}).get("quest_id"),
        report_payload.get("quest_id") if report_payload else "",
        (report_payload or {}).get("report", {}).get("quest_id") if report_payload else "",
        (report_payload or {}).get("correlation", {}).get("quest_id") if report_payload else "",
    )
    if not quest_id:
        raise ValueError("quest_id를 verdict JSON에서 찾지 못했습니다.")
    return quest_id


def _resolve_session_id(verdict_data: dict[str, Any], report_payload: dict[str, Any] | None) -> str:
    return _first_non_empty(
        verdict_data.get("session_id"),
        (verdict_data.get("correlation") or {}).get("session_id"),
        (report_payload or {}).get("session_id") if report_payload else "",
        (report_payload or {}).get("correlation", {}).get("session_id") if report_payload else "",
    )


def _extract_plan_links(verdict_data: dict[str, Any], report_payload: dict[str, Any] | None) -> list[dict[str, Any]]:
    plan_links = verdict_data.get("plan_links") or verdict_data.get("report", {}).get("plan_links") or []
    if not plan_links and report_payload:
        plan_links = report_payload.get("report", {}).get("plan_links") or []
    return plan_links


def _extract_attachments(verdict_data: dict[str, Any], report_payload: dict[str, Any] | None) -> list[dict[str, Any]]:
    attachments = verdict_data.get("attachments") or verdict_data.get("report", {}).get("attachments") or []
    if not attachments and report_payload:
        attachments = report_payload.get("report", {}).get("attachments") or []
    return attachments


def _normalize_plan_impact(raw: Any) -> dict[str, str]:
    impact = {bucket: "--" for bucket in PLAN_BUCKETS}
    if isinstance(raw, dict):
        for bucket, value in raw.items():
            if bucket in impact and value:
                impact[bucket] = str(value)
    elif isinstance(raw, str) and raw.strip():
        impact["today"] = raw.strip()
    return impact


def _validate_required_fields(
    report_ref: str,
    quest_id: str,
    plan_impact: dict[str, str],
    has_raw_plan_impact: bool,
) -> None:
    if not report_ref:
        raise ValueError("report_ref 누락")
    if not quest_id:
        raise ValueError("quest_id 누락")
    if not has_raw_plan_impact:
        raise ValueError("plan_impact 누락")
    for bucket in PLAN_BUCKETS:
        if bucket not in plan_impact:
            raise ValueError("plan_impact 키 누락")


def import_verdicts() -> None:
    if not VERDICTS_DIR.exists():
        return

    for file_path in VERDICTS_DIR.glob("*.json"):
        if not file_path.is_file():
            continue

        try:
            data = _read_json(file_path)
        except json.JSONDecodeError as exc:
            logger.error("JSON 파싱 실패: %s (%s)", file_path.name, exc)
            move_to_failed(file_path)
            continue

        report_ref = _first_non_empty(
            data.get("report_ref"),
            data.get("report_id"),
            (data.get("metadata") or {}).get("report_ref"),
        )

        report_payload = _load_report_payload(report_ref)
        verdict_group = data.get("verdict", {})
        judge_group = data.get("judge", {})

        try:
            quest_id = _resolve_quest_id(data, report_payload)
        except ValueError as exc:
            logger.error("%s: %s", file_path.name, exc)
            move_to_failed(file_path)
            continue

        verdict_status = verdict_group.get("status", data.get("verdict", ""))
        reason = verdict_group.get("reason", data.get("reason", ""))
        restart_point = verdict_group.get("restart_point", data.get("restart_point", ""))
        next_hint = verdict_group.get("next_hint", data.get("next_hint", ""))
        raw_plan_impact = verdict_group.get("plan_impact")
        fallback_plan_impact = data.get("plan_impact")
        plan_impact_source = raw_plan_impact if raw_plan_impact is not None else fallback_plan_impact
        plan_impact = _normalize_plan_impact(plan_impact_source)

        try:
            _validate_required_fields(
                report_ref,
                quest_id,
                plan_impact,
                has_raw_plan_impact=plan_impact_source is not None,
            )
        except ValueError as exc:
            logger.error("필수 필드 오류 (%s): %s", file_path.name, exc)
            move_to_failed(file_path)
            continue

        provider = judge_group.get("provider") or data.get("provider") or "external"
        session_id = _resolve_session_id(data, report_payload)
        confidence = verdict_group.get("confidence")
        ai_tags = verdict_group.get("ai_tags") or []

        metadata = dict(data.get("metadata") or {})
        metadata.setdefault("schema_version", data.get("schema_version", "1.0"))
        metadata["ai_tags"] = ai_tags
        metadata["confidence"] = confidence
        metadata["report_ref"] = report_ref
        metadata["plan_links"] = _extract_plan_links(data, report_payload)
        metadata["attachments"] = _extract_attachments(data, report_payload)
        metadata["correlation"] = _merge_correlations(data, report_payload)
        metadata.setdefault("verdict_seq", verdict_group.get("verdict_seq") or data.get("verdict_seq") or 1)
        metadata["judge"] = judge_group
        if judge_group.get("prompt_hash"):
            metadata["prompt_hash"] = judge_group["prompt_hash"]
        elif verdict_group.get("prompt_hash"):
            metadata["prompt_hash"] = verdict_group["prompt_hash"]

        try:
            apply_verdict(
                quest_id=quest_id,
                verdict=verdict_status,
                reason=reason,
                restart_point=restart_point,
                next_hint=next_hint,
                plan_impact=plan_impact,
                provider=provider,
                metadata=metadata,
                session_id=session_id,
                report_ref=report_ref,
            )
        except DuplicateVerdict as exc:
            logger.info("중복/무시 verdict (%s): %s", file_path.name, exc)
            if exc.code == "stale_revision":
                move_to_archive_revision(file_path)
            else:
                move_to_duplicate(file_path)
            continue
        except Exception as exc:
            logger.error("verdict 적용 실패 (%s): %s", file_path.name, exc, exc_info=True)
            move_to_failed(file_path)
            continue

        move_to_processed(file_path)
        logger.info("Imported verdict for quest %s (file=%s)", quest_id, file_path.name)


if __name__ == "__main__":
    import_verdicts()
