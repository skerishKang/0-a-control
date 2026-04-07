#!/usr/bin/env python3
"""
공통 유틸리티 함수들
"""

import re
import html
from pathlib import Path


# 경로 설정
ROOT_DIR = Path(__file__).parent.parent.parent
DATA_DIR = ROOT_DIR / "data"
DB_PATH = DATA_DIR / "db" / "notices.sqlite3"


def escape_html(text):
    """HTML 이스케이프"""
    if not text:
        return ""
    return (text
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;"))


def parse_date(raw):
    """날짜 파싱"""
    if not raw:
        return ""
    cleaned = re.sub(r'[.\-\s]', '', raw.strip())
    if re.match(r'^\d{8}$', cleaned):
        return f"{cleaned[:4]}-{cleaned[4:6]}-{cleaned[6:8]}"
    return raw.strip()


def parse_date_range(text):
    """날짜 범위 파싱"""
    match = re.search(r'(\d{4}[./]\d{2}[./]\d{2})\s*[~~]\s*(\d{4}[./]\d{2}[./]\d{2})', text)
    if match:
        return parse_date(match.group(1)), parse_date(match.group(2))
    return "", ""


def extract_notice_id(url):
    """공고 ID 추출"""
    match = re.search(r'pblancId=([^&]+)', url)
    if match:
        return match.group(1)
    return ""
