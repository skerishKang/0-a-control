#!/usr/bin/env bash
set -euo pipefail

# Force the .cmd version
export KILO_BIN="C:\\Users\\limone\\AppData\\Roaming\\npm\\kilo.cmd"

"$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/agent-work.sh" kilo "$@"

