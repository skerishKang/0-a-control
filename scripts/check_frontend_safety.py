#!/usr/bin/env python3
"""Compatibility wrapper for the frontend static safety checker."""

from __future__ import annotations

import sys

from scripts.checks.frontend_safety import *  # noqa: F401,F403
from scripts.checks.frontend_safety import main


if __name__ == "__main__":
    sys.exit(main())
