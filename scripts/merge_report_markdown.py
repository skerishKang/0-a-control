#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from collections import OrderedDict
from pathlib import Path


HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
IMAGE_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")


def split_sections(text: str) -> OrderedDict[str, list[str]]:
    sections: OrderedDict[str, list[str]] = OrderedDict()
    current = "__preamble__"
    sections[current] = []
    for line in text.splitlines():
        m = HEADING_RE.match(line.strip())
        if m:
            current = m.group(2).strip()
            sections.setdefault(current, [])
            sections[current].append(line)
        else:
            sections.setdefault(current, [])
            sections[current].append(line)
    return sections


def section_blocks(lines: list[str]) -> list[str]:
    blocks: list[str] = []
    current: list[str] = []
    for line in lines:
        if not line.strip():
            if current:
                blocks.append("\n".join(current).strip())
                current = []
            continue
        current.append(line)
    if current:
        blocks.append("\n".join(current).strip())
    return blocks


def image_blocks(lines: list[str]) -> list[str]:
    result: list[str] = []
    for block in section_blocks(lines):
        if "![" in block and "](" in block:
            result.append(block)
    return result


def extract_image_paths(text: str) -> list[str]:
    return [match.group(1).strip() for match in IMAGE_RE.finditer(text)]


def dedupe_image_blocks(text: str) -> str:
    kept: list[str] = []
    seen_paths: set[str] = set()
    for block in section_blocks(text.splitlines()):
        block_paths = extract_image_paths(block)
        if block_paths and any(path in seen_paths for path in block_paths):
            continue
        kept.append(block)
        for path in block_paths:
            seen_paths.add(path)
    return "\n\n".join(kept).strip()


def merge_markdown(primary_path: Path, secondary_path: Path, output_path: Path) -> None:
    primary = split_sections(primary_path.read_text(encoding="utf-8"))
    secondary = split_sections(secondary_path.read_text(encoding="utf-8"))

    merged_sections: list[str] = []
    for section_name, primary_lines in primary.items():
        section_text = "\n".join(primary_lines).rstrip()
        secondary_lines = secondary.get(section_name)
        if secondary_lines:
            existing_paths = set(extract_image_paths(section_text))
            for block in image_blocks(secondary_lines):
                block_paths = extract_image_paths(block)
                if not block_paths:
                    continue
                if any(path in existing_paths for path in block_paths):
                    continue
                if section_text and not section_text.endswith("\n\n"):
                    section_text += "\n\n"
                section_text += block
                for path in block_paths:
                    existing_paths.add(path)
        merged_sections.append(dedupe_image_blocks(section_text))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n\n".join(part for part in merged_sections if part).strip() + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge primary report markdown with image/caption blocks from a secondary markdown.")
    parser.add_argument("--primary", required=True)
    parser.add_argument("--secondary", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    merge_markdown(Path(args.primary), Path(args.secondary), Path(args.output))
    print(args.output)


if __name__ == "__main__":
    main()
