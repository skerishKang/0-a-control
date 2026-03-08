#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUNTIME_DIR="$ROOT_DIR/data/runtime"
SESSION_FILE="$RUNTIME_DIR/current_session.json"

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

RESULT="$(
  PYTHONPATH="$ROOT_DIR/scripts" python3 "$ROOT_DIR/scripts/session_cli.py" start \
    --agent "$AGENT" \
    --source-type "$SOURCE_TYPE" \
    --project "$PROJECT" \
    --title "$TITLE" \
    --model "$MODEL"
)"

printf '%s\n' "$RESULT" > "$SESSION_FILE"

python3 - <<'PY' "$SESSION_FILE"
import json, sys
from pathlib import Path
payload = json.loads(Path(sys.argv[1]).read_text())
print(f"started: {payload['id']}")
print(f"agent: {payload['agent_name']}")
print(f"project: {payload.get('project_key') or '-'}")
print(f"title: {payload.get('title') or '-'}")
PY
