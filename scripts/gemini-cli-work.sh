#!/usr/bin/env bash
set -euo pipefail
# Canonical Gemini wrapper. Keep this name stable for launchers and docs.
"$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/agent-work.sh" gemini-cli "$@"
