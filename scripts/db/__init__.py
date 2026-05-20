"""Compatibility package for database modules during scripts package split."""

from __future__ import annotations

import os
from datetime import timezone
from pathlib import Path

UTC = timezone.utc
ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = Path(os.getenv("CONTROL_TOWER_DATA_DIR", str(ROOT_DIR / "data")))
DB_PATH = Path(os.getenv("CONTROL_TOWER_DB_PATH", str(DATA_DIR / "control_tower.db")))
WORKDIARY_DIR = Path(os.getenv("CONTROL_TOWER_WORKDIARY_DIR", str(ROOT_DIR.parent)))

__all__ = ["DB_PATH", "ROOT_DIR", "WORKDIARY_DIR", "UTC"]
