---
name: codex-session-recovery
description: "Codex 세션에서 이전 작업 맥락을 복원한다. sqlite/ history.jsonl에서 대화를 추출하고 주제별로 작업 흐름을 정리한다."
---

# codex-session-recovery

## 언제 쓰는지

- "이전 codex 세션 복원해줘"
- "codex 세션 읽어서 이어갈 일 정리해줘"
- "resume previous codex work"
- 긴 Codex 세션이 있고 prior work를 이어가고 싶을 때
- 사용자가 `.codex` 세션 히스토리를 검사하고 싶을 때

## 입력으로 기대하는 정보

1. `~/.codex/state_5.sqlite` — 스레드 메타데이터
2. `~/.codex/history.jsonl` — 사용자 메시지 로그
3. (옵션) `G:\Ddrive\BatangD\task\workdiary\0-a-control\sessions` — 로컬 세션 아카이브

## 실행 절차

### Step 1: SQLite에서 스레드 목록 조회

```python
import sqlite3
conn = sqlite3.connect('C:/Users/limone/.codex/state_5.sqlite')
cur = conn.cursor()
cur.execute('SELECT id, title, first_user_message, created_at FROM threads ORDER BY created_at DESC LIMIT 10')
for row in cur.fetchall():
    print(f'{row[0]} | {row[1][:50]}... | {row[3]}')
```

### Step 2: history.jsonl에서 세션 메시지 추출

```python
import json

session_id = '019d089f-2859-75a0-b3a9-d9b3a0eb0317'  # 사용자가 선택한 세션

with open('C:/Users/limone/.codex/history.jsonl', 'r', encoding='utf-8') as f:
    messages = [json.loads(line) for line in f if json.loads(line).get('session_id') == session_id]

# 시간순 정렬
messages.sort(key=lambda x: x.get('ts', 0))

print(f'총 메시지: {len(messages)}개')
```

### Step 3: 주제별 분류

주제별 키워드로 메시지 필터링:

| 주제 | 키워드 |
|------|--------|
| board-v2 | board, v2, 보드, 171-HAIA, dashboard, 대시보드 |
| 메가존 | 메가존, mega, 171-HAIA |
| 아파트 | 아파트, 부동산, 관리규약 |
| 0-a-control | 0-a-control, control tower, 킬로, skill |
| 파일삭제 | 삭제, 지워, delete, Temp, AppData |
| MCP | mcp, MCP |

### Step 4: 주제별 상태 정리

각 주제마다:

```
## {주제명}
- 처음 나온 시점: {YYYY-MM-DD HH:MM}
- 메시지 수: {N}개
- 마지막 활동: {YYYY-MM-DD HH:MM}
- 마지막 메시지: {텍스트 100자}
- 현재 상태: {진행중/보류/완료}
- 남은 것: {남은 작업}
```

### Step 5: 우선순위 판단

```
## 이어야 할 것
1. {가장 중요한 주제} — 이유
2. {두 번째} — 이유

## 복원만으로 충분한 주제
- {주제명}

## 추가 transcript 필요한 주제
- {주제명} — 이유
```

## 출력 형식

- 한국어로 출력
- 원문 출처 명시 (sqlite / history.jsonl / sessions folder / human context)
- assistant 응답이 없으면 반드시 명시

### 출력 예시

```
=== Codex 세션 복원 ===

선택된 세션: 019d089f-2859-75a0-b3a9-d9b3a0eb0317
총 사용자 메시지: 794개
분석 기간: 2026-03-20 ~ 2026-03-29

---

## 1. board-v2 (111개)
시작: 2026-03-21 09:09
마지막: 2026-03-29 12:20
상태: 진행중
남은 것: CSS/JS 리팩토링, HWPX 템플릿 완성

## 2. 0-a-control (105개)
시작: 2026-03-20 10:53
마지막: 2026-03-29 12:26
상태: 진행중
남은 것: 스킬 정의 및 세션 관리

## 3. 메가존 (139개)
시작: 2026-03-20 15:18
마지막: 2026-03-27 16:53
상태: 보류
남은 것: 저장소 복구 결과 확인

## 4. 아파트 (9개)
시작: 2026-03-23 13:47
마지막: 2026-03-27 19:53
상태: 진행중
남은 것: PDF 관리규약 검토 필요

---

### 우선순위
1. board-v2 — 오늘(03-29)까지 활발히 진행, 마지막 활동 12:20
2. 0-a-control — 스킬 정립 중

### 복원 충분: board-v2, 0-a-control
### 추가 transcript 필요: 아파트 (PDF 내용 모름), 메가존 (Git 복구 결과 모름)
```

## 3층 구조 원칙

이 스킬은 다음을 구분해야 한다:

1. **원문층**: sqlite metadata, history.jsonl 사용자 메시지
2. **복원층**: 주제별 요약, 현재 상태, 남은 것, 다음 액션
3. **표시층**: HTML 대시보드 (원문 대체물이 아님)

**중요**: 요약을 원문으로 오해하지 말 것. assistant 응답이 없으면 그 사실을 명확히 밝힐 것.

## 실패/누락 시 fallback

| 상황 | fallback |
|------|----------|
| sqlite 접근 불가 | history.jsonl만으로 복원 시도 |
| history.jsonl 세션 없음 | "해당 세션 메시지를 찾을 수 없음" 안내 |
| 메시지가 너무 적음 | "대화 복원에 필요한 메시지가 부족합니다" 안내 |
| 주제 분류 곤란 | "명확한 주제 패턴을 찾을 수 없습니다" 안내 |

## 관련 파일

- `~/.codex/state_5.sqlite` — 스레드 메타데이터
- `~/.codex/history.jsonl` — 사용자 대화 로그
- `~/.codex/log/codex-tui.log` — 시스템 로그 (참조용)
- `docs/skills/session-recovery-skill/01-session-architecture-prompt.md` — 아키텍처 원칙
- `docs/skills/session-recovery-skill/02-codex-session-skill.md` — 스킬 설계

## 제한 사항

- 이 스킬은 **Codex** 전용이다 (Claude Code, Kilo 아님)
- assistant 응답은 직접 저장되지 않음 → 항상 "assistant 응답 없음" 명시
- 원문 vs 요약을 구분하여 출력할 것
