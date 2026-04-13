# Operating Loop

## Objective
Define the concrete daily loop for the control tower so any agent or developer can implement the same behavior.

## Core Loop
The system runs as a strategic execution loop:

1. morning briefing
2. mission selection
3. quest execution
4. quest evaluation
5. plan revision
6. end-of-day report
7. next-session restart strategy

## Morning Flow
### Inputs
- current state
- dated items
- unfinished items from the previous day
- new information since last session
- short-term and long-term pressure

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
### Principle
The system should keep the user focused on one current quest.

### Expected behavior
- explain what the current quest is
- accept progress updates through CMD
- evaluate whether the quest is done, partial, or hold
- propose the next quest
- explain why that next quest is appropriate
- revise plan placement when required

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
### Primary output order
1. what was actually done
2. what remains unfinished
3. strategy for unfinished items
4. first quest for the next session

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
