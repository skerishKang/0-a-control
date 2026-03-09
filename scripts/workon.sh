#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUNTIME_DIR="$ROOT_DIR/data/runtime"
SESSIONS_DIR="$RUNTIME_DIR/sessions"
SESSION_FILE="$RUNTIME_DIR/current_session.json"

mkdir -p "$SESSIONS_DIR"

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
RESUME_MODE="${CONTROL_TOWER_RESUME_MODE:-resume}"

if [[ $# -lt 3 ]]; then
  echo "Usage: bash scripts/workon.sh <agent> <source-type> <project> [title] [model]" >&2
  exit 1
fi

mkdir -p "$RUNTIME_DIR"

AGENT="$1"
SOURCE_TYPE="$2"
PROJECT="$3"
TITLE="${4:-}"
MODEL="${5:-}"
META_JSON="${6:-}"

RESULT="$(
  if [[ "$RESUME_MODE" == "fresh" ]]; then
    PYTHONPATH="$ROOT_DIR/scripts" $PYTHON_CMD "$ROOT_DIR/scripts/session_cli.py" start \
      --agent "$AGENT" \
      --source-type "$SOURCE_TYPE" \
      --project "$PROJECT" \
      --title "$TITLE" \
      --model "$MODEL" \
      --metadata-json "$META_JSON"
  else
    PYTHONPATH="$ROOT_DIR/scripts" $PYTHON_CMD "$ROOT_DIR/scripts/session_cli.py" start \
      --agent "$AGENT" \
      --source-type "$SOURCE_TYPE" \
      --project "$PROJECT" \
      --title "$TITLE" \
      --model "$MODEL" \
      --with-resume-context \
      --metadata-json "$META_JSON"
  fi
)"

# Save to both current_session.json (pointer) and specific session file
printf '%s\n' "$RESULT" > "$SESSION_FILE"

SESSION_ID="$(echo "$RESULT" | $PYTHON_CMD -c "import sys, json; print(json.load(sys.stdin)['id'])")"
printf '%s\n' "$RESULT" > "$SESSIONS_DIR/${SESSION_ID}.json"

$PYTHON_CMD - <<'PY' "$SESSION_FILE"
import json, sys
from pathlib import Path
payload = json.loads(Path(sys.argv[1]).read_text())
resume_mode = payload.get("resume_context") and "resume" or "fresh"
print(f"started: {payload['id']}")
print(f"agent: {payload['agent_name']}")
print(f"project: {payload.get('project_key') or '-'}")
print(f"title: {payload.get('title') or '-'}")
resume = payload.get("resume_context") or {}
print(f"resume_mode: {resume_mode}")
print(f"resume_from: {resume.get('source_session_id') or '-'}")
if resume_mode == "fresh":
    print("resume_note: stored memory not injected")
else:
    print("resume_note: stored memory injected")
PY
