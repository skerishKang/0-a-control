#!/usr/bin/env python3
"""
K-Startup 공고 어댑터
공공데이터포털 API 우선, HTML 파싱 보충
"""

import re
import json
import urllib.request
import ssl
import urllib.parse
from html import unescape
from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict, field
from pathlib import Path
import sys

# 설정 파일에서 API 키 로드 (settings 함수 사용)
sys.path.insert(0, str(Path(__file__).parent))
try:
    import settings
    KSTARTUP_API_KEY = settings.get_kstartup_api_key() or ""
except ImportError:
    KSTARTUP_API_KEY = ''


@dataclass
class AttachmentInfo:
    name: str = ""
    view_url: str = ""
    download_url: str = ""
    section_name: str = "첨부파일"


@dataclass
class NoticeData:
    source_site: str = "kstartup"
    source_url: str = ""
    source_notice_id: str = ""
    title: str = ""
    category: str = ""
    posted_at: str = ""
    apply_start: str = ""
    apply_end: str = ""
    ministry: str = ""
    agency: str = ""
    apply_method: str = ""
    apply_site_url: str = ""
    source_origin_url: str = ""
    contact: str = ""
    summary_html: str = ""
    summary_text: str = ""
    attachments: list = field(default_factory=list)


def extract_notice_id(url: str) -> str:
    """K-Startup URL에서 공고 ID 추출"""
    # URL 패턴: https://www.k-startup.go.kr/web/contents/bizpbanc-ongoing.do?schM=view&pbancSn=163048
    match = re.search(r'pbancSn=(\d+)', url)
    if match:
        return match.group(1)
    
    # 대안 패턴
    match = re.search(r'bizpbanc.*?(\d{6,})', url)
    if match:
        return match.group(1)
    
    return ""


def parse_date(raw: str) -> str:
    """날짜 문자열을 YYYY-MM-DD 형식으로 변환"""
    if not raw:
        return ""
    
    # YYYYMMDD -> YYYY-MM-DD
    cleaned = re.sub(r'[.\-\s]', '', raw.strip())
    if re.match(r'^\d{8}$', cleaned):
        return f"{cleaned[:4]}-{cleaned[4:6]}-{cleaned[6:8]}"
    
    # YYYY/MM/DD -> YYYY-MM-DD
    match = re.match(r'^(\d{4})[./](\d{2})[./](\d{2})$', raw.strip())
    if match:
        return f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
    
    return raw.strip()


def parse_date_range(text: str) -> tuple:
    """신청기간 파싱"""
    # 다양한 형식 지원
    patterns = [
        r'(\d{4}[./]\d{2}[./]\d{2})\s*[~~~\-]\s*(\d{4}[./]\d{2}[./]\d{2})',
        r'(\d{4}-\d{2}-\d{2})\s*~\s*(\d{4}-\d{2}-\d{2})',
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return parse_date(match.group(1)), parse_date(match.group(2))
    return "", ""


def fetch_url(url: str, timeout: int = 15) -> str:
    """URL에서 HTML Fetch"""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
    )

    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as response:
        return response.read().decode("utf-8")


