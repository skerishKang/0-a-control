from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    import sys

    project_root = Path(__file__).resolve().parents[1]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from scripts.db_base import connect, now_iso
    from scripts.db_state import refresh_current_state
else:
    from .db_base import connect, now_iso
    from .db_state import refresh_current_state

FINAL_VERDICTS = {"done", "partial", "hold"}


def _parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _load_meta(raw: str | None) -> dict[str, Any]:
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


def find_repair_candidates(stale_minutes: int = 10) -> list[dict[str, Any]]:
    threshold = timedelta(minutes=stale_minutes)
    now = datetime.now(timezone.utc)
    candidates: list[dict[str, Any]] = []

    with connect() as conn:
        rows = conn.execute(
            """
            SELECT q.*, p.title AS plan_title, p.status AS plan_status
            FROM quests q
            LEFT JOIN plan_items p ON p.id = q.plan_item_id
            WHERE q.status = 'pending'
            ORDER BY q.updated_at DESC
            """
        ).fetchall()
        for row in rows:
            item = dict(row)
            meta = _load_meta(item.get("metadata_json"))
            report = meta.get("report") or {}
            latest_report = meta.get("latest_report") or {}
            ai_verdict = meta.get("ai_verdict") or {}

            reported_at = _parse_iso(report.get("reported_at"))
            latest_report_ref = latest_report.get("report_ref")
            ai_report_ref = ai_verdict.get("report_ref")
            ai_status = ai_verdict.get("verdict")
            ai_updated_at = _parse_iso(ai_verdict.get("updated_at"))

            if not reported_at or not latest_report_ref:
                continue
            if now - reported_at <= threshold:
                continue
            if ai_status not in FINAL_VERDICTS or not ai_report_ref or not ai_updated_at:
                continue
            if latest_report_ref == ai_report_ref:
                continue
            if ai_updated_at >= reported_at:
                continue

            candidates.append(
                {
                    "quest_id": item["id"],
                    "quest_title": item["title"],
                    "plan_item_id": item.get("plan_item_id"),
                    "plan_title": item.get("plan_title"),
                    "plan_status": item.get("plan_status"),
                    "reported_at": report.get("reported_at"),
                    "latest_report_ref": latest_report_ref,
                    "ai_report_ref": ai_report_ref,
                    "revert_to_status": ai_status,
                    "ai_updated_at": ai_verdict.get("updated_at"),
                    "ai_reason": ai_verdict.get("reason", ""),
                    "restart_point": ai_verdict.get("restart_point", ""),
                    "next_hint": ai_verdict.get("next_hint", ""),
                }
            )

    return candidates


def apply_repair(stale_minutes: int = 10) -> list[dict[str, Any]]:
    candidates = find_repair_candidates(stale_minutes=stale_minutes)
    if not candidates:
        return []

    repaired_at = now_iso()
    with connect() as conn:
        for candidate in candidates:
            quest = conn.execute("SELECT * FROM quests WHERE id = ?", (candidate["quest_id"],)).fetchone()
            if quest is None:
                continue

            meta = _load_meta(quest["metadata_json"])
            archived = meta.get("stale_report_archive") or []
            archived.append(
                {
                    "report": meta.get("report"),
                    "latest_report": meta.get("latest_report"),
                    "preliminary_ai_verdict": meta.get("preliminary_ai_verdict"),
                    "repaired_at": repaired_at,
                    "repair_reason": "stale pending report reverted to last final ai_verdict",
                }
            )
            meta["stale_report_archive"] = archived
            meta.pop("report", None)
            meta.pop("latest_report", None)
            meta.pop("preliminary_ai_verdict", None)
            meta["stale_pending_recovery"] = {
                "repaired_at": repaired_at,
                "reverted_to_verdict": candidate["revert_to_status"],
                "reverted_from_report_ref": candidate["latest_report_ref"],
                "restored_ai_report_ref": candidate["ai_report_ref"],
            }

            conn.execute(
                """
                UPDATE quests
                SET status = ?,
                    verdict_reason = ?,
                    restart_point = ?,
                    next_quest_hint = ?,
                    updated_at = ?,
                    metadata_json = ?
                WHERE id = ?
                """,
                (
                    candidate["revert_to_status"],
                    candidate["ai_reason"],
                    candidate["restart_point"],
                    candidate["next_hint"],
                    repaired_at,
                    json.dumps(meta, ensure_ascii=False),
                    candidate["quest_id"],
                ),
            )

            if candidate["plan_item_id"]:
                plan_status = "done" if candidate["revert_to_status"] == "done" else candidate["revert_to_status"]
                conn.execute(
                    "UPDATE plan_items SET status = ?, updated_at = ? WHERE id = ?",
                    (plan_status, repaired_at, candidate["plan_item_id"]),
                )

        refresh_current_state(conn)

    return candidates


def main() -> None:
    parser = argparse.ArgumentParser(description="Repair stale pending quests using the last final ai_verdict")
    parser.add_argument("--stale-minutes", type=int, default=10, help="Only consider reports older than this many minutes")
    parser.add_argument("--apply", action="store_true", help="Apply repair instead of dry-run")
    args = parser.parse_args()

    if args.apply:
        items = apply_repair(stale_minutes=args.stale_minutes)
        print(json.dumps({"mode": "apply", "repaired": items, "count": len(items)}, ensure_ascii=False, indent=2))
        return

    items = find_repair_candidates(stale_minutes=args.stale_minutes)
    print(json.dumps({"mode": "dry-run", "candidates": items, "count": len(items)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
