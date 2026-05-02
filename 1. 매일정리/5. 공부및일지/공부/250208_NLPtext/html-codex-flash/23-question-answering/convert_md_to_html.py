import os
import re

source_dir = r"G:\Ddrive\BatangD\task\workdiary\1. 매일정리\5. 공부및일지\공부\250208_NLPtext\html-codex-flash\23-question-answering\pages"
output_dir = r"G:\Ddrive\BatangD\task\workdiary\1. 매일정리\5. 공부및일지\공부\250208_NLPtext\html-codex-flash\23-question-answering\html"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

template_head = """<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} | Question Answering</title>
<style>
:root {{ --bg: #f6f1e8; --paper: #fffdf8; --ink: #1f1b16; --muted: #6f675d; --line: #ddd2c2; --accent: #8c5a2b; --accent-soft: #f1e2cf; --note-bg: #faf4ea; --source-bg: #f5f3ef; --translation-bg: #fff8ea; --shadow: 0 10px 30px rgba(53, 40, 24, 0.08); --radius: 18px; }}
* {{ box-sizing: border-box; }}
html {{ scroll-behavior: smooth; }}
body {{ margin: 0; background: radial-gradient(circle at top left, rgba(140, 90, 43, 0.1), transparent 28%), linear-gradient(180deg, #f9f4ec 0%, var(--bg) 100%); color: var(--ink); font: 16px/1.7 "Noto Sans KR", "Apple SD Gothic Neo", "Malgun Gothic", sans-serif; }}
.shell {{ width: min(1100px, calc(100% - 32px)); margin: 0 auto; padding: 24px 0 64px; }}
.topbar {{ position: sticky; top: 0; z-index: 10; backdrop-filter: blur(10px); background: rgba(246, 241, 232, 0.88); border-bottom: 1px solid rgba(221, 210, 194, 0.85); margin-bottom: 24px; }}
.topbar-inner {{ width: min(1100px, calc(100% - 32px)); margin: 0 auto; padding: 14px 0; display: flex; gap: 16px; align-items: center; justify-content: space-between; flex-wrap: wrap; }}
.doc-meta {{ display: flex; flex-direction: column; gap: 2px; }}
.eyebrow {{ color: var(--muted); font-size: 13px; letter-spacing: 0.06em; text-transform: uppercase; }}
h1 {{ margin: 0; font-size: clamp(22px, 4vw, 34px); line-height: 1.15; font-weight: 800; }}
.quick-nav, .actions {{ display: flex; gap: 8px; flex-wrap: wrap; }}
.chip, .action-btn {{ border: 1px solid var(--line); background: rgba(255, 253, 248, 0.92); color: var(--ink); border-radius: 999px; padding: 8px 14px; font: inherit; font-size: 14px; cursor: pointer; text-decoration: none; transition: transform 0.15s ease, background 0.15s ease; }}
.chip:hover, .action-btn:hover {{ transform: translateY(-1px); background: #fff; }}
.hero {{ background: var(--paper); border: 1px solid var(--line); border-radius: calc(var(--radius) + 4px); box-shadow: var(--shadow); padding: 28px; margin-bottom: 24px; }}
.hero p {{ margin: 10px 0 0; color: var(--muted); }}
.hero-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin-top: 18px; }}
.meta-card {{ padding: 14px 16px; border-radius: 14px; background: #fcf7f0; border: 1px solid var(--line); }}
.meta-card dt {{ font-size: 12px; color: var(--muted); margin-bottom: 6px; }}
.meta-card dd {{ margin: 0; font-weight: 700; }}
.page {{ margin-bottom: 28px; background: var(--paper); border: 1px solid var(--line); border-radius: calc(var(--radius) + 2px); box-shadow: var(--shadow); overflow: hidden; }}
.page-header {{ padding: 20px 24px; background: linear-gradient(135deg, #fff8eb, #f5ead8); border-bottom: 1px solid var(--line); }}
.page-header h2 {{ margin: 0; font-size: 28px; line-height: 1.15; }}
.page-subtitle {{ margin-top: 6px; color: var(--muted); font-size: 14px; }}
.blocks {{ padding: 18px; display: grid; gap: 16px; }}
.block {{ border: 1px solid var(--line); border-radius: var(--radius); overflow: hidden; background: #fffdfa; }}
.block-head {{ padding: 14px 16px; border-bottom: 1px solid var(--line); display: flex; justify-content: space-between; gap: 10px; align-items: center; flex-wrap: wrap; }}
.block-title {{ font-weight: 800; }}
.block-type {{ color: var(--accent); background: var(--accent-soft); border-radius: 999px; padding: 4px 10px; font-size: 13px; font-weight: 700; }}
.block-body {{ padding: 16px; display: grid; gap: 14px; }}
.label {{ display: inline-block; font-size: 12px; font-weight: 800; letter-spacing: 0.04em; color: var(--muted); text-transform: uppercase; margin-bottom: 8px; }}
.source, .translation, .note-panel {{ border-radius: 14px; padding: 14px 16px; border: 1px solid var(--line); }}
.source {{ background: var(--source-bg); }}
.translation {{ background: var(--translation-bg); }}
.note-panel {{ background: var(--note-bg); }}
.source pre, .translation pre, .note-panel pre {{ margin: 0; white-space: pre-wrap; word-break: break-word; font: inherit; }}
.mono pre {{ font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace; font-size: 14px; line-height: 1.6; }}
.note-toggle {{ align-self: start; border: 1px solid var(--line); background: #fff; border-radius: 999px; padding: 8px 12px; font: inherit; font-size: 14px; cursor: pointer; }}
.note-panel[hidden] {{ display: none; }}
@media (max-width: 720px) {{ .shell {{ width: min(100% - 20px, 100%); }} .topbar-inner {{ width: min(100% - 20px, 100%); }} .hero, .page-header, .blocks, .block-head, .block-body {{ padding-left: 14px; padding-right: 14px; }} }}
</style>
</head>
<body>
<div class="topbar">
<div class="topbar-inner">
<div class="doc-meta">
<div class="eyebrow">23 Question Answering</div>
<h1>Question Answering</h1>
</div>
<div class="quick-nav">
{quick_nav}
</div>
<div class="actions">
<button class="action-btn" type="button" data-expand-all>모든 주석 펼치기</button>
<button class="action-btn" type="button" data-collapse-all>모든 주석 접기</button>
</div>
</div>
</div>

<main class="shell">
<section class="hero">
<div class="eyebrow">Study Edition</div>
<h2>{title} Annotated Page</h2>
<p>본문은 바로 읽고, `study_note`만 접어서 여는 형태로 구성했습니다.</p>
<div class="hero-grid">
<dl class="meta-card">
<dt>Source</dt>
<dd>23. Question Answering.pdf</dd>
</dl>
<dl class="meta-card">
<dt>Workflow</dt>
<dd>html-codex-flash</dd>
</dl>
<dl class="meta-card">
<dt>Status</dt>
<dd>Accepted</dd>
</dl>
</div>
</section>
"""