def fetch_kstartup_api(service_key: str, notice_id: str) -> Optional[Dict[str, Any]]:
    """
    공공데이터포털 K-Startup API에서 공고 상세 정보 조회
    실제 endpoint 사용: https://apis.data.go.kr/B552735/kisedKstartupService01
    """
    if not service_key:
        return None
    
    # 실제 K-Startup API endpoint (공공데이터포털)
    base_url = "https://apis.data.go.kr/B552735/kisedKstartupService01"
    
    # 공고 상세 정보 조회
    url = f"{base_url}/getAnnouncementInformation01"
    
    params = {
        'serviceKey': service_key,
        'numOfRows': '1',
        'pageNo': '1',
        'pbancSn': notice_id  # 공고일련번호
    }
    
    full_url = url + "&" + urllib.parse.urlencode(params)
    
    try:
        print(f"[kstartup] Fetching API: {full_url[:100]}...", flush=True)
        content = fetch_url(full_url, timeout=20)
        
        # XML 파싱 (K-Startup API는 XML 반환)
        data = {}
        
        # XML에서 주요 태그 추출
        # items/item 하위의 태그들
        item_match = re.search(r'<item>(.*?)</item>', content, re.DOTALL)
        if not item_match:
            print(f"[kstartup] No <item> found in API response", flush=True)
            return None
        
        item_content = item_match.group(1)
        
        # XML 태그에서 텍스트 추출
        def extract_xml_value(xml_content: str, tag: str) -> str:
            match = re.search(f'<{tag}>([^<]*)</{tag}>', xml_content)
            return match.group(1).strip() if match else ""
        
        # 주요 필드 매핑
        data['title'] = extract_xml_value(item_content, 'title') or extract_xml_value(item_content, 'pbancNm')
        data['biztitle'] = extract_xml_value(item_content, 'biztitle')
        data['supporttype'] = extract_xml_value(item_content, 'supporttype')
        data['organizationname'] = extract_xml_value(item_content, 'organizationname')
        data['posttarget'] = extract_xml_value(item_content, 'posttarget')
        data['startdate'] = extract_xml_value(item_content, 'startdate')
        data['enddate'] = extract_xml_value(item_content, 'enddate')
        data['detailurl'] = extract_xml_value(item_content, 'detailurl')
        data['content'] = extract_xml_value(item_content, 'content')
        
        if data.get('title'):
            print(f"[kstartup] API parse success: {data.get('title', '')[:30]}", flush=True)
            return data
        
        return None
        
    except Exception as e:
        print(f"[kstartup] API error: {e}, using HTML fallback", flush=True)
        return None


def api_response_to_noticedata(api_data: Dict[str, Any], url: str, notice_id: str) -> NoticeData:
    """API 응답을 NoticeData로 변환"""
    result = NoticeData(source_url=url)
    result.source_notice_id = notice_id
    
    # API 응답 필드 매핑
    result.title = api_data.get('title', '')
    result.category = api_data.get('biztitle') or api_data.get('supporttype', '')
    
    # 등록일
    posted = api_data.get('insertdate') or ''
    if posted:
        result.posted_at = parse_date(posted)
    
    # 신청기간
    start_date = api_data.get('startdate', '')
    end_date = api_data.get('enddate', '')
    if start_date:
        result.apply_start = parse_date(start_date)
    if end_date:
        result.apply_end = parse_date(end_date)
    
    # 기관
    result.agency = api_data.get('organizationname', '')
    
    # 요약
    result.summary_text = api_data.get('content', '')
    result.summary_html = f"<div>{result.summary_text}</div>"
    
    # 상세 URL
    result.source_origin_url = api_data.get('detailurl') or url
    
    print(f"[kstartup] API parse done: title={result.title[:30] if result.title else ''}", flush=True)
    return result


