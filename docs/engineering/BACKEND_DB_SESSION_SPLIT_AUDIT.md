# Backend DB/Session Module Split Audit

**Date**: 2026-05-11
**Issue**: #84
**Status**: Audit

## Target Files

| File | Lines | Primary Responsibility |
|------|-------|------------------------|
| `scripts/db_state.py` | 792 | State queries, workdiary, briefs |
| `scripts/db_sessions.py` | 571 | Session lifecycle, source records |
| `scripts/db_base.py` | 513 | DB connection, schema, helpers |

Note: `scripts/db.py` (121 lines) is a re-export aggregator and is NOT over the target.

---

## Current Architecture

```
scripts/db.py (re-export aggregator)
  └── imports from:
      ├── scripts/db_base.py    (connect, schema, helpers)
      ├── scripts/db_sessions.py (session ops)
      ├── scripts/db_state.py    (state queries)
      ├── scripts/db_ops.py      (current_state, quests)
      ├── scripts/plan_ops.py    (plans, briefs)
      ├── scripts/verdict_ops.py (verdicts)
      └── ...other modules

scripts/server.py
  └── from scripts import db as _db
      └── aliases ~20 functions from db.py
```

The three target files are **already separate modules** - they're not a single large file. The issue is each module individually exceeds 500 lines.

---

## File Responsibilities

### scripts/db_base.py (513 lines)

**Data model/state ownership**:
- DB path configuration (ROOT_DIR, DATA_DIR, DB_PATH, WORKDIARY_DIR)
- UTC timezone constant

**Persistence/read/write boundaries**:
- `connect()` context manager - DB connection factory
- `init_db()` - schema initialization
- `migrate_search_state()` - FTS migration

**Shared constants/helpers**:
- `now_iso()` - timestamp helper
- `get_db_path()` - path resolution
- `TELEGRAM_INBOX_SCHEMA` and `SCHEMA` - table definitions
- `row_to_dict()`, `rows_to_dicts()` - row conversion utilities
- `upsert_state()`, `merge_metadata()` - state helpers
- `record_event()` - event logging

**Import dependencies**:
- stdlib only (sqlite3, pathlib, datetime, contextlib)

**Likely safe extraction candidates**:
- Row conversion utilities (`row_to_dict`, `rows_to_dicts`) - pure functions, no DB dependency in signatures
- `now_iso()` - trivial helper
- `get_db_path()` - trivial helper
- Constants (ROOT_DIR, DATA_DIR, etc.) - constants only

**Unsafe extraction candidates**:
- `connect()` - core DB abstraction, used by everything
- `SCHEMA` / `TELEGRAM_INBOX_SCHEMA` - schema definitions, needed by init
- `init_db()` - schema creation, needs SCHEMA constants

---

### scripts/db_sessions.py (571 lines)

**Data model/state ownership**:
- Session lifecycle (start, end, update summary)
- Source records (chat messages, transcripts)

**Session lifecycle functions**:
- `start_session()`
- `end_session()`
- `update_session_summary()`
- `close_latest_active_session_for_agent()`

**Session query functions**:
- `get_session()`
- `get_session_view_model()`
- `get_resume_context()`

**Source record functions**:
- `append_source_record()`
- `get_source_records()`

**Internal helpers**:
- `_load_current_state()` - loads state for resume context
- `_compact_text()` - text truncation
- `_load_transcript_excerpt()` - loads recent messages
- `_format_resume_prompt()` - formats prompt

**Import dependencies**:
- `scripts.db_base` (connect)
- stdlib only (uuid, json, datetime, collections)

**Likely safe extraction candidates**:
- Text helpers (`_compact_text()`) - pure function
- `_load_transcript_excerpt()` - query helper

**Unsafe extraction candidates**:
- Session lifecycle functions - core business logic
- `get_session_view_model()` - complex query with multiple joins
- `get_resume_context()` - business logic with state lookups

---

### scripts/db_state.py (792 lines)

**Data model/state ownership**:
- Workdiary file system queries
- External inbox overview
- Brief generation
- Current state refresh

**Workdiary functions**:
- `get_workdiary_top_level()`
- `get_workdiary_priority_candidates()`

**External inbox functions**:
- `get_external_inbox_overview()`
- `get_external_inbox_source_messages()`

**State refresh functions**:
- `refresh_current_state()`
- `_refresh_current_state_impl()`

**Brief/summary functions**:
- `generate_morning_brief()`
- `build_day_progress_summary()`
- `generate_priority_recommendation()`

**Helper functions**:
- `build_workdiary_item()` - dict builder
- `build_today_done_quests()` - query helper
- `build_tomorrow_first_quest()` - query helper
- `extract_completion_criteria_for_plan()` - query helper
- `latest_decision_summary()` - query helper

**Import dependencies**:
- `scripts.db_base` (connect, SCHEMA)
- stdlib only (pathlib, datetime, sqlite3, uuid)

**Likely safe extraction candidates**:
- Dict builders (`build_workdiary_item()`) - pure function
- Brief generation helpers (`extract_completion_criteria_for_plan()`) - query helper

**Unsafe extraction candidates**:
- Most query functions - complex SQL with business logic
- State refresh functions - critical system state
- Brief generation - business logic

