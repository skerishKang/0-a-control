# Data Schema

## Objective
Define the minimum SQLite schema for `0-a-control` v1.

The schema is optimized for:

- agent-readable continuity
- quest-based execution
- shared state across multiple coding agents
- traceability from raw conversation to current planning state

## Design Rules
- SQLite is the canonical store.
- Raw logs remain recoverable.
- Every higher layer should be traceable down to lower layers when possible.
- `current_state` is the operational entry point for most agents.
- Do not optimize for perfect normalization before operational usefulness.

## Table: `source_records`
Raw source truth.

Suggested columns:

- `id` TEXT PRIMARY KEY
- `source_type` TEXT NOT NULL
  - examples: `cmd`, `ide`, `manual`, `import`
- `source_name` TEXT NOT NULL
  - canonical examples: `codex`, `gemini-cli`, `antigravity`, `windsurf`, `kilo`, `opencode`
- `session_id` TEXT
- `project_key` TEXT
- `working_dir` TEXT
- `role` TEXT
  - examples: `user`, `assistant`, `system`, `tool`
- `content` TEXT NOT NULL
- `created_at` TEXT NOT NULL
- `metadata_json` TEXT

Notes:
- This table stores conversation turns or other atomic raw entries.
- Avoid heavy processing assumptions here.

## Table: `sessions`
One meaningful work block.

Suggested columns:

- `id` TEXT PRIMARY KEY
- `agent_name` TEXT NOT NULL
  - canonical values: `codex`, `gemini-cli`, `antigravity`, `windsurf`, `kilo`, `opencode`
- `model_name` TEXT
- `source_type` TEXT NOT NULL
- `project_key` TEXT
- `working_dir` TEXT
- `title` TEXT
- `started_at` TEXT NOT NULL
- `ended_at` TEXT
- `summary_md` TEXT
- `status` TEXT NOT NULL
  - examples: `active`, `closed`, `interrupted`
- `files_touched_json` TEXT
- `actions_json` TEXT
- `metadata_json` TEXT

## Table: `plan_items`
Core planning structure.

Suggested columns:

- `id` TEXT PRIMARY KEY
- `bucket` TEXT NOT NULL
  - one of: `today`, `short_term`, `long_term`, `recurring`, `dated`
- `title` TEXT NOT NULL
- `description` TEXT
- `status` TEXT NOT NULL
  - examples: `active`, `pending`, `done`, `partial`, `hold`, `cancelled`
- `priority_score` INTEGER
- `priority_reason` TEXT
- `due_at` TEXT
- `project_key` TEXT
- `related_session_id` TEXT
- `related_source_id` TEXT
- `created_at` TEXT NOT NULL
- `updated_at` TEXT NOT NULL
- `metadata_json` TEXT

## Table: `quests`
Execution-level unit under missions and plans.

Suggested columns:

- `id` TEXT PRIMARY KEY
- `plan_item_id` TEXT
- `parent_quest_id` TEXT
- `title` TEXT NOT NULL
- `why_now` TEXT
- `completion_criteria` TEXT NOT NULL
- `status` TEXT NOT NULL
  - examples: `active`, `done`, `partial`, `hold`, `queued`
- `verdict_reason` TEXT
- `restart_point` TEXT
- `next_quest_hint` TEXT
- `created_at` TEXT NOT NULL
- `updated_at` TEXT NOT NULL
- `metadata_json` TEXT

## Table: `decision_records`
Important strategic decisions and planning changes.

Suggested columns:

- `id` TEXT PRIMARY KEY
- `decision_type` TEXT NOT NULL
  - examples: `priority_change`, `mission_selection`, `scope_cut`, `schedule_shift`
- `title` TEXT NOT NULL
- `reason` TEXT
- `impact_summary` TEXT
- `related_plan_item_id` TEXT
- `related_quest_id` TEXT
- `related_session_id` TEXT
- `created_at` TEXT NOT NULL
- `metadata_json` TEXT

## Table: `current_state`
Operational snapshot.

Suggested columns:

- `state_key` TEXT PRIMARY KEY
- `state_value` TEXT
- `updated_at` TEXT NOT NULL
- `metadata_json` TEXT

Recommended keys:

- `main_mission_id`
- `main_mission_title`
- `main_mission_reason`
- `main_mission_completion_criteria`
- `current_quest_id`
- `current_quest_title`
- `current_quest_completion_criteria`
- `recent_verdict`
- `recommended_next_quest`
- `top_unfinished_summary`
- `dated_pressure_summary`
- `latest_decision_summary`
- `restart_point`
- `day_progress_summary`

Notes:
- Keep this table small and fast to read.
- This is the default entry point for most agents.

## Table: `brief_records`
Reusable restart briefs for human and agent sessions.

Suggested columns:

- `id` TEXT PRIMARY KEY
- `brief_type` TEXT NOT NULL
  - examples: `morning`, `midday`, `end_of_day`, `project_restart`
- `title` TEXT NOT NULL
- `content_md` TEXT NOT NULL
- `related_plan_item_id` TEXT
- `related_quest_id` TEXT
- `related_session_id` TEXT
- `created_at` TEXT NOT NULL
- `metadata_json` TEXT

## Table: `event_log`
Operational event timeline for exact "when did we do this?" queries.

Suggested columns:

- `id` TEXT PRIMARY KEY
- `event_type` TEXT NOT NULL
  - examples: `session_start`, `session_end`, `session_summary_updated`, `quest_reported`, `quest_verdict`, `plan_item_created`
- `entity_id` TEXT NOT NULL
- `entity_type` TEXT NOT NULL
  - examples: `session`, `quest`, `plan_item`
- `detail` TEXT
- `metadata_json` TEXT
- `created_at` TEXT NOT NULL

## Minimal Relationships
- `source_records.session_id -> sessions.id`
- `quests.plan_item_id -> plan_items.id`
- `plan_items.related_session_id -> sessions.id`
- `decision_records.related_plan_item_id -> plan_items.id`
- `decision_records.related_quest_id -> quests.id`

## Query Priorities
The app and agents should optimize for these queries:

1. get current main mission and current quest
2. get due-soon items
3. get unfinished items from yesterday
4. get active short-term items
5. get latest quest verdict
6. get next restart point
7. get recent sessions for a project
8. drill into raw source records only if needed

## Search Layer
SQLite remains the source of truth.

For retrieval, the app may maintain SQLite FTS5 indexes for:

- `sessions.title`, `sessions.summary_md`
- `source_records.source_name`, `source_records.content`
- `brief_records.title`, `brief_records.content_md`
- `decision_records.title`, `decision_records.reason`, `decision_records.impact_summary`
- `external_inbox.source_name`, `external_inbox.author`, `external_inbox.title`, `external_inbox.raw_content`, `external_inbox.attachment_path`

This improves "find the prior context" queries without introducing a separate vector DB.

## V1 Constraint
Do not add channel-specific tables for Telegram or email yet.
Use source-agnostic tables first.

When external ingestion arrives later, it should map into the same schema through `source_records`, `sessions`, and planning links.
