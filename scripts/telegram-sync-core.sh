#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if command -v python3 >/dev/null 2>&1; then
  python3 scripts/telegram_cli.py sync-core
else
  python scripts/telegram_cli.py sync-core
fi

bash scripts/log-event.sh \
  telegram_sync \
  external_inbox \
  "telegram-sync-$(date +%Y%m%d-%H%M%S)" \
  --detail "core sync completed"
