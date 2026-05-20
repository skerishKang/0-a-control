#!/usr/bin/env python3
"""Compatibility wrapper for the repository hygiene checker."""

from __future__ import annotations

import sys

from scripts.checks.repo_hygiene import *  # noqa: F401,F403
from scripts.checks.repo_hygiene import main


if __name__ == "__main__":
    sys.exit(main())