def parse_kstartup_html(html: str, url: str) -> NoticeData:
    """K-Startup HTML 파싱 (개선된 버전)"""
    result = NoticeData(source_url=url)
    result.source_notice_id = extract_notice_id(url)
    
    print(f"[kstartup] HTML fallback parsing", flush=True)
    
    # ====== title ======
    # 1. 메타 태그
    title_match = re.search(r'<meta[^>]+name="title"[^>]+content="([^"]+)"', html)
    if title_match:
        result.title = title_match.group(1)
    # 2. h1 태그
    if not result.title:
        title_match = re.search(r'<h1[^>]*>([^<]+)</h1>', html)
        if title_match:
            result.title = title_match.group(1).strip()
    # 3. view_tit 클래스
    if not result.title:
        title_match = re.search(r'<div[^>]*class="view_tit"[^>]*>([^<]+)</div>', html)
        if title_match:
            result.title = title_match.group(1).strip()
    
    # ====== category (사업유형) ======
    category_match = re.search(r'사업유형[^:]*:\s*<span[^>]*>([^<]+)</span>', html)
    if category_match:
        result.category = category_match.group(1).strip()
    if not result.category:
        category_match = re.search(r'<span[^>]*class="cate"[^>]*>([^<]+)</span>', html)
        if category_match:
            result.category = category_match.group(1).strip()
    
    # ====== posted_at (게시일) ======
    # 여러 패턴 시도
    posted_patterns = [
        r'게시일[^:]*:\s*<span[^>]*>(\d{4}[./]\d{2}[./]\d{2})',
        r'게시일[^:]*:\s*(\d{4}-\d{2}-\d{2})',
        r'<li[^>]*>게시일\s*:?\s*(\d{4}[./]\d{2}[./]\d{2})',
    ]
    for pattern in posted_patterns:
        posted_match = re.search(pattern, html)
        if posted_match:
            result.posted_at = parse_date(posted_match.group(1))
            break
    
    # ====== apply_start / apply_end (접수기간) ======
    date_patterns = [
        r'접수기간[^:]*:\s*<span[^>]*>(\d{4}[./]\d{2}[./]\d{2})\s*~\s*(\d{4}[./]\d{2}[./]\d{2})',
        r'접수기간[^:]*:\s*(\d{4}-\d{2}-\d{2})\s*~\s*(\d{4}-\d{2}-\d{2})',
        r'신청기간[^:]*:\s*<span[^>]*>(\d{4}[./]\d{2}[./]\d{2})\s*~\s*(\d{4}[./]\d{2}[./]\d{2})',
    ]
    for pattern in date_patterns:
        date_match = re.search(pattern, html)
        if date_match:
            result.apply_start = parse_date(date_match.group(1))
            result.apply_end = parse_date(date_match.group(2))
            break
    
    # ====== agency (주관기관/주최기관) ======
    agency_patterns = [
        r'(?:주최기관|주관기관|사업수행기관)[^:]*:\s*<span[^>]*>([^<]+)</span>',
        r'<span[^>]*class="institution"[^>]*>([^<]+)</span>',
    ]
    for pattern in agency_patterns:
        agency_match = re.search(pattern, html)
        if agency_match:
            result.agency = agency_match.group(1).strip()
            break
    
    # ====== ministry (소관부처) ======
    ministry_match = re.search(r'소관부처[^:]*:\s*<span[^>]*>([^<]+)</span>', html)
    if ministry_match:
        result.ministry = ministry_match.group(1).strip()
    
    # ====== apply_method (신청방법) ======
    method_match = re.search(r'(?:신청방법|접수방법)[^:]*:\s*<span[^>]*>([^<]+)</span>', html)
    if method_match:
        result.apply_method = method_match.group(1).strip()
    
    # ====== apply_site_url (신청사이트) ======
    site_match = re.search(r'<a[^>]*href="(https?://[^"]+)"[^>]*>(?:신청하기|접수처|바로가기)', html)
    if site_match:
        result.apply_site_url = site_match.group(1)
    
    # ====== contact (문의처) ======
    contact_match = re.search(r'문의처[^:]*:\s*<span[^>]*>([^<]+)</span>', html)
    if contact_match:
        result.contact = contact_match.group(1).strip()
    
    # ====== summary (본문/요약) ======
    # view_cont 또는 content 클래스 찾기
    summary_match = re.search(r'<div[^>]*class="(view_cont|content|view_box)"[^>]*>(.*?)</div>', html, re.DOTALL)
    if summary_match:
        content = summary_match.group(2)
        result.summary_html = content
        # HTML 태그 제거하여 텍스트 추출
        text = re.sub(r'<[^>]+>', '', content)
        text = re.sub(r'\s+', ' ', text).strip()
        result.summary_text = unescape(text)
    
    # ====== attachments ======
    attachments = []
    file_items = re.findall(r'<li[^>]*class="file"[^>]*>(.*?)</li>', html, re.DOTALL)
    for item in file_items:
        name_match = re.search(r'<a[^>]*>([^<]+)</a>', item)
        url_match = re.search(r'href="([^"]+)"', item)
        if name_match:
            attachments.append(AttachmentInfo(
                name=name_match.group(1).strip(),
                view_url=url_match.group(1) if url_match else "",
                download_url=url_match.group(1) if url_match else "",
                section_name="첨부파일"
            ))
    result.attachments = attachments
    
    # ====== source_origin_url ======
    result.source_origin_url = url
    
    print(f"[kstartup] HTML fallback done: title={result.title[:30] if result.title else ''}, posted={result.posted_at}, end={result.apply_end}", flush=True)
    return result


