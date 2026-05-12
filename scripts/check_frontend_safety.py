#!/usr/bin/env python3
"""Lightweight frontend static safety checker for the public dashboard.

Scans public/**/*.js and public/**/*.html for known unsafe patterns:

1. Inline event handler attributes (onclick=, onchange=, etc.)
2. Unsafe script/javascript: URL schemes

NOTE: innerHTML assignments are common in legacy code and not rejected
at this stage; they are tracked as a warning count for trend monitoring.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

PUBLIC_DIR = Path(__file__).resolve().parents[1] / "public"

# Patterns to detect
INLINE_EVENT_RE = re.compile(
    r"\bon\w+\s*=\s*['\"]",
    re.IGNORECASE,
)
UNSAFE_URL_RE = re.compile(
    r"""['"]\s*javascript\s*:""",
    re.IGNORECASE,
)
INNER_HTML_RE = re.compile(r"\.innerHTML\s*=")

# Patterns known to be safe — e.g. React-like attribute assignments
SAFE_PATTERNS: list[re.Pattern] = []


def check_file(filepath: Path) -> dict:
    """Check a single file for unsafe patterns. Returns result dict."""
    try:
        text = filepath.read_text(encoding="utf-8", errors="replace")
    except (OSError, UnicodeDecodeError):
        return {"path": str(filepath), "error": "unreadable", "issues": [], "warnings": []}

    issues: list[dict] = []
    warnings: list[dict] = []

    # Check inline event handlers
    for match in INLINE_EVENT_RE.finditer(text):
        start = max(0, match.start() - 30)
        end = min(len(text), match.end() + 40)
        context = text[start:end].replace("\n", " ").strip()
        # Skip safe patterns
        if any(p.search(context) for p in SAFE_PATTERNS):
            continue
        issues.append({
            "line": text[: match.start()].count("\n") + 1,
            "pattern": match.group(),
            "context": context,
        })

    # Check unsafe URL schemes
    for match in UNSAFE_URL_RE.finditer(text):
        start = max(0, match.start() - 30)
        end = min(len(text), match.end() + 40)
        context = text[start:end].replace("\n", " ").strip()
        issues.append({
            "line": text[: match.start()].count("\n") + 1,
            "pattern": match.group(),
            "context": context,
        })

    # Track innerHTML usage (warning only)
    for match in INNER_HTML_RE.finditer(text):
        start = max(0, match.start() - 30)
        end = min(len(text), match.end() + 40)
        context = text[start:end].replace("\n", " ").strip()
        warnings.append({
            "line": text[: match.start()].count("\n") + 1,
            "pattern": match.group(),
            "context": context,
        })

    return {
        "path": str(filepath.relative_to(PUBLIC_DIR.parent)),
        "issues": issues,
        "warnings": warnings,
    }


def main() -> int:
    exit_code = 0
    total_issues = 0
    total_warnings = 0

    for ext in ("*.js", "*.html"):
        for filepath in sorted(PUBLIC_DIR.rglob(ext)):
            result = check_file(filepath)
            if result.get("error"):
                print(f"[SKIP] {result['path']}: {result['error']}")
                continue

            for issue in result["issues"]:
                total_issues += 1
                print(
                    f"[FAIL] {result['path']}:{issue['line']} "
                    f"unsafe pattern {issue['pattern']!r} "
                    f"in `{issue['context']}`"
                )

            for warning in result["warnings"]:
                total_warnings += 1
                print(
                    f"[WARN] {result['path']}:{warning['line']} "
                    f"innerHTML assignment in `{warning['context']}`"
                )

    if total_issues:
        print(f"\nFAIL: {total_issues} unsafe pattern(s) found.")
        exit_code = 1
    else:
        print(f"\nPASS: No unsafe patterns found.")

    if total_warnings:
        print(f"NOTE: {total_warnings} innerHTML usage(s) detected (legacy, not blocking).")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
