# Session Recovery Operator Prompts

## Recovery 읽기 순서

모든 프롬프트는 다음 순서를 따릅니다:

1. **current urgent state** 확인
2. **관련 sessions archive** 확인 (full archive)
3. **sessions_html**로 빠른 탐색 (필요 시)
4. **raw transcript / DB source_records** 확인 (부족할 때)
5. **summary/current quest**로 압축 (마지막 정리)

## Default Prompt
```text
이전 codex 세션 복원해줘.

읽기 순서:
1. 먼저 sessions/ 폴더에서 관련 세션 archive를 찾아 전체 대화를 읽어줘
2. sessions_html/에서 빠르게 탐색이 필요하면 사용해줘
3. 그 다음 current state / summary를 보고 압축해줘

board-v2, 0-a-control 스킬, 메가존, 아파트 순으로 정리하고,
각 주제마다 지금까지 한 것 / 현재 상태 / 남은 것 / 다음 할 일을 써줘.
마지막에는 지금 가장 먼저 다시 시작할 주제 1개를 골라줘.
```

## If Continuity Is Weak
```text
codex 세션 읽어서 이어갈 일 정리해줘.

먼저 sessions/ 폴더의 전체 archive를 읽고,
부족하면 DB source_records나 raw transcript를 추가로 확인해줘.

복원이 충분한지 먼저 판단하고,
부족하면 어떤 주제만 추가 handoff가 필요한지 따로 표시해줘.
```

## board-v2 Only
```text
board-v2 관련 codex 세션을 복원해줘.

sessions/ 폴더에서 board-v2 관련 세션을 찾아 전체 대화를 먼저 읽어줘.
그 다음 완료 탭, overdue quick action, 날짜/시간 표시, 모듈화 상태 중심으로 정리해줘.
```

## Megazone Only
```text
메가존 관련 codex 세션을 복원해줘.

sessions/ 폴더에서 메가존 관련 세션을 찾아 전체 대화를 먼저 읽어줘.
그 다음 사건정리 / 대응문서 / 남은 실무 조치 중심으로 정리해줘.
```

## Apartment Only
```text
아파트 관련 codex 세션을 복원해줘.

sessions/ 폴더에서 아파트 관련 세션을 찾아 전체 대화를 먼저 읽어줘.
그 다음 dashboard 검산 상태, 숫자 불일치, 추가로 필요한 원문 자료 중심으로 정리해줘.
```

## Skill/Infra Only
```text
0-a-control 스킬 관련 codex 세션을 복원해줘.

sessions/ 폴더에서 스킬 관련 세션을 찾아 전체 대화를 먼저 읽어줘.
그 다음 Antigravity, Kilo, session-recovery 스킬 상태를 중심으로 정리해줘.
```

## 전체 archive 읽기 (빠른 탐색용)
```text
최근 세션 archive를 확인해줘.

sessions_html/index.html에서 최근 세션 목록을 보고,
관심 있는 세션을 선택하면 sessions/ 폴더의 원본 markdown을 읽어줘.
요약보다는 전체 대화 흐름을 먼저 확인하는 방식으로 진행해줘.
```
