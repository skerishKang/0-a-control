# SKILL: Session Refresh

## Description

This skill defines the standard procedure for refreshing session notes from the database to the operational memory structure.

**Goal**: Keep sessions/ as the canonical source of operational memory, not transcript dumps.

---

## Trigger Conditions

Use this skill when:

1. **Session memo needs refresh** - You want to export the latest sessions from DB to sessions/ folder
2. **Before starting a new session** - You need to review recent work context
3. **After many sessions accumulate** - You need to update the read-friendly structure (HTML view)
4. **When requested by user** - User explicitly asks to refresh session notes

---

## Standard Command

### Unix/WSL
```bash
bash scripts/refresh_sessions.sh
```

### Windows
```cmd
refresh-sessions.bat
```

Or directly:
```cmd
python scripts\export_sessions.py
python scripts\generate_session_html.py
```

---

## Expected Outputs

| Output | Location |
|--------|----------|
| Session notes (Markdown) | `sessions/YYYY-MM-DD/*.md` |
| Session index | `sessions/INDEX.md` |
| HTML view (optional) | `sessions_html/index.html` |

---

## What Should Happen

1. `scripts/export_sessions.py` runs
   - Reads from `data/control_tower.db` (sessions table)
   - Exports each session as a Markdown note
   - Uses Intent/Actions/Decisions/Artifacts/Next Start/Raw Refs structure
   - Updates `sessions/INDEX.md`

2. `scripts/generate_session_html.py` runs (if HTML is needed)
   - Converts Markdown notes to HTML
   - Creates `sessions_html/` structure

---

## Failure Conditions

The following are considered failures:

1. **Transcript dump** - Creating full transcript copies instead of operational notes
2. **Non-standard command** - Using ad-hoc Python commands instead of the standard script
3. **Verbose summaries** - Making session notes unnecessarily long
4. **Wrong structure** - Using prose paragraphs instead of Intent/Actions/Decisions format
5. **Modifying raw data** - Changing the DB schema or raw session data

---

## Example

### Before
```
User: Can you refresh the session notes?
```

### Response
```
I'll refresh the session notes using the standard command.
```

### Action
```bash
bash scripts/refresh_sessions.sh
```

### Result
```
=== Session Refresh ===
Project: /path/to/0-a-control

1. Export sessions from DB...
Found 145 sessions
  Created: 2026-03-16/2026-03-16_2058_d665e5b9.md
  ...
Updated INDEX.md with 145 entries

2. Generate HTML view...
Generated 145 session HTMLs + index.html

=== Done ===
Sessions exported to: sessions/
HTML view generated to: sessions_html/
```

---

## Key Principles

- **Operational memory, not transcript dump** - Store decisions and next actions, not full logs
- **Standard command only** - Never run export scripts manually; use the refresh script
- **Read-friendly output** - Both Markdown (source) and HTML (view) are available
- **No DB modifications** - This is a read/export operation only
