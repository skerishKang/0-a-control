# Memory Model

## Objective
Define the shared memory layers that make the control tower resilient across sessions and across different coding agents.

## Design Principle
Do not force every agent to reread full conversation history.
Preserve full raw context, but operate from compressed current state whenever possible.

## Layers
### 1. Raw Logs
Purpose:
- preserve source truth
- allow audits and gap recovery
- protect against summary loss

Examples:
- full CMD conversations
- full CLI agent outputs
- important IDE conversation exports

### 2. Sessions
Purpose:
- group raw activity into meaningful work chunks
- summarize a work block without losing traceability

Each session should capture:
- agent
- model
- working directory
- project guess
- start time
- end time
- summary
- actions created
- files touched

### 3. Plans
Purpose:
- maintain execution structure

Plan buckets:
- `today`
- `short_term`
- `long_term`
- `recurring`
- `dated`

Each plan item should capture:
- title
- description
- priority rationale
- status
- due date if any
- related project
- related session ids
- related source ids

### 4. Current State
Purpose:
- provide the minimum operational context required to continue work quickly

Current state should include:
- current main mission
- current quest
- recent verdict
- top unfinished items
- dated pressures
- latest important decision
- recommended next quest
- restart point

## Read Order
Agents should read:

1. current state
2. plans
3. recent sessions
4. raw logs only if needed

## Storage Approach
### Canonical store
- local SQLite

### Exchange format
- JSON

### Human/agent brief format
- Markdown

### Large files
- keep on filesystem
- store references in the database

## Why SQLite First
- works locally without external dependencies
- strong enough for structured planning state
- easy for multiple local agents to query
- much better than scattered JSON once data grows
