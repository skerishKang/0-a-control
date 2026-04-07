#!/usr/bin/env python3
"""
공고 서비스
URL 도메인에 따라 bizinfo / kstartup 어댑터 분기
"""

import json
import re
import urllib.request
import ssl
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import importlib.util

# 공통 유틸 import
import sys
sys.path.insert(0, str(Path(__file__).parent))
import repositories.notice_repo as notice_repo

# 경로 설정
ROOT_DIR = Path(__file__).parent.parent.parent
DATA_DIR = ROOT_DIR / "data"


def fetch_url(url: str, timeout: int = 15) -> str:
    """URL Fetch (공통)"""
    print(f"[collect] fetch start: {url}", flush=True)
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    )
    
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as response:
        content = response.read().decode("utf-8")
        print(f"[collect] fetch done: {len(content)} chars", flush=True)
        return content


def get_adapter_for_url(url: str):
    """
    URL 도메인에 따라 적절한 어댑터 반환
    Returns: adapter_module, source_site, api_key
    """
    url_lower = url.lower()
    
    if 'bizinfo.go.kr' in url_lower:
        spec = importlib.util.spec_from_file_location(
            "adapter_bizinfo", 
            Path(__file__).parent.parent / "adapter_bizinfo.py"
        )
        adapter = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(adapter)
        
        # API 키 로드 (settings 함수 사용)
        api_key = ""
        try:
            import settings
            api_key = settings.get_bizinfo_api_key() or ""
        except:
            pass
        
        return adapter, "bizinfo", api_key
    
    elif 'k-startup.go.kr' in url_lower:
        spec = importlib.util.spec_from_file_location(
            "adapter_kstartup",
            Path(__file__).parent.parent / "adapter_kstartup.py"
        )
        adapter = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(adapter)
        
        # API 키 로드 (settings 함수 사용)
        api_key = ""
        try:
            import settings
            api_key = settings.get_kstartup_api_key() or ""
        except:
            pass
        
        return adapter, "kstartup", api_key
    
    else:
        raise ValueError(f"Unsupported URL domain: {url}")


def notice_data_to_dict(notice_data, source_site: str, url: str) -> Dict[str, Any]:
    """NoticeData 객체를 딕셔너리로 변환"""
    attachments = []
    if hasattr(notice_data, 'attachments') and notice_data.attachments:
        for att in notice_data.attachments:
            if hasattr(att, 'name'):
                attachments.append({
                    'name': att.name,
                    'view_url': att.view_url,
                    'download_url': att.download_url,
                    'section_name': att.section_name
                })
            elif isinstance(att, dict):
                attachments.append(att)
    
    return {
        'source_site': source_site,
        'source_url': getattr(notice_data, 'source_url', url),
        'source_notice_id': getattr(notice_data, 'source_notice_id', ''),
        'source_origin_url': getattr(notice_data, 'source_origin_url', url),
        'title': getattr(notice_data, 'title', ''),
        'category': getattr(notice_data, 'category', ''),
        'posted_at': getattr(notice_data, 'posted_at', ''),
        'apply_start': getattr(notice_data, 'apply_start', ''),
        'apply_end': getattr(notice_data, 'apply_end', ''),
        'ministry': getattr(notice_data, 'ministry', ''),
        'agency': getattr(notice_data, 'agency', ''),
        'apply_method': getattr(notice_data, 'apply_method', ''),
        'apply_site_url': getattr(notice_data, 'apply_site_url', ''),
        'contact': getattr(notice_data, 'contact', ''),
        'summary_html': getattr(notice_data, 'summary_html', ''),
        'summary_text': getattr(notice_data, 'summary_text', ''),
        'attachments': attachments,
    }


