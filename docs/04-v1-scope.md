# V1 Scope

## Build Now
- local-first control tower in `0-a-control`
- local SQLite memory store
- raw logs / sessions / plans / current state model
- morning / in-progress / end-of-day UI spec
- quest-based operational loop
- CMD-first workflow
- AI-guided quest verdicts: `done`, `partial`, `hold`
- unfinished-item strategy generation

## Defer
- Telegram ingestion
- email ingestion
- OpenClaw bridge
- remote sync
- Supabase or hosted-first architecture
- heavy UI editing workflows
- full passive auto-observation of every external window

## Multi-Agent Architecture
### Near term
- one main local control tower process
- one or more coding agents used for implementation
- mostly manual or semi-automatic cross-agent context transfer

### Later
- background log ingestion
- plan state auto-refresh
- per-channel import services
- shared contracts for sibling projects like `0-b-control` and `0-c-control`

## Success Criteria
V1 is successful when:

- the user can start the day from `0-a-control`
- the system can propose a single main mission
- the system can present a single current quest
- quest completion can be evaluated with explanation
- unfinished work becomes restart strategy rather than dead backlog
- the UI reflects the same planning state that the CMD conversation uses
