#!/usr/bin/env python3
"""Frontend static safety checker for public dashboard files.

The current dashboard is incrementally hardening legacy string-rendered UI code.
This checker blocks high-risk script URL patterns immediately and prevents the
legacy inline event-handler count from increasing beyond an explicit baseline.
Raw innerHTML assignments are reported as warnings only for now.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

PUBLIC_DIR = Path(__file__).resolve().parent.parent / "public"
DEFAULT_INLINE_EVENT_BASELINE = int(os.getenv("CONTROL_TOWER_FRONTEND_INLINE_EVENT_BASELINE", "47"))

INLINE_EVENT_RE = re.compile(
    r"\bon(click|change|submit|load|mouseover|mouseout|focus|blur|dblclick|keydown|keyup|keypress|input|scroll|resize|drag|drop|error|unload)\s*=",
    re.IGNORECASE,
)
SCRIPT_URL_SCHEME_RE = re.compile(r"""['"]\s*javascript\s*:\s*""", re.IGNORECASE)
INNER_HTML_RE = re.compile(r"\.innerHTML\s*=")

EXCLUDED_DIRS = frozenset({"docs"})
EXCLUDED_FILES = frozenset()


class SafetyReport:
    def __init__(self) -> None:
        self.inline_handlers: list[tuple[str, int, str]] = []
        self.script_urls: list[tuple[str, int, str]] = []
        self.inner_html_uses: list[tuple[str, int, str]] = []
        self.errors: list[str] = []

    def should_fail(self, inline_event_baseline: int) -> bool:
        return bool(self.errors or self.script_urls or len(self.inline_handlers) > inline_event_baseline)

    def print_summary(self, inline_event_baseline: int, verbose: bool = False) -> None:
        inline_count = len(self.inline_handlers)
        print("Frontend static safety check")
        print(f"inline-event count: {inline_count} / baseline {inline_event_baseline}")
        print(f"script-url count: {len(self.script_urls)}")
        print(f"innerHTML warnings: {len(self.inner_html_uses)}")

        if self.errors:
            print("\nErrors:")
            for err in self.errors:
                print(f"  {err}")

        if self.script_urls:
            print("\nUnsafe script URL patterns:")
            for path, lineno, line in sorted(self.script_urls):
                print(f"  {path}:{lineno}  {line.strip()[:120]}")

        if inline_count > inline_event_baseline or verbose:
            print("\nInline event-handler attributes:")
            for path, lineno, line in sorted(self.inline_handlers):
                print(f"  {path}:{lineno}  {line.strip()[:120]}")

        if verbose and self.inner_html_uses:
            print("\ninnerHTML assignments [report-only]:")
            for path, lineno, line in sorted(self.inner_html_uses):
                print(f"  {path}:{lineno}  {line.strip()[:120]}")

        verdict = "FAIL" if self.should_fail(inline_event_baseline) else "PASS"
        print(f"\nRESULT: {verdict}")


def scan_file(filepath: Path, report: SafetyReport) -> None:
    try:
        text = filepath.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        report.errors.append(f"Cannot read {filepath}: {exc}")
        return

    for lineno, line in enumerate(text.splitlines(), start=1):
        if INLINE_EVENT_RE.search(line):
            report.inline_handlers.append((str(filepath), lineno, line))
        if SCRIPT_URL_SCHEME_RE.search(line):
            report.script_urls.append((str(filepath), lineno, line))
        if INNER_HTML_RE.search(line):
            report.inner_html_uses.append((str(filepath), lineno, line))


def scan_directory(root: Path, report: SafetyReport) -> None:
    if not root.exists():
        report.errors.append(f"Directory not found: {root}")
        return

    for entry in sorted(root.iterdir()):
        if entry.name.startswith("."):
            continue
        if entry.is_dir():
            if entry.name in EXCLUDED_DIRS:
                continue
            scan_directory(entry, report)
            continue
        if entry.suffix not in {".js", ".html"}:
            continue
        if entry.name in EXCLUDED_FILES:
            continue
        scan_file(entry, report)


def main() -> int:
    parser = argparse.ArgumentParser(description="Check frontend files for risky static patterns.")
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("--dir", type=str, default=None)
    parser.add_argument("--inline-event-baseline", type=int, default=DEFAULT_INLINE_EVENT_BASELINE)
    args = parser.parse_args()

    report = SafetyReport()
    target_dir = Path(args.dir) if args.dir else PUBLIC_DIR
    scan_directory(target_dir.resolve(), report)
    report.print_summary(args.inline_event_baseline, verbose=args.verbose)
    return 1 if report.should_fail(args.inline_event_baseline) else 0


if __name__ == "__main__":
    sys.exit(main())
