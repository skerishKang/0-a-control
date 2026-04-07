#!/usr/bin/env python3
"""
HTML 페이지 렌더러
"""

from typing import List, Dict, Any

# 공통 import
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from common.utils import escape_html
from common.constants import STATUS_LABELS, STATUS_COLORS


def render_main_page(notices: List[Dict[str, Any]]) -> str:
    """메인 페이지 HTML"""
    rows = []
    for n in notices:
        title = escape_html(n.get('title') or '제목 없음')
        apply_end = n.get('apply_end') or '-'
        agency = escape_html(n.get('agency') or n.get('ministry') or '-')
        source_url = escape_html(n.get('source_url') or '')
        source_origin_url = escape_html(n.get('source_origin_url') or '')
        status = n.get('status', 'new')
        one_line = escape_html(n.get('one_line_summary') or '')
        has_note = bool(n.get('manual_note'))
        
        status_label = STATUS_LABELS.get(status, status)
        status_color = STATUS_COLORS.get(status, '#6c757d')
        origin_link = f'<a href="{source_origin_url}" target="_blank" title="출처 바로가기">🔗</a>' if source_origin_url else ''
        
        rows.append(f"""        <tr data-status="{status}" data-title="{title}" data-agency="{agency}" data-summary="{one_line}" data-id="{n['id']}">
            <td>
                <a href="/notice/{n['id']}">{title}</a>
                {f'<br><small class="summary">{one_line}</small>' if one_line else ''}
            </td>
            <td><span class="status-badge" style="background:{status_color}">{status_label}</span></td>
            <td>{apply_end}</td>
            <td>{agency} {origin_link}</td>
            <td>{'📝' if has_note else ''}</td>
            <td><a href="{source_url}" target="_blank">원문</a></td>
            <td><a href="/notice/{n['id']}">보기</a></td>
            <td><a href="#" class="delete-btn" data-id="{n['id']}" title="삭제">🗑️</a></td>
        </tr>""")

    if not rows:
        rows = ['        <tr><td colspan="8">등록된 공고가 없습니다.</td></tr>']

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
        .collect-form {{ display: flex; gap: 10px; margin-bottom: 15px; }}
        .collect-form input {{ flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 4px; }}
        .collect-form button {{ padding: 10px 20px; background: #198754; color: white; border: none; border-radius: 4px; cursor: pointer; }}
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
        .msg {{ padding: 10px; margin-bottom: 10px; border-radius: 4px; display: none; }}
        .msg.success {{ background: #d4edda; color: #155724; }}
        .msg.error {{ background: #f8d7da; color: #721c24; }}
        .delete-btn {{ color: #dc3545; text-decoration: none; font-size: 16px; cursor: pointer; }}
        .delete-btn:hover {{ color: #bb2d3b; }}
        .sort-info {{ color: #6c757d; font-size: 14px; margin-bottom: 10px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📋 지원사업 대시보드</h1>
        
        <div class="controls">
            <form class="collect-form" id="collectForm">
                <input type="text" id="urlInput" placeholder="지원사업 공고 URL을 입력하세요 (bizinfo, k-startup)" required>
                <button type="submit">수집</button>
            </form>
            <div id="msg" class="msg"></div>
            
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
        <p class="sort-info">📅 기본은 마감일 빠른 순입니다.</p>
        <p><button type="button" id="sortDeadlineBtn">마감일 정렬 ↑</button></p>
        <table>
            <thead>
                <tr>
                    <th>공고명</th>
                    <th>상태</th>
                    <th>마감일 ↑</th>
                    <th>기관</th>
                    <th>사용자 메모</th>
                    <th>원문</th>
                    <th>상세</th>
                    <th></th>
                </tr>
            </thead>
            <tbody id="noticeTable">
{chr(10).join(rows)}
            </tbody>
        </table>
    </div>
    
    <script>
        const form = document.getElementById('collectForm');
        const msg = document.getElementById('msg');
        
        form.addEventListener('submit', async (e) => {{
            e.preventDefault();
            const url = document.getElementById('urlInput').value;
            msg.style.display = 'block';
            msg.className = 'msg';
            msg.textContent = '수집 중...';
            
            try {{
                const res = await fetch('/collect', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{url}})
                }});
                const data = await res.json();
                
                if (data.success) {{
                    msg.className = 'msg success';
                    msg.textContent = '수집 완료: ' + data.title;
                    setTimeout(() => location.reload(), 700);
                }} else {{
                    msg.className = 'msg error';
                    msg.textContent = '오류: ' + data.error;
                }}
            }} catch (err) {{
                msg.className = 'msg error';
                msg.textContent = '오류: ' + err.message;
            }}
        }});
        
        const buttons = document.querySelectorAll('.filter-buttons button');
        const searchBox = document.getElementById('searchBox');
        const rows = document.querySelectorAll('#noticeTable tr');
        const tableBody = document.getElementById('noticeTable');
        const sortDeadlineBtn = document.getElementById('sortDeadlineBtn');
        let deadlineAsc = true;
        
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

        function parseDeadline(value) {{
            const text = (value || '').trim();
            if (!text || text === '-') return '9999-99-99';
            return text;
        }}

        sortDeadlineBtn.addEventListener('click', () => {{
            const sortableRows = Array.from(tableBody.querySelectorAll('tr'));
            sortableRows.sort((a, b) => {{
                const aDate = parseDeadline(a.children[2]?.innerText || '');
                const bDate = parseDeadline(b.children[2]?.innerText || '');
                if (aDate < bDate) return deadlineAsc ? -1 : 1;
                if (aDate > bDate) return deadlineAsc ? 1 : -1;
                return 0;
            }});

            sortableRows.forEach(row => tableBody.appendChild(row));
            deadlineAsc = !deadlineAsc;
            sortDeadlineBtn.textContent = deadlineAsc ? '마감일 정렬 ↑' : '마감일 정렬 ↓';
        }});
        
        // 삭제 버튼 처리
        document.querySelectorAll('.delete-btn').forEach(btn => {{
            btn.addEventListener('click', async (e) => {{
                e.preventDefault();
                const id = btn.dataset.id;
                if (!confirm('이 공고를 삭제하시겠습니까?')) return;
                
                try {{
                    const res = await fetch('/delete', {{
                        method: 'POST',
                        headers: {{'Content-Type': 'application/json'}},
                        body: JSON.stringify({{ notice_id: id }})
                    }});
                    const data = await res.json();
                    
                    if (data.success) {{
                        const row = btn.closest('tr');
                        row.remove();
                    }} else {{
                        alert('삭제 실패: ' + (data.error || '알 수 없는 오류'));
                    }}
                }} catch (err) {{
                    alert('오류: ' + err.message);
                }}
            }});
        }});
    </script>
</body>
</html>"""


def render_detail_page(notice: Dict[str, Any]) -> str:
    """상세 페이지 HTML"""
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
        meta_rows.append(f"        <tr><th>사용자 메모</th><td class='note'>{escape_html(manual_note)}</td></tr>")
    
    # AI 분석 섹션
    ai_fit_score = notice.get('ai_fit_score')
    ai_summary = notice.get('ai_summary')
    ai_strengths = notice.get('ai_strengths')
    ai_risks = notice.get('ai_risks')
    ai_next_actions = notice.get('ai_next_actions')
    ai_model = notice.get('ai_model')
    ai_updated_at = notice.get('ai_updated_at')
    ai_mode = notice.get('ai_mode')
    ai_provider = notice.get('ai_provider')
    ai_fallback_used = notice.get('ai_fallback_used')
    
    # mode별 라벨
    mode_labels = {
        'quick': '⚡ 빠른 분석',
        'medium': '📊 중간 분석',
        'deep': '🔍 깊은 분석',
        'glm': '🎯 GLM 분석'
    }
    
    ai_table_rows = []
    if ai_fit_score is not None:
        ai_table_rows.append(f"        <tr><th>적합도</th><td>{ai_fit_score}/10</td></tr>")
    else:
        ai_table_rows.append("        <tr><th>적합도</th><td>-</td></tr>")
    if ai_summary:
        ai_table_rows.append(f"        <tr><th>요약</th><td>{escape_html(ai_summary)}</td></tr>")
    else:
        ai_table_rows.append("        <tr><th>요약</th><td>-</td></tr>")
    if ai_strengths:
        ai_table_rows.append(f"        <tr><th>주요 장점</th><td>{escape_html(ai_strengths)}</td></tr>")
    else:
        ai_table_rows.append("        <tr><th>주요 장점</th><td>-</td></tr>")
    if ai_risks:
        ai_table_rows.append(f"        <tr><th>주요 위험</th><td>{escape_html(ai_risks)}</td></tr>")
    else:
        ai_table_rows.append("        <tr><th>주요 위험</th><td>-</td></tr>")
    if ai_next_actions:
        ai_table_rows.append(f"        <tr><th>추천 액션</th><td>{escape_html(ai_next_actions)}</td></tr>")
    else:
        ai_table_rows.append("        <tr><th>추천 액션</th><td>-</td></tr>")
    if ai_mode:
        mode_label = mode_labels.get(ai_mode, ai_mode)
        ai_table_rows.append(f"        <tr><th>분석 모드</th><td>{mode_label}</td></tr>")
    if ai_provider:
        ai_table_rows.append(f"        <tr><th>Provider</th><td>{escape_html(ai_provider)}</td></tr>")
    if ai_model:
        fallback_indicator = " ↩️" if ai_fallback_used else ""
        ai_table_rows.append(f"        <tr><th>모델명</th><td>{escape_html(ai_model)}{fallback_indicator}</td></tr>")
    else:
        ai_table_rows.append("        <tr><th>모델명</th><td>-</td></tr>")
    if ai_fallback_used:
        ai_table_rows.append("        <tr><th>Fallback</th><td>✅ 사용됨</td></tr>")
    if ai_updated_at:
        ai_table_rows.append(f"        <tr><th>마지막 분석 시각</th><td>{escape_html(ai_updated_at)}</td></tr>")
    else:
        ai_table_rows.append("        <tr><th>마지막 분석 시각</th><td>-</td></tr>")
    
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

    update_form = f"""
    <h2>상태 수정</h2>
    <form id="updateForm">
        <select id="statusSelect">
            <option value="new" {"selected" if status == "new" else ""}>신규</option>
            <option value="reviewing" {"selected" if status == "reviewing" else ""}>검토중</option>
            <option value="writing" {"selected" if status == "writing" else ""}>작성중</option>
            <option value="submitted" {"selected" if status == "submitted" else ""}>제출완료</option>
            <option value="pass" {"selected" if status == "pass" else ""}>합격</option>
            <option value="hold" {"selected" if status == "hold" else ""}>보류</option>
        </select>
        <input type="text" id="summaryInput" placeholder="한줄요약" value="{escape_html(one_line or '')}">
        <textarea id="noteInput" placeholder="사용자 메모">{escape_html(manual_note or '')}</textarea>
        <button type="submit">저장</button>
    </form>
    <div id="updateMsg"></div>
    <script>
        document.getElementById('updateForm').addEventListener('submit', async (e) => {{
            e.preventDefault();
            const data = {{
                notice_id: '{notice['source_notice_id']}',
                status: document.getElementById('statusSelect').value,
                summary: document.getElementById('summaryInput').value,
                note: document.getElementById('noteInput').value
            }};
            const res = await fetch('/update', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify(data)
            }});
            const result = await res.json();
            document.getElementById('updateMsg').innerHTML = result.success 
                ? '<span style="color:green">저장 완료</span>' 
                : '<span style="color:red">오류: ' + result.error + '</span>';
        }});
    <\/script>
    """

    storage_path = notice.get('storage_path') or ''
    files_section = ""
    if storage_path:
        url_path = storage_path.replace('\\', '/')
        files_section = f"""
    <h2>로컬 파일</h2>
    <div class="files">
 <a href="../../data/notices/{url_path}/meta.json">meta.json</a>
 <a href="../../data/notices/{url_path}/source.html">source.html</a>
 <a href="../../data/notices/{url_path}/attachments.json">attachments.json</a>
    </div>"""

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
        #updateForm {{ display: flex; flex-direction: column; gap: 10px; max-width: 400px; }}
        #updateForm select, #updateForm input, #updateForm textarea, #updateForm button {{ padding: 8px; }}
        #updateForm textarea {{ min-height: 80px; }}
    </style>
</head>
<body>
    <div class="container">
        <p class="back"><a href="/">← 목록으로</a></p>
        <h1>{title}</h1>

        <h2>기본 정보</h2>
        <table>
{chr(10).join(meta_rows)}
        </table>

        <h2>AI 분석</h2>
        <table>
{chr(10).join(ai_table_rows)}
        </table>
        <p style="margin-top:10px;">
            <button type="button" id="analyzeQuickBtn" style="background:#22c55e;color:white;padding:10px 20px;border:none;border-radius:4px;cursor:pointer;margin-right:8px;">
                ⚡ 빠른 분석
            </button>
            <button type="button" id="analyzeMediumBtn" style="background:#f59e0b;color:white;padding:10px 20px;border:none;border-radius:4px;cursor:pointer;margin-right:8px;">
                📊 중간 분석
            </button>
            <button type="button" id="analyzeDeepBtn" style="background:#8b5cf6;color:white;padding:10px 20px;border:none;border-radius:4px;cursor:pointer;margin-right:8px;">
                🔍 깊은 분석
            </button>
            <button type="button" id="analyzeGlmBtn" style="background:#ec4899;color:white;padding:10px 20px;border:none;border-radius:4px;cursor:pointer;">
                🎯 GLM 분석
            </button>
        </p>
        <div id="analyzeMsg"></div>
        <script>
            const modeConfig = {{
                'quick': {{ label: '⚡ 빠른 분석', color: '#22c55e' }},
                'medium': {{ label: '📊 중간 분석', color: '#f59e0b' }},
                'deep': {{ label: '🔍 깊은 분석', color: '#8b5cf6' }},
                'glm': {{ label: '🎯 GLM 분석', color: '#ec4899' }}
            }};
            
            async function runAnalyze(mode) {{
                const quickBtn = document.getElementById('analyzeQuickBtn');
                const mediumBtn = document.getElementById('analyzeMediumBtn');
                const deepBtn = document.getElementById('analyzeDeepBtn');
                const glmBtn = document.getElementById('analyzeGlmBtn');
                const buttons = {{ 'quick': quickBtn, 'medium': mediumBtn, 'deep': deepBtn, 'glm': glmBtn }};
                const msg = document.getElementById('analyzeMsg');
                const btn = buttons[mode];
                
                btn.disabled = true;
                btn.textContent = modeConfig[mode].label.replace('분석', '분석 중...');
                msg.innerHTML = '';
                
                try {{
                    const res = await fetch('/analyze-ai', {{
                        method: 'POST',
                        headers: {{'Content-Type': 'application/json'}},
                        body: JSON.stringify({{ notice_id: "{notice.get('source_notice_id', '')}", mode: mode }})
                    }});
                    const result = await res.json();
                    
                    if (result.success) {{
                        const r = result.result;
                        const fbInfo = r.fallback_used ? ' (fallback 사용)' : '';
                        msg.innerHTML = '<span style="color:green">' + modeConfig[mode].label + ' 완료 - ' + r.provider + '/' + r.model + fbInfo + '</span>';
                        setTimeout(() => location.reload(), 1500);
                    }} else {{
                        msg.innerHTML = '<span style="color:red">오류: ' + (result.error || '분석 실패') + '</span>';
                        btn.disabled = false;
                        btn.textContent = modeConfig[mode].label;
                    }}
                }} catch (err) {{
                    msg.innerHTML = '<span style="color:red">오류: ' + err.message + '</span>';
                    btn.disabled = false;
                    btn.textContent = modeConfig[mode].label;
                }}
            }}
            
            document.getElementById('analyzeQuickBtn').addEventListener('click', () => runAnalyze('quick'));
            document.getElementById('analyzeMediumBtn').addEventListener('click', () => runAnalyze('medium'));
            document.getElementById('analyzeDeepBtn').addEventListener('click', () => runAnalyze('deep'));
            document.getElementById('analyzeGlmBtn').addEventListener('click', () => runAnalyze('glm'));
        <\/script>

        <h2>AI 분석 입력</h2>
     <form id="aiForm">
         <input type="number" id="aiFitScore" placeholder="적합도 (0-10)" step="0.1" min="0" max="10">
         <textarea id="aiSummary" placeholder="AI 요약"></textarea>
         <textarea id="aiStrengths" placeholder="주요 장점"></textarea>
         <textarea id="aiRisks" placeholder="주요 위험"></textarea>
         <textarea id="aiNextActions" placeholder="추천 액션"></textarea>
         <input type="text" id="aiModel" placeholder="모델명">
         <button type="submit">AI 분석 저장</button>
     </form>
     <div id="aiMsg"></div>
      <script>
          document.getElementById('aiForm').addEventListener('submit', async (e) => {{
              e.preventDefault();
              const data = {{
                  notice_id: "{notice.get('source_notice_id', '')}",
                  ai_fit_score: document.getElementById('aiFitScore').value,
                  ai_summary: document.getElementById('aiSummary').value,
                  ai_strengths: document.getElementById('aiStrengths').value,
                  ai_risks: document.getElementById('aiRisks').value,
                  ai_next_actions: document.getElementById('aiNextActions').value,
                  ai_model: document.getElementById('aiModel').value
              }};
              const res = await fetch('/update-ai', {{
                  method: 'POST',
                  headers: {{'Content-Type': 'application/json'}},
                  body: JSON.stringify(data)
              }});
              const result = await res.json();
              document.getElementById('aiMsg').innerHTML = result.success 
                  ? '<span style="color:green">AI 분석 저장 완료</span>' 
                  : '<span style="color:red">오류: ' + result.error + '</span>';
          }});
      <\/script>

        <h2>사업개요</h2>
        <div class="summary">{escape_html(summary)}</div>

{attach_section}

{files_section}

        <h2>링크</h2>
        <p><a href="{escape_html(notice.get('source_url') or '')}" target="_blank">공고 바로가기</a></p>
{origin_link}

{update_form}
  </div>
</body>
</html>"""
