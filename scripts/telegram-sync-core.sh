#!/usr/bin/env bash

cd "$(dirname "$0")/.."

if command -v python3 >/dev/null 2>&1; then
  python3 scripts/telegram_cli.py sync-core
else
  python scripts/telegram_cli.py sync-core
fi
