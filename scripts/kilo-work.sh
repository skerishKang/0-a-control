#!/usr/bin/env bash
set -euo pipefail

# Force the Windows npm shim via a WSL path so agent-work.sh can convert it once.
export KILO_BIN="/mnt/c/Users/limone/AppData/Roaming/npm/kilo.cmd"

"$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/agent-work.sh" kilo "$@"
