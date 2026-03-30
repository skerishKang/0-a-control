#!/usr/bin/env python3
"""
Export sessions from DB to session archive structure.
Creates full session preservation notes in sessions/YYYY-MM-DD/ folder.

Philosophy:
- sessions/ holds the complete session archive, not compressed notes.
- Summary is a supplementary layer (short box), not the main body.
- Dialogue records and transcript content are preserved in full.
- Display layer (HTML) renders all of this.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

try:
    from scripts.db_sessions import get_session_view_model
    from scripts.db_base import connect, rows_to_dicts
except ModuleNotFoundError:
    from db_sessions import get_session_view_model
    from db_base import connect, rows_to_dicts


SESSIONS_DIR = Path("G:/Ddrive/BatangD/task/workdiary/0-a-control/sessions")


def parse_timestamp(ts: str | None) -> tuple[datetime | None, str | None]:
    if not ts:
        return None, None
    try:
        dt = datetime.fromisoformat(ts.replace("+00:00", ""))
        return dt, dt.strftime("%Y-%m-%d")
    except Exception:
        return None, None


def format_time(ts: str | None) -> str:
    dt, _ = parse_timestamp(ts)
    return dt.strftime("%H:%M") if dt else ""


def _format_list(items: list[str], fallback: str) -> list[str]:
    cleaned = [item.strip() for item in items if item and item.strip()]
    return cleaned or [fallback]


def _display_text(value: str | None, fallback: str) -> str:
    text = (value or "").strip()
    if not text:
        return fallback
    broken_markers = ("\ufffd", "?붿", "덈", "몄", "湲", "떎")
    if any(marker in text for marker in broken_markers) or text.count("?") >= 2:
        return fallback
    return text


def session_note_from_view(view: dict) -> tuple[str, str, str]:
    header = view.get("header", {})
    meta = view.get("meta", {})
    summary = view.get("summary", {})
    artifacts = view.get("artifacts", {})
    transcript = view.get("transcript", {})
    quest = view.get("quest", {})
    dialogue = view.get("dialogue", [])

    session_id = view["session_id"]
    started_at = header.get("started_at")
    ended_at = header.get("ended_at")
    started_dt, date_str = parse_timestamp(started_at)

    if not date_str:
        date_str = "unknown"

    title = header.get("title") or meta.get("project_key") or "Untitled session"
    agent_name = meta.get("agent_name") or "-"
    status = header.get("status") or "-"
    source_type = meta.get("source_type") or "-"
    project_key = meta.get("project_key") or "-"
    model_name = meta.get("model_name") or "-"
    working_dir = meta.get("working_dir") or "-"

    start_time = format_time(started_at)
    end_time = format_time(ended_at) if ended_at else "active"
    time_str = f"{start_time} ~ {end_time}" if start_time else ""

    time_prefix = start_time.replace(":", "") if start_time else "0000"
    short_id = session_id[:8]
    filename = f"{date_str}_{time_prefix}_{short_id}.md"

    # --- Summary block (supplementary, not main body) ---
    intent = _display_text(summary.get("intent"), "요약이 없습니다.")
    actions_summary = _format_list(summary.get("actions") or [], "(no specific actions recorded)")
    decisions = _format_list(summary.get("decisions") or [], "(none recorded)")
    next_start = _format_list(
        summary.get("next_start") or [],
        "Check current-state API for today's mission",
    )
    files_touched = [item.strip() for item in (artifacts.get("files_touched") or []) if item and item.strip()]
    actions_json = [item.strip() for item in (artifacts.get("actions") or []) if item and item.strip()]

    note = f"""# {title}

## Metadata

- **Session ID**: `{session_id}`
- **Date**: {date_str}
- **Time**: {time_str}
- **Agent**: {agent_name}
- **Model**: {model_name}
- **Project**: {project_key}
- **Working Dir**: `{working_dir}`
- **Source Type**: {source_type}
- **Status**: {status}

---

## Summary