---

## Proposed Split Phases

### Phase 1: Constants and Pure Helpers Only

**Goal**: Smallest safe reduction with zero behavior change risk.

**Files to modify**: `scripts/db_base.py`

**Extract to** `scripts/db_helpers.py` (new):
- `now_iso()` - timestamp
- `get_db_path()` - path resolution
- `row_to_dict()` - row conversion
- `rows_to_dicts()` - rows conversion

**Keep in db_base.py**:
- `connect()` context manager
- Schema definitions
- `init_db()` and migration functions
- `upsert_state()`, `merge_metadata()`, `record_event()` - need connect()

**Risk level**: LOW
**Expected reduction**: ~30-40 lines from db_base.py
**Rollback**: Delete import, re-import from db_base

### Phase 2: Session Query Helpers

**Goal**: Separate complex query construction from business logic.

**Files to modify**: `scripts/db_sessions.py`

**Extract to** `scripts/db_session_queries.py` (new):
- `_compact_text()`
- `_load_transcript_excerpt()`
- `_format_resume_prompt()`

**Keep in db_sessions.py**:
- All public session functions
- `_load_current_state()` - needs db_base.connect()

**Risk level**: LOW
**Expected reduction**: ~20-30 lines from db_sessions.py
**Rollback**: Inline the helpers

### Phase 3: Workdiary Query Helpers

**Goal**: Separate workdiary-specific helpers from state queries.

**Files to modify**: `scripts/db_state.py`

**Extract to** `scripts/db_workdiary_helpers.py` (new):
- `build_workdiary_item()`
- `build_today_done_quests()` - returns list of dicts
- `build_tomorrow_first_quest()` - returns single dict
- `extract_completion_criteria_for_plan()`

**Keep in db_state.py**:
- External inbox functions (telegram-specific)
- State refresh functions
- Brief generation functions

**Risk level**: MEDIUM - these helpers still use `connect()`

### Phase 4: External Inbox Separation (Future)

**Goal**: Separate Telegram inbox logic from generic state queries.

**Files to modify**: `scripts/db_state.py`

**Extract to** `scripts/db_inbox.py` (new):
- `get_external_inbox_overview()`
- `get_external_inbox_source_messages()`

**Keep in db_state.py**:
- Workdiary functions
- State refresh
- Brief generation

**Risk level**: MEDIUM-HIGH - changes import graph

---

## Non-Goals

- No API behavior changes
- No runtime data migration
- No server route refactor (tracked by #83)
- No Telegram module refactor (tracked by #85)
- No frontend refactor (tracked by #86, #87)
- No migration to ORM
- No schema changes

---

## Validation Required for Future Implementation PRs

For each PR:
1. `python -m py_compile scripts/db_base.py` - syntax check
2. `python -m py_compile scripts/db_sessions.py` - syntax check
3. `python -m py_compile scripts/db_state.py` - syntax check
4. `python -m py_compile scripts/<new_module>.py` - syntax check
5. `python scripts/smoke_server.py` - smoke validation (if db behavior changes)
6. `python -m pytest` - run existing tests if any

No runtime data staging in PR descriptions or commit messages.

---

## Recommended First Implementation PR

**Candidate**: Phase 1 - Extract pure helpers from db_base.py

**Rationale**:
- Smallest possible change
- Pure functions with no external dependencies
- Zero behavior change risk
- Easy to rollback

**Expected files**:
- `scripts/db_helpers.py` (new, ~30 lines)
- `scripts/db_base.py` (modified, remove ~30 lines)

**Risk level**: LOW

**Changes**:
1. Create `scripts/db_helpers.py` with extracted functions
2. Update `scripts/db_base.py` to import from `db_helpers`
3. Update `scripts/db.py` to also re-export from `db_helpers` for backward compatibility
4. Verify `python -m py_compile` passes
5. Verify `python scripts/smoke_server.py` passes

**Rollback plan**: Revert commit, functions automatically available via db_base re-exports

---

## Line Count Projections

| File | Current | Phase 1 | Phase 2 | Phase 3 | Phase 4 |
|------|---------|---------|---------|---------|---------|
| scripts/db_base.py | 513 | ~480 | - | - | - |
| scripts/db_sessions.py | 571 | - | ~540 | - | - |
| scripts/db_state.py | 792 | - | - | ~720 | ~600 |
| scripts/db_helpers.py | NEW | ~30 | - | - | - |
| scripts/db_session_queries.py | NEW | - | ~30 | - | - |
| scripts/db_workdiary_helpers.py | NEW | - | - | ~70 | - |
| scripts/db_inbox.py | NEW | - | - | - | ~120 |
| scripts/db.py (re-export) | 121 | +5 | - | - | - |

Note: Phase 4 (db_inbox) only reduces db_state by ~172 lines, which may not justify the complexity. Consider whether partial extraction is sufficient.

---

## Open Questions

1. Is the Phase 4 `db_inbox.py` extraction worth the complexity, or should `db_state.py` remain as-is above 500 lines?
2. Should the re-export pattern in `db.py` be preserved, or should consumers import from specific modules directly?
3. Is there existing test coverage for the session/state query functions?