import re, os

PAGES_DIR = r"G:\Ddrive\BatangD\task\workdiary\1. 매일정리\5. 공부및일지\공부\250208_NLPtext\html-codex-flash\11-machine-translation-and-encoder-decoder-models\pages"
HTML_DIR = r"G:\Ddrive\BatangD\task\workdiary\1. 매일정리\5. 공부및일지\공부\250208_NLPtext\html-codex-flash\11-machine-translation-and-encoder-decoder-models\html"

CSS = """\
:root { --bg: #f6f1e8; --paper: #fffdf8; --ink: #1f1b16; --muted: #6f675d; --line: #ddd2c2; --accent: #8c5a2b; --accent-soft: #f1e2cf; --note-bg: #faf4ea; --source-bg: #f5f3ef; --translation-bg: #fff8ea; --shadow: 0 10px 30px rgba(53, 40, 24, 0.08); --radius: 18px; }
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body { margin: 0; background: radial-gradient(circle at top left, rgba(140, 90, 43, 0.1), transparent 28%), linear-gradient(180deg, #f9f4ec 0%, var(--bg) 100%); color: var(--ink); font: 16px/1.7 "Noto Sans KR", "Apple SD Gothic Neo", "Malgun Gothic", sans-serif; }
.shell { width: min(1100px, calc(100% - 32px)); margin: 0 auto; padding: 24px 0 64px; }
.topbar { position: sticky; top: 0; z-index: 10; backdrop-filter: blur(10px); background: rgba(246, 241, 232, 0.88); border-bottom: 1px solid rgba(221, 210, 194, 0.85); margin-bottom: 24px; }
.topbar-inner { width: min(1100px, calc(100% - 32px)); margin: 0 auto; padding: 14px 0; display: flex; gap: 16px; align-items: center; justify-content: space-between; flex-wrap: wrap; }
.doc-meta { display: flex; flex-direction: column; gap: 2px; }
.eyebrow { color: var(--muted); font-size: 13px; letter-spacing: 0.06em; text-transform: uppercase; }
h1 { margin: 0; font-size: clamp(22px, 4vw, 34px); line-height: 1.15; font-weight: 800; }
.quick-nav, .actions { display: flex; gap: 8px; flex-wrap: wrap; }
.chip, .action-btn { border: 1px solid var(--line); background: rgba(255, 253, 248, 0.92); color: var(--ink); border-radius: 999px; padding: 8px 14px; font: inherit; font-size: 14px; cursor: pointer; text-decoration: none; transition: transform 0.15s ease, background 0.15s ease; }
.chip:hover, .action-btn:hover { transform: translateY(-1px); background: #fff; }
.hero { background: var(--paper); border: 1px solid var(--line); border-radius: calc(var(--radius) + 4px); box-shadow: var(--shadow); padding: 28px; margin-bottom: 24px; }
.hero p { margin: 10px 0 0; color: var(--muted); }
.hero-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin-top: 18px; }
.meta-card { padding: 14px 16px; border-radius: 14px; background: #fcf7f0; border: 1px solid var(--line); }
.meta-card dt { font-size: 12px; color: var(--muted); margin-bottom: 6px; }
.meta-card dd { margin: 0; font-weight: 700; }
.page { margin-bottom: 28px; background: var(--paper); border: 1px solid var(--line); border-radius: calc(var(--radius) + 2px); box-shadow: var(--shadow); overflow: hidden; }
.page-header { padding: 20px 24px; background: linear-gradient(135deg, #fff8eb, #f5ead8); border-bottom: 1px solid var(--line); }
.page-header h2 { margin: 0; font-size: 28px; line-height: 1.15; }
.page-subtitle { margin-top: 6px; color: var(--muted); font-size: 14px; }
.blocks { padding: 18px; display: grid; gap: 16px; }
.block { border: 1px solid var(--line); border-radius: var(--radius); overflow: hidden; background: #fffdfa; }
.block-head { padding: 14px 16px; border-bottom: 1px solid var(--line); display: flex; justify-content: space-between; gap: 10px; align-items: center; flex-wrap: wrap; }
.block-title { font-weight: 800; }
.block-type { color: var(--accent); background: var(--accent-soft); border-radius: 999px; padding: 4px 10px; font-size: 13px; font-weight: 700; }
.block-body { padding: 16px; display: grid; gap: 14px; }
.label { display: inline-block; font-size: 12px; font-weight: 800; letter-spacing: 0.04em; color: var(--muted); text-transform: uppercase; margin-bottom: 8px; }
.source, .translation, .note-panel { border-radius: 14px; padding: 14px 16px; border: 1px solid var(--line); }
.source { background: var(--source-bg); }
.translation { background: var(--translation-bg); }
.note-panel { background: var(--note-bg); }
.source pre, .translation pre, .note-panel pre { margin: 0; white-space: pre-wrap; word-break: break-word; font: inherit; }
.mono pre { font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace; font-size: 14px; line-height: 1.6; }
.note-toggle { align-self: start; border: 1px solid var(--line); background: #fff; border-radius: 999px; padding: 8px 12px; font: inherit; font-size: 14px; cursor: pointer; }
.note-panel[hidden] { display: none; }
@media (max-width: 720px) { .shell { width: min(100% - 20px, 100%); } .topbar-inner { width: min(100% - 20px, 100%); } .hero, .page-header, .blocks, .block-head, .block-body { padding-left: 14px; padding-right: 14px; } }"""

