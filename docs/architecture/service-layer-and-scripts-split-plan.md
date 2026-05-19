# Service layer and scripts split plan

This document defines the target direction for reducing direct coupling between the HTTP server, database helpers, and CLI-style scripts.

Related issues: #249, #250

## Current problem

The current `scripts/` directory mixes several responsibilities:

- HTTP request handling
- database connection and schema setup
- DB query helpers
- CLI entrypoints
- sync/import utilities
- migration and audit utilities
- local operator wrappers
- frontend smoke and repository checks

This makes small changes harder to review because an import in one area can unexpectedly affect another area.

## Target principles

1. Keep existing public entrypoints stable.
2. Move reusable business logic out of server handlers before moving files.
3. Keep CLI wrappers thin.
4. Prefer small compatibility shims over large import rewrites.
5. Avoid changing runtime behavior during package split PRs.
6. Add tests before moving logic that touches the database or server routing.

## Proposed package layout

The target layout is incremental, not a single large move.

```text
control_tower/
  db/
    base.py
    schema.py
    migrations.py
    integrity.py
  services/
    quests.py
    plans.py
    sessions.py
    external_inbox.py
    agents.py
    operations.py
  web/
    server.py
    request_guard.py
    handlers/
      quests.py
      plans.py
      board.py
      external.py
  cli/
    telegram.py
    db_integrity.py
    imports.py
  checks/
    repo_hygiene.py
    frontend_safety.py
```

`scripts/` should remain as a compatibility layer while the transition is underway.

## Migration sequence

### Phase 1: document and classify

- Document target package boundaries.
- Identify current imports from `scripts.server`.
- Identify functions that can move without changing behavior.
- Avoid file moves in the first PR.

### Phase 2: extract pure services

Move pure or near-pure logic first:

- state formatting helpers
- plan/quest query helpers
- external inbox aggregation helpers
- agent status formatting helpers

Rules:

- no route path changes
- no API response shape changes
- no DB schema changes
- keep old imports working through thin wrappers if needed

### Phase 3: split web request handlers

After service functions exist, move route handlers into web handler modules.

Suggested order:

1. read-only board/state endpoints
2. read-only status endpoints
3. mutation endpoints with existing tests
4. Telegram/external sync endpoints last

### Phase 4: move DB helpers

Move DB base/schema/migration helpers only after FK and migration work is stable.

Do not combine DB package moves with FK migration PRs.

### Phase 5: reduce scripts directory

After services and web handlers are stable, convert `scripts/` files into compatibility entrypoints.

Examples:

- `scripts/server.py` imports and runs `control_tower.web.server`
- `scripts/db_base.py` re-exports from `control_tower.db.base`
- `scripts/check_frontend_safety.py` can later move to `control_tower.checks.frontend_safety`

## Acceptance criteria for issue closure

### #249 closure target

Issue #249 can close when:

- at least one server handler group no longer depends directly on large `scripts.server` internals;
- reusable logic for that group lives in a service module;
- tests verify the moved behavior;
- old entrypoints still work.

### #250 closure target

Issue #250 can close when:

- the target package layout exists;
- core DB/web/service/check modules are no longer all mixed in `scripts/`;
- compatibility imports or wrappers preserve existing operator commands;
- CI and smoke checks pass.

This planning PR alone should not close #249 or #250.

## Guardrails

Do not do these in the same PR:

- service extraction plus DB schema migration
- route split plus frontend rewrite
- file move plus behavior change
- FK migration plus package restructure
- mass rename of scripts without compatibility wrappers

## First implementation candidate

The safest first implementation slice is a read-only extraction:

- create `control_tower/services/agent_status.py`
- move agent status formatting or selection logic there
- keep endpoint behavior unchanged
- add focused tests
- leave `scripts/server.py` route registration intact

This gives a real service-layer foothold without forcing a broad package move.
