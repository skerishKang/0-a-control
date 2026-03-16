#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import tempfile
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET


HP_NS = "http://www.hancom.co.kr/hwpml/2011/paragraph"
P_TAG = f"{{{HP_NS}}}p"


def load_root(path: Path) -> ET.Element:
    with zipfile.ZipFile(path) as zf:
        return ET.fromstring(zf.read("Contents/section0.xml"))


def find_first_para_by_id(root: ET.Element, para_id: str) -> ET.Element | None:
    for para in root.findall(f".//{P_TAG}"):
        if para.attrib.get("id") == para_id:
            return para
    return None


def restore_front_para(current_hwpx: Path, reference_hwpx: Path, para_id: str = "0") -> None:
    with tempfile.TemporaryDirectory(prefix="hwpx-restore-front-") as tmpdir:
        tmpdir_path = Path(tmpdir)
        unzip_dir = tmpdir_path / "unzipped"
        unzip_dir.mkdir()

        with zipfile.ZipFile(current_hwpx) as zf:
            zf.extractall(unzip_dir)
            infos = [copy.copy(info) for info in zf.infolist()]

        current_root = ET.parse(unzip_dir / "Contents" / "section0.xml").getroot()
        reference_root = load_root(reference_hwpx)

        current_para = find_first_para_by_id(current_root, para_id)
        reference_para = find_first_para_by_id(reference_root, para_id)
        if current_para is None or reference_para is None:
            raise RuntimeError(f"Could not find paragraph id={para_id} in both HWPX files")

        parent = current_root
        children = list(parent)
        idx = children.index(current_para)
        parent.remove(current_para)
        parent.insert(idx, copy.deepcopy(reference_para))

        ET.ElementTree(current_root).write(
            unzip_dir / "Contents" / "section0.xml",
            encoding="utf-8",
            xml_declaration=True,
        )

        with zipfile.ZipFile(current_hwpx, "w") as zf:
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
    parser = argparse.ArgumentParser(description="Restore the first front-matter paragraph from a reference HWPX.")
    parser.add_argument("--current", required=True, help="Current HWPX to patch in place")
    parser.add_argument("--reference", required=True, help="Reference HWPX to copy paragraph from")
    parser.add_argument("--para-id", default="0", help="Paragraph id to restore (default: 0)")
    args = parser.parse_args()
    restore_front_para(Path(args.current), Path(args.reference), para_id=args.para_id)


if __name__ == "__main__":
    main()
