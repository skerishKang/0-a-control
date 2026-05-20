"""Compatibility wrapper for the server smoke test."""

from __future__ import annotations

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from scripts.checks.server_smoke import *  # noqa: F401,F403,E402
from scripts.checks.server_smoke import main  # noqa: E402


if __name__ == "__main__":
    sys.exit(main())
