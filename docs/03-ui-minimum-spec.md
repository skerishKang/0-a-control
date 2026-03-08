# UI Minimum Spec

## Objective
Define the minimum web UI needed for `0-a-control` v1.

The UI is not the main thinking interface.
It is a readable situation board for the human operator.

## Screen 1: Morning
### Center card
`Main Mission`

Required fields:
- main mission title
- why it is first priority
- completion criteria
- immediate small action

### Support panels
Order:
1. due soon
2. unfinished from yesterday
3. new information
4. short-term plans
5. long-term plans
6. recurring plans

## Screen 2: In Progress
### Center card
`Current Quest`

Required fields:
- quest title
- why now
- completion criteria

### Support panels
- recent verdict
- next quest candidates
- plan change summary

## Screen 3: End of Day
### Center card
`Progress / Completion`

Required fields:
- completion summary for the day
- done count / partial count / hold count, or equivalent summary

### Support panels
- work actually done
- unfinished items
- unfinished-item strategies
- first quest for tomorrow

## UI Interaction Model
The UI is mostly read-oriented.

Primary interaction happens through CMD conversation.
The UI should make state easy to scan, not compete with the command workflow.

Minimal write interaction, if added later, should be limited to:
- acknowledgement
- status check
- lightweight flags

Do not make the UI the primary strategic editing surface in v1.
