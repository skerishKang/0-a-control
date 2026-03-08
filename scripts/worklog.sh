#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SESSION_FILE="$ROOT_DIR/data/runtime/current_session.json"

if [[ ! -f "$SESSION_FILE" ]]; then
  echo "No active session. Start one with: bash scripts/workon.sh ..." >&2
  exit 1
fi

ROLE="${1:-user}"
shift || true
CONTENT="${*:-}"

if [[ -z "$CONTENT" ]]; then
  CONTENT="$(cat)"
fi

if [[ -z "$CONTENT" ]]; then
  echo "Usage: bash scripts/worklog.sh [role] <content>" >&2
  exit 1
fi

readarray -t SESSION_META < <(python3 - <<'PY' "$SESSION_FILE"
import json, sys
from pathlib import Path
payload = json.loads(Path(sys.argv[1]).read_text())
print(payload["id"])
print(payload["agent_name"])
print(payload.get("source_type") or "cmd")
print(payload.get("project_key") or "")
print(payload.get("working_dir") or "")
PY
)

SESSION_ID="${SESSION_META[0]}"
SOURCE_NAME="${SESSION_META[1]}"
SOURCE_TYPE="${SESSION_META[2]}"
PROJECT="${SESSION_META[3]}"
CWD_VALUE="${SESSION_META[4]}"

PYTHONPATH="$ROOT_DIR/scripts" python3 "$ROOT_DIR/scripts/session_cli.py" log \
  --session-id "$SESSION_ID" \
  --source-name "$SOURCE_NAME" \
  --source-type "$SOURCE_TYPE" \
  --role "$ROLE" \
  --project "$PROJECT" \
  --cwd "$CWD_VALUE" \
  --content "$CONTENT" >/dev/null

echo "logged: $ROLE -> $CONTENT"
