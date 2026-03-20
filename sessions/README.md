# sessions/ - Operational Memory

## Purpose

This folder stores **compressed session notes** for continuity across sessions.
Not a transcript dump — operational memory only.

## Structure

```
sessions/
├── TEMPLATE.md           # Session note template
├── README.md             # This file
└── YYYY-MM-DD/           # Session folders
    └── YYYY-MM-DD_HHMM.md # Individual session notes
```

## Why Not Full Transcripts?

### The Problem with Transcripts

- Full conversation logs are hard to parse at session start
- Important decisions get buried in noise
- Next session has to re-read everything to find context
- No clear "what changed" from previous session

### What We Store Instead

| What | Why |
|------|-----|
| **Topics covered** | Quick context refresh |
| **Key decisions** | What was decided, why |
| **Main mission candidates** | Today's priorities |
| **Current quest candidates** | Immediate next actions |
| **Plan items** | What to save to plans table |
| **Prompts/rules to reuse** | Next session can pick up directly |
| **Open questions** | Unfinished business |
| **Next session start points** | Jump back in quickly |

### What We Skip

- Raw conversation turns
- Exploration that led to nothing
- Testing prompts that didn't work
- Full context that can be re-loaded if needed

## Control Tower Fit

This structure supports the 0-a-control operating model:

1. **Start fast**: Next session reads 1-2 pages instead of full transcript
2. **Main mission focus**: Captures what was discussed as mission candidates
3. **Quest continuity**: "Current quest candidates" bridges to next session
4. **Plan integration**: Direct plan items ready for DB insertion
5. **Rule reuse**: Prompt fragments can be copied to next session

## AUTO.md Alignment

This sessions/ structure aligns with AUTO.md's session flow:

- Session starts by reading AUTO.md → AGENTS.md → current-state → plans
- Session ends by creating a note with: topics, decisions, missions, quests, plan-items
- Next session can read previous session note for context before diving into current-state

The note is **input to the next session's "read current state" phase**, not a replacement for it.
