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

SESSION_FILE=""
if [[ -n "${CONTROL_TOWER_SESSION_ID:-}" ]]; then
    if [[ -f "$SESSIONS_DIR/${CONTROL_TOWER_SESSION_ID}.json" ]]; then
        SESSION_FILE="$SESSIONS_DIR/${CONTROL_TOWER_SESSION_ID}.json"
    fi
fi

if [[ -z "$SESSION_FILE" && -f "$DEFAULT_SESSION_FILE" ]]; then
    SESSION_FILE="$DEFAULT_SESSION_FILE"
fi

if [[ -z "$SESSION_FILE" ]]; then
  echo "No active session."
  exit 0
fi

$PYTHON_CMD - <<'PY' "$SESSION_FILE" | tr -d '\r'
import json, sys
from pathlib import Path
payload = json.loads(Path(sys.argv[1]).read_text())
print(f"id: {payload['id']}")
print(f"agent: {payload.get('agent_name') or '-'}")
print(f"project: {payload.get('project_key') or '-'}")
print(f"title: {payload.get('title') or '-'}")
print(f"started_at: {payload.get('started_at') or '-'}")
PY
