# Relational integrity plan

This document inventories the core table relationships that should be enforced with foreign keys in a future schema migration.

The current database now has migration bookkeeping in `schema_migrations`. Actual foreign-key enforcement should be added as a separate migration after existing data is audited for orphaned references.

## Goals

- Add foreign keys only for high-confidence relationships.
- Use `ON DELETE SET NULL` where child records should survive parent deletion.
- Avoid constraints for polymorphic or loosely typed references until the data model is narrowed.
- Keep existing databases upgradeable through a migration, not a fresh-only schema rewrite.

## High-confidence relationships

These relationships are direct references between stable core tables and are good candidates for migration version 2.

| Table | Column | Target | Suggested action |
| --- | --- | --- | --- |
| `source_records` | `session_id` | `sessions(id)` | `ON DELETE SET NULL` |
| `plan_items` | `related_session_id` | `sessions(id)` | `ON DELETE SET NULL` |
| `plan_items` | `related_source_id` | `source_records(id)` | `ON DELETE SET NULL` |
| `quests` | `plan_item_id` | `plan_items(id)` | `ON DELETE SET NULL` |
| `quests` | `parent_quest_id` | `quests(id)` | `ON DELETE SET NULL` |
| `decision_records` | `related_plan_item_id` | `plan_items(id)` | `ON DELETE SET NULL` |
| `decision_records` | `related_quest_id` | `quests(id)` | `ON DELETE SET NULL` |
| `decision_records` | `related_session_id` | `sessions(id)` | `ON DELETE SET NULL` |
| `brief_records` | `related_plan_item_id` | `plan_items(id)` | `ON DELETE SET NULL` |
| `brief_records` | `related_quest_id` | `quests(id)` | `ON DELETE SET NULL` |
| `brief_records` | `related_session_id` | `sessions(id)` | `ON DELETE SET NULL` |
| `external_inbox` | `session_id` | `sessions(id)` | `ON DELETE SET NULL` |

## Relationships to defer

These should not receive foreign keys in the first FK migration.

| Table | Column(s) | Reason |
| --- | --- | --- |
| `event_log` | `entity_type`, `entity_id` | Polymorphic reference across several entity tables. Enforcing this needs a narrower event model or separate typed event tables. |
| `current_state` | `state_key`, `state_value` | Key/value state store. Values may contain serialized references but are not relational columns. |
| `external_inbox` | `source_id` | Can represent multiple external source classes. `telegram_sources(source_id)` is only one possible source domain. |
| FTS tables | all columns | Derived virtual tables maintained by triggers. They should not be FK owners. |

## Migration version 2 outline

SQLite cannot add foreign keys to an existing table with a simple `ALTER TABLE`. The safe path is table rebuild per affected table.

For each affected table:

1. Create a new table with the desired foreign-key constraints.
2. Copy existing rows into the new table.
3. Set orphaned reference columns to `NULL` before or during copy.
4. Recreate indexes and triggers as needed.
5. Replace the old table with the new table.
6. Run `PRAGMA foreign_key_check`.
7. Record migration version 2 only after all steps succeed.

## Orphan audit queries

Before migration version 2, run queries like these and either fix rows or set references to `NULL`.

```sql
SELECT source_records.id, source_records.session_id
FROM source_records
LEFT JOIN sessions ON sessions.id = source_records.session_id
WHERE source_records.session_id IS NOT NULL
  AND sessions.id IS NULL;
```

```sql
SELECT quests.id, quests.plan_item_id
FROM quests
LEFT JOIN plan_items ON plan_items.id = quests.plan_item_id
WHERE quests.plan_item_id IS NOT NULL
  AND plan_items.id IS NULL;
```

```sql
SELECT quests.id, quests.parent_quest_id
FROM quests
LEFT JOIN quests AS parent ON parent.id = quests.parent_quest_id
WHERE quests.parent_quest_id IS NOT NULL
  AND parent.id IS NULL;
```

## Test plan for the FK migration

The migration PR should add tests that verify:

- Fresh database initialization creates the FK-enabled schema.
- Existing database upgrade path records migration version 2 exactly once.
- Orphaned references are set to `NULL` during migration.
- `PRAGMA foreign_key_check` returns no rows after migration.
- At least these relationships are enforced:
  - `source_records.session_id -> sessions.id`
  - `quests.plan_item_id -> plan_items.id`
  - `quests.parent_quest_id -> quests.id`
  - `decision_records.related_quest_id -> quests.id`

## Non-goals for the first FK migration

- Do not redesign `event_log`.
- Do not add cascade deletes for business records.
- Do not enforce relationships stored only inside JSON metadata.
- Do not change public API response shapes.
