#!/usr/bin/env python3
"""
Generate HTML view from session Markdown notes.
Creates sessions_html/ directory with index and individual session HTMLs.
"""

import re
import os
from pathlib import Path
from datetime import datetime

SESSIONS_DIR = Path("G:/Ddrive/BatangD/task/workdiary/0-a-control/sessions")
OUTPUT_DIR = Path("G:/Ddrive/BatangD/task/workdiary/0-a-control/sessions_html")

CSS = """
<style>
* { box-sizing: border-box; }
body { 
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    max-width: 900px; 
    margin: 0 auto; 
    padding: 20px; 
    line-height: 1.6;
    color: #333;
}
h1 { border-bottom: 2px solid #333; padding-bottom: 10px; }
h2 { 
    margin-top: 30px; 
    padding: 8px 12px; 
    background: #f5f5f5; 
    border-left: 4px solid #666;
}
h3 { color: #555; margin-top: 20px; }
a { color: #0066cc; text-decoration: none; }
a:hover { text-decoration: underline; }
table { width: 100%; border-collapse: collapse; margin: 15px 0; }
th, td { border: 1px solid #ddd; padding: 10px; text-align: left; }
th { background: #f5f5f5; }
tr:hover { background: #fafafa; }
code { 
    background: #f4f4f4; 
    padding: 2px 6px; 
    border-radius: 3px; 
    font-family: 'Consolas', 'Monaco', monospace;
}
pre { 
    background: #f4f4f4; 
    padding: 15px; 
    overflow-x: auto; 
    border-radius: 5px;
}
.back-link { 
    display: inline-block; 
    margin-bottom: 20px; 
    padding: 8px 16px;
    background: #f5f5f5;
    border-radius: 5px;
}
.meta { 
    color: #666; 
    font-size: 14px; 
}
.status-active { color: #e67e22; font-weight: bold; }
.status-closed { color: #27ae60; font-weight: bold; }
.intent-box {
    background: #fffbea;
    border-left: 4px solid #f1c40f;
    padding: 15px;
    margin: 15px 0;
}
.actions-list { padding-left: 20px; }
.actions-list li { margin: 5px 0; }
.next-box {
    background: #e8f5e9;
    border-left: 4px solid #27ae60;
    padding: 15px;
    margin: 15px 0;
}
.raw-refs {
    background: #f8f9fa;
    padding: 10px;
    font-size: 13px;
    color: #666;
}
.nav { margin-bottom: 20px; }
.nav a { margin-right: 15px; }
</style>
"""

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    {css}
</head>
<body>
    <div class="nav">
        <a href="../index.html">← Index</a>
    </div>
    {content}
</body>
</html>
"""

INDEX_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Session Notes</title>
    {css}
</head>
<body>
    <h1>Session Notes</h1>
    <p class="meta">Total: {count} sessions | <span style="color:#27ae60;">결정</span> <span style="color:#3498db;">다음</span> <span style="color:#9b59b6;">행동</span> <span style="color:#f39c12;">트랜스크립트</span> <span style="color:#e74c3c;">비어있음</span></p>
    <table>
        <thead>
            <tr>
                <th>Date</th>
                <th>Time</th>
                <th>Agent</th>
                <th>Status</th>
                <th>Badges</th>
                <th>Title / Preview</th>
            </tr>
        </thead>
        <tbody>
            {rows}
        </tbody>
    </table>
</body>
</html>
"""