JS = """\
const toggles = Array.from(document.querySelectorAll(".note-toggle"));
function setPanelState(toggle, expanded) {
const panel = toggle.nextElementSibling;
toggle.setAttribute("aria-expanded", expanded ? "true" : "false");
toggle.textContent = expanded ? "study_note 접기" : "study_note 보기";
panel.hidden = !expanded;
}
toggles.forEach((toggle) => {
setPanelState(toggle, false);
toggle.addEventListener("click", () => {
const expanded = toggle.getAttribute("aria-expanded") === "true";
setPanelState(toggle, !expanded);
});
});
document.querySelector("[data-expand-all]").addEventListener("click", () => {
toggles.forEach((toggle) => setPanelState(toggle, true));
});
document.querySelector("[data-collapse-all]").addEventListener("click", () => {
toggles.forEach((toggle) => setPanelState(toggle, false));
});"""

def parse_md(content):
    pages = []
    current_page = None
    current_block = None
    for line in content.split("\n"):
        if line.startswith("# Page "):
            if current_page and current_block:
                current_page["blocks"].append(current_block)
                current_block = None
            if current_page:
                pages.append(current_page)
            page_num = int(line.replace("# Page ", "").strip())
            current_page = {"num": page_num, "blocks": []}
        elif line.startswith("## Block "):
            if current_block:
                current_page["blocks"].append(current_block)
            block_num = int(line.replace("## Block ", "").strip())
            current_block = {"num": block_num, "type": "", "source_text": "", "korean_translation": "", "study_note": ""}
        elif current_block is not None:
            m = re.match(r"-\s+(\w+):\s*(.*)", line)
            if m:
                key, val = m.group(1), m.group(2)
                if key in current_block:
                    if current_block[key]:
                        current_block[key] += "\n" + val
                    else:
                        current_block[key] = val
    if current_block and current_page:
        current_page["blocks"].append(current_block)
    if current_page:
        pages.append(current_page)
    return pages

def get_subtitle(pages):
    for p in pages:
        for b in p["blocks"]:
            if b["type"] == "section_title":
                return b["korean_translation"]
    return ""

def build_html(pages):
    page_nums = [p["num"] for p in pages]
    min_p, max_p = min(page_nums), max(page_nums)
    title = f"Pages {min_p}-{max_p} | Machine Translation and Encoder-Decoder Models"
    chips = ""
    for p in pages:
        chips += f'<a class="chip" href="#page-{p["num"]}">Page {p["num"]}</a>\n'
    subtitle = get_subtitle(pages)
    page_sections = ""
    for p in pages:
        blocks_html = ""
        for b in p["blocks"]:
            mono_class = " mono" if b["type"] in ("formula", "structural_formula", "code") else ""
            blocks_html += '<article class="block">\n'
            blocks_html += f'<div class="block-head"><div class="block-title">Block {b["num"]}</div><div class="block-type">{b["type"]}</div></div>\n'
            blocks_html += '<div class="block-body">\n'
            blocks_html += f'<section class="source{mono_class}"><div class="label">Source Text</div><pre>{b["source_text"]}</pre></section>\n'
            blocks_html += f'<section class="translation"><div class="label">Korean Translation</div><pre>{b["korean_translation"]}</pre></section>\n'
            blocks_html += '<button class="note-toggle" type="button" aria-expanded="false">study_note 보기</button>\n'
            blocks_html += f'<section class="note-panel" hidden><div class="label">Study Note</div><pre>{b["study_note"]}</pre></section>\n'
            blocks_html += "</div>\n</article>\n"
        page_sections += f'\n<section class="page" id="page-{p["num"]}">\n'
        page_sections += '<header class="page-header">\n'
        page_sections += f'<h2>Page {p["num"]}</h2>\n'
        page_sections += f'<div class="page-subtitle">{subtitle}</div>\n'
        page_sections += '</header>\n'
        page_sections += '<div class="blocks">\n'
        page_sections += blocks_html
        page_sections += "</div>\n</section>\n"

    html = f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
{CSS}
</style>
</head>
<body>
<div class="topbar">
<div class="topbar-inner">
<div class="doc-meta">
<div class="eyebrow">11 Machine Translation and Encoder-Decoder Models</div>
<h1>Machine Translation and Encoder-Decoder Models</h1>
</div>
<div class="quick-nav">
{chips}</div>
<div class="actions">
<button class="action-btn" type="button" data-expand-all>모든 주석 펼치기</button>
<button class="action-btn" type="button" data-collapse-all>모든 주석 접기</button>
</div>
</div>
</div>

