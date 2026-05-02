import re, os, html as htmlmod

base = r'G:\Ddrive\BatangD\task\workdiary\1. 매일정리\5. 공부및일지\공부\250208_NLPtext\html-codex-flash\11-machine-translation-and-encoder-decoder-models'

files = [
    ('pages/02-pages-03-04.md', 'html/02-pages-03-04.html', '03-04'),
    ('pages/03-pages-05-06.md', 'html/03-pages-05-06.html', '05-06'),
    ('pages/04-pages-07-08.md', 'html/04-pages-07-08.html', '07-08'),
    ('pages/05-pages-09-10.md', 'html/05-pages-09-10.html', '09-10'),
    ('pages/06-pages-11-12.md', 'html/06-pages-11-12.html', '11-12'),
    ('pages/07-pages-13-14.md', 'html/07-pages-13-14.html', '13-14'),
    ('pages/08-pages-15-16.md', 'html/08-pages-15-16.html', '15-16'),
]

def parse_md(content):
    pages = {}
    current_page = None
    current_block = None
    current_field = None
    field_content = {}

    for line in content.split('\n'):
        m = re.match(r'^# Page (\d+)', line)
        if m:
            if current_page is not None and current_block is not None:
                if current_field and field_content.get(current_field):
                    current_block[current_field] = field_content[current_field].rstrip('\n')
                pages[current_page].append(current_block)
            current_page = int(m.group(1))
            if current_page not in pages:
                pages[current_page] = []
            current_block = None
            current_field = None
            field_content = {}
            continue

        m = re.match(r'^## Block (\d+)', line)
        if m:
            if current_block is not None:
                if current_field and field_content.get(current_field):
                    current_block[current_field] = field_content[current_field].rstrip('\n')
                pages[current_page].append(current_block)
            current_block = {'num': int(m.group(1))}
            current_field = None
            field_content = {}
            continue

        m = re.match(r'^- (type|source_text|korean_translation|study_note): (.*)', line)
        if m:
            if current_field and field_content.get(current_field):
                current_block[current_field] = field_content[current_field].rstrip('\n')
            current_field = m.group(1)
            field_content[current_field] = m.group(2) + '\n'
            continue

        if current_field and current_block is not None:
            if line.startswith('  ') or line.startswith('\t'):
                field_content[current_field] += line + '\n'
            elif line.strip() == '':
                if current_field in ('source_text', 'korean_translation', 'study_note'):
                    field_content[current_field] += '\n'

    if current_block is not None:
        if current_field and field_content.get(current_field):
            current_block[current_field] = field_content[current_field].rstrip('\n')
        pages[current_page].append(current_block)

    return pages


CSS = r''':root { --bg: #f6f1e8; --paper: #fffdf8; --ink: #1f1b16; --muted: #6f675d; --line: #ddd2c2; --accent: #8c5a2b; --accent-soft: #f1e2cf; --note-bg: #faf4ea; --source-bg: #f5f3ef; --translation-bg: #fff8ea; --shadow: 0 10px 30px rgba(53, 40, 24, 0.08); --radius: 18px; }
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
@media (max-width: 720px) { .shell { width: min(100% - 20px, 100%); } .topbar-inner { width: min(100% - 20px, 100%); } .hero, .page-header, .blocks, .block-head, .block-body { padding-left: 14px; padding-right: 14px; } }'''

JS = r'''const toggles = Array.from(document.querySelectorAll(".note-toggle"));
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
});'''

