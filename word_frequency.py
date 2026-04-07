#!/usr/bin/env python3
"""CLI 기반 단어 빈도 분석기"""

import argparse
import re
import sys
from collections import Counter
from pathlib import Path


STOPWORDS = {"a", "an", "the", "is", "in", "of", "to", "and", "or", "it"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="텍스트 파일의 단어 빈도를 분석합니다."
    )
    parser.add_argument(
        "file",
        type=str,
        help="분석할 텍스트 파일 경로",
    )
    parser.add_argument(
        "-n", "--top",
        type=int,
        default=10,
        help="출력할 상위 단어 개수 (기본값: 10)",
    )
    parser.add_argument(
        "--no-stopwords",
        action="store_true",
        help="불용어를 제거하지 않음",
    )
    parser.add_argument(
        "--min-length",
        type=int,
        default=1,
        help="최소 단어 길이 (기본값: 1)",
    )
    return parser.parse_args()


def extract_words(text: str, stopwords: set[str] | None, min_length: int) -> list[str]:
    words = re.findall(r"[a-zA-Z0-9']+", text.lower())
    filtered = []
    for word in words:
        word = word.strip("'")
        if len(word) < min_length:
            continue
        if stopwords and word in stopwords:
            continue
        filtered.append(word)
    return filtered


def print_report(counter: Counter, total_words: int) -> None:
    if not counter:
        print("\n분석할 단어가 없습니다.")
        return

    max_count = counter.most_common(1)[0][1]
    bar_max_width = 30

    print(f"\n{'순위':<6} {'단어':<20} {'횟수':>6}  {'분포'}")
    print("-" * 50)

    for rank, (word, count) in enumerate(counter.most_common(), start=1):
        bar_width = int((count / max_count) * bar_max_width) if max_count else 0
        bar = "█" * bar_width
        pct = (count / total_words * 100) if total_words else 0
        print(f"{rank:<6} {word:<20} {count:>6}  {bar} ({pct:.1f}%)")

    print(f"\n총 단어 수: {total_words}")
    print(f"고유 단어 수: {len(counter)}")


def main() -> None:
    args = parse_args()

    filepath = Path(args.file)

    if not filepath.exists():
        print(f"오류: 파일 '{filepath}'을(를) 찾을 수 없습니다.", file=sys.stderr)
        sys.exit(1)

    if not filepath.is_file():
        print(f"오류: '{filepath}'은(는) 파일이 아닙니다.", file=sys.stderr)
        sys.exit(1)

    try:
        text = filepath.read_text(encoding="utf-8")
    except PermissionError:
        print(f"오류: 파일 '{filepath}'에 대한 읽기 권한이 없습니다.", file=sys.stderr)
        sys.exit(1)
    except UnicodeDecodeError:
        print(f"오류: 파일 '{filepath}'을(를) UTF-8로 읽을 수 없습니다.", file=sys.stderr)
        sys.exit(1)

    if not text.strip():
        print(f"오류: 파일 '{filepath}'이(가) 비어 있습니다.", file=sys.stderr)
        sys.exit(1)

    stopwords = None if args.no_stopwords else STOPWORDS
    words = extract_words(text, stopwords, args.min_length)

    if not words:
        print("\n필터링 후 분석할 단어가 없습니다.")
        sys.exit(0)

    counter = Counter(words)
    top_n = counter.most_common(args.top)
    top_counter = Counter(dict(top_n))

    print(f"\n📊 단어 빈도 분석 결과: {filepath.name}")
    print_report(top_counter, len(words))


if __name__ == "__main__":
    main()
