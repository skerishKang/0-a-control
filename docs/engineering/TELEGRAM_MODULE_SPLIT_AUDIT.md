# Telegram Module Split Audit

**Issue:** #85  
**Date:** May 11, 2026  
**Status:** Audit Complete - Implementation Pending

## 1. Target Files and Current Line Counts

| File | Lines | Status |
|------|-------|--------|
| scripts/telegram_cli.py | 666 | ❌ Exceeds 500 |
| scripts/telegram_service.py | 520 | ❌ Exceeds 500 |
| scripts/telegram_db.py | 56 | ✓ Below 500 |

## 2. File Responsibilities

### scripts/telegram_cli.py (666 lines)

**CLI Command Responsibilities:**
- `list-sources` - List all Telegram sources from DB
- `sync-core` - Sync core Telegram sources
- `sync-status` - Show sync status for core sources
- `telegram-status` - Show Telegram connection status
- `import-chat` - Import chat messages for a source
- `backfill-chat` - Backfill historical messages
- `fill-missing-attachments` - Download missing attachments
- `attachment-status` - Show attachment status for a source

**Core Functions:**
- `get_core_sources_sync_status()` - Query DB for core source sync status
- `run_sync_core()` - Orchestrate core source sync
- `import_chat()` - Main import logic with DB insert
- `backfill_chat()` - Batch backfill logic
- `fill_missing_attachments()` - Attachment fill logic
- `import_message_ids()` - Specific message import

**Parsing/Normalization Helpers:**
- `_normalize_message_timestamp()` - Convert various timestamp formats to ISO
- `_format_bytes()` - Format byte sizes for display
- `AttachmentProgressReporter` - Progress callback class
- `_metadata_file_size()` - Extract file size from metadata JSON

**DB/Storage Touchpoints:**
- Uses `telegram_db.get_db_connection()`
- Writes to `external_inbox` table
- Updates `telegram_sources` table

**Dependencies:**
- `telegram_db` - Database connection
- `telegram_service` - `fetch_messages`, `get_telegram_status`, `get_telegram_session_lock_status`

**Imports elsewhere:**
- `telegram_attachment_status.py` imports `show_attachment_status`
- `server.py` imports `get_core_sources_sync_status`, `run_sync_core`

### scripts/telegram_service.py (520 lines)

**Telegram Client/Session Handling:**
- `_get_telegram_client()` - Create Telethon client
- `_connect_client()` - Connect and authenticate
- `_disconnect_client()` - Cleanup connection
- `acquire_telegram_session_lock()` - Process-level lock
- `_clear_session_lock()` - Lock cleanup

**Message/Chat Fetch Logic:**
- `fetch_messages()` - Main fetch with lock management
- `fetch_chats()` - Fetch dialogs/list
- `_fetch_messages_async()` - Async message fetching
- `_fetch_chats_async()` - Async chat fetching

**Attachment Handling:**
- `_download_attachment()` - Async download with progress
- `_inspect_attachment()` - Extract attachment metadata
- `_build_attachment_path()` - Construct storage path

**Status/State:**
- `get_telegram_status()` - Overall connection status
- `get_telegram_session_lock_status()` - Lock status

**Parsing/Normalization Helpers:**
- `_classify_message_type()` - Determine message type (image/audio/video/file/text)
- `_original_attachment_name()` - Extract original filename
- `_safe_path_part()` - Sanitize filename
- `_message_sender_label()` - Extract sender display name

**Dependencies:**
- `telegram_db` - `DATA_DIR` for paths

**Imports elsewhere:**
- `server.py` imports `fetch_chats`, `fetch_messages`, `get_telegram_status`
- `telegram_cli.py` imports several functions

## 3. Coupling Risks

### High Coupling (Difficult to Extract)

1. **Telegram Session/Lock Management**
   - Both files share session lock mechanism
   - `telegram_service` owns lock, but `telegram_cli` calls service functions that use locks
   - Lock file path and TTL constants are in service

2. **Status Reporting**
   - `telegram_service` writes status to `telegram_status.json`
   - `telegram_cli.get_core_sources_sync_status()` reads from DB
   - Both contribute to overall "sync status" view

3. **Runtime Data Paths**
   - Both write to `DATA_DIR/runtime/`
   - Service writes status and cache files
   - CLI writes to DB

4. **Server-Visible Functions**
   - `server.py` imports from both files
   - `get_core_sources_sync_status`, `run_sync_core` from CLI
   - `fetch_chats`, `fetch_messages`, `get_telegram_status` from service

### Low Coupling (Safe to Extract)

