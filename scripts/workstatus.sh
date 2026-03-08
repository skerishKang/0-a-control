#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SESSION_FILE="$ROOT_DIR/data/runtime/current_session.json"

if [[ ! -f "$SESSION_FILE" ]]; then
  echo "No active session."
  exit 0
fi

python3 - <<'PY' "$SESSION_FILE"
import json, sys
from pathlib import Path
payload = json.loads(Path(sys.argv[1]).read_text())
print(f"id: {payload['id']}")
print(f"agent: {payload.get('agent_name') or '-'}")
print(f"project: {payload.get('project_key') or '-'}")
print(f"title: {payload.get('title') or '-'}")
print(f"started_at: {payload.get('started_at') or '-'}")
PY
