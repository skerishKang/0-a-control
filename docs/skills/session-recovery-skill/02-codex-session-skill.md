# Codex Session Recovery Skill Draft

## Skill Name
`codex-session-recovery`

## Purpose
Recover prior Codex work context from local session sources and reconstruct a usable working state.

## Data Sources

### Primary
- `sessions/` — Full session archive (Markdown with Dialogue + Transcript)
- `sessions_html/` — HTML display layer for quick browsing

### Secondary
- `~/.codex/state_5.sqlite` — Thread metadata
- `~/.codex/history.jsonl` — User message log

### Tertiary
- `data/control_tower.db` — Source records (raw DB)

## Recovery Reading Order
1. **current urgent state** check
2. **sessions/ archive** — read full session files
3. **sessions_html/** — quick browser search if needed
4. **sqlite / history.jsonl** — additional verification
5. **summary/current quest** — compressed final state

## What This Skill Must Do
1. Find relevant sessions from `sessions/` archive
2. Read full Dialogue + Transcript for each session
3. Identify the most relevant session(s)
4. Reconstruct current working state by topic
5. Distinguish:
   - raw session source (DB, transcripts)
   - full archive (sessions/ .md files)
   - display layer (sessions_html/ .html files)
   - summarized recovery (final output)

## Recovery Topics
- `board-v2`
- `0-a-control skills`
- `메가존`
- `아파트`
- `기타 운영 이슈`

## Output Format
For each topic:
- what was done
- current state
- what remains
- next immediate action

Then always include:
1. most important next topic
2. whether recovery is sufficient
3. whether an extra handoff document is needed

## Rules
- Never pretend summary is the raw source
- Always identify whether a claim came from:
  - sessions/ archive (full Dialogue)
  - sqlite metadata
  - history.jsonl user messages
  - human-provided context
- If assistant replies are missing, state that clearly
- Prefer recovery from evidence over guesswork
- Read full archive before summarizing
- HTML is never source of truth

## When To Use
- when a long Codex session exists
- when the user wants to continue prior work
- when handoff quality is uncertain

## When Not To Use
- when only a single simple thread exists
- when the user already has a trusted handoff summary
