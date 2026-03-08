#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORKDIARY_ROOT="$(cd "$ROOT_DIR/.." && pwd)"
RUNTIME_DIR="$ROOT_DIR/data/runtime"
TRANSCRIPT_DIR="$RUNTIME_DIR/transcripts"

if [[ $# -lt 3 ]]; then
  echo "Usage: bash scripts/agent-work.sh <tool> <project-or-path> <title> [model] [-- tool args...]" >&2
  exit 1
fi

AGENT_NAME="$1"
PROJECT_INPUT="$2"
TITLE="$3"
shift 3

MODEL=""
if [[ $# -gt 0 && "$1" != "--" ]]; then
  MODEL="$1"
  shift
fi

if [[ $# -gt 0 && "$1" == "--" ]]; then
  shift
fi

resolve_workspace() {
  local input="$1"
  if [[ -d "$input" ]]; then
    cd "$input" && pwd
    return
  fi
  if [[ -d "$WORKDIARY_ROOT/$input" ]]; then
    cd "$WORKDIARY_ROOT/$input" && pwd
    return
  fi
  echo "$WORKDIARY_ROOT/$input"
}

WORKSPACE="$(resolve_workspace "$PROJECT_INPUT")"
PROJECT_KEY="$(basename "$WORKSPACE")"

if [[ ! -d "$WORKSPACE" ]]; then
  echo "Workspace not found: $PROJECT_INPUT" >&2
  exit 1
fi

TOOL="$(
  PYTHONPATH="$ROOT_DIR/scripts" python3 - <<'PY' "$AGENT_NAME"
from agent_registry import canonical_agent_name, resolve_executable
import sys
name = canonical_agent_name(sys.argv[1])
print(resolve_executable(name))
PY
)"

CANONICAL_AGENT="$(
  PYTHONPATH="$ROOT_DIR/scripts" python3 - <<'PY' "$AGENT_NAME"
from agent_registry import canonical_agent_name
import sys
print(canonical_agent_name(sys.argv[1]))
PY
)"

cd "$WORKSPACE"

START_OUTPUT="$("$ROOT_DIR/scripts/workon.sh" "$CANONICAL_AGENT" "cmd" "$PROJECT_KEY" "$TITLE" "$MODEL")"
echo "$START_OUTPUT"

SESSION_ID="$(python3 - <<'PY' "$RUNTIME_DIR/current_session.json"
import json, sys
from pathlib import Path
payload = json.loads(Path(sys.argv[1]).read_text())
print(payload["id"])
PY
)"

PYTHONPATH="$ROOT_DIR/scripts" python3 "$ROOT_DIR/scripts/session_cli.py" log \
  --session-id "$SESSION_ID" \
  --source-name "$CANONICAL_AGENT" \
  --source-type "cmd" \
  --role "user" \
  --project "$PROJECT_KEY" \
  --cwd "$WORKSPACE" \
  --content "$TITLE" >/dev/null 2>&1 || true

mkdir -p "$TRANSCRIPT_DIR"
TRANSCRIPT_FILE="$TRANSCRIPT_DIR/${SESSION_ID}.log"

cleanup() {
  local exit_code=$?
  local summary=""
  if [[ $exit_code -ne 0 ]]; then
    summary="${CANONICAL_AGENT} wrapper session exited with code ${exit_code}"
  fi
  if [[ -f "$TRANSCRIPT_FILE" ]]; then
    PYTHONPATH="$ROOT_DIR/scripts" python3 "$ROOT_DIR/scripts/import_transcript.py" \
      --session-id "$SESSION_ID" \
      --source-name "$CANONICAL_AGENT" \
      --project "$PROJECT_KEY" \
      --cwd "$WORKSPACE" \
      --file "$TRANSCRIPT_FILE" >/dev/null 2>&1 || true
  fi
  PYTHONPATH="$ROOT_DIR/scripts" python3 "$ROOT_DIR/scripts/session_cli.py" end \
    --session-id "$SESSION_ID" \
    --summary "$summary" >/dev/null 2>&1 || true
  if [[ -f "$RUNTIME_DIR/current_session.json" ]]; then
    ACTIVE_ID="$(python3 - <<'PY' "$RUNTIME_DIR/current_session.json"
import json, sys
from pathlib import Path
payload = json.loads(Path(sys.argv[1]).read_text())
print(payload.get("id", ""))
PY
)"
    if [[ "$ACTIVE_ID" == "$SESSION_ID" ]]; then
      rm -f "$RUNTIME_DIR/current_session.json"
    fi
  fi
  exit "$exit_code"
}

trap cleanup EXIT

printf -v TOOL_CMD '%q ' "$TOOL" "$@"
script -q -f -e -c "${TOOL_CMD% }" "$TRANSCRIPT_FILE"
