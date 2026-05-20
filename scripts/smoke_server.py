"""Compatibility wrapper for the server smoke test."""

from __future__ import annotations

import sys

from scripts.checks.server_smoke import *  # noqa: F401,F403
from scripts.checks.server_smoke import main


if __name__ == "__main__":
    sys.exit(main())