def parse_session_markdown(content, filepath):
    """Parse session markdown and extract sections."""
    lines = content.split("\n")
    
    metadata = {}
    sections = {}
    current_section = None
    current_content = []
    
    in_metadata = False
    in_section = False
    
    for line in lines:
        line = line.rstrip()
        
        # Metadata section
        if line.startswith("## Metadata"):
            in_metadata = True
            in_section = False
            continue
        elif in_metadata and line.startswith("## "):
            in_metadata = False
            current_section = line.replace("## ", "").strip()
            current_content = []
            in_section = True
            continue
        elif in_metadata and line.startswith("- **"):
            # Parse metadata line like "- **Key**: value"
            match = re.match(r"- \*\*(\w+)\*\*: (.+)", line)
            if match:
                metadata[match.group(1)] = match.group(2).strip()
            continue
        
        # Content sections
        if line.startswith("## "):
            if current_section and current_content:
                sections[current_section] = "\n".join(current_content).strip()
            current_section = line.replace("## ", "").strip()
            current_content = []
            in_section = True
            continue
        elif in_section and line:
            current_content.append(line)
        elif in_section and not line:
            current_content.append(line)
    
    # Save last section
    if current_section and current_content:
        sections[current_section] = "\n".join(current_content).strip()
    
    return metadata, sections


