#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SESSION_FILE="$ROOT_DIR/data/runtime/current_session.json"

if [[ ! -f "$SESSION_FILE" ]]; then
  echo "No active session to close." >&2
  exit 1
fi

SUMMARY="${1:-}"
shift || true

if [[ -z "$SUMMARY" ]]; then
  SUMMARY="session closed"
fi

readarray -t SESSION_META < <(python3 - <<'PY' "$SESSION_FILE"
import json, sys
from pathlib import Path
payload = json.loads(Path(sys.argv[1]).read_text())
print(payload["id"])
print(payload.get("title") or "")
PY
)

SESSION_ID="${SESSION_META[0]}"

PYTHONPATH="$ROOT_DIR/scripts" python3 "$ROOT_DIR/scripts/session_cli.py" end \
  --session-id "$SESSION_ID" \
  --summary "$SUMMARY" >/dev/null

rm -f "$SESSION_FILE"
echo "ended: $SESSION_ID"
