#!/usr/bin/env python3
import sys
import json
import re
import sqlite3
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from adapter_bizinfo import fetch_url, parse_bizinfo_html
from init_db import get_connection


ROOT_DIR = Path(__file__).parent.parent
DATA_DIR = ROOT_DIR / "data"
NOTICES_DIR = DATA_DIR / "notices"
DB_PATH = DATA_DIR / "db" / "notices.sqlite3"


def make_slug(title: str, notice_id: str) -> str:
    if not title:
        title = notice_id
    slug = re.sub(r'[^\w가-힣]', '_', title)
    slug = re.sub(r'_+', '_', slug)
    slug = slug.strip('_')[:50]
    if not slug:
        slug = notice_id
    return slug


def make_storage_path(notice_data) -> Path:
    if notice_data.posted_at:
        try:
            posted_date = datetime.strptime(notice_data.posted_at, "%Y-%m-%d")
            year = posted_date.strftime("%Y")
            month = posted_date.strftime("%m")
        except:
            now = datetime.now()
            year = now.strftime("%Y")
            month = now.strftime("%m")
    else:
        now = datetime.now()
        year = now.strftime("%Y")
        month = now.strftime("%m")
    
    slug = make_slug(notice_data.title, notice_data.source_notice_id)
    
    return Path(year) / month / slug


def save_notice_files(full_html: str, notice_data, storage_path: Path) -> None:
    full_path = NOTICES_DIR / storage_path
    full_path.mkdir(parents=True, exist_ok=True)
    
    meta = {
        "source_site": notice_data.source_site,
        "source_url": notice_data.source_url,
        "source_notice_id": notice_data.source_notice_id,
        "title": notice_data.title,
        "category": notice_data.category,
        "posted_at": notice_data.posted_at,
        "apply_start": notice_data.apply_start,
        "apply_end": notice_data.apply_end,
        "ministry": notice_data.ministry,
        "agency": notice_data.agency,
        "apply_method": notice_data.apply_method,
        "apply_site_url": notice_data.apply_site_url,
        "source_origin_url": notice_data.source_origin_url,
        "contact": notice_data.contact,
        "summary_html": notice_data.summary_html,
        "summary_text": notice_data.summary_text,
    }
    
    with open(full_path / "meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    
    with open(full_path / "source.html", "w", encoding="utf-8") as f:
        f.write(full_html)
    
    attachments_info = []
    for i, att in enumerate(notice_data.attachments):
        attachments_info.append({
            "name": att.name,
            "view_url": att.view_url,
            "download_url": att.download_url,
            "section_name": att.section_name,
            "sort_order": i
        })
    
    if attachments_info:
        with open(full_path / "attachments.json", "w", encoding="utf-8") as f:
            json.dump(attachments_info, f, ensure_ascii=False, indent=2)


def upsert_notice(conn: sqlite3.Connection, notice_data, storage_path: Path) -> int:
    cursor = conn.cursor()
    
    existing = None
    if notice_data.source_notice_id:
        cursor.execute("SELECT id FROM notices WHERE source_notice_id = ?", (notice_data.source_notice_id,))
        existing = cursor.fetchone()
    
    if not existing:
        cursor.execute("SELECT id FROM notices WHERE source_url = ?", (notice_data.source_url,))
        existing = cursor.fetchone()
    
    now = datetime.now().isoformat()
    
    if existing:
        notice_id = existing[0]
        cursor.execute("""
            UPDATE notices SET
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
            notice_data.source_notice_id,
            notice_data.title,
            notice_data.category,
            notice_data.posted_at,
            notice_data.apply_start,
            notice_data.apply_end,
            notice_data.ministry,
            notice_data.agency,
            notice_data.apply_method,
            notice_data.apply_site_url,
            notice_data.source_origin_url,
            notice_data.contact,
            notice_data.summary_html,
            notice_data.summary_text,
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
            notice_data.source_site,
            notice_data.source_url,
            notice_data.source_notice_id,
            notice_data.title,
            notice_data.category,
            notice_data.posted_at,
            notice_data.apply_start,
            notice_data.apply_end,
            notice_data.ministry,
            notice_data.agency,
            notice_data.apply_method,
            notice_data.apply_site_url,
            notice_data.source_origin_url,
            notice_data.contact,
            notice_data.summary_html,
            notice_data.summary_text,
            str(storage_path),
            now,
            now
        ))
        notice_id = cursor.lastrowid
    
    cursor.execute("DELETE FROM attachments WHERE notice_id = ?", (notice_id,))
    
    for i, att in enumerate(notice_data.attachments):
        cursor.execute("""
            INSERT INTO attachments (
                notice_id, section_name, name, view_url, download_url, sort_order
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            notice_id,
            att.section_name,
            att.name,
            att.view_url,
            att.download_url,
            i
        ))
    
    conn.commit()
    return notice_id


def collect(url: str, auto_render: bool = True) -> int:
    print(f"Collecting: {url}")
    
    from adapter_bizinfo import fetch_url
    full_html = fetch_url(url)
    notice_data = parse_bizinfo_html(full_html, url)
    
    print(f"Title: {notice_data.title}")
    
    storage_path = make_storage_path(notice_data)
    print(f"Storage path: {storage_path}")
    
    save_notice_files(full_html, notice_data, storage_path)
    
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = get_connection(DB_PATH)
    notice_id = upsert_notice(conn, notice_data, storage_path)
    conn.close()
    
    print(f"Saved to DB with id: {notice_id}")
    
    if auto_render:
        from render_dashboard import render_all
        render_all()
    
    return notice_id


def main():
    if len(sys.argv) < 2:
        print("Usage: python collect_notice.py <bizinfo_url>")
        print("Example:")
        print("  python collect_notice.py \"https://www.bizinfo.go.kr/sii/siia/selectSIIA200Detail.do?pblancId=PBLN_000000000119288\"")
        sys.exit(1)
    
    url = sys.argv[1]
    collect(url)


if __name__ == "__main__":
    main()