1. **Pure Parsing Helpers in telegram_cli.py**
   - `_normalize_message_timestamp()` - Pure function
   - `_format_bytes()` - Pure function
   - `_metadata_file_size()` - Pure function

2. **Pure Parsing Helpers in telegram_service.py**
   - `_classify_message_type()` - Pure function
   - `_safe_path_part()` - Pure function
   - `_message_sender_label()` - Pure function
   - `_mask_phone()` - Pure function

3. **Attachment Progress Reporter (CLI)**
   - `AttachmentProgressReporter` class - No external dependencies

## 4. Safe Split Phases

### Phase 1: Pure Helpers Extraction (Lowest Risk)

**Target:** Extract pure parsing/formatting functions to `telegram_helpers.py`

**From telegram_cli.py:**
- `_normalize_message_timestamp()` (lines 21-31)
- `_format_bytes()` (lines 37-47)
- `_metadata_file_size()` (lines 105-117)

**From telegram_service.py:**
- `_classify_message_type()` (lines 240-251)
- `_safe_path_part()` (lines 231-237)
- `_message_sender_label()` (lines 452-464)
- `_mask_phone()` (lines 223-228)

**Expected result:** ~40 lines moved, minimal risk

### Phase 2: CLI Argument Parsing Extraction

**Target:** Separate argparse logic from business logic

**Changes:**
- Keep command handler functions in CLI
- Move `argparse` setup to separate module or keep inline
- This is mostly structural, not functional

**Expected result:** No net line reduction, better organization

### Phase 3: Attachment Progress Handler

**Target:** Extract `AttachmentProgressReporter` to separate module

**Current:** Lines 50-102 in CLI
**Extraction:** Move to `telegram_progress.py` or combine with Phase 1 helpers

**Expected result:** ~52 lines moved

### Phase 4: Service Fetch/Sync Helpers (Higher Risk)

**Target:** After test coverage established, extract:
- Message download orchestration
- Chat fetch orchestration

**Risk:** Higher - requires async handling, lock management knowledge

### Phase 5: Deep Client/Session Boundary (Highest Risk)

**Target:** If needed, deeper refactor of Telethon client management

**Risk:** Highest - touches credential handling, session state

## 5. Explicit Non-Goals

- ❌ No credential/session migration to other storage
- ❌ No Telegram API behavior changes
- ❌ No server route refactor (tracked by #83)
- ❌ No backend DB/session refactor (#84 completed)
- ❌ No frontend/CSS changes (tracked by #86/#87)
- ❌ No runtime data changes
- ❌ No file moves outside scripts/ directory

## 6. Validation Requirements for Implementation PRs

Each implementation PR must pass:

```bash
# Syntax validation
python -m py_compile scripts/telegram_cli.py
python -m py_compile scripts/telegram_service.py
python -m py_compile scripts/telegram_db.py

# Import check (if new module added)
python -c "from scripts.telegram_cli import *"
python -c "from scripts.telegram_service import *"

# Server smoke if server-visible behavior affected
python scripts/smoke_server.py

# Tests (if applicable)
python -m pytest tests/test_telegram_*.py

# No runtime data staging
# No Telegram/private payload dumps
```

## 7. Recommended First Implementation PR

### Phase 1: Extract Pure Helpers

**Target Module:** `scripts/telegram_helpers.py` (new file)

**Functions to extract:**
- From CLI: `_normalize_message_timestamp`, `_format_bytes`, `_metadata_file_size`
- From Service: `_classify_message_type`, `_safe_path_part`, `_message_sender_label`, `_mask_phone`

**Expected changes:**
- Create `telegram_helpers.py` (~50 lines)
- Update imports in `telegram_cli.py`
- Update imports in `telegram_service.py`

**Risk Level:** **LOW**
- Pure functions with no side effects
- No behavior changes
- Easy to rollback (remove new file, restore imports)

**Line reduction estimate:**
- `telegram_cli.py`: 666 → ~610 (-56 lines)
- `telegram_service.py`: 520 → ~470 (-50 lines)
- New file: ~50 lines

**Rollback Plan:**
1. Delete `telegram_helpers.py`
2. Restore original import statements in both files
3. No DB or runtime changes to revert

## 8. Summary

| Phase | Description | Risk | Line Reduction |
|-------|-------------|------|----------------|
| 1 | Pure helpers extraction | LOW | ~100 lines |
| 2 | CLI structure | LOW | Organizational |
| 3 | Progress handler | LOW | ~50 lines |
| 4 | Fetch/sync helpers | MEDIUM | ~100 lines |
| 5 | Client/session boundary | HIGH | TBD |

**Recommended start:** Phase 1 (pure helpers extraction) - lowest risk, good warm-up