template_foot = """
</main>

<script>
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
});
</script>
</body>
</html>
"""

def parse_md(content):
    pages = []
    current_page = None
    
    # Split by Page headers
    page_splits = re.split(r'^# Page (\d+)', content, flags=re.MULTILINE)
    
    for i in range(1, len(page_splits), 2):
        page_num = page_splits[i]
        page_content = page_splits[i+1]
        
        # Split by Block headers
        block_splits = re.split(r'^## Block (\d+)', page_content, flags=re.MULTILINE)
        blocks = []
        for j in range(1, len(block_splits), 2):
            block_num = block_splits[j]
            block_body = block_splits[j+1]
            
            # Parse fields
            fields = {}
            current_field = None
            lines = block_body.split('\n')
            for line in lines:
                original_line = line
                stripped_line = line.strip()
                if not stripped_line: continue
                
                # Check if it's a new field: starts with "- field_name:"
                match = re.match(r'^- (\w+):\s*(.*)', stripped_line)
                if match:
                    current_field = match.group(1)
                    fields[current_field] = match.group(2).strip()
                elif current_field:
                    # If it's not a new field, it's a continuation of the current field
                    # We preserve the indentation relative to the field start if possible, 
                    # but simple strip and append is usually enough for this structure.
                    if fields[current_field]:
                        fields[current_field] += '\n' + stripped_line
                    else:
                        fields[current_field] = stripped_line
            
            blocks.append({
                'id': block_num,
                'type': fields.get('type', 'other').strip(),
                'source_text': fields.get('source_text', '').strip(),
                'korean_translation': fields.get('korean_translation', '').strip(),
                'study_note': fields.get('study_note', '').strip()
            })
        
        # Determine page subtitle from the first section_title block if exists
        subtitle = ""
        for b in blocks:
            if b['type'] in ['chapter_title', 'section_title', 'subsection_title']:
                lines = [l.strip() for l in b['korean_translation'].split('\n') if l.strip()]
                if lines:
                    subtitle = " ".join(lines)
                break
        
        pages.append({
            'num': page_num,
            'subtitle': subtitle,
            'blocks': blocks
        })
    return pages

