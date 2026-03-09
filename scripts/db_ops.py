from __future__ import annotations

import json
import re
import uuid

from scripts.ai_verdict import generate_verdict
from scripts.db_base import connect, now_iso, row_to_dict, rows_to_dicts
from scripts.db_sessions import append_source_record
from scripts.db_state import refresh_current_state
from scripts.report_export import export_quest_report


class DuplicateVerdict(Exception):
    def __init__(self, message: str, code: str = "duplicate") -> None:
        super().__init__(message)
        self.code = code


VERDICT_STATUS_RE = re.compile(r"^AI 판정:\s*(done|partial|hold|pending)\b", re.MULTILINE)


def get_current_state() -> dict:
    with connect() as conn:
        refresh_current_state(conn)
        rows = conn.execute(
            "SELECT state_key, state_value, updated_at, metadata_json FROM current_state ORDER BY state_key ASC"
        ).fetchall()
        state: dict = {}
        for row in rows:
            value = row["state_value"]
            try:
                state[row["state_key"]] = json.loads(value)
            except (TypeError, json.JSONDecodeError):
                state[row["state_key"]] = value
        return state


def get_plans() -> list[dict]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT * FROM plan_items
            ORDER BY
                CASE bucket
                    WHEN 'today' THEN 1
                    WHEN 'dated' THEN 2
                    WHEN 'short_term' THEN 3
                    WHEN 'long_term' THEN 4
                    WHEN 'recurring' THEN 5
                    ELSE 6
                END,
                priority_score DESC,
                updated_at DESC
            """
        ).fetchall()
        return rows_to_dicts(rows)


def get_quests() -> list[dict]:
    with connect() as conn:
        return rows_to_dicts(conn.execute("SELECT * FROM quests ORDER BY updated_at DESC").fetchall())


def approve_plan_candidates(candidates: list[dict], session_id: str = "") -> list[dict]:
    """
    Takes a list of plan candidates (from AI summary) and creates plan_items in the database.
    Each candidate should have: 'title', 'bucket', and optionally 'description', 'priority_score', 'related_source_id'.
    """
    created_items = []
    updated_at = now_iso()
    
    with connect() as conn:
        for cand in candidates:
            item_id = str(uuid.uuid4())
            bucket = cand.get("bucket", "short_term")
            title = cand.get("title", "Untitled Plan")
            description = cand.get("description", "")
            status = "pending"
            priority_score = cand.get("priority_score", 50)
            related_source_id = cand.get("related_source_id")
            
            conn.execute(
                """
                INSERT INTO plan_items (
                    id, bucket, title, description, status, 
                    priority_score, related_session_id, related_source_id,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item_id, bucket, title, description, status,
                    priority_score, session_id or None, related_source_id,
                    updated_at, updated_at
                )
            )
            
            # If related to an inbox item, mark it as accepted
            if related_source_id:
                conn.execute(
                    "UPDATE external_inbox SET status = 'accepted', processed_at = ? WHERE id = ?",
                    (updated_at, related_source_id)
                )
            
            row = conn.execute("SELECT * FROM plan_items WHERE id = ?", (item_id,)).fetchone()
            created_items.append(row_to_dict(row))

        if session_id:
            # Log the action to the session
            log_lines = [f"Approved {len(created_items)} plan items:"]
            for item in created_items:
                log_lines.append(f"- [{item['bucket']}] {item['title']}")
            
            append_source_record(
                session_id=session_id,
                source_name="inbox_cli",
                source_type="plan_update",
                content="\n".join(log_lines),
                role="system"
            )
            
        refresh_current_state(conn)
        
    return created_items


def get_latest_briefs(limit: int = 10) -> list[dict]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM brief_records
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return rows_to_dicts(rows)


def get_recent_sessions(limit: int = 10) -> list[dict]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT
                s.*,
                EXISTS(
                    SELECT 1
                    FROM source_records sr
                    WHERE sr.session_id = s.id
                      AND sr.source_type = 'quest_verdict'
                ) AS has_quest_verdict
            FROM sessions s
            ORDER BY s.started_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        sessions = rows_to_dicts(rows)
        for session in sessions:
            verdict_row = conn.execute(
                """
                SELECT content
                FROM source_records
                WHERE session_id = ?
                  AND source_type = 'quest_verdict'
                ORDER BY created_at DESC
                LIMIT 1
                """,
                (session["id"],),
            ).fetchone()
            status = ""
            if verdict_row and verdict_row["content"]:
                match = VERDICT_STATUS_RE.search(verdict_row["content"])
                if match:
                    status = match.group(1)
            session["quest_verdict_status"] = status
        return sessions


