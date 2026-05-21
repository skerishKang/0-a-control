from __future__ import annotations

from pathlib import Path
from typing import Any

from scripts.services import project_reader as _impl

ROOT_DIR = _impl.ROOT_DIR
CONFIG_PATH = _impl.CONFIG_PATH
OUTPUT_PATH = _impl.OUTPUT_PATH


def _sync_paths() -> None:
    _impl.CONFIG_PATH = CONFIG_PATH
    _impl.OUTPUT_PATH = OUTPUT_PATH


def load_config() -> dict:
    _sync_paths()
    return _impl.load_config()


def get_git_state(project_path: Path) -> dict[str, Any]:
    return _impl.get_git_state(project_path)


def get_recent_files(project_path: Path, scan_rules: dict) -> list[dict[str, str]]:
    return _impl.get_recent_files(project_path, scan_rules)


def get_entry_point(project_path: Path, entry_points: dict) -> dict[str, Any]:
    return _impl.get_entry_point(project_path, entry_points)


def scan_project(project: dict) -> dict[str, Any]:
    _sync_paths()
    return _impl.scan_project(project)


def scan_projects() -> dict:
    _sync_paths()
    return _impl.scan_projects()


def main() -> None:
    _sync_paths()
    _impl.main()


if __name__ == "__main__":
    main()
