#!/usr/bin/env bash
set -euo pipefail
# Compatibility alias for older `gemini-work.sh` callers. Canonical wrapper is `gemini-cli-work.sh`.
"$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/agent-work.sh" gemini-cli "$@"
