#!/usr/bin/env python3
"""
Export sessions from DB to operational memory structure.
Creates session notes in sessions/YYYY-MM-DD/ folder.
"""

import sqlite3
import json
import os
from datetime import datetime
from pathlib import Path

DB_PATH = "G:/Ddrive/BatangD/task/workdiary/0-a-control/data/control_tower.db"
SESSIONS_DIR = Path("G:/Ddrive/BatangD/task/workdiary/0-a-control/sessions")


def parse_timestamp(ts):
    """Parse ISO timestamp to datetime and date string."""
    if not ts:
        return None, None
    try:
        dt = datetime.fromisoformat(ts.replace("+00:00", ""))
        return dt, dt.strftime("%Y-%m-%d")
    except:
        return None, None


def format_time(ts):
    """Format timestamp to HH:MM."""
    dt, _ = parse_timestamp(ts)
    return dt.strftime("%H:%M") if dt else ""


def extract_sections(summary_md, metadata_json):
    """
    Extract Intent, Actions, Decisions, Next Start from summary_md.
    Rule-based extraction only - don't fabricate content.
    """
    if not summary_md:
        return "See transcript for details", [], [], []

    lines = [l.strip() for l in summary_md.strip().split("\n") if l.strip()]
    if not lines:
        return "No summary", [], [], []

    # Extract: first line as Intent
    intent = lines[0]

    # Categorize remaining lines
    actions = []
    decisions = []
    next_start = []

    # Keywords for categorization
    decision_keywords = ["완료", "종료", "정리", "결정", "done", "complete", "finished", "ended", "updated", "created", "수정", "변경"]
    next_keywords = ["다음", "next", "continue", "다음으로", "다음 단계", "then", "after this"]
    action_indicators = ["-", "•", "*", "1.", "2.", "3."]

    for line in lines[1:]:
        # Skip token usage lines
        if "Token usage" in line or "left ·" in line or "esc to interrupt" in line:
            continue
        if "session ended" in line.lower() or "session exited" in line.lower():
            decisions.append(line)
            continue

        # Check for next/start keywords
        lower_line = line.lower()
        is_next = any(k in lower_line for k in next_keywords)
        is_decision = any(k in lower_line for k in decision_keywords)

        # Check if it's a list item
        is_list = any(line.startswith(indicator) for indicator in action_indicators)

        if is_next:
            next_start.append(line)
        elif is_decision:
            decisions.append(line)
        elif is_list:
            actions.append(line)
        elif len(line) > 10:  # Only include meaningful lines
            # Default to actions if ambiguous
            actions.append(line)

    # Deduplicate while preserving order
    def dedupe(items):
        seen = set()
        result = []
        for item in items:
            if item not in seen:
                seen.add(item)
                result.append(item)
        return result

    actions = dedupe(actions)[:5]  # Max 5 items
    decisions = dedupe(decisions)[:3]  # Max 3 items
    next_start = dedupe(next_start)[:3]  # Max 3 items

    return intent, actions, decisions, next_start