def apply_verdict(
    quest_id: str,
    verdict: str,
    reason: str,
    restart_point: str,
    next_hint: str,
    plan_impact: str | dict,
    provider: str,
    metadata: dict | None = None,
    session_id: str = "",
    report_ref: str = "",
) -> dict:
    if verdict not in {"done", "partial", "hold"}:
        raise ValueError("verdict must be one of: done, partial, hold")

    with connect() as conn:
        quest = conn.execute("SELECT * FROM quests WHERE id = ?", (quest_id,)).fetchone()
        if quest is None:
            raise ValueError("quest not found")

        existing_metadata = json.loads(quest["metadata_json"] or "{}")

        incoming_seq = 1
        if metadata and metadata.get("verdict_seq"):
            try:
                incoming_seq = int(metadata.get("verdict_seq"))
            except (TypeError, ValueError):
                incoming_seq = 1

        prev_verdict = existing_metadata.get("ai_verdict", {})
        prev_report_ref = prev_verdict.get("report_ref")
        prev_seq = prev_verdict.get("verdict_seq") or 0

        if report_ref and prev_report_ref == report_ref:
            if incoming_seq < prev_seq:
                raise DuplicateVerdict(
                    f"Stale verdict revision detected for report {report_ref}",
                    code="stale_revision",
                )
            if incoming_seq == prev_seq and prev_verdict.get("verdict") == verdict:
                raise DuplicateVerdict(
                    f"Verdict for report {report_ref} with status {verdict} already applied.",
                    code="duplicate",
                )

        updated_at = now_iso()
        if metadata:
            existing_metadata.update(metadata)

        existing_metadata.pop("preliminary_ai_verdict", None)
        existing_metadata["ai_verdict"] = {
            "verdict": verdict,
            "reason": reason,
            "restart_point": restart_point,
            "next_hint": next_hint,
            "plan_impact": plan_impact,
            "provider": provider,
            "confidence": (metadata or {}).get("confidence"),
            "judge": (metadata or {}).get("judge"),
            "prompt_hash": (metadata or {}).get("prompt_hash"),
            "verdict_seq": incoming_seq,
            "updated_at": updated_at,
            "report_ref": report_ref,
            "is_preliminary": False,
        }

        # Format structured plan_impact to string for decision_records
        impact_str = plan_impact
        if isinstance(plan_impact, dict):
            parts = []
            for b, desc in plan_impact.items():
                if desc and desc != "--":
                    parts.append(f"[{b}] {desc}")
            impact_str = "\n".join(parts) if parts else "영향 없음"

        conn.execute(
            """
            UPDATE quests
            SET status = ?, verdict_reason = ?, restart_point = ?, next_quest_hint = ?, updated_at = ?, metadata_json = ?
            WHERE id = ?
            """,
            (
                verdict,
                reason,
                restart_point,
                next_hint,
                updated_at,
                json.dumps(existing_metadata, ensure_ascii=False),
                quest_id,
            ),
        )
        if quest["plan_item_id"]:
            conn.execute(
                "UPDATE plan_items SET status = ?, updated_at = ? WHERE id = ?",
                ("done" if verdict == "done" else verdict, updated_at, quest["plan_item_id"]),
            )
        conn.execute(
            """
            INSERT INTO decision_records (
                id, decision_type, title, reason, impact_summary,
                related_plan_item_id, related_quest_id, related_session_id, created_at, metadata_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(uuid.uuid4()),
                "quest_verdict",
                f"Quest verdict: {quest['title']}",
                reason,
                impact_str,
                quest["plan_item_id"],
                quest_id,
                session_id or None,
                updated_at,
                json.dumps({"report_ref": report_ref, "raw_impact": plan_impact}, ensure_ascii=False),
            ),
        )
        refresh_current_state(conn)
        updated_quest = row_to_dict(conn.execute("SELECT * FROM quests WHERE id = ?", (quest_id,)).fetchone())

    if session_id:
        with connect() as conn:
            session = conn.execute(
                "SELECT agent_name, project_key, working_dir FROM sessions WHERE id = ?",
                (session_id,),
            ).fetchone()
        if session is not None:
            assistant_lines = [
                f"AI 판정: {verdict}",
                f"- 이유: {reason or '-'}",
                f"- 재시작 지점: {restart_point or '-'}",
                f"- 다음 퀘스트: {next_hint or '-'}",
                f"- 계획 반영: {plan_impact or '-'}",
                f"- provider: {provider}",
            ]
            append_source_record(
                session_id=session_id,
                source_name=session["agent_name"],
                source_type="quest_verdict",
                content="\n".join(assistant_lines),
                role="assistant",
                project_key=session["project_key"] or "",
                working_dir=session["working_dir"] or "",
                metadata={
                    "quest_id": quest_id,
                    "provider": provider,
                },
            )

    return updated_quest


def evaluate_quest(
    quest_id: str,
    verdict: str,
    reason: str,
    restart_point: str,
    next_quest_hint: str,
    plan_impact: str,
) -> dict:
    if verdict not in {"done", "partial", "hold"}:
        raise ValueError("verdict must be one of: done, partial, hold")

    with connect() as conn:
        quest = conn.execute("SELECT * FROM quests WHERE id = ?", (quest_id,)).fetchone()
        if quest is None:
            raise ValueError("quest not found")

        updated_at = now_iso()
        conn.execute(
            """
            UPDATE quests
            SET status = ?, verdict_reason = ?, restart_point = ?, next_quest_hint = ?, updated_at = ?
            WHERE id = ?
            """,
            (verdict, reason, restart_point, next_quest_hint, updated_at, quest_id),
        )
        if quest["plan_item_id"]:
            conn.execute(
                "UPDATE plan_items SET status = ?, updated_at = ? WHERE id = ?",
                ("done" if verdict == "done" else verdict, updated_at, quest["plan_item_id"]),
            )
        conn.execute(
            """
            INSERT INTO decision_records (
                id, decision_type, title, reason, impact_summary,
                related_plan_item_id, related_quest_id, related_session_id, created_at, metadata_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(uuid.uuid4()),
                "quest_verdict",
                f"Quest verdict: {quest['title']}",
                reason,
                plan_impact,
                quest["plan_item_id"],
                quest_id,
                None,
                updated_at,
                None,
            ),
        )
        refresh_current_state(conn)
        row = conn.execute("SELECT * FROM quests WHERE id = ?", (quest_id,)).fetchone()
        return row_to_dict(row) if row else {}