def format_markdown_simple(text):
    """Simple markdown to HTML converter for session notes."""
    if not text:
        return ""
    
    html = text
    
    # Escape HTML
    html = html.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    
    # Code blocks
    html = re.sub(r'```(\w*)\n(.*?)```', r'<pre><code>\2</code></pre>', html, flags=re.DOTALL)
    
    # Inline code
    html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)
    
    # Bold
    html = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', html)
    
    # Italic
    html = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', html)
    
    # Links
    html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html)
    
    # Unordered lists
    html = re.sub(r'^- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
    html = re.sub(r'(<li>.*</li>)', r'<ul>\1</ul>', html)
    
    # Horizontal rule
    html = re.sub(r'^---$', '<hr>', html, flags=re.MULTILINE)
    
    # Tables (simple)
    lines = html.split("\n")
    new_lines = []
    in_table = False
    for l in lines:
        if "|" in l and l.strip().startswith("|"):
            if not in_table:
                in_table = True
                new_lines.append("<table>")
            cells = [c.strip() for c in l.split("|") if c.strip()]
            if all(c.replace("-", "").replace(":", "") == "" for c in cells):
                # Skip separator row
                continue
            tag = "td"
            if "---" in l:
                continue
            new_lines.append("<tr>" + "".join(f"<{tag}>{c}</{tag}>" for c in cells) + "</tr>")
        else:
            if in_table:
                new_lines.append("</table>")
                in_table = False
            new_lines.append(l)
    if in_table:
        new_lines.append("</table>")
    html = "\n".join(new_lines)
    
    # Paragraphs
    html = re.sub(r'\n\n+', '</p><p>', html)
    html = '<p>' + html + '</p>'
    html = html.replace('<p></p>', '')
    html = re.sub(r'<p>(<h[123]>.*?</h[123]>)</p>', r'\1', html)
    html = re.sub(r'<p>(<ul>.*?</ul>)</p>', r'\1', html)
    html = re.sub(r'<p>(<table>.*?</table>)</p>', r'\1', html)
    html = re.sub(r'<p>(<pre>.*?</pre>)</p>', r'\1', html)
    html = re.sub(r'<p>(<hr>)</p>', r'\1', html)
    
    return html


def generate_session_html(filepath, relative_path):
    """Generate HTML for a single session note."""
    content = filepath.read_text(encoding="utf-8")
    metadata, sections = parse_session_markdown(content, filepath)
    
    # Build HTML
    html_parts = []
    
    # Header
    title = metadata.get("Title", "Session Note")
    session_id = metadata.get("Session ID", "")
    date = metadata.get("Date", "")
    time = metadata.get("Time", "")
    agent = metadata.get("Agent", "")
    status = metadata.get("Status", "")
    
    html_parts.append(f'<h1>{title}</h1>')
    html_parts.append(f'<p class="meta">')
    html_parts.append(f'Session: {session_id} | ')
    html_parts.append(f'Date: {date} | ')
    html_parts.append(f'Time: {time} | ')
    html_parts.append(f'Agent: {agent} | ')
    status_class = f'status-{status}' if status else ''
    html_parts.append(f'Status: <span class="{status_class}">{status}</span>')
    html_parts.append('</p>')
    
    # Intent section
    if "Intent" in sections:
        intent = sections["Intent"]
        html_parts.append('<div class="intent-box">')
        html_parts.append('<h2>Intent</h2>')
        html_parts.append(format_markdown_simple(intent))
        html_parts.append('</div>')
    
    # Actions section
    if "Actions" in sections:
        actions = sections["Actions"]
        html_parts.append('<h2>Actions</h2>')
        html_parts.append(format_markdown_simple(actions))
    
    # Decisions section
    if "Decisions" in sections:
        decisions = sections["Decisions"]
        html_parts.append('<h2>Decisions</h2>')
        html_parts.append(format_markdown_simple(decisions))
    
    # Artifacts section
    if "Artifacts" in sections:
        artifacts = sections["Artifacts"]
        html_parts.append('<h2>Artifacts</h2>')
        html_parts.append(format_markdown_simple(artifacts))
    
    # Next Start section
    if "Next Start" in sections:
        next_start = sections["Next Start"]
        html_parts.append('<div class="next-box">')
        html_parts.append('<h2>Next Start</h2>')
        html_parts.append(format_markdown_simple(next_start))
        html_parts.append('</div>')
    
    # Raw Refs section
    if "Raw Refs" in sections:
        raw_refs = sections["Raw Refs"]
        html_parts.append('<div class="raw-refs">')
        html_parts.append('<h2>Raw Refs</h2>')
        html_parts.append(format_markdown_simple(raw_refs))
        html_parts.append('</div>')
    
    content_html = "\n".join(html_parts)
    
    return HTML_TEMPLATE.format(
        title=f"Session: {date} {time}",
        css=CSS,
        content=content_html
    )


def analyze_session(sections, full_content):
    """
    Analyze session for badges and preview.
    Returns: length_badge, value_badge, preview
    """
    # Calculate content length (excluding metadata)
    content_length = len(full_content)
    
    # Determine length badge
    if content_length < 1500:
        length_badge = "short"
    elif content_length < 2500:
        length_badge = "medium"
    else:
        length_badge = "long"
    
    # Check for value indicators
    has_actions = False
    has_decisions = False
    has_next = False
    has_transcript = False
    
    # Check Actions section
    actions = sections.get("Actions", "")
    if actions and "(no specific actions recorded)" not in actions:
        has_actions = True
    
    # Check Decisions section
    decisions = sections.get("Decisions", "")
    if decisions and "(none recorded)" not in decisions:
        has_decisions = True
    
    # Check Next Start section
    next_start = sections.get("Next Start", "")
    if next_start and "Check current-state" not in next_start:
        has_next = True
    
    # Check Raw Refs for transcript
    raw_refs = sections.get("Raw Refs", "")
    if raw_refs and "Transcript:" in raw_refs and "(no transcript)" not in raw_refs:
        has_transcript = True
    
    # Determine value badge
    if has_decisions:
        value_badge = "decisions"
    elif has_next:
        value_badge = "next-action"
    elif has_actions:
        value_badge = "actions"
    elif has_transcript:
        value_badge = "transcript-only"
    else:
        value_badge = "empty"
    
    # Generate preview (first meaningful line from Intent)
    intent = sections.get("Intent", "")
    preview_lines = []
    if intent:
        # Get first non-empty line from Intent
        for line in intent.split("\n"):
            line = line.strip()
            if line and not line.startswith(">"):
                preview_lines.append(line[:80])
                break
    
    # Add Actions line if exists and Intent was empty
    if not preview_lines and actions and "(no specific" not in actions:
        for line in actions.split("\n"):
            line = line.strip()
            if line and line.startswith("-"):
                preview_lines.append(line[:80])
                break
    
    # Add Decisions line if still empty
    if not preview_lines and decisions and "(none" not in decisions:
        for line in decisions.split("\n"):
            line = line.strip()
            if line and "|" not in line:
                preview_lines.append(line[:80])
                break
    
    preview = preview_lines[0] if preview_lines else "(no preview)"
    
    return {
        "length_badge": length_badge,
        "value_badge": value_badge,
        "preview": preview
    }


def generate_index(sessions):
    """Generate index.html with session list."""
    rows = []
    for s in sessions:
        date = s.get("date", "")
        time = s.get("time", "")
        agent = s.get("agent", "")
        status = s.get("status", "")
        title = s.get("title", "")
        filename = s.get("filename", "")
        length_badge = s.get("length_badge", "short")
        value_badge = s.get("value_badge", "empty")
        preview = s.get("preview", "")[:60]
        
        status_class = f'status-{status}' if status else ''
        
        # Badge styles
        length_color = {"short": "#999", "medium": "#f39c12", "long": "#27ae60"}.get(length_badge, "#999")
        value_label = {"decisions": "결정", "next-action": "다음", "actions": "행동", "transcript-only": "트랜스크립트", "empty": "비어있음"}.get(value_badge, value_badge)
        value_color = {"decisions": "#27ae60", "next-action": "#3498db", "actions": "#9b59b6", "transcript-only": "#f39c12", "empty": "#e74c3c"}.get(value_badge, "#999")
        
        preview_escaped = preview.replace("|", " ").replace("<", "&lt;").replace(">", "&gt;")
        
        rows.append(f"""<tr>
            <td>{date}</td>
            <td>{time}</td>
            <td>{agent}</td>
            <td class="{status_class}">{status}</td>
            <td><span style="color:{length_color};font-size:11px;">{length_badge}</span> <span style="color:{value_color};font-size:11px;margin-left:4px;">{value_label}</span></td>
            <td><a href="{filename}">{title[:50]}{'...' if len(title) > 50 else ''}</a><br><span style="color:#777;font-size:11px;">{preview_escaped}</span></td>
        </tr>""")
    
    return INDEX_TEMPLATE.format(
        css=CSS,
        count=len(sessions),
        rows="\n".join(rows)
    )


def main():
    """Main function to generate HTML from session notes."""
    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    sessions = []
    
    # Find all session markdown files
    for md_file in sorted(SESSIONS_DIR.glob("**/*.md"), reverse=True):
        # Skip TEMPLATE.md and README.md
        if md_file.name in ["TEMPLATE.md", "README.md", "INDEX.md"]:
            continue
        
        # Parse filename: YYYY-MM-DD_HHMM_<id>.md
        filename = md_file.name
        parts = filename.replace(".md", "").split("_")
        if len(parts) < 3:
            continue
        
        date = parts[0]
        time = parts[1]
        
        # Read metadata and sections
        content = md_file.read_text(encoding="utf-8")
        metadata, sections = parse_session_markdown(content, md_file)
        
        session_id = metadata.get("Session ID", "")
        agent = metadata.get("Agent", "")
        status = metadata.get("Status", "")
        title = metadata.get("Title", "Untitled")
        
        # Analyze session for badges and preview
        analysis = analyze_session(sections, content)
        
        # Generate HTML for this session
        relative_path = md_file.relative_to(SESSIONS_DIR)
        html_filename = filename.replace(".md", ".html")
        
        # Create date folder in output
        date_dir = OUTPUT_DIR / date
        date_dir.mkdir(parents=True, exist_ok=True)
        
        html_path = date_dir / html_filename
        html_content = generate_session_html(md_file, relative_path)
        html_path.write_text(html_content, encoding="utf-8")
        
        print(f"  Created: {date}/{html_filename}")
        
        sessions.append({
            "date": date,
            "time": time,
            "agent": agent,
            "status": status,
            "title": title,
            "filename": f"{date}/{html_filename}",
            "session_id": session_id,
            "length_badge": analysis["length_badge"],
            "value_badge": analysis["value_badge"],
            "preview": analysis["preview"]
        })
    
    # Generate index
    sessions.sort(key=lambda x: (x["date"], x["time"]), reverse=True)
    index_html = generate_index(sessions)
    (OUTPUT_DIR / "index.html").write_text(index_html, encoding="utf-8")
    
    print(f"\nGenerated {len(sessions)} session HTMLs + index.html")
    print(f"Output: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
