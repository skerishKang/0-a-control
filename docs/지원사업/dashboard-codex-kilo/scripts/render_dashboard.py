#!/usr/bin/env python3
import json
import sqlite3
from pathlib import Path
from datetime import datetime

ROOT_DIR = Path(__file__).parent.parent
DATA_DIR = ROOT_DIR / "data"
OUTPUT_DIR = ROOT_DIR / "output" / "site"
NOTICES_DIR = DATA_DIR / "notices"
DB_PATH = DATA_DIR / "db" / "notices.sqlite3"


def get_connection():
    return sqlite3.connect(DB_PATH)


def escape_html(text: str) -> str:
    if not text:
        return ""
    return (text
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;"))


def fetch_notices():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            id, source_site, source_url, source_notice_id, title, category,
            posted_at, apply_start, apply_end, ministry, agency,
            apply_method, apply_site_url, source_origin_url, contact,
            summary_text, storage_path, status, manual_note, one_line_summary,
            created_at, updated_at
        FROM notices
        ORDER BY 
            CASE WHEN status IN ('submitted', 'pass') THEN 1 ELSE 0 END,
            apply_end ASC, posted_at DESC
    """)

    columns = [desc[0] for desc in cursor.description]
    notices = []
    for row in cursor.fetchall():
        notices.append(dict(zip(columns, row)))

    for notice in notices:
        cursor.execute("""
            SELECT name, view_url, download_url, section_name
            FROM attachments
            WHERE notice_id = ?
            ORDER BY sort_order
        """, (notice['id'],))
        att_columns = ['name', 'view_url', 'download_url', 'section_name']
        notice['attachments'] = [dict(zip(att_columns, row)) for row in cursor.fetchall()]

    conn.close()
    return notices


STATUS_LABELS = {
    'new': '신규',
    'reviewing': '검토중',
    'writing': '작성중',
    'submitted': '제출완료',
    'pass': '합격',
    'hold': '보류'
}

STATUS_COLORS = {
    'new': '#6c757d',
    'reviewing': '#0d6efd',
    'writing': '#ffc107',
    'submitted': '#198754',
    'pass': '#20c997',
    'hold': '#dc3545'
}


def render_index(notices: list) -> str:
    rows = []
    for n in notices:
        title = escape_html(n.get('title') or '제목 없음')
        apply_end = n.get('apply_end') or '-'
        agency = escape_html(n.get('agency') or n.get('ministry') or '-')
        source_url = escape_html(n.get('source_url') or '')
        source_origin_url = escape_html(n.get('source_origin_url') or '')
        storage_path = n.get('storage_path', '')
        status = n.get('status', 'new')
        one_line = escape_html(n.get('one_line_summary') or '')
        has_note = bool(n.get('manual_note'))
        
        detail_link = f"notices/{n['id']}.html"
        
        status_label = STATUS_LABELS.get(status, status)
        status_color = STATUS_COLORS.get(status, '#6c757d')
        
        origin_link = f'<a href="{source_origin_url}" target="_blank" title="출처 바로가기">🔗</a>' if source_origin_url else ''
        
        rows.append(f"""        <tr data-status="{status}" data-title="{title}" data-agency="{agency}" data-summary="{one_line}">
            <td>
                <a href="{detail_link}">{title}</a>
                {f'<br><small class="summary">{one_line}</small>' if one_line else ''}
            </td>
            <td><span class="status-badge" style="background:{status_color}">{status_label}</span></td>
            <td>{apply_end}</td>
            <td>{agency} {origin_link}</td>
            <td>{'📝' if has_note else ''}</td>
            <td><a href="{source_url}" target="_blank">원문</a></td>
            <td><a href="{detail_link}">보기</a></td>
        </tr>""")

    if not rows:
        rows = ['        <tr><td colspan="7">등록된 공고가 없습니다.</td></tr>']

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="utf-8">
    <title>지원사업 대시보드</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 20px; background: #f8f9fa; }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        h1 {{ margin-bottom: 20px; color: #333; }}
        .controls {{ margin-bottom: 20px; padding: 15px; background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .filter-buttons {{ margin-bottom: 10px; }}
        .filter-buttons button {{ padding: 6px 12px; margin-right: 5px; border: 1px solid #ddd; background: white; cursor: pointer; border-radius: 4px; }}
        .filter-buttons button.active {{ background: #0d6efd; color: white; border-color: #0d6efd; }}
        .search-box {{ width: 100%; max-width: 300px; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }}
        table {{ border-collapse: collapse; width: 100%; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        th, td {{ border: 1px solid #eee; padding: 12px; text-align: left; }}
        th {{ background: #f8f9fa; font-weight: 600; }}
        tr:hover {{ background: #f9f9f9; }}
        .status-badge {{ display: inline-block; padding: 3px 8px; border-radius: 4px; color: white; font-size: 12px; }}
        .summary {{ color: #666; font-size: 13px; }}
        .empty {{ color: #888; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📋 지원사업 대시보드</h1>
        <div class="controls">
            <div class="filter-buttons">
                <button class="active" data-filter="all">전체</button>
                <button data-filter="new">신규</button>
                <button data-filter="reviewing">검토중</button>
                <button data-filter="writing">작성중</button>
                <button data-filter="submitted">제출완료</button>
                <button data-filter="pass">합격</button>
                <button data-filter="hold">보류</button>
            </div>
            <input type="text" class="search-box" id="searchBox" placeholder="제목, 기관, 요약 검색...">
        </div>
        <p>총 {len(notices)}개 공고</p>
        <table>
            <thead>
                <tr>
                    <th>공고명</th>
                    <th>상태</th>
                    <th>마감일</th>
                    <th>기관</th>
                    <th>메모</th>
                    <th>원문</th>
                    <th>상세</th>
                </tr>
            </thead>
            <tbody id="noticeTable">
{chr(10).join(rows)}
            </tbody>
        </table>
    </div>
    <script>
        const buttons = document.querySelectorAll('.filter-buttons button');
        const searchBox = document.getElementById('searchBox');
        const rows = document.querySelectorAll('#noticeTable tr');
        
        function filter() {{
            const status = document.querySelector('.filter-buttons button.active').dataset.filter;
            const search = searchBox.value.toLowerCase();
            
            rows.forEach(row => {{
                const rowStatus = row.dataset.status;
                const title = row.dataset.title.toLowerCase();
                const agency = row.dataset.agency.toLowerCase();
                const summary = row.dataset.summary.toLowerCase();
                
                const statusMatch = status === 'all' || rowStatus === status;
                const searchMatch = !search || title.includes(search) || agency.includes(search) || summary.includes(search);
                
                row.style.display = statusMatch && searchMatch ? '' : 'none';
            }});
        }}
        
        buttons.forEach(btn => {{
            btn.addEventListener('click', () => {{
                buttons.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                filter();
            }});
        }});
        
        searchBox.addEventListener('input', filter);
    </script>
</body>
</html>"""


def render_detail(notice: dict) -> str:
    meta_rows = []

    status = notice.get('status', 'new')
    status_label = STATUS_LABELS.get(status, status)
    status_color = STATUS_COLORS.get(status, '#6c757d')
    
    meta_rows.append(f"        <tr><th>상태</th><td><span class='status-badge' style='background:{status_color}'>{status_label}</span></td></tr>")
    
    one_line = notice.get('one_line_summary')
    if one_line:
        meta_rows.append(f"        <tr><th>한줄요약</th><td>{escape_html(one_line)}</td></tr>")

    fields = [
        ('source_notice_id', '공고번호'),
        ('category', '분류'),
        ('posted_at', '게시일'),
        ('apply_start', '접수시작'),
        ('apply_end', '접수마감'),
        ('ministry', '소관부처'),
        ('agency', '주관기관'),
        ('apply_method', '신청방법'),
        ('apply_site_url', '접수처'),
        ('contact', '문의처'),
    ]

    for key, label in fields:
        value = notice.get(key)
        if value:
            meta_rows.append(f"        <tr><th>{label}</th><td>{escape_html(str(value))}</td></tr>")

    manual_note = notice.get('manual_note')
    if manual_note:
        meta_rows.append(f"        <tr><th>수동메모</th><td class='note'>{escape_html(manual_note)}</td></tr>")

    storage_path = notice.get('storage_path')
    if storage_path:
        meta_rows.append(f"        <tr><th>저장경로</th><td>{escape_html(storage_path)}</td></tr>")

    attach_rows = []
    for att in notice.get('attachments', []):
        name = escape_html(att['name'] or '첨부파일')
        url = escape_html(att['download_url'] or att['view_url'] or '')
        attach_rows.append(f'            <li><a href="{url}" target="_blank">{name}</a></li>')

    attach_section = ""
    if attach_rows:
        attach_section = f"""
    <h3>첨부파일</h3>
    <ul>
{chr(10).join(attach_rows)}
    </ul>"""

    summary = notice.get('summary_text') or ''
    if not summary:
        summary = "(사업개요가 없습니다)"

    title = escape_html(notice.get('title') or '제목 없음')
    
    source_origin_url = notice.get('source_origin_url')
    origin_link = ""
    if source_origin_url:
        origin_link = f"""    <p><a href="{escape_html(source_origin_url)}" target="_blank" class="origin-btn">🔗 출처 바로가기</a></p>"""

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="utf-8">
    <title>{title} - 지원사업 상세</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 20px; background: #f8f9fa; }}
        .container {{ max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ margin-bottom: 20px; color: #333; }}
        h2 {{ margin-top: 30px; color: #333; border-bottom: 2px solid #eee; padding-bottom: 10px; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #eee; padding: 12px; text-align: left; }}
        th {{ background: #f8f9fa; width: 150px; }}
        ul {{ list-style: none; padding: 0; }}
        li {{ margin: 5px 0; }}
        a {{ color: #0066cc; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        .back {{ margin-bottom: 20px; }}
        .summary {{ background: #f9f9f9; padding: 15px; border-radius: 5px; line-height: 1.6; }}
        .status-badge {{ display: inline-block; padding: 3px 8px; border-radius: 4px; color: white; font-size: 12px; }}
        .note {{ background: #fff3cd; padding: 10px; border-radius: 4px; white-space: pre-wrap; }}
        .origin-btn {{ display: inline-block; padding: 8px 16px; background: #0d6efd; color: white; border-radius: 4px; }}
        .files {{ background: #e9ecef; padding: 15px; border-radius: 4px; }}
        .files a {{ display: block; margin: 5px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <p class="back"><a href="../index.html">← 목록으로</a></p>
        <h1>{title}</h1>

        <h2>기본 정보</h2>
        <table>
{chr(10).join(meta_rows)}
        </table>

        <h2>사업개요</h2>
        <div class="summary">{escape_html(summary)}</div>

{attach_section}

<h2>로컬 파일</h2>
<div class="files">
{chr(10).join([f' <a href="../../data/notices/{storage_path.replace(chr(92), "/")}/{f}">{f}</a>' for f in ['meta.json', 'source.html', 'attachments.json'] if storage_path]) if storage_path else ' <span>파일 없음</span>'}
</div>

        <h2>링크</h2>
        <p><a href="{escape_html(notice.get('source_url') or '')}" target="_blank">bizinfo.go.kr에서 보기</a></p>
{origin_link}
    </div>
</body>
</html>"""


def render_all():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    notices = fetch_notices()

    with open(OUTPUT_DIR / "index.html", "w", encoding="utf-8") as f:
        f.write(render_index(notices))

    for notice in notices:
        detail_path = OUTPUT_DIR / "notices" / f"{notice['id']}.html"
        detail_path.parent.mkdir(parents=True, exist_ok=True)

        with open(detail_path, "w", encoding="utf-8") as f:
            f.write(render_detail(notice))

    print(f"Rendered {len(notices)} notices to {OUTPUT_DIR}")


if __name__ == "__main__":
    render_all()