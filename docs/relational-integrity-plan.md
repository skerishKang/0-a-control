# Relational integrity status

This document records the current relational-integrity status for issue #247.

## Implemented relationships

The high-confidence nullable references are now enforced through schema migrations and table rebuilds.

| Migration | Relationship | Status |
| --- | --- | --- |
| v3 | `source_records.session_id -> sessions.id` | Implemented |
| v4 | `quests.plan_item_id -> plan_items.id` | Implemented |
| v4 | `quests.parent_quest_id -> quests.id` | Implemented |
| v5 | `decision_records.related_plan_item_id -> plan_items.id` | Implemented |
| v5 | `decision_records.related_quest_id -> quests.id` | Implemented |
| v6 | `brief_records.related_plan_item_id -> plan_items.id` | Implemented |
| v6 | `brief_records.related_quest_id -> quests.id` | Implemented |
| v7 | `decision_records.related_session_id -> sessions.id` | Implemented |
| v8 | `brief_records.related_session_id -> sessions.id` | Implemented |
| v9 | `plan_items.related_session_id -> sessions.id` | Implemented |
| v10 | `external_inbox.session_id -> sessions.id` | Implemented |

All implemented relationships use nullable references so child rows can remain when parent rows are removed.

## Deferred relationships

These references should stay unconstrained until the data model is narrowed.

| Reference | Reason |
| --- | --- |
| `plan_items.related_source_id` | Target is ambiguous. Older docs suggested `source_records.id`, while current plan approval code treats the value as an `external_inbox.id` candidate. |
| `event_log.entity_type` + `event_log.entity_id` | Polymorphic reference across several entity tables. |
| `current_state.state_value` | Key/value storage, not a stable relational column. |
| `external_inbox.source_id` | May represent more than Telegram sources. |
| FTS tables | Derived virtual tables maintained by triggers. |
| JSON metadata | Embedded references should stay application-level unless promoted to columns. |

## Migration notes

The FK series uses SQLite table rebuilds rather than fresh-only schema rewrites. The migration path normalizes legacy missing session references to `NULL`, recreates indexes and FTS triggers where needed, and verifies the result with `PRAGMA foreign_key_check`.

The v9 `plan_items` migration also rebuilds dependent FK tables after the `plan_items` table rebuild. This avoids stale SQLite FK metadata that can otherwise point at the temporary table name after a rename.

## Test coverage

The migration tests cover version bookkeeping, idempotency, invalid and valid references, parent-removal behavior, session-reference normalization, FTS trigger survival, `external_inbox` uniqueness preservation, and clean `PRAGMA foreign_key_check` results.

## Current conclusion

The high-confidence relationships in #247 are implemented through schema migration v10. The remaining references are intentionally deferred because they are polymorphic, key/value based, derived, JSON embedded, or target ambiguous.
