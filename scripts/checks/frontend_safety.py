#!/usr/bin/env python3
"""Frontend static safety checker for public dashboard files."""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

PUBLIC_DIR = Path(__file__).resolve().parents[2] / "public"
DEFAULT_INLINE_EVENT_BASELINE = int(os.getenv("CONTROL_TOWER_FRONTEND_INLINE_EVENT_BASELINE", "0"))
DEFAULT_INNER_HTML_BASELINE = int(os.getenv("CONTROL_TOWER_FRONTEND_INNER_HTML_BASELINE", "49"))

INLINE_EVENT_RE = re.compile(
    r"\bon(click|change|submit|load|mouseover|mouseout|focus|blur|dblclick|keydown|keyup|keypress|input|scroll|resize|drag|drop|error|unload)\s*=",
    re.IGNORECASE,
)
SCRIPT_URL_SCHEME_RE = re.compile(r"""['"]\s*javascript\s*:\s*""", re.IGNORECASE)
INNER_HTML_RE = re.compile(r"\.innerHTML\s*=")
STYLESHEET_HREF_RE = re.compile(
    r"<link\b(?=[^>]*\brel\s*=\s*['\"]stylesheet['\"])[^>]*\bhref\s*=\s*['\"]([^'\"]+)['\"]",
    re.IGNORECASE,
)
SCRIPT_SRC_RE = re.compile(r"<script\b[^>]*\bsrc\s*=\s*['\"]([^'\"]+)['\"]", re.IGNORECASE)
ASSET_VERSION_RE = re.compile(r"(?:\?|&)v=\d{8}-\d+-\d+(?:$|[&#])")

EXCLUDED_DIRS = frozenset({"docs"})
EXCLUDED_FILES = frozenset()
LOCAL_ASSET_EXTENSIONS = (".css", ".js")


class SafetyReport:
    def __init__(self) -> None:
        self.inline_handlers: list[tuple[str, int, str]] = []
        self.script_urls: list[tuple[str, int, str]] = []
        self.inner_html_uses: list[tuple[str, int, str]] = []
        self.missing_asset_versions: list[tuple[str, int, str]] = []
        self.errors: list[str] = []

    def should_fail(self, inline_event_baseline: int, inner_html_baseline: int) -> bool:
        return bool(
            self.errors
            or self.script_urls
            or self.missing_asset_versions
            or len(self.inline_handlers) > inline_event_baseline
            or len(self.inner_html_uses) > inner_html_baseline
        )

    def print_summary(self, inline_event_baseline: int, inner_html_baseline: int, verbose: bool = False) -> None:
        inline_count = len(self.inline_handlers)
        inner_html_count = len(self.inner_html_uses)
        print("Frontend static safety check")
        print(f"inline-event count: {inline_count} / baseline {inline_event_baseline}")
        print(f"script-url count: {len(self.script_urls)}")
        print(f"asset-version errors: {len(self.missing_asset_versions)}")
        print(f"innerHTML warnings: {inner_html_count} / baseline {inner_html_baseline}")

        if self.errors:
            print("\nErrors:")
            for err in self.errors:
                print(f"  {err}")

        if self.script_urls:
            print("\nUnsafe script URL patterns:")
            for path, lineno, line in sorted(self.script_urls):
                print(f"  {path}:{lineno}  {line.strip()[:120]}")

        if self.missing_asset_versions:
            print("\nMissing static asset version queries:")
            for path, lineno, asset_url in sorted(self.missing_asset_versions):
                print(f"  {path}:{lineno}  {asset_url}")

        if inline_count > inline_event_baseline or verbose:
            print("\nInline event-handler attributes:")
            for path, lineno, line in sorted(self.inline_handlers):
                print(f"  {path}:{lineno}  {line.strip()[:120]}")

        if (inner_html_count > inner_html_baseline or verbose) and self.inner_html_uses:
            print("\ninnerHTML assignments:")
            for path, lineno, line in sorted(self.inner_html_uses):
                print(f"  {path}:{lineno}  {line.strip()[:120]}")

        verdict = "FAIL" if self.should_fail(inline_event_baseline, inner_html_baseline) else "PASS"
        print(f"\nRESULT: {verdict}")


def _is_external_url(asset_url: str) -> bool:
    parsed = urlparse(asset_url)
    return parsed.scheme in {"http", "https"} or asset_url.startswith("//")


def _asset_path(asset_url: str) -> str:
    parsed = urlparse(asset_url)
    return parsed.path or asset_url.split("?", 1)[0].split("#", 1)[0]


def _requires_version_query(asset_url: str) -> bool:
    if _is_external_url(asset_url):
        return False
    return _asset_path(asset_url).lower().endswith(LOCAL_ASSET_EXTENSIONS)


def _has_valid_version_query(asset_url: str) -> bool:
    parsed = urlparse(asset_url)
    query_and_fragment = ""
    if parsed.query:
        query_and_fragment += "?" + parsed.query
    if parsed.fragment:
        query_and_fragment += "#" + parsed.fragment
    return bool(ASSET_VERSION_RE.search(query_and_fragment))


def _iter_html_asset_urls(line: str) -> list[str]:
    urls = [match.group(1) for match in STYLESHEET_HREF_RE.finditer(line)]
    urls.extend(match.group(1) for match in SCRIPT_SRC_RE.finditer(line))
    return urls


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
        if filepath.suffix == ".html":
            for asset_url in _iter_html_asset_urls(line):
                if _requires_version_query(asset_url) and not _has_valid_version_query(asset_url):
                    report.missing_asset_versions.append((str(filepath), lineno, asset_url))


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
    parser.add_argument("--inner-html-baseline", type=int, default=DEFAULT_INNER_HTML_BASELINE)
    args = parser.parse_args()

    report = SafetyReport()
    target_dir = Path(args.dir) if args.dir else PUBLIC_DIR
    scan_directory(target_dir.resolve(), report)
    report.print_summary(args.inline_event_baseline, args.inner_html_baseline, verbose=args.verbose)
    return 1 if report.should_fail(args.inline_event_baseline, args.inner_html_baseline) else 0


if __name__ == "__main__":
    sys.exit(main())
