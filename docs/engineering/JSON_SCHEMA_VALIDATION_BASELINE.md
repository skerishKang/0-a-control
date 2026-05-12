# JSON Schema Validation Baseline

Refs #112.

## Scope

This document records the initial schema baseline for report and verdict payloads.

Added schemas:

- `schemas/report.schema.json`
- `schemas/verdict.schema.json`

The schemas are intentionally permissive through `additionalProperties: true` at top-level and selected nested objects so current producers can keep adding metadata while the required operational contract is enforced.

## Required report fields

The report schema requires:

- `schema_version`
- `report`
- `report.quest_id`
- `report.quest_title`
- `report.completion_criteria`
- `report.work_summary`

Optional report fields include `remaining_work`, `blocker`, `self_assessment`, `plan_links`, and `attachments`.

## Required verdict fields

The verdict schema requires:

- `schema_version`
- `report_ref`
- `verdict`
- `verdict.status`
- `verdict.reason`
- `verdict.plan_impact`
- all plan-impact buckets: `today`, `short_term`, `long_term`, `recurring`, `dated`

Allowed verdict statuses:

- `done`
- `partial`
- `hold`

## Follow-up implementation path

A follow-up code PR should add a small validation utility, for example:

```bash
python scripts/validate_contract.py schemas/verdict.schema.json data/queue/verdicts/example.json
```

Recommended behavior:

1. Load the schema from `schemas/`.
2. Validate payloads before or during ingest.
3. Return clear missing-field errors.
4. Keep existing `scripts/verdict_import.py` failed-file routing semantics.

## Test fixture matrix

Recommended fixtures:

| Fixture | Expected result |
| --- | --- |
| valid report | pass |
| report missing `report.quest_id` | fail |
| report missing `report.work_summary` | fail |
| valid verdict | pass |
| verdict missing `report_ref` | fail |
| verdict missing `verdict.status` | fail |
| verdict with invalid status | fail |
| verdict missing one `plan_impact` bucket | fail |

## Compatibility note

The current ingest implementation accepts some fallback locations, including selected root-level and metadata/correlation fields. The schemas define the canonical contract. Compatibility fallbacks should remain explicit in code and should not silently expand without test coverage.
