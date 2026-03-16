#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import re
import tempfile
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET


HP_NS = "http://www.hancom.co.kr/hwpml/2011/paragraph"
ET.register_namespace("hp", HP_NS)

P_TAG = f"{{{HP_NS}}}p"
RUN_TAG = f"{{{HP_NS}}}run"
TEXT_TAG = f"{{{HP_NS}}}t"


def paragraph_text(para: ET.Element) -> str:
    return "".join(t.text or "" for t in para.findall(f".//{TEXT_TAG}"))


def clone_run(run: ET.Element, text: str, *, char_pr: str | None = None) -> ET.Element:
    new_run = copy.deepcopy(run)
    if char_pr:
        new_run.attrib["charPrIDRef"] = char_pr
    for child in list(new_run):
        if child.tag == TEXT_TAG:
            new_run.remove(child)
    text_el = ET.SubElement(new_run, TEXT_TAG)
    text_el.text = text
    return new_run


def split_markdown_bold(text: str) -> list[tuple[str, bool]]:
    parts: list[tuple[str, bool]] = []
    idx = 0
    for match in re.finditer(r"\*\*(.+?)\*\*", text):
        if match.start() > idx:
            parts.append((text[idx:match.start()], False))
        parts.append((match.group(1), True))
        idx = match.end()
    if idx < len(text):
        parts.append((text[idx:], False))
    return [(chunk, is_bold) for chunk, is_bold in parts if chunk]


def restyle_generated_paragraphs(section_xml: bytes) -> bytes:
    root = ET.fromstring(section_xml)
    body_char_pr = "62"

    for para in root.findall(f".//{P_TAG}"):
        pid = para.attrib.get("id", "")
        text = paragraph_text(para)
        if not text:
            continue

        is_generated = pid.isdigit() and int(pid) >= 300000000
        if not is_generated:
            continue

        runs = para.findall(f"./{RUN_TAG}")
        if not runs:
            continue
        base_run = runs[0]

        if "**" in text:
            if text.startswith("• "):
                para.attrib["paraPrIDRef"] = "0"
            for child in list(para):
                if child.tag == RUN_TAG:
                    para.remove(child)
            for chunk, is_bold in split_markdown_bold(text):
                # Keep markdown emphasis subtle inside HWPX.
                para.append(clone_run(base_run, chunk.replace("**", ""), char_pr=body_char_pr))
            continue

        stripped = text.strip()
        if stripped == "목차":
            for run in para.findall(f"./{RUN_TAG}"):
                run.attrib["charPrIDRef"] = body_char_pr
            continue

        if stripped.startswith("• "):
            content = stripped[2:].strip()
            if re.match(r"^\d+\.\s+", content):
                para.attrib["paraPrIDRef"] = "0"
                for run in para.findall(f"./{RUN_TAG}"):
                    run.attrib["charPrIDRef"] = body_char_pr
                continue

            if re.match(r"^\d+-\d+\.\s+", content):
                para.attrib["paraPrIDRef"] = "0"
                for run in para.findall(f"./{RUN_TAG}"):
                    run.attrib["charPrIDRef"] = body_char_pr
                continue

            if re.match(r"^\d+(?:-\d+){2,}\.\s+", content):
                para.attrib["paraPrIDRef"] = "0"
                for run in para.findall(f"./{RUN_TAG}"):
                    run.attrib["charPrIDRef"] = body_char_pr
                continue

    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def update_hwpx(path: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="hwpx-restyle-") as tmpdir:
        tmpdir_path = Path(tmpdir)
        unzip_dir = tmpdir_path / "unzipped"
        unzip_dir.mkdir()

        with zipfile.ZipFile(path) as zf:
            zf.extractall(unzip_dir)
            infos = [copy.copy(info) for info in zf.infolist()]

        section_path = unzip_dir / "Contents" / "section0.xml"
        section_path.write_bytes(restyle_generated_paragraphs(section_path.read_bytes()))

        with zipfile.ZipFile(path, "w") as zf:
            for info in infos:
                src_path = unzip_dir / Path(info.filename)
                if src_path.is_dir():
                    continue
                data = src_path.read_bytes()
                new_info = zipfile.ZipInfo(info.filename)
                new_info.date_time = info.date_time
                new_info.compress_type = info.compress_type
                new_info.comment = info.comment
                new_info.extra = info.extra
                new_info.create_system = info.create_system
                new_info.create_version = info.create_version
                new_info.extract_version = info.extract_version
                new_info.flag_bits = info.flag_bits
                new_info.volume = info.volume
                new_info.internal_attr = info.internal_attr
                new_info.external_attr = info.external_attr
                zf.writestr(new_info, data, compress_type=info.compress_type)


def main() -> None:
    parser = argparse.ArgumentParser(description="Restyle generated markdown content inside an existing HWPX file.")
    parser.add_argument("hwpx_path", help="Path to the HWPX file to patch in place.")
    args = parser.parse_args()
    update_hwpx(Path(args.hwpx_path))


if __name__ == "__main__":
    main()
