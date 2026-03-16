#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import html
import re
import shutil
import tempfile
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET


HP_NS = "http://www.hancom.co.kr/hwpml/2011/paragraph"
ET.register_namespace("hp", HP_NS)

P_TAG = f"{{{HP_NS}}}p"
RUN_TAG = f"{{{HP_NS}}}run"
TEXT_TAG = f"{{{HP_NS}}}t"
LINESEGARRAY_TAG = f"{{{HP_NS}}}linesegarray"
LINESEG_TAG = f"{{{HP_NS}}}lineseg"


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return text


def load_markdown(md_path: Path) -> list[tuple[str, str]]:
    text = normalize_text(md_path.read_text(encoding="utf-8"))
    blocks: list[tuple[str, str]] = []
    in_code = False
    code_lines: list[str] = []

    for raw_line in text.split("\n"):
        line = raw_line.rstrip()

        if line.startswith("```"):
            if in_code:
                if code_lines:
                    blocks.append(("code", "\n".join(code_lines)))
                code_lines = []
                in_code = False
            else:
                in_code = True
            continue

        if in_code:
            code_lines.append(line)
            continue

        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("# "):
            blocks.append(("h1", stripped[2:].strip()))
        elif stripped.startswith("## "):
            blocks.append(("h2", stripped[3:].strip()))
        elif stripped.startswith("### "):
            blocks.append(("h3", stripped[4:].strip()))
        elif "![" in stripped and "](" in stripped:
            blocks.append(("image", stripped))
        elif re.match(r"^[-*]\s+", stripped):
            blocks.append(("bullet", re.sub(r"^[-*]\s+", "", stripped)))
        elif re.match(r"^\d+\.\s+", stripped):
            blocks.append(("number", stripped))
        elif stripped.startswith(">"):
            blocks.append(("quote", stripped.lstrip("> ").strip()))
        else:
            blocks.append(("body", stripped))

    if code_lines:
        blocks.append(("code", "\n".join(code_lines)))

    return blocks


