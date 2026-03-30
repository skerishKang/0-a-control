# Operating Loop

## Objective
Define the concrete daily loop for the control tower so any agent or developer can implement the same behavior.

## Core Loop
The system runs as a strategic execution loop:

1. morning briefing (with archive context)
2. mission selection
3. quest execution (with archive as needed)
4. quest evaluation
5. plan revision
6. end-of-day report
7. next-session restart strategy

## Recovery Reading Order (All Phases)

Every phase follows this reading order:

1. **current urgent state** — current_state API
2. **related sessions archive** — only relevant .md files
3. **sessions_html/** — quick browser search if needed
4. **raw transcript / DB** — additional verification
5. **summary/current quest** — compressed final state

**Important**: Read only what's relevant. Not all archives, every time.

## Morning Flow

### Reading Order (1 minute)
1. **current state** (10s) — today's mission, current quest
2. **related archive** (30s) — yesterday's session on same topic, if any
3. **mission decision** (20s) — pick one main mission

### Inputs
- current state
- related sessions archive (selective, not all)
- dated items
- unfinished items from the previous day
- new information since last session

### Outputs
- single main mission for the day
- explanation for why it is the top priority
- one immediate small action
- supporting context panels in the UI

### Tone
Morning output should feel like a short operations briefing:

- concise
- direct
- priority-first
- action-biased

## During Work

### Reading Order (30 seconds, only when needed)
- **current quest** — always in focus
- **related archive** — only when context is lost
- **sessions_html** — quick scan if topic is unclear

### Principle
The system should keep the user focused on one current quest.

### Expected behavior
- explain what the current quest is
- accept progress updates through CMD
- evaluate whether the quest is done, partial, or hold
- propose the next quest
- explain why that next quest is appropriate
- revise plan placement when required

### When To Read Archive During Work
| Situation | Action |
|-----------|--------|
| Context is lost | Read relevant session Dialogue |
| New session starts | Run `codex 세션 복원해줘` or read archive |
| Quest completed | Verify, then propose next quest |

### Next Quest Selection Priority
1. dated urgency
2. short-term continuation
3. long-term item that now needs action
4. recurring maintenance
5. new incoming information

## Quest Evaluation
Every quest evaluation must contain:

- verdict: `done`, `partial`, or `hold`
- reason
- remaining gap against the original completion criteria
- suggested restart point
- plan adjustments

### Done
Use when the original completion criteria are satisfied.

### Partial
Use when meaningful progress happened but the completion criteria were not fully met.

### Hold
Use when stopping is the correct strategic choice for now.

## End-of-Day Flow

### Reading Order (2 minutes)
1. **today's sessions** (30s) — check archive was saved
2. **unfinished items** (1m) — what remains
3. **restart strategy** (30s) — tomorrow's first action

### Primary output order
1. what was actually done
2. what remains unfinished
3. strategy for unfinished items
4. first quest for the next session

### Archive Check
```bash
ls sessions/$(date +%Y-%m-%d)/
```
Verify today's sessions are properly archived.

### Restart Strategy
Leave a compressed sentence for tomorrow's recovery:
```
내일 아침 시작점: [topic]의 [specific state]
```

### Tone
The end-of-day output is:

1. report-like
2. reflective
3. strategic

## Human Interaction Model
The user mainly needs to tell the system:

- that the day has started
- what mission or project is being entered
- that a quest should be evaluated
- that the day is ending

The system should do the rest of the structuring and revision work.
