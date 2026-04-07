#!/usr/bin/env python3
import sys
import json
import sqlite3
from pathlib import Path
from datetime import datetime

ROOT_DIR = Path(__file__).parent.parent
DATA_DIR = ROOT_DIR / "data"
DB_PATH = DATA_DIR / "db" / "notices.sqlite3"


def update_ai_analysis(
    notice_id: str = None,
    id: int = None,
    fit_score: float = None,
    summary: str = None,
    strengths: str = None,
    risks: str = None,
    next_actions: str = None,
    model: str = None,
    raw_json: str = None
) -> int:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if id is not None:
        target_id = id
    elif notice_id:
        cursor.execute("SELECT id FROM notices WHERE source_notice_id = ?", (notice_id,))
        row = cursor.fetchone()
        if not row:
            print(f"Error: Notice with source_notice_id '{notice_id}' not found")
            conn.close()
            return -1
        target_id = row[0]
    else:
        print("Error: Must provide --notice-id or --id")
        conn.close()
        return -1

    updates = []
    params = []

    if fit_score is not None:
        updates.append("ai_fit_score = ?")
        params.append(fit_score)
    if summary is not None:
        updates.append("ai_summary = ?")
        params.append(summary)
    if strengths is not None:
        updates.append("ai_strengths = ?")
        params.append(strengths)
    if risks is not None:
        updates.append("ai_risks = ?")
        params.append(risks)
    if next_actions is not None:
        updates.append("ai_next_actions = ?")
        params.append(next_actions)
    if model is not None:
        updates.append("ai_model = ?")
        params.append(model)
    if raw_json is not None:
        updates.append("ai_raw_json = ?")
        params.append(raw_json)

    if not updates:
        print("Error: No AI analysis fields to update")
        conn.close()
        return -1

    updates.append("ai_updated_at = ?")
    params.append(datetime.now().isoformat())
    params.append(target_id)

    sql = f"UPDATE notices SET {', '.join(updates)} WHERE id = ?"
    cursor.execute(sql, params)
    conn.commit()

    cursor.execute("SELECT id, source_notice_id, ai_fit_score, ai_summary, ai_model, ai_updated_at FROM notices WHERE id = ?", (target_id,))
    row = cursor.fetchone()
    print(f"Updated AI analysis for notice {target_id}:")
    print(f"  source_notice_id: {row[1]}")
    print(f"  ai_fit_score: {row[2]}")
    print(f"  ai_summary: {row[3]}")
    print(f"  ai_model: {row[4]}")
    print(f"  ai_updated_at: {row[5]}")

    conn.close()
    return target_id


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Update AI analysis for a notice")
    parser.add_argument("--notice-id", type=str, help="Source notice ID (e.g., PBLN_000000000119288)")
    parser.add_argument("--id", type=int, help="Internal notice ID")
    parser.add_argument("--fit-score", type=float, help="AI fit score (0-10)")
    parser.add_argument("--summary", type=str, help="AI summary text")
    parser.add_argument("--strengths", type=str, help="AI strengths analysis")
    parser.add_argument("--risks", type=str, help="AI risks analysis")
    parser.add_argument("--next-actions", type=str, help="AI recommended next actions")
    parser.add_argument("--model", type=str, help="AI model name")
    parser.add_argument("--raw-json", type=str, help="Raw AI analysis JSON")

    args = parser.parse_args()

    if not args.notice_id and not args.id:
        print("Usage:")
        print("  python update_ai_analysis.py --notice-id PBLN_000000000119288 --fit-score 8.5 --summary '...'")
        print("  python update_ai_analysis.py --notice-id PBLN_000000000119288 --fit-score 8.5 --summary 'SW기업 중심 컨소시엄형 XaaS 지원 과제' --strengths 'SW 중심 구조, 지원금 규모 큼, 클라우드/데이터 활용 적합' --risks '수요기업 확보 필요, 컨소시엄 구성 난이도' --next-actions '수요기업 후보 정리, 역할 분담안 초안 작성' --model 'free-model'")
        sys.exit(1)

    update_ai_analysis(
        notice_id=args.notice_id,
        id=args.id,
        fit_score=args.fit_score,
        summary=args.summary,
        strengths=args.strengths,
        risks=args.risks,
        next_actions=args.next_actions,
        model=args.model,
        raw_json=args.raw_json
    )


if __name__ == "__main__":
    main()