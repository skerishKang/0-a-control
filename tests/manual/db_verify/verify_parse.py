import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent))

from inbox_parse import parse_time_range, resolve_source_aliases
from datetime import datetime

print("--- [검증] 시간 범위 파서 ---")
# ... 나머지 테스트 코드

print("--- [검증] 시간 범위 파서 ---")
test_times = ["6h", "1d", "today-morning", "09:00-11:00", "2026-03-09 09:00-11:00"]
for t in test_times:
    try:
        start, end = parse_time_range(t)
        print(f"'{t}' -> {start} ~ {end}")
    except ValueError as e:
        print(f"'{t}' -> 에러: {e}")

print("\n--- [검증] 소스 별칭 해석기 ---")
test_aliases = ["self", "강혜림", "핵심4개", "뉴스", "unknown"]
resolved = resolve_source_aliases(test_aliases)
print(f"{test_aliases} -> {resolved}")

# 검증 결과 확인
assert "self_chat" in resolve_source_aliases(["self"])
assert "kang_hyerim_chat" in resolve_source_aliases(["강혜림"])
assert "local_chat" in resolve_source_aliases(["핵심4개"])
print("\n[검증 결과] 모든 테스트 통과")