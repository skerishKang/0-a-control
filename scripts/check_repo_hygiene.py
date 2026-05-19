#!/usr/bin/env python3
"""Repository hygiene checker for local-only artifacts.

This checker scans tracked text files for patterns that should stay out of the
repository, such as machine-specific workspace paths and generated runtime
artifacts. It is intentionally lightweight and allowlist-driven.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

BINARY_SUFFIXES = {
    ".db",
    ".sqlite",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".zip",
    ".pdf",
    ".hwp",
    ".hwpx",
    ".doc",
    ".docx",
    ".ppt",
    ".pptx",
    ".xls",
    ".xlsx",
}

DENYLIST_PATHS = {
    "data/config/tracked_projects.json",
}

DENYLIST_PREFIXES = (
    "data/runtime/",
    "data/blobs/",
    "sessions/",
    "sessions_html/",
    "session_exports/",
)

DENYLIST_REGEXES: list[tuple[str, re.Pattern[str]]] = [
    ("windows_drive_path", re.compile(r"\b[A-Z]:[\\/][^\s\"'<>]+")),
    ("windows_user_path", re.compile(r"\b[A-Z]:[\\/]Users[\\/][^\s\"'<>]+", re.IGNORECASE)),
    ("unix_user_path", re.compile(r"(?<![A-Za-z0-9_])/(?:Users|home)/[^\s\"'<>]+")),
]

ALLOWLIST: set[tuple[str, str]] = {
    ("scripts/check_repo_hygiene.py", "windows_drive_path"),
    ("scripts/check_repo_hygiene.py", "windows_user_path"),
    ("scripts/check_repo_hygiene.py", "unix_user_path"),
}


def tracked_files() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def is_binary_like(path: str) -> bool:
    return Path(path).suffix.lower() in BINARY_SUFFIXES


def read_text(path: str) -> str | None:
    try:
        return (ROOT / path).read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None
    except OSError:
        return None


def check_paths(files: list[str]) -> list[str]:
    errors: list[str] = []
    for path in files:
        if path in DENYLIST_PATHS:
            errors.append(f"tracked local-only file: {path}")
        for prefix in DENYLIST_PREFIXES:
            if path.startswith(prefix):
                errors.append(f"tracked runtime artifact path: {path}")
                break
    return errors


def check_content(files: list[str]) -> list[str]:
    errors: list[str] = []
    for path in files:
        if is_binary_like(path):
            continue
        text = read_text(path)
        if text is None:
            continue
        for label, pattern in DENYLIST_REGEXES:
            if (path, label) in ALLOWLIST:
                continue
            for lineno, line in enumerate(text.splitlines(), start=1):
                if pattern.search(line):
                    errors.append(f"{path}:{lineno}: disallowed {label}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Check repository hygiene for local-only artifacts.")
    parser.add_argument("--verbose", action="store_true")
    parser.parse_args()

    files = tracked_files()
    errors = check_paths(files) + check_content(files)

    print("Repository hygiene check")
    print(f"tracked files scanned: {len(files)}")
    print(f"errors: {len(errors)}")

    if errors:
        print("\nDisallowed tracked content:")
        for error in errors:
            print(f"  {error}")
        print("\nRESULT: FAIL")
        return 1

    print("\nRESULT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
