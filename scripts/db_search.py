from __future__ import annotations

import argparse
import json
from typing import Any

try:
    from scripts.db_base import connect, init_db, migrate_search_state, now_iso, record_event
except ModuleNotFoundError:
    from db_base import connect, init_db, migrate_search_state, now_iso, record_event


FTS_TABLES = {
    "sessions": {
        "table": "sessions_fts",
        "join_table": "sessions",
        "join_id": "id",
        "time_col": "started_at",
        "text_cols": "title, summary_md",
        "select_cols": "j.id, j.title, j.started_at, j.agent_name, j.project_key",
    },
    "sources": {
        "table": "source_records_fts",
        "join_table": "source_records",
        "join_id": "id",
        "time_col": "created_at",
        "text_cols": "source_name, content",
        "select_cols": "j.id, j.source_name, j.created_at, j.source_type, j.session_id",
    },
    "briefs": {
        "table": "brief_records_fts",
        "join_table": "brief_records",
        "join_id": "id",
        "time_col": "created_at",
        "text_cols": "title, content_md",
        "select_cols": "j.id, j.title, j.created_at, j.brief_type",
    },
    "decisions": {
        "table": "decision_records_fts",
        "join_table": "decision_records",
        "join_id": "id",
        "time_col": "created_at",
        "text_cols": "title, reason, impact_summary",
        "select_cols": "j.id, j.title, j.created_at, j.decision_type, j.related_session_id",
    },
    "inbox": {
        "table": "external_inbox_fts",
        "join_table": "external_inbox",
        "join_id": "id",
        "time_col": "imported_at",
        "text_cols": "source_name, author, title, raw_content, attachment_path",
        "select_cols": "j.id, j.source_name, j.author, j.item_timestamp, j.imported_at, j.status, j.attachment_path",
    },
}


def _print_json(obj: Any) -> None:
    print(json.dumps(obj, ensure_ascii=False, indent=2))


def search_events(args: argparse.Namespace) -> None:
    sql = """
        SELECT id, event_type, entity_type, entity_id, detail, created_at, metadata_json
        FROM event_log
        WHERE 1 = 1
    """
    params: list[Any] = []

    if args.event_type:
        sql += " AND event_type = ?"
        params.append(args.event_type)
    if args.entity_type:
        sql += " AND entity_type = ?"
        params.append(args.entity_type)
    if args.entity_id:
        sql += " AND entity_id = ?"
        params.append(args.entity_id)
    if args.query:
        sql += " AND (detail LIKE ? OR COALESCE(metadata_json, '') LIKE ?)"
        needle = f"%{args.query}%"
        params.extend([needle, needle])

    sql += " ORDER BY created_at DESC LIMIT ?"
    params.append(args.limit)

    with connect() as conn:
        rows = conn.execute(sql, params).fetchall()
        for row in rows:
            item = dict(row)
            if item["metadata_json"]:
                try:
                    item["metadata_json"] = json.loads(item["metadata_json"])
                except json.JSONDecodeError:
                    pass
            _print_json(item)


def search_fts(args: argparse.Namespace) -> None:
    spec = FTS_TABLES[args.domain]
    sql = f"""
        SELECT
            {spec['select_cols']},
            snippet({spec['table']}, -1, '[', ']', '...', 18) AS snippet,
            bm25({spec['table']}) AS score
        FROM {spec['table']} f
        JOIN {spec['join_table']} j ON j.{spec['join_id']} = f.id
        WHERE {spec['table']} MATCH ?
    """
    params: list[Any] = [args.query]

    if args.project_key and args.domain == "sessions":
        sql += " AND COALESCE(j.project_key, '') = ?"
        params.append(args.project_key)

    sql += " ORDER BY score LIMIT ?"
    params.append(args.limit)

    with connect() as conn:
        rows = conn.execute(sql, params).fetchall()
        for row in rows:
            _print_json(dict(row))


def show_stats(_: argparse.Namespace) -> None:
    with connect() as conn:
        tables = [
            "sessions",
            "source_records",
            "brief_records",
            "decision_records",
            "external_inbox",
            "event_log",
            "sessions_fts",
            "source_records_fts",
            "brief_records_fts",
            "decision_records_fts",
            "external_inbox_fts",
        ]
        stats = {}
        for table in tables:
            stats[table] = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        _print_json(stats)


def log_event(args: argparse.Namespace) -> None:
    metadata = {}
    if args.metadata:
        try:
            metadata = json.loads(args.metadata)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"invalid JSON for --metadata: {exc}")
    with connect() as conn:
        event_id = record_event(
            conn,
            event_type=args.event_type,
            entity_id=args.entity_id,
            entity_type=args.entity_type,
            detail=args.detail,
            metadata=metadata,
            created_at=args.created_at or now_iso(),
        )
        row = conn.execute(
            "SELECT id, event_type, entity_type, entity_id, detail, created_at, metadata_json FROM event_log WHERE id = ?",
            (event_id,),
        ).fetchone()
        item = dict(row)
        if item["metadata_json"]:
            item["metadata_json"] = json.loads(item["metadata_json"])
        _print_json(item)


def main() -> None:
    init_db()

    parser = argparse.ArgumentParser(description="Search control_tower.db memory and events")
    sub = parser.add_subparsers(dest="command", required=True)

    events = sub.add_parser("events", help="search event_log")
    events.add_argument("query", nargs="?", default="")
    events.add_argument("--event-type", default="")
    events.add_argument("--entity-type", default="")
    events.add_argument("--entity-id", default="")
    events.add_argument("--limit", type=int, default=10)
    events.set_defaults(func=search_events)

    fts = sub.add_parser("fts", help="search FTS domains")
    fts.add_argument("domain", choices=sorted(FTS_TABLES.keys()))
    fts.add_argument("query")
    fts.add_argument("--project-key", default="")
    fts.add_argument("--limit", type=int, default=10)
    fts.set_defaults(func=search_fts)

    stats = sub.add_parser("stats", help="show DB/FTS row counts")
    stats.set_defaults(func=show_stats)

    rebuild = sub.add_parser("rebuild-search", help="rebuild event backfill and FTS indexes")
    rebuild.set_defaults(func=lambda _: migrate_search_state())

    log = sub.add_parser("log-event", help="append an operational event")
    log.add_argument("event_type")
    log.add_argument("entity_type")
    log.add_argument("entity_id")
    log.add_argument("--detail", default="")
    log.add_argument("--metadata", default="")
    log.add_argument("--created-at", default="")
    log.set_defaults(func=log_event)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

