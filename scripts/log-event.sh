#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

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

if [[ $# -lt 3 ]]; then
  echo "Usage: bash scripts/log-event.sh <event_type> <entity_type> <entity_id> [--detail ...] [--metadata ...] [--created-at ...]" >&2
  exit 1
fi

cd "$ROOT_DIR"
PYTHONPATH="$ROOT_DIR/scripts" $PYTHON_CMD "$ROOT_DIR/scripts/db_search.py" log-event "$@"