def collect_from_url(url: str, api_key: str = "") -> NoticeData:
    """
    K-Startup URL에서 공고 수집
    API 우선 + HTML 파싱 fallback
    """
    print(f"[kstartup] Collecting: {url}", flush=True)
    
    notice_id = extract_notice_id(url)
    if not notice_id:
        print(f"[kstartup] No notice ID in URL, using HTML fallback", flush=True)
        html_content = fetch_url(url)
        return parse_kstartup_html(html_content, url)
    
    # API 시도
    if api_key:
        api_data = fetch_kstartup_api(api_key, notice_id)
        if api_data:
            print(f"[kstartup] API mode success for {notice_id}", flush=True)
            result = api_response_to_noticedata(api_data, url, notice_id)
            
            # API에 부족한 필드가 있으면 HTML로 보충
            try:
                html_content = fetch_url(url)
                html_result = parse_kstartup_html(html_content, url)
                
                # HTML에서 더 많은 정보가 있으면 덮어쓰기
                if not result.title and html_result.title:
                    result.title = html_result.title
                if not result.category and html_result.category:
                    result.category = html_result.category
                if not result.posted_at and html_result.posted_at:
                    result.posted_at = html_result.posted_at
                if not result.apply_start and html_result.apply_start:
                    result.apply_start = html_result.apply_start
                if not result.apply_end and html_result.apply_end:
                    result.apply_end = html_result.apply_end
                if not result.agency and html_result.agency:
                    result.agency = html_result.agency
                if not result.apply_method and html_result.apply_method:
                    result.apply_method = html_result.apply_method
                if not result.apply_site_url and html_result.apply_site_url:
                    result.apply_site_url = html_result.apply_site_url
                if not result.contact and html_result.contact:
                    result.contact = html_result.contact
                if not result.summary_text and html_result.summary_text:
                    result.summary_text = html_result.summary_text
                if not result.summary_html and html_result.summary_html:
                    result.summary_html = html_result.summary_html
                if not result.attachments and html_result.attachments:
                    result.attachments = html_result.attachments
                    
                print(f"[kstartup] API + HTML supplement done", flush=True)
            except Exception as e:
                print(f"[kstartup] HTML supplement error: {e}", flush=True)
            
            return result
    
    # API 키 없거나 실패 시 HTML 파싱
    print("[kstartup] HTML fallback mode", flush=True)
    html_content = fetch_url(url)
    return parse_kstartup_html(html_content, url)


# 테스트
if __name__ == "__main__":
    test_urls = [
        "https://www.k-startup.go.kr/web/contents/bizpbanc-ongoing.do?schM=view&pbancSn=163048",
    ]

    for url in test_urls:
        print(f"\nFetching: {url}")
        try:
            data = collect_from_url(url, KSTARTUP_API_KEY)
            print(f"title: {data.title}")
            print(f"posted_at: {data.posted_at}")
            print(f"apply_end: {data.apply_end}")
            print(f"agency: {data.agency}")
            print(json.dumps(asdict(data), ensure_ascii=False, indent=2))
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()