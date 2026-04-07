#!/usr/bin/env python3
"""
Generate HTML view from DB-backed session view models.
Creates sessions_html/ directory with index and individual session HTMLs.
"""

from __future__ import annotations

import html
from datetime import datetime
from pathlib import Path

try:
    from scripts.db_sessions import get_session_view_model
    from scripts.db_base import connect, rows_to_dicts
except ModuleNotFoundError:
    from db_sessions import get_session_view_model
    from db_base import connect, rows_to_dicts


PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "sessions_html"

CSS = """
<style>
* { box-sizing: border-box; }
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    max-width: 980px;
    margin: 0 auto;
    padding: 20px;
    line-height: 1.6;
    color: #333;
}
h1 { border-bottom: 2px solid #333; padding-bottom: 10px; }
h2 {
    margin-top: 28px;
    padding: 8px 12px;
    background: #f5f5f5;
    border-left: 4px solid #666;
}
a { color: #0066cc; text-decoration: none; }
a:hover { text-decoration: underline; }
table { width: 100%; border-collapse: collapse; margin: 15px 0; }
th, td { border: 1px solid #ddd; padding: 10px; text-align: left; vertical-align: top; }
th { background: #f5f5f5; }
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
    white-space: pre-wrap;
    word-break: break-word;
}
.meta { color: #666; font-size: 14px; }
.back-link {
    display: inline-block;
    margin-bottom: 20px;
    padding: 8px 16px;
    background: #f5f5f5;
    border-radius: 5px;
}
.summary-box {
    background: #fffbea;
    border-left: 4px solid #f1c40f;
    padding: 15px;
    margin: 15px 0;
}
.next-box {
    background: #e8f5e9;
    border-left: 4px solid #27ae60;
    padding: 15px;
    margin: 15px 0;
}
.raw-box {
    background: #f8f9fa;
    border-left: 4px solid #95a5a6;
    padding: 15px;
    margin: 15px 0;
}
.badge {
    display: inline-block;
    font-size: 11px;
    font-weight: 600;
    padding: 2px 8px;
    border-radius: 999px;
    margin-right: 6px;
}
.list { padding-left: 20px; }
.list li { margin: 6px 0; }
.transcript-toolbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    flex-wrap: wrap;
    margin: 10px 0 12px;
}
.chip-row { display: flex; gap: 8px; flex-wrap: wrap; }
.chip-btn {
    border: 1px solid #ccd3da;
    background: #fff;
    color: #334155;
    border-radius: 999px;
    padding: 6px 12px;
    font-size: 12px;
    cursor: pointer;
}
.chip-btn.active {
    background: #1f2937;
    color: #fff;
    border-color: #1f2937;
}
.transcript-panel[hidden] { display: none; }
</style>
"""

SCRIPT = """
<script>
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("[data-transcript-root]").forEach((root) => {
    const buttons = root.querySelectorAll("[data-transcript-mode]");
    const panels = root.querySelectorAll("[data-transcript-panel]");
    buttons.forEach((button) => {
      button.addEventListener("click", () => {
        const mode = button.dataset.transcriptMode;
        buttons.forEach((item) => item.classList.toggle("active", item === button));
        panels.forEach((panel) => {
          panel.hidden = panel.dataset.transcriptPanel !== mode;
        });
      });
    });
  });
});
</script>
"""


def parse_timestamp(ts: str | None) -> tuple[datetime | None, str | None]:
    if not ts:
        return None, None
    try:
        dt = datetime.fromisoformat(ts.replace("+00:00", ""))
        return dt, dt.strftime("%Y-%m-%d")
    except Exception:
        return None, None


def format_time(ts: str | None) -> str:
    dt, _ = parse_timestamp(ts)
    return dt.strftime("%H:%M") if dt else ""


def _esc(value: str | None) -> str:
    return html.escape(value or "")


def _display_text(value: str | None, fallback: str) -> str:
    text = (value or "").strip()
    if not text:
        return fallback
    broken_markers = ("\ufffd", "?붿", "덈", "몄", "湲", "떎")
    if any(marker in text for marker in broken_markers) or text.count("?") >= 2:
        return fallback
    return text


def _render_list(items: list[str], fallback: str) -> str:
    cleaned = [item.strip() for item in items if item and item.strip()]
    if not cleaned:
        cleaned = [fallback]
    return "<ul class=\"list\">" + "".join(f"<li>{_esc(item)}</li>" for item in cleaned) + "</ul>"


