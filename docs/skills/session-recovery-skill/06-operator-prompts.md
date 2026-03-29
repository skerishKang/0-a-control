# Session Recovery Operator Prompts

## Default Prompt
```text
이전 codex 세션 복원해줘.
board-v2, 0-a-control 스킬, 메가존, 아파트 순으로 정리하고,
각 주제마다 지금까지 한 것 / 현재 상태 / 남은 것 / 다음 할 일을 써줘.
마지막에는 지금 가장 먼저 다시 시작할 주제 1개를 골라줘.
```

## If Continuity Is Weak
```text
codex 세션 읽어서 이어갈 일 정리해줘.
복원이 충분한지 먼저 판단하고,
부족하면 어떤 주제만 추가 handoff가 필요한지 따로 표시해줘.
```

## board-v2 Only
```text
board-v2 관련 codex 세션만 복원해줘.
완료 탭, overdue quick action, 날짜/시간 표시, 모듈화 상태 중심으로 정리해줘.
```

## Megazone Only
```text
메가존 관련 codex 세션을 복원해줘.
사건정리 / 대응문서 / 남은 실무 조치 중심으로 정리해줘.
```

## Apartment Only
```text
아파트 관련 codex 세션을 복원해줘.
dashboard 검산 상태, 숫자 불일치, 추가로 필요한 원문 자료 중심으로 정리해줘.
```

## Skill/Infra Only
```text
0-a-control 스킬 관련 codex 세션만 복원해줘.
Antigravity, Kilo, session-recovery 스킬 상태를 중심으로 정리해줘.
```
