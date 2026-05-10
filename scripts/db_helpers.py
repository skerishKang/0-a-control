from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import sqlite3

UTC = timezone.utc

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = Path(os.getenv("CONTROL_TOWER_DATA_DIR", str(ROOT_DIR / "data")))


def now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def get_db_path() -> Path:
    return Path(os.getenv("CONTROL_TOWER_DB_PATH", str(DATA_DIR / "control_tower.db")))


def row_to_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    if row is None:
        return None
    import json
    item = dict(row)
    for key, value in list(item.items()):
        if key.endswith("_json") and value:
            try:
                item[key] = json.loads(value)
            except json.JSONDecodeError:
                pass
    return item


def rows_to_dicts(rows: list[sqlite3.Row]) -> list[dict[str, Any]]:
    return [row_to_dict(row) for row in rows]