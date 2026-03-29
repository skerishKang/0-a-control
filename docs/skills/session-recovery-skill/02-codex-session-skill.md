# Codex Session Recovery Skill Draft

## Skill Name
`codex-session-recovery`

## Purpose
Recover prior Codex work context from local session sources and reconstruct a usable working state.

## Data Sources
### Required
- `~/.codex/state_5.sqlite`
- `~/.codex/history.jsonl`

### Optional
- `G:\Ddrive\BatangD\task\workdiary\0-a-control\sessions`
- `G:\Ddrive\BatangD\task\workdiary\0-a-control\sessions_html`

## What This Skill Must Do
1. Find recent Codex threads from sqlite
2. Identify the most relevant thread(s)
3. Recover the user-message flow from `history.jsonl`
4. Reconstruct current working state by topic
5. Distinguish:
   - raw session source
   - summarized recovery
   - display/view artifacts

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
  - sqlite metadata
  - history.jsonl user messages
  - local sessions folder
  - human-provided context
- If assistant replies are missing, state that clearly
- Prefer recovery from evidence over guesswork

## When To Use
- when a long Codex session exists
- when the user wants to continue prior work
- when handoff quality is uncertain

## When Not To Use
- when only a single simple thread exists
- when the user already has a trusted handoff summary