> 이 세션의 요약입니다. 전체 대화는 아래 본문에 포함되어 있습니다.

**Intent**: {intent}

**Key Actions**:
"""
    for item in actions_summary:
        note += f"- {item}\n"

    note += "\n**Decisions**:\n"
    for item in decisions:
        note += f"- {item}\n"

    note += "\n**Files Touched**:\n"
    if files_touched:
        for item in files_touched:
            note += f"- {item}\n"
    else:
        note += "- (none recorded)\n"

    note += "\n**Next Start**:\n"
    for index, item in enumerate(next_start, 1):
        note += f"{index}. {item}\n"

    note += "\n**Quest**:\n"
    note += f"- Report: {quest.get('report') or '(none recorded)'}\n"
    note += f"- Verdict: {quest.get('verdict') or '(none recorded)'}\n"

    # --- Dialogue (full conversation flow) ---
    note += """

---

## Dialogue

> 세션의 전체 대화 흐름입니다.

"""
    if dialogue:
        for record in dialogue:
            role = (record.get("role") or "tool").upper()
            ts = record.get("created_at") or ""
            content = record.get("content") or ""
            note += f"### [{ts}] {role}\n\n"
            note += f"{content}\n\n---\n\n"
    else:
        note += "(대화 기록 없음)\n"

    # --- Transcript (full raw content) ---
    note += """

## Transcript

> 원시 세션 기록입니다.

"""
    if transcript.get("available"):
        profile = transcript.get("profile") or "default"
        record_count = transcript.get("record_count", 0)
        note += f"- Profile: {profile}\n"
        note += f"- Record count: {record_count}\n\n"

        cleaned = transcript.get("cleaned_content") or ""
        raw = transcript.get("raw_content") or ""

        if cleaned:
            note += "### Cleaned Transcript\n\n"
            note += f"```\n{cleaned}\n```\n\n"

        if raw:
            note += "### Raw Transcript\n\n"
            note += f"```\n{raw}\n```\n"
    else:
        note += "(transcript 없음)\n"

    note += f"\n---\n\n- DB session: `{session_id}`\n"

    return date_str, filename, note


def export_sessions() -> int:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM sessions
            ORDER BY started_at DESC
            """
        ).fetchall()
        sessions = rows_to_dicts(rows)

    print(f"Found {len(sessions)} sessions")

    index_entries: list[dict] = []

    for session in sessions:
        view = get_session_view_model(session["id"])
        date_str, filename, content = session_note_from_view(view)

        date_dir = SESSIONS_DIR / date_str
        date_dir.mkdir(parents=True, exist_ok=True)
        filepath = date_dir / filename
        filepath.write_text(content, encoding="utf-8")

        index_entries.append(
            {
                "date": date_str,
                "filename": filename,
                "status": view["header"].get("status") or "-",
                "agent": view["meta"].get("agent_name") or "-",
                "title": (view["header"].get("title") or "Untitled")[:50],
            }
        )
        print(f"  Created: {date_str}/{filename}")

    update_index(index_entries)
    print("\nExport complete!")
    return len(sessions)


def update_index(entries: list[dict]) -> None:
    entries.sort(key=lambda item: item["date"], reverse=True)
    lines = [
        "# Session Index",
        "",
        "| Date | Session | Agent | Status | Title |",
        "|------|---------|-------|--------|-------|",
    ]

    for item in entries:
        title_escaped = item["title"].replace("|", "\\|")
        lines.append(
            f"| {item['date']} | {item['filename'][:16]}... | {item['agent']} | {item['status']} | {title_escaped} |"
        )

    lines.extend(
        [
            "",
            "## Usage",
            "",
            "sessions/ is a read-only export from SQLite.",
            "If DB state changes, rerun the export instead of editing these files manually.",
        ]
    )

    index_path = SESSIONS_DIR / "INDEX.md"
    index_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nUpdated INDEX.md with {len(entries)} entries")


if __name__ == "__main__":
    export_sessions()

