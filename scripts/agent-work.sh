#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORKDIARY_ROOT="$(cd "$ROOT_DIR/.." && pwd)"
RUNTIME_DIR="$ROOT_DIR/data/runtime"
TRANSCRIPT_DIR="$RUNTIME_DIR/transcripts"

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
  PYTHONPATH="$ROOT_DIR/scripts" $PYTHON_CMD - <<'PY' "$AGENT_NAME"
from agent_registry import canonical_agent_name, resolve_executable
import sys
name = canonical_agent_name(sys.argv[1])
print(resolve_executable(name))
PY
)"

CANONICAL_AGENT="$(
  PYTHONPATH="$ROOT_DIR/scripts" $PYTHON_CMD - <<'PY' "$AGENT_NAME"
from agent_registry import canonical_agent_name
import sys
print(canonical_agent_name(sys.argv[1]))
PY
)"

cd "$WORKSPACE"

META_JSON="$(
  PYTHONPATH="$ROOT_DIR/scripts" $PYTHON_CMD - <<'PY' "$CANONICAL_AGENT" "$TOOL"
import sys, json, os
print(json.dumps({
    "agent_name": sys.argv[1],
    "executable": sys.argv[2],
    "argv": sys.argv,
    "env_cwd": os.getcwd()
}))
PY
)"

START_OUTPUT="$("$ROOT_DIR/scripts/workon.sh" "$CANONICAL_AGENT" "cmd" "$PROJECT_KEY" "$TITLE" "$MODEL" "$META_JSON")"
echo "$START_OUTPUT"

SESSION_ID="$(echo "$START_OUTPUT" | grep "^started: " | cut -d' ' -f2 | tr -d '\r')"
export CONTROL_TOWER_SESSION_ID="$SESSION_ID"

if [[ -z "$SESSION_ID" ]]; then
  echo "Failed to start session or parse session ID." >&2
  exit 1
fi

SESSION_FILE="$RUNTIME_DIR/sessions/${SESSION_ID}.json"

RESUME_PROMPT="$($PYTHON_CMD - <<'PY' "$SESSION_FILE" | tr -d '\r'
import json, sys
from pathlib import Path
payload = json.loads(Path(sys.argv[1]).read_text())
resume = payload.get("resume_context") or {}
print(resume.get("prompt", ""))
PY
)"
RESUME_PROMPT="${RESUME_PROMPT% }" # Trim the space

if [[ "$RESUME_MODE" == "fresh" ]]; then
  RESUME_PROMPT=""
fi

PYTHONPATH="$ROOT_DIR/scripts" $PYTHON_CMD "$ROOT_DIR/scripts/session_cli.py" log \
  --session-id "$SESSION_ID" \
  --source-name "$CANONICAL_AGENT" \
  --source-type "cmd" \
  --role "user" \
  --project "$PROJECT_KEY" \
  --cwd "$WORKSPACE" \
  --content "$TITLE" >/dev/null 2>&1 || true

if [[ -n "$RESUME_PROMPT" ]]; then
  PYTHONPATH="$ROOT_DIR/scripts" $PYTHON_CMD "$ROOT_DIR/scripts/session_cli.py" log \
    --session-id "$SESSION_ID" \
    --source-name "$CANONICAL_AGENT" \
    --source-type "session_resume" \
    --role "system" \
    --project "$PROJECT_KEY" \
    --cwd "$WORKSPACE" \
    --content "$RESUME_PROMPT" >/dev/null 2>&1 || true
fi

mkdir -p "$TRANSCRIPT_DIR"
TRANSCRIPT_FILE="$TRANSCRIPT_DIR/${SESSION_ID}.log"

cleanup() {
  local exit_code=$?
  local summary=""
  if [[ $exit_code -ne 0 ]]; then
    summary="${CANONICAL_AGENT} wrapper session exited with code ${exit_code}"
  fi
  if [[ -f "$TRANSCRIPT_FILE" ]]; then
    PYTHONPATH="$ROOT_DIR/scripts" $PYTHON_CMD "$ROOT_DIR/scripts/import_transcript.py" \
      --session-id "$SESSION_ID" \
      --source-name "$CANONICAL_AGENT" \
      --project "$PROJECT_KEY" \
      --cwd "$WORKSPACE" \
      --file "$TRANSCRIPT_FILE" >/dev/null 2>&1 || true
  fi
  PYTHONPATH="$ROOT_DIR/scripts" $PYTHON_CMD "$ROOT_DIR/scripts/session_cli.py" end \
    --session-id "$SESSION_ID" \
    --summary "$summary" >/dev/null 2>&1 || true

  rm -f "$RUNTIME_DIR/sessions/${SESSION_ID}.json"

  if [[ -f "$RUNTIME_DIR/current_session.json" ]]; then
    ACTIVE_ID="$($PYTHON_CMD - <<'PY' "$RUNTIME_DIR/current_session.json"
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

TOOL_ARGS=("$TOOL")
if [[ "$TOOL" == *.cmd || "$TOOL" == *.bat ]]; then
  WIN_TOOL="$TOOL"
  if command -v wslpath >/dev/null 2>&1; then
    WIN_TOOL="$(wslpath -w "$TOOL")"
  fi
  TOOL_ARGS=("cmd.exe" "/c" "$WIN_TOOL")
fi
if [[ "$CANONICAL_AGENT" == "codex" && -n "$RESUME_PROMPT" && $# -eq 0 ]]; then
  TOOL_ARGS+=("$RESUME_PROMPT")
fi
if [[ $# -gt 0 ]]; then
  TOOL_ARGS+=("$@")
fi

printf -v TOOL_CMD '%q ' "${TOOL_ARGS[@]}"

if command -v script >/dev/null 2>&1; then
  script -q -f -e -c "${TOOL_CMD% }" "$TRANSCRIPT_FILE"
else
  # Fallback for environments without 'script' (like Windows Git Bash)
  eval "${TOOL_CMD% }" 2>&1 | tee "$TRANSCRIPT_FILE"
fi
