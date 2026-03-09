from __future__ import annotations

import argparse
import json
import shutil
import sqlite3
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from db_sessions import append_source_record, update_session_summary

OPENCODE_DB_PATH = Path("/mnt/c/Users/limone/.local/share/opencode/opencode.db")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Import latest Opencode session into control tower source records")
    parser.add_argument("--session-id", required=True)
    parser.add_argument("--project", default="")
    parser.add_argument("--cwd", default="")
    parser.add_argument("--source-name", default="opencode")
    parser.add_argument("--db-path", default=str(OPENCODE_DB_PATH))
    return parser.parse_args()


def iso_to_epoch_ms(value: str) -> int:
    if not value:
        return 0
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return int(dt.timestamp() * 1000)


def to_windows_path(path: str) -> str:
    if path.startswith("/mnt/") and len(path) > 6:
        drive = path[5].upper()
        rest = path[6:].replace("/", "\\")
        return f"{drive}:{rest}"
    return path.replace("/", "\\")


def normalize_path(path: str) -> str:
    return path.replace("/", "\\").rstrip("\\").lower()


def copy_sqlite_bundle(db_path: Path, temp_dir: Path) -> Path:
    dest = temp_dir / db_path.name
    shutil.copy2(db_path, dest)
    for suffix in ("-wal", "-shm"):
        sidecar = Path(str(db_path) + suffix)
        if sidecar.exists():
            shutil.copy2(sidecar, Path(str(dest) + suffix))
    return dest


def select_session(conn: sqlite3.Connection, cwd: str, started_after_ms: int) -> dict | None:
    candidates = {
        normalize_path(cwd),
        normalize_path(to_windows_path(cwd)),
    }
    rows = conn.execute(
        """
        SELECT id, title, directory, time_created, time_updated
        FROM session
        WHERE time_updated >= ?
        ORDER BY time_updated DESC
        LIMIT 20
        """,
        (max(0, started_after_ms - 60_000),),
    ).fetchall()
    for row in rows:
        if normalize_path(row["directory"]) in candidates:
            return dict(row)
    return dict(rows[0]) if rows else None


def build_message_content(parts: list[sqlite3.Row], role: str) -> str:
    texts: list[str] = []
    reasoning: list[str] = []

    for part in parts:
        payload = json.loads(part["data"])
        part_type = payload.get("type")
        if part_type == "text" and payload.get("text"):
            texts.append(payload["text"])
        elif part_type == "reasoning" and payload.get("text"):
            reasoning.append(payload["text"])

    if role == "assistant" and reasoning:
        chunks = [f"Thinking:\n{'\n\n'.join(reasoning).strip()}"]
        if texts:
            chunks.append("\n\n".join(texts).strip())
        return "\n\n".join(chunk for chunk in chunks if chunk).strip()
    return "\n\n".join(texts).strip()


def main() -> None:
    args = parse_args()
    db_path = Path(args.db_path)
    if not db_path.exists():
        raise SystemExit(f"opencode db not found: {db_path}")

    with tempfile.TemporaryDirectory() as temp_dir_str:
        temp_dir = Path(temp_dir_str)
        temp_db = copy_sqlite_bundle(db_path, temp_dir)

        conn = sqlite3.connect(temp_db)
        conn.row_factory = sqlite3.Row

        control_db = Path(__file__).resolve().parents[1] / "data" / "control_tower.db"
        ct_conn = sqlite3.connect(control_db)
        ct_conn.row_factory = sqlite3.Row
        session_row = ct_conn.execute(
            "SELECT started_at FROM sessions WHERE id = ?",
            (args.session_id,),
        ).fetchone()
        ct_conn.close()
        started_after_ms = iso_to_epoch_ms(session_row["started_at"]) if session_row else 0

        oc_session = select_session(conn, args.cwd, started_after_ms)
        if not oc_session:
            raise SystemExit("no matching opencode session found")

        message_rows = conn.execute(
            """
            SELECT id, data, time_created
            FROM message
            WHERE session_id = ?
            ORDER BY time_created ASC
            """,
            (oc_session["id"],),
        ).fetchall()

        imported = 0
        for message in message_rows:
            message_data = json.loads(message["data"])
            role = message_data.get("role", "assistant")
            parts = conn.execute(
                """
                SELECT id, data, time_created
                FROM part
                WHERE message_id = ?
                ORDER BY time_created ASC
                """,
                (message["id"],),
            ).fetchall()
            content = build_message_content(parts, role)
            if not content:
                continue
            append_source_record(
                session_id=args.session_id,
                source_name=args.source_name,
                source_type="agent_turn",
                content=content,
                role=role,
                project_key=args.project,
                working_dir=args.cwd,
                metadata={
                    "opencode_session_id": oc_session["id"],
                    "opencode_message_id": message["id"],
                    "opencode_message_time": message["time_created"],
                },
            )
            imported += 1

        append_source_record(
            session_id=args.session_id,
            source_name=args.source_name,
            source_type="opencode_session",
            content=json.dumps(oc_session, ensure_ascii=False, indent=2),
            role="tool",
            project_key=args.project,
            working_dir=args.cwd,
            metadata={"opencode_session_id": oc_session["id"], "imported_messages": imported},
        )

        summary = oc_session.get("title") or "opencode session imported"
        update_session_summary(
            session_id=args.session_id,
            summary_md=summary,
            metadata={"summary_source": "opencode_session", "opencode_session_id": oc_session["id"]},
        )


if __name__ == "__main__":
    main()