def report_quest_progress(
    quest_id: str,
    work_summary: str,
    remaining_work: str,
    blocker: str,
    self_assessment: str,
    session_id: str = "",
) -> dict:
    with connect() as conn:
        quest = conn.execute("SELECT * FROM quests WHERE id = ?", (quest_id,)).fetchone()
        if quest is None:
            raise ValueError("quest not found")

        # 1. Export report to file
        report_path = None
        try:
            report_path = export_quest_report(
                quest_id=quest_id,
                quest_title=quest["title"],
                completion_criteria=quest["completion_criteria"],
                work_summary=work_summary,
                remaining_work=remaining_work,
                blocker=blocker,
                self_assessment=self_assessment,
                session_id=session_id,
            )
        except Exception as e:
            print(f"Failed to export report: {e}")

        # 2. Heuristic fallback (temporary)
        verdict_data = generate_verdict(
            quest_title=quest["title"],
            completion_criteria=quest["completion_criteria"],
            work_summary=work_summary,
            remaining_work=remaining_work,
            blocker=blocker,
            self_assessment=self_assessment,
        )

        # 3. Update DB to 'pending' state
        updated_at = now_iso()
        report_data = {
            "work_summary": work_summary,
            "remaining_work": remaining_work,
            "blocker": blocker,
            "self_assessment": self_assessment,
            "reported_at": updated_at,
        }

        metadata = json.loads(quest["metadata_json"] or "{}")
        metadata["report"] = report_data
        if report_path is not None:
            report_name = report_path.name
            report_ref = report_name.removesuffix(".report.json")
            metadata["latest_report"] = {
                "report_ref": report_ref,
                "file_name": report_name,
                "reported_at": updated_at,
            }
        metadata["preliminary_ai_verdict"] = {
            "verdict": verdict_data["verdict"],
            "reason": verdict_data["reason"],
            "provider": verdict_data["provider"],
            "is_preliminary": True,
        }

        conn.execute(
            """
            UPDATE quests
            SET status = ?, updated_at = ?, metadata_json = ?
            WHERE id = ?
            """,
            (
                "pending",
                updated_at,
                json.dumps(metadata, ensure_ascii=False),
                quest_id,
            ),
        )
        refresh_current_state(conn)
        updated_quest = row_to_dict(conn.execute("SELECT * FROM quests WHERE id = ?", (quest_id,)).fetchone())

    if session_id:
        with connect() as conn:
            session = conn.execute(
                "SELECT agent_name, project_key, working_dir FROM sessions WHERE id = ?",
                (session_id,),
            ).fetchone()
        if session is not None:
            user_report_lines = [
                f"퀘스트 보고: {quest['title']} (판정 대기중)",
                f"- 한 일: {work_summary or '-'}",
                f"- 남은 일: {remaining_work or '-'}",
                f"- 막힌 점: {blocker or '-'}",
                f"- 자기 판단: {self_assessment or '-'}",
            ]
            append_source_record(
                session_id=session_id,
                source_name=session["agent_name"],
                source_type="quest_report",
                content="\n".join(user_report_lines),
                role="user",
                project_key=session["project_key"] or "",
                working_dir=session["working_dir"] or "",
                metadata={"quest_id": quest_id, "status": "pending"},
            )

    return updated_quest
