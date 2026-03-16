#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUNTIME_DIR="$ROOT_DIR/data/runtime"
SESSIONS_DIR="$RUNTIME_DIR/sessions"
DEFAULT_SESSION_FILE="$RUNTIME_DIR/current_session.json"

resolve_python() {
  if command -v python >/dev/null 2>&1; then
    echo python
    return
  fi
  if command -v python3 >/dev/null 2>&1; then
    echo python3
    return
  fi
  if command -v py >/dev/null 2>&1; then
    echo "py -3"
    return
  fi
  echo "Python interpreter not found in PATH." >&2
  exit 1
}

PYTHON_CMD="$(resolve_python)"

# Identify target session
# 1. Argument
# 2. Environment variable
# 3. Default session file
SESSION_ID_ARG="${1:-}"
if [[ -n "$SESSION_ID_ARG" && "$SESSION_ID_ARG" =~ ^[0-9a-f-]{36}$ ]]; then
    SESSION_ID="$SESSION_ID_ARG"
fi

SESSION_FILE=""
if [[ -n "${SESSION_ID:-}" ]]; then
    if [[ -f "$SESSIONS_DIR/${SESSION_ID}.json" ]]; then
        SESSION_FILE="$SESSIONS_DIR/${SESSION_ID}.json"
    fi
fi

if [[ -z "$SESSION_FILE" && -n "${CONTROL_TOWER_SESSION_ID:-}" ]]; then
    if [[ -f "$SESSIONS_DIR/${CONTROL_TOWER_SESSION_ID}.json" ]]; then
        SESSION_FILE="$SESSIONS_DIR/${CONTROL_TOWER_SESSION_ID}.json"
    fi
fi

if [[ -z "$SESSION_FILE" && -f "$DEFAULT_SESSION_FILE" ]]; then
    SESSION_FILE="$DEFAULT_SESSION_FILE"
fi

if [[ -z "$SESSION_FILE" ]]; then
  echo "No active session file found." >&2
  exit 1
fi

readarray -t SESSION_META < <($PYTHON_CMD - <<'PY' "$SESSION_FILE" | tr -d '\r'
import json, sys
from pathlib import Path
payload = json.loads(Path(sys.argv[1]).read_text())
print(payload["id"])
print(payload.get("project_key") or "")
print(payload.get("working_dir") or "")
PY
)

SESSION_ID="${SESSION_META[0]}"
PROJECT_KEY="${SESSION_META[1]}"
WORKING_DIR="${SESSION_META[2]}"

set +e
IMPORT_OUTPUT="$(
  PYTHONPATH="$ROOT_DIR/scripts" $PYTHON_CMD "$ROOT_DIR/scripts/import_kilo_session.py" \
    --session-id "$SESSION_ID" \
    --source-name "kilo" \
    --project "$PROJECT_KEY" \
    --cwd "$WORKING_DIR" 2>&1
)"
IMPORT_EXIT=$?
set -e

if [[ $IMPORT_EXIT -eq 0 ]]; then
  if [[ -n "$IMPORT_OUTPUT" ]]; then
    printf '%s\n' "$IMPORT_OUTPUT"
  fi
  exit 0
fi

if [[ "$IMPORT_OUTPUT" == *"no matching kilo session found"* ]]; then
  echo "kilo session import skipped: no matching session found"
  exit 0
fi

printf '%s\n' "$IMPORT_OUTPUT" >&2
exit "$IMPORT_EXIT"