def session_note_from_row(row):
    """Create session note content from DB row."""
    (session_id, agent_name, model_name, source_type, project_key,
     working_dir, title, started_at, ended_at, summary_md, status,
     files_touched_json, actions_json, metadata_json) = row

    # Parse metadata
    meta = json.loads(metadata_json) if metadata_json else {}
    transcript_path = meta.get("transcript_path", "")

    # Parse timestamps
    started_dt, date_str = parse_timestamp(started_at)
    ended_dt, _ = parse_timestamp(ended_at)

    time_str = ""
    if started_dt:
        end_time = format_time(ended_at) if ended_at else "active"
        time_str = f"{format_time(started_at)} ~ {end_time}"

    # File naming: YYYY-MM-DD/YYYY-MM-DD_HHMM_<short-id>.md
    time_prefix = format_time(started_at).replace(":", "") if started_dt else "0000"
    short_id = session_id[:8]
    filename = f"{date_str}_{time_prefix}_{short_id}.md" if date_str else f"unknown_{short_id}.md"

    # Extract sections
    intent, actions, decisions, next_start = extract_sections(summary_md, metadata_json)

    # Build note content
    note = f"""# Session Note

## Metadata

- **Session ID**: `{session_id}`
- **Date**: {date_str or "unknown"}
- **Time**: {time_str}
- **Agent**: {agent_name}
- **Status**: {status}
- **Previous Session**: N/A (exported from DB)

---

## Intent

> What was this session trying to accomplish?

- {intent}

---

## Actions

> What was actually done? (bullet points)

"""

    if actions:
        for a in actions:
            if a.strip():
                note += f"- {a.strip()}\n"
    else:
        note += "- (no specific actions recorded)\n"

    note += """

## Decisions

> What was decided? (with rationale if available)

| Decision | Rationale |
|----------|-----------|
"""

    if decisions:
        for d in decisions:
            note += f"| {d} | - |\n"
    else:
        note += "| (none recorded) | |\n"

    note += """---

## Artifacts

> Files created or modified

| File | Role |
|------|------|
| (none recorded) |       |

---

## Next Start

> Where should the next session pick up?

"""

    if next_start:
        for i, n in enumerate(next_start, 1):
            note += f"{i}. {n}\n"
    else:
        note += "1. Check current-state API for today's mission\n"
        note += "2. Review plans for pending items\n"

    note += """---

## Raw Refs

> Transcript path or other references (not full content)

"""

    if transcript_path:
        note += f"- Transcript: `{transcript_path}`\n"
    else:
        note += "- (no transcript)\n"

    note += f"- DB session: `{session_id}`\n"

    return filename, note


def export_sessions():
    """Export all sessions from DB to sessions/ folder."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT id, agent_name, model_name, source_type, project_key,
               working_dir, title, started_at, ended_at, summary_md, status,
               files_touched_json, actions_json, metadata_json
        FROM sessions
        ORDER BY started_at DESC
    """)
    rows = cur.fetchall()
    conn.close()

    print(f"Found {len(rows)} sessions")

    # Track for INDEX
    index_entries = []

    for row in rows:
        session_id = row[0]
        started_at = row[7]
        _, date_str = parse_timestamp(started_at)

        if not date_str:
            date_str = "unknown"
            print(f"  Skipping session without date: {session_id}")
            continue

        # Create date folder
        date_dir = SESSIONS_DIR / date_str
        date_dir.mkdir(parents=True, exist_ok=True)

        # Generate note
        filename, content = session_note_from_row(row)

        # Write note
        filepath = date_dir / filename
        filepath.write_text(content, encoding="utf-8")

        # Add to index
        status = row[10]
        agent = row[1]
        title = row[6] or "Untitled"
        index_entries.append({
            "date": date_str,
            "filename": filename,
            "status": status,
            "agent": agent,
            "title": title[:50]
        })

        print(f"  Created: {date_str}/{filename}")

    # Update INDEX.md
    update_index(index_entries)

    print("\nExport complete!")
    return len(rows)


def update_index(entries):
    """Update sessions/INDEX.md with session list."""
    # Sort by date descending
    entries.sort(key=lambda x: x["date"], reverse=True)

    lines = [
        "# Session Index",
        "",
        "| Date | Session | Agent | Status | Title |",
        "|------|---------|-------|--------|-------|",
    ]

    for e in entries:
        title_escaped = e["title"].replace("|", "\\|")
        lines.append(f"| {e['date']} | {e['filename'][:16]}... | {e['agent']} | {e['status']} | {title_escaped} |")

    lines.append("")
    lines.append("## Usage")
    lines.append("")
    lines.append("1. New session: Copy `TEMPLATE.md` as `YYYY-MM-DD_HHMM_<id>.md`")
    lines.append("2. Fill in during/after session")
    lines.append("3. Next session reads last session note for context")

    index_path = SESSIONS_DIR / "INDEX.md"
    index_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nUpdated INDEX.md with {len(entries)} entries")


if __name__ == "__main__":
    export_sessions()
