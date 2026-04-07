#!/usr/bin/env python3
"""
Bizinfo (기업마당) 어댑터
API 우선 + HTML 파싱 fallback
표준 라이브러리만 사용
"""

import re
import json
import urllib.request
import ssl
import urllib.parse
from html import unescape
from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from dataclasses import dataclass, asdict, field
from pathlib import Path
import sys

# 설정 파일에서 API 키 로드 (settings 함수 사용)
sys.path.insert(0, str(Path(__file__).parent))
try:
    import settings
    BIZINFO_API_KEY = settings.get_bizinfo_api_key() or ""
except ImportError:
    BIZINFO_API_KEY = ''


@dataclass
class AttachmentInfo:
    name: str = ""
    view_url: str = ""
    download_url: str = ""
    section_name: str = "첨부파일"


@dataclass
class NoticeData:
    source_site: str = "bizinfo"
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
    collection_mode: str = "html"  # "api" or "html"


def extract_notice_id(url: str) -> str:
    """bizinfo URL에서 공고 ID 추출"""
    match = re.search(r'pblancId=([^&]+)', url)
    if match:
        return match.group(1)
    return ""


def parse_date(raw: str) -> str:
    """날짜 문자열을 YYYY-MM-DD 형식으로 변환"""
    if not raw:
        return ""
    cleaned = re.sub(r'[.\-\s]', '', raw.strip())
    if re.match(r'^\d{8}$', cleaned):
        return f"{cleaned[:4]}-{cleaned[4:6]}-{cleaned[6:8]}"
    return raw.strip()


def parse_date_range(text: str) -> tuple:
    """신청기간 파싱"""
    match = re.search(r'(\d{4}[./]\d{2}[./]\d{2})\s*[~~]\s*(\d{4}[./]\d{2}[./]\d{2})', text)
    if match:
        return parse_date(match.group(1)), parse_date(match.group(2))
    return "", ""


def fetch_url(url: str, timeout: int = 30) -> str:
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


def fetch_bizinfo_api(notice_id: str, api_key: str) -> Optional[Dict[str, Any]]:
    """
    기업마당 RSS API에서 공고 정보 조회
    다양한 응답 구조를 유연하게 처리
    """
    if not api_key:
        return None
    
    # 기업마당 지원사업 API
    base_url = "https://www.bizinfo.go.kr/uss/rss/bizinfoApi.do"
    
    # 넉넉하게 100개 조회
    params = {
        'crtfcKey': api_key,
        'dataType': 'json',
        'searchCnt': '100',
    }
    
    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    
    try:
        print(f"[bizinfo] Fetching API: {url[:80]}...", flush=True)
        html_content = fetch_url(url, timeout=20)
        
        # JSON 파싱
        try:
            data = json.loads(html_content)
        except json.JSONDecodeError:
            print(f"[bizinfo] API JSON parse failed, using HTML fallback", flush=True)
            return None
        
        # 다양한 응답 구조 처리
        items = None
        
        # Case 1: data['jsonArray']['item'] - list
        if isinstance(data, dict):
            json_array = data.get('jsonArray')
            if json_array:
                if isinstance(json_array, dict):
                    items = json_array.get('item')
                elif isinstance(json_array, list):
                    items = json_array
        
        # Case 2: data['item'] - direct list
        if items is None and isinstance(data, dict):
            items = data.get('item')
        
        # Case 3: data is a list
        if items is None and isinstance(data, list):
            items = data
        
        # items가 없거나 빈 리스트
        if not items:
            print(f"[bizinfo] No items in API response", flush=True)
            return None
        
        # items가 단일 dict면 리스트로 변환
        if isinstance(items, dict):
            items = [items]
        
        # 해당 notice_id 찾기
        if isinstance(items, list):
            for item in items:
                if not isinstance(item, dict):
                    continue
                # pblancId 또는 seq에서 찾기
                item_id = item.get('pblancId') or item.get('seq') or ''
                if notice_id in item_id:
                    print(f"[bizinfo] Found item via API: {item_id}", flush=True)
                    return item
        
        print(f"[bizinfo] Notice ID {notice_id} not found in API response", flush=True)
        return None
        
    except Exception as e:
        print(f"[bizinfo] API error: {e}, using HTML fallback", flush=True)
        return None