def blocks_to_preview_text(blocks: list[tuple[str, str]]) -> str:
    lines: list[str] = []
    for kind, text in blocks:
        if kind == "h1":
            lines.append(text)
            lines.append("")
        elif kind == "h2":
            lines.append(text)
        elif kind == "h3":
            lines.append(text)
        elif kind == "bullet":
            lines.append(f"• {text}")
        elif kind == "image":
            lines.append(re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", r"[이미지] \1 (\2)", text))
        else:
            lines.append(text)
    return "\n".join(lines).strip() + "\n"


def blocks_to_html(blocks: list[tuple[str, str]], title: str) -> str:
    pages: list[list[str]] = [[]]
    in_list = False

    def current_page() -> list[str]:
        return pages[-1]

    def close_list() -> None:
        nonlocal in_list
        if in_list:
            current_page().append("</ul>")
            in_list = False

    def start_new_page() -> None:
        close_list()
        if pages[-1]:
            pages.append([])

    for kind, text in blocks:
        escaped = html.escape(text)
        if kind == "h1":
            start_new_page()
            close_list()
            current_page().append(f"<h1>{escaped}</h1>")
        elif kind == "h2":
            close_list()
            current_page().append(f"<h2>{escaped}</h2>")
        elif kind == "h3":
            close_list()
            current_page().append(f"<h3>{escaped}</h3>")
        elif kind == "bullet":
            if not in_list:
                current_page().append("<ul>")
                in_list = True
            current_page().append(f"<li>{escaped}</li>")
        elif kind == "number":
            close_list()
            current_page().append(f"<p>{escaped}</p>")
        elif kind == "image":
            close_list()
            match = re.search(r'!\[([^\]]*)\]\(([^)]+)\)', text)
            if match:
                alt, src = match.group(1), match.group(2)
                prefix = text[: match.start()].strip(" -")
                caption = html.escape(prefix or alt or "이미지")
                current_page().append(
                    f'<figure class="report-figure"><img src="{html.escape(src)}" alt="{html.escape(alt)}" /><figcaption>{caption}</figcaption></figure>'
                )
            else:
                current_page().append(f"<p>{escaped}</p>")
        elif kind == "quote":
            close_list()
            current_page().append(f"<blockquote>{escaped}</blockquote>")
        elif kind == "code":
            close_list()
            current_page().append(f"<pre><code>{escaped}</code></pre>")
        else:
            close_list()
            current_page().append(f"<p>{escaped}</p>")
    close_list()

    rendered_pages = []
    for idx, page in enumerate(pages):
        if not page:
            continue
        cls = "page" if idx < len(pages) - 1 else "page last-page"
        rendered_pages.append(f'<section class="{cls}">{"".join(page)}</section>')

    return f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8" />
  <title>{html.escape(title)}</title>
  <style>
    @page {{ size: A4; margin: 18mm 16mm 18mm 16mm; }}
    * {{ box-sizing: border-box; }}
    body {{ font-family: 'Malgun Gothic', 'Noto Sans KR', sans-serif; margin: 0; color: #111; background: #f3f4f6; line-height: 1.7; }}
    .page {{
      width: 210mm;
      min-height: 297mm;
      margin: 0 auto 12mm;
      padding: 18mm 16mm 18mm 16mm;
      background: white;
      box-shadow: 0 8px 24px rgba(0,0,0,.08);
      page-break-after: always;
      break-after: page;
    }}
    .last-page {{ page-break-after: auto; break-after: auto; }}
    h1 {{ font-size: 24px; margin: 0 0 1rem; border-bottom: 2px solid #222; padding-bottom: .35rem; }}
    h2 {{ font-size: 18px; margin-top: 1.35rem; margin-bottom: .55rem; }}
    h3 {{ font-size: 18px; margin-top: 1.2rem; }}
    p, li, blockquote, pre {{ font-size: 13px; margin: .35rem 0; }}
    ul {{ padding-left: 1.2rem; margin: .35rem 0; }}
    blockquote {{ border-left: 3px solid #ccc; padding-left: 12px; color: #444; }}
    pre {{ background: #f6f8fa; padding: 12px; overflow-x: auto; }}
    .report-figure {{ margin: 1rem 0 1.2rem; page-break-inside: avoid; break-inside: avoid; }}
    .report-figure img {{ max-width: 100%; display: block; border: 1px solid #ddd; }}
    .report-figure figcaption {{ font-size: 12px; color: #444; margin-top: .35rem; }}
    @media print {{
      body {{ background: white; }}
      .page {{
        width: auto;
        min-height: auto;
        margin: 0;
        padding: 0;
        box-shadow: none;
      }}
    }}
  </style>
</head>
<body>
{''.join(rendered_pages)}
</body>
</html>
"""


def clone_base_paragraph(
    base_para: ET.Element,
    text: str,
    *,
    page_break: bool = False,
    char_pr: str | None = None,
    para_id: int = 0,
) -> ET.Element:
    para = copy.deepcopy(base_para)
    para.attrib["id"] = str(para_id)
    para.attrib["pageBreak"] = "1" if page_break else "0"
    para.attrib["columnBreak"] = "0"
    para.attrib["merged"] = "0"

    # Remove everything except a single run + linesegarray.
    for child in list(para):
        para.remove(child)

    run = ET.SubElement(para, RUN_TAG)
    run.attrib["charPrIDRef"] = char_pr or "125"
    text_el = ET.SubElement(run, TEXT_TAG)
    text_el.text = text

    linesegarray = ET.SubElement(para, LINESEGARRAY_TAG)
    lineseg = ET.SubElement(linesegarray, LINESEG_TAG)
    lineseg.attrib.update(
        {
            "textpos": "0",
            "vertpos": "0",
            "vertsize": "1200",
            "textheight": "1200",
            "baseline": "1020",
            "spacing": "720",
            "horzpos": "0",
            "horzsize": "46488",
            "flags": "393216",
        }
    )
    return para


def build_paragraphs(blocks: list[tuple[str, str]], base_para: ET.Element) -> list[ET.Element]:
    paragraphs: list[ET.Element] = []
    first_h1 = True
    next_id = 300000000
    body_char_pr = "129"
    for kind, text in blocks:
        if kind == "h1":
            paragraphs.append(clone_base_paragraph(base_para, text, page_break=not first_h1, char_pr=body_char_pr, para_id=next_id))
            first_h1 = False
        elif kind == "h2":
            paragraphs.append(clone_base_paragraph(base_para, text, char_pr=body_char_pr, para_id=next_id))
        elif kind == "h3":
            paragraphs.append(clone_base_paragraph(base_para, text, char_pr=body_char_pr, para_id=next_id))
        elif kind == "bullet":
            paragraphs.append(clone_base_paragraph(base_para, f"• {text}", char_pr=body_char_pr, para_id=next_id))
        elif kind == "number":
            paragraphs.append(clone_base_paragraph(base_para, text, char_pr=body_char_pr, para_id=next_id))
        elif kind == "image":
            cleaned = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", r"[이미지] \1 (\2)", text)
            paragraphs.append(clone_base_paragraph(base_para, cleaned, char_pr=body_char_pr, para_id=next_id))
        elif kind == "quote":
            paragraphs.append(clone_base_paragraph(base_para, f"인용: {text}", char_pr=body_char_pr, para_id=next_id))
        elif kind == "code":
            for line in text.splitlines():
                paragraphs.append(clone_base_paragraph(base_para, line or " ", char_pr=body_char_pr, para_id=next_id))
                next_id += 1
        else:
            paragraphs.append(clone_base_paragraph(base_para, text, char_pr=body_char_pr, para_id=next_id))
        next_id += 1
    return paragraphs


def update_hwpx(
    template_hwpx: Path,
    md_path: Path,
    output_hwpx: Path,
    *,
    html_output: Path | None = None,
    text_output: Path | None = None,
) -> None:
    blocks = load_markdown(md_path)
    with tempfile.TemporaryDirectory(prefix="hwpx-build-") as tmpdir:
        tmpdir_path = Path(tmpdir)
        unzip_dir = tmpdir_path / "unzipped"
        unzip_dir.mkdir()
        with zipfile.ZipFile(template_hwpx) as zf:
            zf.extractall(unzip_dir)
            original_infos = [copy.copy(info) for info in zf.infolist()]

        section_path = unzip_dir / "Contents" / "section0.xml"
        tree = ET.parse(section_path)
        root = tree.getroot()
        paragraphs = root.findall(P_TAG)
        if len(paragraphs) < 16:
            raise RuntimeError("Unexpected HWPX structure: section0.xml paragraph count is too small.")

        base_para = paragraphs[15]
        new_body = build_paragraphs(blocks, base_para)
        # Keep only the actual front matter pages from the source HWPX.
        # Drop instruction pages and old body/appendix pages so the rebuilt
        # report is driven by the current markdown content.
        # Keep the original cover/front-matter selection.
        keep_prefix_indexes = [0, 2, 4]
        prefix = [paragraphs[idx] for idx in keep_prefix_indexes if idx < len(paragraphs)]

        for child in list(root):
            if child.tag == P_TAG:
                root.remove(child)

        for para in prefix + new_body:
            root.append(para)

        tree.write(section_path, encoding="utf-8", xml_declaration=True)

        preview_text = blocks_to_preview_text(blocks)
        (unzip_dir / "Preview" / "PrvText.txt").write_text(preview_text, encoding="utf-8")

        output_hwpx.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(output_hwpx, "w") as zf:
            for info in original_infos:
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

    if html_output:
        html_output.parent.mkdir(parents=True, exist_ok=True)
        html_output.write_text(blocks_to_html(blocks, md_path.stem), encoding="utf-8")
    if text_output:
        text_output.parent.mkdir(parents=True, exist_ok=True)
        text_output.write_text(blocks_to_preview_text(blocks), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a draft HWPX report from markdown and an existing HWPX template.")
    parser.add_argument("--template", required=True, help="Path to the source HWPX template.")
    parser.add_argument("--markdown", required=True, help="Path to the markdown source file.")
    parser.add_argument("--output", required=True, help="Path to the generated HWPX file.")
    parser.add_argument("--html-output", help="Optional path to a companion HTML preview.")
    parser.add_argument("--text-output", help="Optional path to a companion text preview.")
    args = parser.parse_args()

    update_hwpx(
        Path(args.template),
        Path(args.markdown),
        Path(args.output),
        html_output=Path(args.html_output) if args.html_output else None,
        text_output=Path(args.text_output) if args.text_output else None,
    )
    print(args.output)


if __name__ == "__main__":
    main()
