# Session Recovery Operational Rollout

## Goal
Put the session recovery skills into real daily operation so that:
- long Codex sessions can be resumed reliably
- agent changes do not destroy continuity
- raw source, summary, and display remain clearly separated

## Adopted Skills

### Kilo
- `.kilocode/skills/codex-session-recovery/SKILL.md`

### Antigravity
- `docs/skills/session-recovery-skill/SKILL.md`

## Standard Use Cases

### 1. Resume after a long break
Use when:
- work stopped for hours or days
- current state is unclear
- multiple topics were mixed in one session

Expected result:
- topic-by-topic recovery
- next immediate action
- whether extra handoff is needed

### 2. Switch agents
Use when:
- Kilo -> Antigravity
- Antigravity -> Kilo
- Codex session needs to be resumed from another tool

Expected result:
- same work context restored from local evidence

### 3. Recover after partial failure
Use when:
- shell/tools are broken
- UI still works but logs are scattered
- user wants to continue without re-explaining everything

Expected result:
- current operational state reconstructed from Codex evidence

## Operational Rule

### First
Try session recovery before writing a new handoff.

### Then
If recovery is insufficient:
- create a short handoff only for missing topics
- do not rewrite what recovery already restored correctly

## Recovery Priority
When the skill runs, it should restore in this order:
1. `board-v2`
2. `0-a-control skills`
3. `메가존`
4. `아파트`
5. other topics

## Required Output Contract
For each topic:
- what was done
- current state
- what remains
- next immediate action

At the end:
- top priority to resume now
- whether recovery was sufficient
- whether extra handoff is needed

## Standard Invocation Phrases

### General
- `이전 codex 세션 복원해줘`
- `codex 세션 읽어서 이어갈 일 정리해줘`
- `resume previous codex work`

### Topic-specific
- `board-v2 관련 codex 세션 복원해줘`
- `메가존 관련 codex 세션 정리해줘`
- `아파트 관련 codex 세션 복원해줘`

## When Not To Use Session Recovery
- when the user already has a fresh trusted handoff
- when the thread is tiny and can be reread directly
- when the work is brand new and has no prior session context

## Important Boundary
- `state_5.sqlite` and `history.jsonl` are raw evidence
- `sessions/` and `sessions_html/` are support layers
- HTML is never the source of truth
- summaries are operational aids, not replacements for raw logs

## Recommended Team Habit
1. Long session ends
2. Next session begins with recovery first
3. Only missing gaps get extra handoff notes
4. Work resumes from restored current state