def api_response_to_noticedata(api_item: Dict[str, Any], url: str, notice_id: str) -> NoticeData:
    """API 응답을 NoticeData로 변환"""
    result = NoticeData(source_url=url)
    result.source_notice_id = notice_id
    result.collection_mode = "api"
    
    # API 응답 필드 매핑 (여러 가능한 필드명 시도)
    result.title = api_item.get('pblancNm') or api_item.get('title') or ''
    
    # 카테고리
    result.category = api_item.get('pldirSportRealmLclasCodeNm') or api_item.get('lcategory') or ''
    
    # 등록일 - 여러 필드명 시도
    creat_pnttm = api_item.get('creatPnttm') or api_item.get('pubDate') or ''
    if creat_pnttm:
        # "2022-09-02 15:38:29" 형식에서 날짜만 추출
        date_match = re.match(r'(\d{4}-\d{2}-\d{2})', creat_pnttm)
        if date_match:
            result.posted_at = date_match.group(1)
        else:
            result.posted_at = parse_date(creat_pnttm[:8] if len(creat_pnttm) >= 8 else creat_pnttm)
    
    # 신청기간 - reqstDt 또는 reqstBeginEndDe
    reqst_period = api_item.get('reqstDt') or api_item.get('reqstBeginEndDe') or ''
    if reqst_period:
        result.apply_start, result.apply_end = parse_date_range(reqst_period)
    
    # 소관기관
    result.ministry = api_item.get('jrsdInsttNm') or api_item.get('author') or ''
    
    # 수행기관
    result.agency = api_item.get('excInsttNm') or ''
    
    # 사업개요
    result.summary_text = api_item.get('bsnsSumryCn') or api_item.get('description') or ''
    # description이 HTML 태그 포함 시 제거
    if result.summary_text:
        result.summary_text = re.sub(r'<[^>]+>', '', result.summary_text).strip()
    result.summary_html = f"<div>{result.summary_text}</div>"
    
    # 신청방법
    result.apply_method = api_item.get('reqstMthPapersCn') or ''
    
    # 신청사이트
    result.apply_site_url = api_item.get('rceptEngnHmpgUrl') or ''
    
    # 문의처
    result.contact = api_item.get('refrncNm') or ''
    
    # 공고URL
    result.source_origin_url = api_item.get('pblancUrl') or api_item.get('link') or url
    
    print(f"[bizinfo] API parse success: title={result.title[:30] if result.title else ''}", flush=True)
    return result


def parse_bizinfo_html(html: str, url: str) -> NoticeData:
    """bizinfo HTML 파싱"""
    result = NoticeData(source_url=url)
    result.source_notice_id = extract_notice_id(url)
    result.collection_mode = "html"
    
    print(f"[bizinfo] HTML fallback parsing", flush=True)
    
    # title - meta 태그
    title_match = re.search(r'<meta[^>]+name="title"[^>]+content="([^"]+)"', html)
    if title_match:
        result.title = title_match.group(1)
    if not result.title:
        title_match = re.search(r'<meta[^>]+content="([^"]+)"[^>]+name="title"', html)
        if title_match:
            result.title = title_match.group(1)
    
    # category
    category_match = re.search(r'<div[^>]*class="category"[^>]*>.*?<span[^>]*>([^<]+)</span>', html, re.DOTALL)
    if category_match:
        result.category = category_match.group(1).strip()
    if not result.category:
        category_match = re.search(r'<div[^>]+class="cate"[^>]*>([^<]+)<', html)
        if category_match:
            cat = category_match.group(1).strip()
            if cat.startswith('#'):
                result.category = cat[1:]
            else:
                result.category = cat
    
    # posted_at - top_info 영역
    posted_match = re.search(r'<div class="top_info"[^>]*>.*?<li[^>]*>\s*(\d{4}[./]\d{2}[./]\d{2})\s*</li>', html, re.DOTALL)
    if posted_match:
        result.posted_at = parse_date(posted_match.group(1))
    
    # origin_url
    origin_match = re.search(r'<a[^>]*href="([^"]+)"[^>]*id="barogagi"', html)
    if origin_match:
        result.source_origin_url = origin_match.group(1)
    
    # view_cont 파싱 (상세 정보)
    view_cont_match = re.search(r'<div class="view_cont"[^>]*>(.*?)</div>\s*<div class="tag_list"', html, re.DOTALL)
    if view_cont_match:
        content = view_cont_match.group(1)
        li_items = re.findall(r'<li>(.*?)</li>', content, re.DOTALL)
        
        for li in li_items:
            label_match = re.search(r'<span class="s_title">([^<]+)</span>', li)
            value_match = re.search(r'<div class="txt">(.*?)</div>', li, re.DOTALL)
            
            if label_match and value_match:
                label = label_match.group(1).strip()
                value_html = value_match.group(1)
                value_text = re.sub(r'<[^>]+>', '', value_html).strip()
                value_text = re.sub(r'\s+', ' ', value_text).strip()
                
                if "소관부처" in label or "지자체" in label:
                    result.ministry = value_text
                elif "사업수행기관" in label or "기관" in label:
                    result.agency = value_text
                elif "신청기간" in label or "접수기간" in label:
                    result.apply_start, result.apply_end = parse_date_range(value_text)
                elif "사업개요" in label:
                    result.summary_html = value_html
                    result.summary_text = unescape(value_text)
                elif "사업신청 방법" in label or "신청방법" in label:
                    result.apply_method = value_text
                elif "사업신청 사이트" in label or "접수처" in label:
                    link_match = re.search(r'href="([^"]+)"', value_html)
                    if link_match:
                        result.apply_site_url = link_match.group(1)
                        if not result.apply_site_url.startswith('http'):
                            result.apply_site_url = "https://www.bizinfo.go.kr" + result.apply_site_url
                    else:
                        result.apply_site_url = value_text
                elif "문의처" in label:
                    result.contact = value_text
    
    # 첨부파일 파싱
    result.attachments = parse_attachments_from_html(html)
    
    print(f"[bizinfo] HTML fallback done: title={result.title[:30] if result.title else ''}", flush=True)
    return result