<main class="shell">
<section class="hero">
<div class="eyebrow">Study Edition</div>
<h2>Pages {min_p}-{max_p} Annotated Page</h2>
<p>본문은 바로 읽고, `study_note`만 접어서 여는 형태로 구성했습니다.</p>
<div class="hero-grid">
<dl class="meta-card"><dt>Source</dt><dd>11. Machine Translation and Encoder-Decoder Models.pdf</dd></dl>
<dl class="meta-card"><dt>Workflow</dt><dd>html-codex-flash</dd></dl>
<dl class="meta-card"><dt>Status</dt><dd>Accepted</dd></dl>
</div>
</section>
{page_sections}
</main>

<script>
{JS}
</script>
</body>
</html>"""
    return html

files_to_process = [
    ("01-pages-01-02.md", "01-pages-01-02.html"),
    ("02-pages-03-04.md", "02-pages-03-04.html"),
    ("03-pages-05-06.md", "03-pages-05-06.html"),
    ("04-pages-07-08.md", "04-pages-07-08.html"),
    ("05-pages-09-10.md", "05-pages-09-10.html"),
    ("06-pages-11-12.md", "06-pages-11-12.html"),
    ("07-pages-13-14.md", "07-pages-13-14.html"),
    ("08-pages-15-16.md", "08-pages-15-16.html"),
    ("09-pages-17-18.md", "09-pages-17-18.html"),
    ("10-pages-19-20.md", "10-pages-19-20.html"),
    ("11-pages-21-22.md", "11-pages-21-22.html"),
    ("12-pages-23-24.md", "12-pages-23-24.html"),
    ("13-pages-25-26.md", "13-pages-25-26.html"),
    ("14-pages-27-28.md", "14-pages-27-28.html"),
    ("15-pages-29-30.md", "15-pages-29-30.html"),
]

for md_name, html_name in files_to_process:
    md_path = os.path.join(PAGES_DIR, md_name)
    html_path = os.path.join(HTML_DIR, html_name)
    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()
    pages = parse_md(content)
    html = build_html(pages)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    block_count = sum(len(p["blocks"]) for p in pages)
    print(f"saved: {html_name} ({len(pages)} pages, {block_count} blocks)")

# Now create index.html
index_html = """<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Machine Translation and Encoder-Decoder Models - Index</title>
<style>
:root { --bg: #f6f1e8; --paper: #fffdf8; --ink: #1f1b16; --muted: #6f675d; --line: #ddd2c2; --accent: #8c5a2b; --accent-soft: #f1e2cf; --shadow: 0 10px 30px rgba(53, 40, 24, 0.08); --radius: 18px; }
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body { margin: 0; background: radial-gradient(circle at top left, rgba(140, 90, 43, 0.1), transparent 28%), linear-gradient(180deg, #f9f4ec 0%, var(--bg) 100%); color: var(--ink); font: 16px/1.7 "Noto Sans KR", "Apple SD Gothic Neo", "Malgun Gothic", sans-serif; }
.shell { width: min(1100px, calc(100% - 32px)); margin: 0 auto; padding: 24px 0 64px; }
.topbar { position: sticky; top: 0; z-index: 10; backdrop-filter: blur(10px); background: rgba(246, 241, 232, 0.88); border-bottom: 1px solid rgba(221, 210, 194, 0.85); margin-bottom: 24px; }
.topbar-inner { width: min(1100px, calc(100% - 32px)); margin: 0 auto; padding: 14px 0; display: flex; gap: 16px; align-items: center; justify-content: space-between; flex-wrap: wrap; }
.doc-meta { display: flex; flex-direction: column; gap: 2px; }
.eyebrow { color: var(--muted); font-size: 13px; letter-spacing: 0.06em; text-transform: uppercase; }
h1 { margin: 0; font-size: clamp(22px, 4vw, 34px); line-height: 1.15; font-weight: 800; }
.content { background: var(--paper); border: 1px solid var(--line); border-radius: calc(var(--radius) + 2px); box-shadow: var(--shadow); padding: 28px; }
.page-links { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; }
.page-link { display: block; padding: 16px; border-radius: var(--radius); background: linear-gradient(135deg, #fff8eb, #f5ead8); border: 1px solid var(--line); text-decoration: none; color: var(--ink); transition: transform 0.15s ease, background 0.15s ease; }
.page-link:hover { transform: translateY(-2px); background: #fff; }
.page-link h3 { margin: 0 0 8px; font-size: 18px; }
.page-link p { margin: 0; color: var(--muted); font-size: 14px; }
@media (max-width: 720px) { .shell { width: min(100% - 20px, 100%); } .topbar-inner { width: min(100% - 20px, 100%); } }
</style>
</head>
<body>
<div class="topbar">
<div class="topbar-inner">
<div class="doc-meta">
<div class="eyebrow">11 Machine Translation and Encoder-Decoder Models</div>
<h1>Machine Translation and Encoder-Decoder Models</h1>
</div>
</div>
</div>

<main class="shell">
<section class="content">
<h2>페이지별 링크</h2>
<div class="page-links">
<a class="page-link" href="01-pages-01-02.html">
<h3>Pages 1-2</h3>
<p>기계 번역 및 인코더-디코더 모델 소개</p>
</a>
<a class="page-link" href="02-pages-03-04.html">
<h3>Pages 3-4</h3>
<p>언어 간 차이 및 유형론</p>
</a>
<a class="page-link" href="03-pages-05-06.html">
<h3>Pages 5-6</h3>
<p>이동 동사 표현 및 형태론적 유형론</p>
</a>
<a class="page-link" href="04-pages-07-08.html">
<h3>Pages 7-8</h3>
<p>인코더 디코더 상세 구조</p>
</a>
<a class="page-link" href="05-pages-09-10.html">
<h3>Pages 9-10</h3>
<p>어텐션 메커니즘</p>
</a>
<a class="page-link" href="06-pages-11-12.html">
<h3>Pages 11-12</h3>
<p>어텐션 메커니즘 (계속)</p>
</a>
<a class="page-link" href="07-pages-13-14.html">
<h3>Pages 13-14</h3>
<p>빔 서치</p>
</a>
<a class="page-link" href="08-pages-15-16.html">
<h3>Pages 15-16</h3>
<p>빔 서치 및 트랜스포머</p>
</a>
<a class="page-link" href="09-pages-17-18.html">
<h3>Pages 17-18</h3>
<p>토큰화 및 코퍼스</p>
</a>
<a class="page-link" href="10-pages-19-20.html">
<h3>Pages 19-20</h3>
<p>역번역 및 평가</p>
</a>
<a class="page-link" href="11-pages-21-22.html">
<h3>Pages 21-22</h3>
<p>MT 평가 (BLEU)</p>
</a>
<a class="page-link" href="12-pages-23-24.html">
<h3>Pages 23-24</h3>
<p>MT 평가 (계속)</p>
</a>
<a class="page-link" href="13-pages-25-26.html">
<h3>Pages 25-26</h3>
<p>편향성, 윤리 및 요약</p>
</a>
<a class="page-link" href="14-pages-27-28.html">
<h3>Pages 27-28</h3>
<p>역사적 배경</p>
</a>
<a class="page-link" href="15-pages-29-30.html">
<h3>Pages 29-30</h3>
<p>참고 문헌</p>
</a>
</div>
</section>
</main>
</body>
</html>"""

with open(os.path.join(HTML_DIR, "index.html"), "w", encoding="utf-8") as f:
    f.write(index_html)

print("saved: index.html")
print("all html rebuilt")