md_files = sorted([f for f in os.listdir(source_dir) if f.endswith('.md')])

for filename in md_files:
    with open(os.path.join(source_dir, filename), 'r', encoding='utf-8') as f:
        content = f.read()
    
    pages = parse_md(content)
    
    title_match = re.match(r'^\d+-pages-(.*)\.md', filename)
    title_suffix = title_match.group(1) if title_match else filename
    title = f"Pages {title_suffix.replace('-', ' ')}"
    
    quick_nav = "".join([f'<a class="chip" href="#page-{p["num"]}">Page {p["num"]}</a>' for p in pages])
    
    html_content = template_head.format(title=title, quick_nav=quick_nav)
    
    for p in pages:
        html_content += f"""
<section class="page" id="page-{p['num']}">
<header class="page-header">
<h2>Page {p['num']}</h2>
<div class="page-subtitle">{p['subtitle']}</div>
</header>
<div class="blocks">
"""
        for b in p['blocks']:
            mono_class = " mono" if b['type'] in ['code', 'formula', 'table'] else ""
            html_content += f"""
<article class="block">
<div class="block-head">
<div class="block-title">Block {b['id']}</div>
<div class="block-type">{b['type']}</div>
</div>
<div class="block-body">
<section class="source{mono_class}"><div class="label">Source Text</div><pre>{b['source_text']}</pre></section>
<section class="translation"><div class="label">Korean Translation</div><pre>{b['korean_translation']}</pre></section>
<button class="note-toggle" type="button" aria-expanded="false">study_note 보기</button>
<section class="note-panel" hidden><div class="label">Study Note</div><pre>{b['study_note']}</pre></section>
</div>
</article>
"""
        html_content += "</div></section>"
    
    html_content += template_foot
    
    output_filename = filename.replace('.md', '.html')
    with open(os.path.join(output_dir, output_filename), 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"- saved: {output_filename}")

# Generate index.html
index_html = """<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Index | Question Answering</title>
<style>
body { font-family: sans-serif; background: #f6f1e8; padding: 40px; }
.container { max-width: 800px; margin: 0 auto; background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
h1 { color: #8c5a2b; }
ul { list-style: none; padding: 0; }
li { margin: 10px 0; }
a { text-decoration: none; color: #1f1b16; font-size: 18px; }
a:hover { color: #8c5a2b; text-decoration: underline; }
</style>
</head>
<body>
<div class="container">
<h1>Chapter 23: Question Answering</h1>
<ul>
"""
for filename in md_files:
    html_filename = filename.replace('.md', '.html')
    title_match = re.match(r'^\d+-pages-(.*)\.md', filename)
    title_suffix = title_match.group(1) if title_match else filename
    display_title = f"Pages {title_suffix.replace('-', ' ')}"
    index_html += f'<li><a href="{html_filename}">{display_title}</a></li>\n'

index_html += """
</ul>
</div>
</body>
</html>
"""
with open(os.path.join(output_dir, "index.html"), 'w', encoding='utf-8') as f:
    f.write(index_html)
print("- saved: index.html")
print("- all html saved")
