#!/usr/bin/env python3
"""
공고 데이터베이스 Repository
"""

import sqlite3
from pathlib import Path
from typing import List, Dict, Optional, Any


# 경로 설정
ROOT_DIR = Path(__file__).parent.parent.parent
DATA_DIR = ROOT_DIR / "data"
DB_PATH = DATA_DIR / "db" / "notices.sqlite3"


def get_connection() -> sqlite3.Connection:
    """DB 연결 반환"""
    return sqlite3.connect(DB_PATH)


def fetch_notices() -> List[Dict[str, Any]]:
    """모든 공고 조회"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT
            id, source_site, source_url, source_notice_id, title, category,
            posted_at, apply_start, apply_end, ministry, agency,
            apply_method, apply_site_url, source_origin_url, contact,
            summary_text, storage_path, status, manual_note, one_line_summary,
            ai_fit_score, ai_summary, ai_strengths, ai_risks, ai_next_actions, ai_model, ai_updated_at,
            ai_mode, ai_provider, ai_fallback_used,
            created_at, updated_at
        FROM notices
        ORDER BY
            CASE WHEN apply_end IS NULL OR apply_end = '' THEN 1 ELSE 0 END,
            apply_end ASC, posted_at DESC
    """)
    
    columns = [desc[0] for desc in cursor.description]
    notices = []
    for row in cursor.fetchall():
        notices.append(dict(zip(columns, row)))
    
    # 첨부파일 조회
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


def fetch_notice_by_id(notice_id: int) -> Optional[Dict[str, Any]]:
    """ID로 공고 조회"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT
            id, source_site, source_url, source_notice_id, title, category,
            posted_at, apply_start, apply_end, ministry, agency,
            apply_method, apply_site_url, source_origin_url, contact,
            summary_text, storage_path, status, manual_note, one_line_summary,
            ai_fit_score, ai_summary, ai_strengths, ai_risks, ai_next_actions, ai_model, ai_updated_at,
            ai_mode, ai_provider, ai_fallback_used,
            created_at, updated_at
        FROM notices WHERE id = ?
    """, (notice_id,))
    
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None
    
    columns = [desc[0] for desc in cursor.description]
    notice = dict(zip(columns, row))
    
    # 첨부파일 조회
    cursor.execute("""
        SELECT name, view_url, download_url, section_name
        FROM attachments
        WHERE notice_id = ?
        ORDER BY sort_order
    """, (notice_id,))
    att_columns = ['name', 'view_url', 'download_url', 'section_name']
    notice['attachments'] = [dict(zip(att_columns, row)) for row in cursor.fetchall()]
    
    conn.close()
    return notice


def fetch_notice_by_source_id(source_notice_id: str) -> Optional[Dict[str, Any]]:
    """source_notice_id로 공고 조회"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT
            id, source_site, source_url, source_notice_id, title, category,
            posted_at, apply_start, apply_end, ministry, agency,
            apply_method, apply_site_url, source_origin_url, contact,
            summary_text, storage_path, status, manual_note, one_line_summary,
            ai_fit_score, ai_summary, ai_strengths, ai_risks, ai_next_actions, ai_model, ai_updated_at,
            ai_mode, ai_provider, ai_fallback_used,
            created_at, updated_at
        FROM notices WHERE source_notice_id = ?
    """, (source_notice_id,))
    
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None
    
    columns = [desc[0] for desc in cursor.description]
    notice = dict(zip(columns, row))
    
    conn.close()
    return notice


def update_notice(
    notice_id: Optional[str] = None,
    id: Optional[int] = None,
    status: Optional[str] = None,
    note: Optional[str] = None,
    summary: Optional[str] = None
) -> Optional[int]:
    """공고 정보 업데이트"""
    conn = get_connection()
    cursor = conn.cursor()
    
    if id is not None:
        target_id = id
    elif notice_id:
        cursor.execute("SELECT id FROM notices WHERE source_notice_id = ?", (notice_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return None
        target_id = row[0]
    else:
        conn.close()
        return None
    
    updates = []
    params = []
    
    if status is not None:
        updates.append("status = ?")
        params.append(status)
    if note is not None:
        updates.append("manual_note = ?")
        params.append(note)
    if summary is not None:
        updates.append("one_line_summary = ?")
        params.append(summary)
    
    if not updates:
        conn.close()
        return None
    
    from datetime import datetime
    updates.append("updated_at = ?")
    params.append(datetime.now().isoformat())
    params.append(target_id)
    
    sql = f"UPDATE notices SET {', '.join(updates)} WHERE id = ?"
    cursor.execute(sql, params)
    conn.commit()
    conn.close()
    
    return target_id


def delete_notice(notice_id: int) -> bool:
    """공고 삭제 (DB + 로컬 폴더)"""
    import shutil
    from pathlib import Path
    
    # ROOT_DIR 경로 (notice_repo.py 기준)
    ROOT_DIR = Path(__file__).parent.parent.parent
    DATA_DIR = ROOT_DIR / "data"
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. storage_path 조회
    cursor.execute("SELECT storage_path FROM notices WHERE id = ?", (notice_id,))
    row = cursor.fetchone()
    storage_path = row[0] if row else None
    
    # 2. DB 삭제
    cursor.execute("DELETE FROM attachments WHERE notice_id = ?", (notice_id,))
    cursor.execute("DELETE FROM notices WHERE id = ?", (notice_id,))
    
    conn.commit()
    conn.close()
    
    # 3. 로컬 폴더 삭제 (있는 경우만)
    if storage_path:
        folder_path = DATA_DIR / "notices" / storage_path
        if folder_path.exists() and folder_path.is_dir():
            try:
                shutil.rmtree(folder_path)
            except Exception as e:
                print(f"Warning: Failed to delete folder {folder_path}: {e}")
    
    return True


def update_ai_analysis(
    notice_id: str,
    ai_fit_score: Optional[float] = None,
    ai_summary: Optional[str] = None,
    ai_strengths: Optional[str] = None,
    ai_risks: Optional[str] = None,
    ai_next_actions: Optional[str] = None,
    ai_model: Optional[str] = None,
    ai_raw_json: Optional[str] = None,
    ai_mode: Optional[str] = None,
    ai_provider: Optional[str] = None,
    ai_fallback_used: Optional[int] = None
) -> bool:
    """AI 분석 결과 저장"""
    conn = get_connection()
    cursor = conn.cursor()
    
    from datetime import datetime
    cursor.execute("""
        UPDATE notices SET
            ai_fit_score = ?,
            ai_summary = ?,
            ai_strengths = ?,
            ai_risks = ?,
            ai_next_actions = ?,
            ai_model = ?,
            ai_raw_json = ?,
            ai_mode = ?,
            ai_provider = ?,
            ai_fallback_used = ?,
            ai_updated_at = ?
        WHERE source_notice_id = ?
    """, (
        ai_fit_score,
        ai_summary,
        ai_strengths,
        ai_risks,
        ai_next_actions,
        ai_model,
        ai_raw_json,
        ai_mode,
        ai_provider,
        ai_fallback_used or 0,
        datetime.now().isoformat(),
        notice_id
    ))
    
    conn.commit()
    conn.close()
    
    return cursor.rowcount > 0
