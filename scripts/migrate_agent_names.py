from __future__ import annotations

from agent_registry import canonical_agent_name
from db_base import connect


def migrate_table(table: str, column: str) -> int:
    updated = 0
    with connect() as conn:
        rows = conn.execute(f"SELECT id, {column} FROM {table}").fetchall()
        for row in rows:
            current = row[column]
            normalized = canonical_agent_name(current)
            if normalized != current:
                conn.execute(f"UPDATE {table} SET {column} = ? WHERE id = ?", (normalized, row["id"]))
                updated += 1
    return updated


def main() -> None:
    session_updates = migrate_table("sessions", "agent_name")
    source_updates = migrate_table("source_records", "source_name")
    print(
        {
            "sessions_updated": session_updates,
            "source_records_updated": source_updates,
        }
    )


if __name__ == "__main__":
    main()