def _render_dialogue(records: list[dict]) -> str:
    if not records:
        return "<p>(no dialogue records)</p>"
    parts = ["<table><thead><tr><th>Role</th><th>Time</th><th>Content</th></tr></thead><tbody>"]
    for record in records:
        parts.append(
            "<tr>"
            f"<td>{_esc((record.get('role') or 'tool').upper())}</td>"
            f"<td>{_esc(record.get('created_at') or '')}</td>"
            f"<td>{_esc(record.get('content') or '')}</td>"
            "</tr>"
        )
    parts.append("</tbody></table>")
    return "".join(parts)


def _render_transcript(content: str) -> str:
    if not content.strip():
        return "<p>(no transcript)</p>"
    return f"<pre>{_esc(content)}</pre>"


def _render_transcript_views(transcript: dict) -> str:
    if not transcript.get("available"):
        return "<p>(no transcript)</p>"

    cleaned = transcript.get("cleaned_content") or transcript.get("content") or ""
    raw = transcript.get("raw_content") or ""
    profile = transcript.get("profile") or "default"

    return (
        '<div data-transcript-root="true">'
        '<div class="transcript-toolbar">'
        '<div class="chip-row">'
        '<button type="button" class="chip-btn active" data-transcript-mode="cleaned">정리본</button>'
        '<button type="button" class="chip-btn" data-transcript-mode="raw">원문</button>'
        "</div>"
        f'<p class="meta">profile: {_esc(profile)}</p>'
        "</div>"
        f'<div class="transcript-panel" data-transcript-panel="cleaned">{_render_transcript(cleaned)}</div>'
        f'<div class="transcript-panel" data-transcript-panel="raw" hidden>{_render_transcript(raw)}</div>'
        "</div>"
    )


def render_session_html(view: dict) -> str:
    header = view.get("header", {})
    meta = view.get("meta", {})
    summary = view.get("summary", {})
    badges = view.get("badges", {})
    artifacts = view.get("artifacts", {})
    transcript = view.get("transcript", {})
    quest = view.get("quest", {})

    title = header.get("title") or "Session"
    started_at = header.get("started_at")
    ended_at = header.get("ended_at")
    date = parse_timestamp(started_at)[1] or "-"
    time = f"{format_time(started_at)} ~ {format_time(ended_at) if ended_at else 'active'}"

    # Build summary box (short supplementary layer)
    intent = _display_text(summary.get("intent"), "요약이 없습니다.")
    actions_list = summary.get("actions") or []
    decisions_list = summary.get("decisions") or []
    next_start_list = summary.get("next_start") or []
    files_touched = artifacts.get("files_touched") or []
    actions_json = artifacts.get("actions") or []

    summary_html = (
        '<div class="summary-box">'
        "<h2>Summary</h2>"
        f"<p><strong>Intent</strong>: {_esc(intent)}</p>"
    )
    if actions_list:
        summary_html += "<p><strong>Key Actions</strong>:</p>" + _render_list(actions_list, "")
    if decisions_list:
        summary_html += "<p><strong>Decisions</strong>:</p>" + _render_list(decisions_list, "")
    if files_touched:
        summary_html += "<p><strong>Files Touched</strong>:</p><ul>"
        for f in files_touched:
            summary_html += f"<li>{_esc(f)}</li>"
        summary_html += "</ul>"
    if next_start_list:
        summary_html += "<p><strong>Next Start</strong>:</p>" + _render_list(next_start_list, "")
    summary_html += "</div>"

    # Build dialogue (full conversation - main body)
    dialogue_records = view.get("dialogue") or []
    if dialogue_records:
        dialogue_parts = [
            '<div class="dialogue-section">',
            "<h2>Dialogue</h2>",
            "<p class=\"meta\">세션의 전체 대화 흐름입니다.</p>",
        ]
        for record in dialogue_records:
            role = (record.get("role") or "tool").upper()
            ts = record.get("created_at") or ""
            content = record.get("content") or ""
            dialogue_parts.append(
                f'<div class="message {record.get("role", "tool")}" style="margin:10px 0;padding:12px;border:1px solid #eee;border-radius:8px;">'
                f'<div class="meta"><strong>{_esc(role)}</strong> | {_esc(ts)}</div>'
                f'<pre style="margin:8px 0 0;white-space:pre-wrap;">{_esc(content)}</pre>'
                f"</div>"
            )
        dialogue_parts.append("</div>")
        dialogue_html = "\n".join(dialogue_parts)
    else:
        dialogue_html = '<div class="dialogue-section"><h2>Dialogue</h2><p>(대화 기록 없음)</p></div>'

    # Build transcript (full, with toggle)
    transcript_html = (
        '<div class="raw-box">'
        "<h2>Transcript</h2>"
        + _render_transcript_views(transcript)
        + "</div>"
    )

    # Build quest box
    quest_html = (
        "<h2>Quest</h2>"
        "<table><tbody>"
        f"<tr><th>Recent quest report</th><td>{_esc(quest.get('report') or '(none recorded)')}</td></tr>"
        f"<tr><th>Recent AI verdict</th><td>{_esc(quest.get('verdict') or '(none recorded)')}</td></tr>"
        "</tbody></table>"
    )

    parts = [
        "<!DOCTYPE html>",
        "<html lang=\"ko\">",
        "<head>",
        "<meta charset=\"UTF-8\">",
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">",
        f"<title>{_esc(title)}</title>",
        CSS,
        "</head>",
        "<body>",
        '<a class="back-link" href="../index.html">Index</a>',
        f"<h1>{_esc(title)}</h1>",
        "<p class=\"meta\">",
        f"Session: <code>{_esc(view.get('session_id'))}</code> | ",
        f"Date: {date} | ",
        f"Time: {time} | ",
        f"Agent: { _esc(meta.get('agent_name')) } | ",
        f"Status: { _esc(header.get('status')) }",
        "</p>",
        "<p>",
        f"<span class=\"badge\" style=\"color:{_esc(badges.get('length_color'))};\">{_esc(badges.get('length_badge'))}</span>",
        f"<span class=\"badge\" style=\"color:{_esc(badges.get('value_color'))};\">{_esc(badges.get('value_label'))}</span>",
        "</p>",
        # Summary box (supplementary)
        summary_html,
        # Dialogue (main body - full conversation)
        dialogue_html,
        # Transcript (full, with cleaned/raw toggle)
        transcript_html,
        # Quest
        quest_html,
        SCRIPT,
        "</body>",
        "</html>",
    ]
    return "\n".join(parts)


