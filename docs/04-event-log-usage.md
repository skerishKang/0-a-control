# Event Log Usage

## Purpose
`event_log` is for exact operational questions such as:

- when did we do this
- what changed first
- which session handled the incident

Use `event_log` for exact timeline facts.
Use FTS for broader context search.

## Rule
Use lowercase snake_case only.

Recommended pattern:

- `{domain}_{action}`

Examples:

- `session_start`
- `session_end`
- `session_summary_updated`
- `kilo_checkpoint_created`
- `kilo_checkpoint_cleanup`
- `kilo_path_move`
- `wsl_move`
- `wsl_cleanup`
- `telegram_sync`
- `telegram_backfill`
- `external_check`
- `antigravity_fix`
- `plan_item_created`
- `plan_item_updated`
- `quest_created`
- `quest_reported`
- `quest_verdict`

## Avoid
Do not use:

- `check`
- `checkpoint`
- `kp`
- `sessionStart`
- `telegram-sync`

These are too vague or inconsistent.

## Entity Type
Use the actual thing that changed.

Examples:

- `session`
- `quest`
- `plan_item`
- `decision`
- `external_inbox`

Recommended pairings:

| event_type | entity_type |
| --- | --- |
| `session_start` | `session` |
| `session_end` | `session` |
| `kilo_checkpoint_created` | `session` |
| `kilo_checkpoint_cleanup` | `session` |
| `kilo_path_move` | `session` |
| `wsl_move` | `session` |
| `wsl_cleanup` | `session` |
| `telegram_sync` | `external_inbox` |
| `telegram_backfill` | `external_inbox` |
| `external_check` | `session` |
| `antigravity_fix` | `session` |
| `plan_item_created` | `plan_item` |
| `plan_item_updated` | `plan_item` |
| `quest_created` | `quest` |
| `quest_reported` | `quest` |
| `quest_verdict` | `quest` |

## CLI
Basic commands:

```powershell
python scripts\db_search.py stats
python scripts\db_search.py events --limit 10
python scripts\db_search.py fts sessions antigravity --limit 10
python scripts\db_search.py fts inbox 강혜림 --limit 10
```

Record an event:

```powershell
python scripts\db_search.py log-event antigravity_fix session SESSION_ID --detail "workspace restore fixed"
```

## Common Examples
Kilo checkpoint created:

```powershell
python scripts\db_search.py log-event kilo_checkpoint_created session SESSION_ID --detail "manual checkpoint before cleanup"
```

Kilo checkpoint cleanup:

```powershell
python scripts\db_search.py log-event kilo_checkpoint_cleanup session SESSION_ID --detail "tmp_pack garbage removed"
```

Kilo path move:

```powershell
python scripts\db_search.py log-event kilo_path_move session SESSION_ID --detail "runtime moved from C to G"
```

WSL move:

```powershell
python scripts\db_search.py log-event wsl_move session SESSION_ID --detail "Ubuntu ext4.vhdx moved to G drive"
```

WSL cleanup:

```powershell
python scripts\db_search.py log-event wsl_cleanup session SESSION_ID --detail "old distro artifacts removed"
```

Telegram sync:

```powershell
python scripts\db_search.py log-event telegram_sync external_inbox telegram-sync-20260321 --detail "core sync completed"
```

Telegram backfill:

```powershell
python scripts\db_search.py log-event telegram_backfill external_inbox telegram-backfill-202603 --detail "2024-01 backlog imported"
```

49-1 external check:

```powershell
python scripts\db_search.py log-event external_check session SESSION_ID --detail "49-1 external usage checked"
```

Antigravity fix:

```powershell
python scripts\db_search.py log-event antigravity_fix session SESSION_ID --detail "wrong workspace restore fixed"
```

Quest verdict:

```powershell
python scripts\db_search.py log-event quest_verdict quest QUEST_ID --detail "partial: restart point updated"
```

Plan item created:

```powershell
python scripts\db_search.py log-event plan_item_created plan_item PLAN_ID --detail "new mission candidate added"
```

## PowerShell Functions
Add these to `$PROFILE` if you want shorter commands:

```powershell
function dbe {
    python scripts\db_search.py events @Args
}

function dbf {
    python scripts\db_search.py fts @Args
}

function dbl {
    python scripts\db_search.py log-event @Args
}

function dbe-kilo {
    python scripts\db_search.py events --event-type kilo_checkpoint_cleanup --limit 20
}

function dbe-verdict {
    python scripts\db_search.py events --event-type quest_verdict --limit 20
}

function dbf-session {
    param([string]$Query)
    python scripts\db_search.py fts sessions $Query --limit 10
}

function dbf-inbox {
    param([string]$Query)
    python scripts\db_search.py fts inbox $Query --limit 10
}
```

## Search Strategy
Use this order:

1. `events` for exact facts
2. `fts sessions` for prior discussion
3. `fts sources` for raw context
4. `fts inbox` for Telegram/external input

Examples:

- `kilo checkpoint는 언제 했지?`
  - `events --event-type kilo_checkpoint_cleanup`
- `Antigravity 고쳤던 맥락 다시 찾아줘`
  - `fts sessions antigravity`
- `강혜림 Telegram 첨부 관련 논의`
  - `fts inbox 강혜림`
  - then `fts sessions 강혜림`

## Notes
- `event_log` should stay small and explicit.
- Do not dump full transcripts into `event_log.detail`.
- Put short exact facts in `detail`.
- Put extra machine-readable fields in `metadata_json`.