def collect_notice(url: str) -> int:
    """
    공고 수집 (bizinfo.go.kr 또는 k-startup.go.kr)
    Returns: notice_id
    """
    print(f"[collect] collect start: {url}", flush=True)
    
    # URL 도메인에 따라 어댑터 선택
    adapter, source_site, api_key = get_adapter_for_url(url)
    
    # 수집 모드 로그
    if source_site == 'bizinfo':
        if api_key:
            print("[collect] bizinfo api mode", flush=True)
        else:
            print("[collect] bizinfo html fallback", flush=True)
    elif source_site == 'kstartup':
        if api_key:
            print("[collect] kstartup api mode", flush=True)
        else:
            print("[collect] kstartup html fallback", flush=True)
    
    # 어댑터로 공고 수집
    if hasattr(adapter, 'collect_from_url'):
        notice_data = adapter.collect_from_url(url, api_key) if api_key else adapter.collect_from_url(url)
    elif hasattr(adapter, 'parse_bizinfo_html'):
        html_content = fetch_url(url)
        notice_data = adapter.parse_bizinfo_html(html_content, url)
    else:
        raise ValueError(f"Adapter does not have collect_from_url or parse_bizinfo_html method")
    
    # NoticeData를 딕셔너리로 변환
    result = notice_data_to_dict(notice_data, source_site, url)
    
    print(f"[collect] parse done: title={result.get('title', '')}, attachments={len(result.get('attachments', []))}", flush=True)
    
    # 파일 저장
    print("[collect] file save start", flush=True)
    storage_path = Path(result.get('posted_at', '')[:7].replace('-', '/')) if result.get('posted_at') else Path(datetime.now().strftime("%Y/%m"))
    full_path = DATA_DIR / "notices" / storage_path
    full_path.mkdir(parents=True, exist_ok=True)
    
    # HTML 소스 저장
    try:
        full_html = fetch_url(url)
        with open(full_path / "source.html", "w", encoding="utf-8") as f:
            f.write(full_html)
    except Exception as e:
        print(f"[collect] Warning: could not save source.html: {e}", flush=True)
    
    meta = {
        "source_site": result.get('source_site', source_site),
        "source_url": result.get('source_url', ''),
        "source_notice_id": result.get('source_notice_id', ''),
        "title": result.get('title', ''),
        "category": result.get('category', ''),
        "posted_at": result.get('posted_at', ''),
        "apply_start": result.get('apply_start', ''),
        "apply_end": result.get('apply_end', ''),
        "ministry": result.get('ministry', ''),
        "agency": result.get('agency', ''),
        "apply_method": result.get('apply_method', ''),
        "apply_site_url": result.get('apply_site_url', ''),
        "source_origin_url": result.get('source_origin_url', ''),
        "contact": result.get('contact', ''),
        "summary_html": result.get('summary_html', ''),
        "summary_text": result.get('summary_text', ''),
    }
    
    with open(full_path / "meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    
    attachments_info = []
    for i, att in enumerate(result.get('attachments', [])):
        attachments_info.append({
            "name": att.get('name', ''),
            "view_url": att.get('view_url', ''),
            "download_url": att.get('download_url', ''),
            "section_name": att.get('section_name', '첨부파일'),
            "sort_order": i
        })
    
    if attachments_info:
        with open(full_path / "attachments.json", "w", encoding="utf-8") as f:
            json.dump(attachments_info, f, ensure_ascii=False, indent=2)
    print(f"[collect] file save done: {full_path}", flush=True)
    
    # DB 저장
    print("[collect] db save start", flush=True)
    conn = notice_repo.get_connection()
    cursor = conn.cursor()
    
    existing = None
    if result.get('source_notice_id'):
        cursor.execute("SELECT id FROM notices WHERE source_notice_id = ?", (result['source_notice_id'],))
        existing = cursor.fetchone()
    
    if not existing:
        cursor.execute("SELECT id FROM notices WHERE source_url = ?", (result['source_url'],))
        existing = cursor.fetchone()
    
    now = datetime.now().isoformat()
    
    if existing:
        notice_id = existing[0]
        cursor.execute("""
            UPDATE notices SET
                source_site = ?,
                source_notice_id = ?,
                title = ?,
                category = ?,
                posted_at = ?,
                apply_start = ?,
                apply_end = ?,
                ministry = ?,
                agency = ?,
                apply_method = ?,
                apply_site_url = ?,
                source_origin_url = ?,
                contact = ?,
                summary_html = ?,
                summary_text = ?,
                storage_path = ?,
                updated_at = ?
            WHERE id = ?
        """, (
            result.get('source_site', source_site),
            result.get('source_notice_id', ''),
            result.get('title', ''),
            result.get('category', ''),
            result.get('posted_at', ''),
            result.get('apply_start', ''),
            result.get('apply_end', ''),
            result.get('ministry', ''),
            result.get('agency', ''),
            result.get('apply_method', ''),
            result.get('apply_site_url', ''),
            result.get('source_origin_url', ''),
            result.get('contact', ''),
            result.get('summary_html', ''),
            result.get('summary_text', ''),
            str(storage_path),
            now,
            notice_id
        ))
    else:
        cursor.execute("""
            INSERT INTO notices (
                source_site, source_url, source_notice_id, title, category,
                posted_at, apply_start, apply_end, ministry, agency,
                apply_method, apply_site_url, source_origin_url, contact,
                summary_html, summary_text, storage_path, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            result.get('source_site', source_site),
            result.get('source_url', ''),
            result.get('source_notice_id', ''),
            result.get('title', ''),
            result.get('category', ''),
            result.get('posted_at', ''),
            result.get('apply_start', ''),
            result.get('apply_end', ''),
            result.get('ministry', ''),
            result.get('agency', ''),
            result.get('apply_method', ''),
            result.get('apply_site_url', ''),
            result.get('source_origin_url', ''),
            result.get('contact', ''),
            result.get('summary_html', ''),
            result.get('summary_text', ''),
            str(storage_path),
            now,
            now
        ))
        notice_id = cursor.lastrowid
    
    # 첨부파일 저장
    cursor.execute("DELETE FROM attachments WHERE notice_id = ?", (notice_id,))
    
    for i, att in enumerate(result.get('attachments', [])):
        cursor.execute("""
            INSERT INTO attachments (
                notice_id, section_name, name, view_url, download_url, sort_order
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            notice_id,
            att.get('section_name', '첨부파일'),
            att.get('name', ''),
            att.get('view_url', ''),
            att.get('download_url', ''),
            i
        ))
    
    conn.commit()
    conn.close()
    print(f"[collect] db save done: notice_id={notice_id}", flush=True)
    
    return notice_id


# re import for parse functions
import re