def generate_index(sessions: list[dict]) -> str:
    rows: list[str] = []
    for session in sessions:
        header = session["header"]
        meta = session["meta"]
        badges = session["badges"]
        summary = session["summary"]
        started_at = header.get("started_at")
        date = parse_timestamp(started_at)[1] or ""
        time = format_time(started_at)
        title = header.get("title") or "Untitled"
        preview = _display_text(summary.get("intent"), "?몄뀡 ?붿빟 ?놁쓬")
        rows.append(
            "<tr>"
            f"<td>{_esc(date)}</td>"
            f"<td>{_esc(time)}</td>"
            f"<td>{_esc(meta.get('agent_name'))}</td>"
            f"<td>{_esc(header.get('status'))}</td>"
            f"<td><span style=\"color:{_esc(badges.get('length_color'))};font-size:11px;\">{_esc(badges.get('length_badge'))}</span> "
            f"<span style=\"color:{_esc(badges.get('value_color'))};font-size:11px;margin-left:4px;\">{_esc(badges.get('value_label'))}</span></td>"
            f"<td><a href=\"{_esc(session['filename'])}\">{_esc(title[:50])}</a><br><span style=\"color:#777;font-size:11px;\">{_esc(preview[:80])}</span></td>"
            "</tr>"
        )

    return "\n".join(
        [
            "<!DOCTYPE html>",
            "<html lang=\"ko\">",
            "<head>",
            "<meta charset=\"UTF-8\">",
            "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">",
            "<title>Session Notes</title>",
            CSS,
            "</head>",
            "<body>",
            "<h1>Session Notes</h1>",
            f"<p class=\"meta\">Total: {len(sessions)} sessions</p>",
            "<table>",
            "<thead><tr><th>Date</th><th>Time</th><th>Agent</th><th>Status</th><th>Badges</th><th>Title / Preview</th></tr></thead>",
            "<tbody>",
            *rows,
            "</tbody>",
            "</table>",
            "</body>",
            "</html>",
        ]
    )


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with connect() as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM sessions
            ORDER BY started_at DESC
            """
        ).fetchall()
        sessions = rows_to_dicts(rows)

    index_sessions: list[dict] = []

    for session in sessions:
        view = get_session_view_model(session["id"])
        started_at = view["header"].get("started_at")
        date = parse_timestamp(started_at)[1] or "unknown"
        time = format_time(started_at).replace(":", "") or "0000"
        html_name = f"{date}_{time}_{view['session_id'][:8]}.html"

        date_dir = OUTPUT_DIR / date
        date_dir.mkdir(parents=True, exist_ok=True)
        output_path = date_dir / html_name
        output_path.write_text(render_session_html(view), encoding="utf-8")
        print(f"  Created: {date}/{html_name}")

        index_sessions.append(
            {
                **view,
                "filename": f"{date}/{html_name}",
            }
        )

    (OUTPUT_DIR / "index.html").write_text(generate_index(index_sessions), encoding="utf-8")
    print(f"\nGenerated {len(index_sessions)} session HTMLs + index.html")
    print(f"Output: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()