def parse_attachments_from_html(html: str) -> list:
    """HTML에서 첨부파일 파싱"""
    attachments = []
    base_url = "https://www.bizinfo.go.kr"
    
    attached_list_match = re.search(r'<div[^>]*class="attached_file_list"[^>]*>(.*?)</div>\s*</div>', html, re.DOTALL)
    if not attached_list_match:
        return attachments
    
    content = attached_list_match.group(1)
    li_items = re.findall(r'<li>(.*?)</li>', content, re.DOTALL)
    
    for li in li_items:
        file_name_match = re.search(r'<div class="file_name"[^>]*>([^<]+)</div>', li)
        name = file_name_match.group(1).strip() if file_name_match else ""
        
        view_url = ""
        view_match = re.search(r"onclick=\"fileBlank\(\s*'([^']+)'\s*\+\s*'/'\s*\+\s*'([^']+)'", li)
        if view_match:
            path = view_match.group(1).rstrip('/')
            filename = view_match.group(2)
            view_url = f"{base_url}{path}/{filename}"
        
        download_url = ""
        download_match = re.search(r'href="(/cmm/fms/fileDown.do\?[^"]+)"', li)
        if download_match:
            download_url = base_url + download_match.group(1)
        
        if name:
            attachments.append(AttachmentInfo(
                name=name,
                view_url=view_url,
                download_url=download_url,
                section_name="첨부파일"
            ))
    
    return attachments


def collect_from_url(url: str, api_key: str = "") -> NoticeData:
    """
    bizinfo URL에서 공고 수집
    API 우선 + HTML fallback
    """
    notice_id = extract_notice_id(url)
    if not notice_id:
        print("[bizinfo] No notice ID in URL, using HTML fallback", flush=True)
        html_content = fetch_url(url)
        return parse_bizinfo_html(html_content, url)
    
    # API 키가 있으면 API 시도
    if api_key:
        api_item = fetch_bizinfo_api(notice_id, api_key)
        if api_item:
            print(f"[bizinfo] API mode success for {notice_id}", flush=True)
            result = api_response_to_noticedata(api_item, url, notice_id)
            
            # API에 부족한 필드가 있으면 HTML로 보충
            try:
                html_content = fetch_url(url)
                html_result = parse_bizinfo_html(html_content, url)
                
                # HTML에서 더 많은 정보가 있으면 덮어쓰기
                if not result.title and html_result.title:
                    result.title = html_result.title
                if not result.category and html_result.category:
                    result.category = html_result.category
                if not result.posted_at and html_result.posted_at:
                    result.posted_at = html_result.posted_at
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
                    
                print(f"[bizinfo] API + HTML supplement done", flush=True)
            except Exception as e:
                print(f"[bizinfo] HTML supplement error: {e}", flush=True)
            
            return result
    
    # API 키 없거나 API 실패 시 HTML 파싱
    print("[bizinfo] HTML fallback mode", flush=True)
    html_content = fetch_url(url)
    return parse_bizinfo_html(html_content, url)


# 테스트
if __name__ == "__main__":
    test_urls = [
        "https://www.bizinfo.go.kr/sii/siia/selectSIIA200Detail.do?pblancId=PBLN_000000000119288",
    ]

    for url in test_urls:
        print(f"\nFetching: {url}")
        try:
            data = collect_from_url(url, BIZINFO_API_KEY)
            print(f"Collection mode: {data.collection_mode}")
            print(f"title: {data.title}")
            print(f"posted_at: {data.posted_at}")
            print(f"apply_end: {data.apply_end}")
            print(json.dumps(asdict(data), ensure_ascii=False, indent=2))
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()