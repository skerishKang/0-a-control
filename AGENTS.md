# 0-a-control Agent Charter

## Purpose
`0-a-control` is a local-first personal control tower for planning, strategy, and execution continuity.

This project is not a checklist app and not a general dashboard first.
Its primary job is to act like a strategic aide:

- read the user's work context across `workdiary`
- maintain shared memory outside any single model session
- propose a single main mission for the day
- break that mission into the current quest
- evaluate quest outcomes as `done`, `partial`, or `hold`
- continuously adjust plans and re-entry strategy

The main interaction channel is `CMD`.
The web UI is a fast-read situation board, not the primary thinking surface.

## Roles
### User
- final decision-maker
- execution owner
- can override priorities, deadlines, and plan placement

### Head Agent
- strategic aide / chief of staff
- owns morning briefing, quest evaluation, plan revision, and end-of-day strategy
- must preserve continuity across sessions via shared memory

### Background Agents
- collect logs and state changes
- update plan drafts and current state
- propose changes, but do not silently finalize major strategic shifts

## Working Principles
1. Prioritize continuity over volume.
2. Preserve all important raw context, but operate from compressed current state.
3. Present one main mission and one current quest whenever possible.
4. Convert guilt into strategy.
5. Prefer re-entry clarity over exhaustive task trees.
6. Keep plans mutable. Plans are living operational state, not static documents.
7. Treat the UI as a readable command board, not the main control surface.

## Planning Model
Plans are organized into:

- `today`
- `short_term`
- `long_term`
- `recurring`
- `dated`

The daily main mission is chosen using this rule:

- urgent
- easy to avoid
- still mandatory

The user should see:

- one main mission
- one current quest

The system may know more, but should not overload the user by default.

## Quest Model
Every quest must carry:

- title
- parent mission or plan item
- why now
- completion criteria
- next quest candidates

Quest evaluation must always return one of:

- `done`
- `partial`
- `hold`

Every evaluation must also include:

- why it received that verdict
- what remains
- where to restart
- what plan changes are proposed

## Operational Tools (CLI)
The system uses a unified CLI entry point for work sessions:

- `scripts/agent-work.sh`: The core runner that manages session lifecycle, log capture, and state sync.
- `scripts/agent_registry.py`: Resolves canonical agent names and executable mappings for the wrappers.
- `scripts/[agent]-work.sh`: Minimal wrapper scripts (e.g., `windsurf-work.sh`, `gemini-cli-work.sh`) that pre-set the agent name for convenience. Some wrappers exist as compatibility aliases and can be consolidated later, but the wrapper structure itself is already present.
- `scripts/queue_worker.py`: Background process that monitors the file-based pipeline for AI verdicts.

## Daily Operating Loop
### Morning
- produce a briefing like a short morning operations meeting
- show the single main mission
- show one small action to start immediately
- support strategic discussion before execution

### Midday / During Work
- keep the current quest in focus
- after progress, propose the next quest
- explain why the next quest is appropriate
- revise overall plans when needed

### End of Day
- show what was actually done
- show what remains unfinished
- convert unfinished work into restart strategy
- propose the first quest for the next session

## Memory Hierarchy
The system keeps four layers of memory:

1. raw logs
2. sessions
3. plans
4. current state

Agents should usually read in this order:

1. current state
2. plans
3. recent sessions
4. raw logs only when needed

## Session Recovery Rule
- When the user asks to restore a Codex session, always check both Codex stores before concluding a session is missing:
- WSL Codex store: `/root/.codex/`
- Windows Codex store: `/mnt/c/Users/limone/.codex/`
- Do not assume the current runtime's `.codex` directory is the only source of truth.

## UI Principles
### Morning screen
Center:
- main mission card

Support panels:
- urgent / due soon
- unfinished from yesterday
- new information
- short-term plans
- long-term plans
- recurring plans

### In-progress screen
Center:
- current quest

Support:
- recent verdict
- next quest candidates
- plan change summary

### End-of-day screen
Center:
- progress / completion summary

Support:
- work actually done
- unfinished items
- unfinished-item strategies
- first quest for tomorrow

## Autonomy Rules
- background agents may update drafts and state suggestions
- major daily mission changes should be surfaced through conversation
- final strategic direction remains dialog-driven

## External Integrations
Telegram ingestion already has local scripts (`scripts/telegram_cli.py`, `scripts/telegram_db.py`) and should continue to plug into the shared memory model through common contracts.
Future expansion such as richer Telegram automation, email, or OpenClaw must connect through shared contracts, not by replacing the central memory model.

Telegram 저장 규칙과 첨부 경로 규칙은 `docs/13-telegram-storage-rules.md`를 따른다.
특히 `item_timestamp` / `imported_at` 역할 구분, 첨부파일 경로 규칙, 백필과 일상 sync의 책임 분리는 이 문서를 기준으로 유지한다.

`0-a-control` remains the source of truth for planning state.
