# Implementation Handoff

## Objective
Give a coding model or engineer a decision-complete starting brief for v1 implementation.

## Build Target
Implement a local-first `0-a-control` app with:

- local SQLite database
- small local web server
- read-oriented web UI
- CMD-first planning workflow
- quest-based state updates

## Non-Goals for V1
Do not build yet:

- Telegram ingestion
- email ingestion
- OpenClaw bridge
- remote hosting-first mode
- auth or multi-user system
- rich UI editing workflows
- full passive monitoring of every external app window

## Required Runtime Shape
- one local app process is enough for v1
- background tasks may run in-process initially
- the UI may poll for updates instead of requiring real-time sockets in v1

## Suggested Technical Shape
Recommended minimal stack:

- Python local server
- SQLite
- simple HTML/CSS/JS frontend

Reason:
- easiest local filesystem access
- easiest SQLite use
- easiest background loop integration
- fastest path to a working control tower

## Core Features
### Feature 1: Morning Board
- read `current_state` and `plan_items`
- render the main mission card
- render support panels in this order:
  - due soon
  - unfinished from yesterday
  - new information
  - short-term plans
  - long-term plans
  - recurring plans

### Feature 2: In-Progress Board
- render current quest as the dominant card
- show recent verdict
- show next quest candidates
- show plan change summary

### Feature 3: End-of-Day Board
- render completion/progress summary
- show work actually done
- show unfinished items
- show unfinished strategies
- show first quest for tomorrow

### Feature 4: Quest Evaluation API
Support quest verdict updates with:

- `done`
- `partial`
- `hold`

Each update must store:

- verdict
- reason
- restart point
- next quest hint
- plan impact

### Feature 5: Current State Refresh
Provide a way to update `current_state` from quest and plan changes.

For v1 this can be:
- explicit refresh command
- server-side helper
- background loop

## Required API Surface
Keep the API small.

Suggested endpoints:

- `GET /api/current-state`
- `GET /api/plans`
- `GET /api/quests`
- `GET /api/sessions/recent`
- `POST /api/quests/evaluate`
- `POST /api/current-state/refresh`
- `GET /api/briefs/latest`

## UX Rules
- the UI is for fast reading, not heavy editing
- the main mission must dominate the morning screen
- the current quest must dominate the in-progress screen
- the completion summary must dominate the end-of-day screen
- avoid clutter and avoid multi-column overload around the primary card

## Agent Workflow Rule
The coding agent implementing this should preserve:

- CMD-first human workflow
- single main mission
- single current quest
- quest verdict loop
- unfinished-to-strategy conversion

Do not accidentally turn the app into a generic kanban board or note-taking tool.

## Suggested Build Order
1. database schema and initialization
2. seed helpers for current state and sample plan data
3. local API server
4. morning screen
5. in-progress screen
6. end-of-day screen
7. quest evaluation flow
8. current state refresh logic

## Acceptance Criteria
Implementation is good enough when:

- the app can run locally with a single command
- the morning screen clearly shows one main mission
- quest evaluation updates can change the visible state
- unfinished items can show restart strategy
- the UI reflects the same planning state that agents can read from SQLite

## Verdict Provider Rule
- `POST /api/quests/report` should use a real model verdict when available.
- Configure this through `CONTROL_TOWER_VERDICT_COMMAND`.
- The command must read the prompt from stdin and print JSON only with:
  - `verdict`
  - `reason`
  - `restart_point`
  - `next_hint`
  - `plan_impact`
- If the command is not configured or fails, the system must fall back to heuristic verdict generation instead of failing the workflow.

Example with Gemini CLI wrapper:

```bash
export CONTROL_TOWER_VERDICT_COMMAND="python3 scripts/gemini_verdict.py"
export GEMINI_VERDICT_MODEL="gemini-2.5-flash"
python3 scripts/server.py
```