for md_path, html_path, page_range in files:
    md_full = os.path.join(base, md_path)
    with open(md_full, 'r', encoding='utf-8') as f:
        content = f.read()

    pages = parse_md(content)
    page_nums = sorted(pages.keys())

    quick_nav = ''
    for pn in page_nums:
        quick_nav += '<a class="chip" href="#page-{}">Page {}</a>\n'.format(pn, pn)

    page_sections = ''
    for pn in page_nums:
        blocks = pages[pn]
        subtitle = 'Page {}'.format(pn)
        for b in blocks:
            if b.get('type') == 'section_title':
                subtitle = b.get('korean_translation', b.get('source_text', 'Page {}'.format(pn)))
                break
            elif b.get('type') in ('paragraph', 'other') and b.get('korean_translation'):
                kt = b['korean_translation']
                if len(kt) > 100:
                    subtitle = kt[:80] + '...'
                else:
                    subtitle = kt
                break

        blocks_html = ''
        for b in blocks:
            btype = b.get('type', 'other')
            mono_class = ' class="mono"' if btype in ('formula', 'structural_formula', 'code') else ''

            src = htmlmod.escape(b.get('source_text', ''))
            kt = htmlmod.escape(b.get('korean_translation', ''))
            sn = htmlmod.escape(b.get('study_note', ''))

            blocks_html += '<article class="block">\n'
            blocks_html += '<div class="block-head">\n'
            blocks_html += '<div class="block-title">Block {}</div>\n'.format(b['num'])
            blocks_html += '<div class="block-type">{}</div>\n'.format(btype)
            blocks_html += '</div>\n'
            blocks_html += '<div class="block-body">\n'
            blocks_html += '<section class="source"{}><div class="label">Source Text</div><pre>{}</pre></section>\n'.format(mono_class, src)
            blocks_html += '<section class="translation"><div class="label">Korean Translation</div><pre>{}</pre></section>\n'.format(kt)
            blocks_html += '<button class="note-toggle" type="button" aria-expanded="false">study_note 보기</button>\n'
            blocks_html += '<section class="note-panel" hidden><div class="label">Study Note</div><pre>{}</pre></section>\n'.format(sn)
            blocks_html += '</div>\n'
            blocks_html += '</article>\n'

        page_sections += '<section class="page" id="page-{}">\n'.format(pn)
        page_sections += '<header class="page-header">\n'
        page_sections += '<h2>Page {}</h2>\n'.format(pn)
        page_sections += '<div class="page-subtitle">{}</div>\n'.format(subtitle)
        page_sections += '</header>\n'
        page_sections += '<div class="blocks">\n'
        page_sections += blocks_html
        page_sections += '</div>\n'
        page_sections += '</section>\n'

    full_html = '<!doctype html>\n<html lang="ko">\n<head>\n'
    full_html += '<meta charset="utf-8">\n'
    full_html += '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
    full_html += '<title>Pages {} | Machine Translation and Encoder-Decoder Models</title>\n'.format(page_range)
    full_html += '<style>\n' + CSS + '\n</style>\n'
    full_html += '</head>\n<body>\n'
    full_html += '<div class="topbar">\n<div class="topbar-inner">\n'
    full_html += '<div class="doc-meta">\n'
    full_html += '<div class="eyebrow">11 Machine Translation and Encoder-Decoder Models</div>\n'
    full_html += '<h1>Machine Translation and Encoder-Decoder Models</h1>\n'
    full_html += '</div>\n'
    full_html += '<div class="quick-nav">\n' + quick_nav + '</div>\n'
    full_html += '<div class="actions">\n'
    full_html += '<button class="action-btn" type="button" data-expand-all>모든 주석 펼치기</button>\n'
    full_html += '<button class="action-btn" type="button" data-collapse-all>모든 주석 접기</button>\n'
    full_html += '</div>\n'
    full_html += '</div>\n</div>\n\n'
    full_html += '<main class="shell">\n'
    full_html += '<section class="hero">\n'
    full_html += '<div class="eyebrow">Study Edition</div>\n'
    full_html += '<h2>Pages {} Annotated Page</h2>\n'.format(page_range)
    full_html += '<p>본문은 바로 읽고, `study_note`만 접어서 여는 형태로 구성했습니다.</p>\n'
    full_html += '<div class="hero-grid">\n'
    full_html += '<dl class="meta-card"><dt>Source</dt><dd>11. Machine Translation and Encoder-Decoder Models.pdf</dd></dl>\n'
    full_html += '<dl class="meta-card"><dt>Workflow</dt><dd>html-codex-flash</dd></dl>\n'
    full_html += '<dl class="meta-card"><dt>Status</dt><dd>Accepted</dd></dl>\n'
    full_html += '</div>\n</section>\n\n'
    full_html += page_sections
    full_html += '</main>\n\n'
    full_html += '<script>\n' + JS + '\n</script>\n'
    full_html += '</body>\n</html>'

    out_path = os.path.join(base, html_path)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(full_html)

    total_blocks = sum(len(v) for v in pages.values())
    print('{}: {} pages, {} blocks'.format(html_path, len(page_nums), total_blocks))

print('Done!')
