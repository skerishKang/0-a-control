from __future__ import annotations

import sqlite3

from db_base import DB_PATH
from db_sessions import update_session_summary
from session_summary import summarize_transcript


def main() -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        """
        SELECT s.id, s.title, s.project_key, sr.content
        FROM sessions s
        JOIN source_records sr ON sr.session_id = s.id
        WHERE sr.source_type = 'terminal_transcript'
        ORDER BY sr.created_at DESC
        """
    ).fetchall()
    conn.close()

    seen: set[str] = set()
    updated = 0
    for row in rows:
        session_id = row["id"]
        if session_id in seen:
            continue
        seen.add(session_id)
        summary = summarize_transcript(row["content"], title=row["title"], project_key=row["project_key"])
        update_session_summary(
            session_id=session_id,
            summary_md=summary,
            metadata={"summary_source": "terminal_transcript"},
        )
        updated += 1

    print({"updated_sessions": updated})


if __name__ == "__main__":
    main()
