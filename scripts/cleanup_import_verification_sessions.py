#!/usr/bin/env python3
from __future__ import annotations

import argparse

try:
    from scripts.db_base import connect, rows_to_dicts
except ModuleNotFoundError:
    from db_base import connect, rows_to_dicts


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="List or delete importer verification sessions from the control tower DB."
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually delete matching sessions. Without this flag the script is dry-run only.",
    )
    parser.add_argument(
        "--project",
        default="0-a-control",
        help="Optional project_key filter. Default: 0-a-control",
    )
    return parser.parse_args()


def find_candidates(project_key: str) -> list[dict]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT id, title, agent_name, project_key, started_at, ended_at, status
            FROM sessions
            WHERE LOWER(COALESCE(title, '')) LIKE '%verification%'
              AND (? = '' OR COALESCE(project_key, '') = ?)
            ORDER BY started_at DESC
            """,
            (project_key, project_key),
        ).fetchall()
        return rows_to_dicts(rows)


def delete_sessions(session_ids: list[str]) -> None:
    if not session_ids:
        return
    placeholders = ",".join("?" for _ in session_ids)
    with connect() as conn:
        conn.execute(
            f"DELETE FROM source_records WHERE session_id IN ({placeholders})",
            session_ids,
        )
        conn.execute(
            f"""
            DELETE FROM event_log
            WHERE session_id IN ({placeholders})
               OR (entity_type = 'session' AND entity_id IN ({placeholders}))
            """,
            session_ids + session_ids,
        )
        conn.execute(
            f"DELETE FROM sessions WHERE id IN ({placeholders})",
            session_ids,
        )


def main() -> None:
    args = parse_args()
    candidates = find_candidates(args.project)
    if not candidates:
        print("No importer verification sessions found.")
        return

    print(f"Found {len(candidates)} importer verification session(s).")
    for item in candidates:
        print(
            f"- {item['id']} | {item.get('agent_name') or '-'} | "
            f"{item.get('started_at') or '-'} | {item.get('title') or '-'}"
        )

    if not args.apply:
        print("\nDry run only. Re-run with --apply to delete these sessions.")
        return

    session_ids = [item["id"] for item in candidates]
    delete_sessions(session_ids)
    print(f"\nDeleted {len(session_ids)} importer verification session(s).")


if __name__ == "__main__":
    main()
