---
name: codex-session-recovery
description: "Codex 세션에서 이전 작업 맥락을 복원한다. sessions/ archive를 먼저 읽고, 필요 시 sqlite/history.jsonl에서 추가 확인한다."
---

# codex-session-recovery

## 언제 쓰는지

- "이전 codex 세션 복원해줘"
- "codex 세션 읽어서 이어갈 일 정리해줘"
- "resume previous codex work"
- 긴 Codex 세션이 있고 prior work를 이어가고 싶을 때
- 사용자가 `.codex` 세션 히스토리를 검사하고 싶을 때

## 입력으로 기대하는 정보

1. `sessions/` 폴더 — 전체 세션 archive (최우선)
2. `sessions_html/` 폴더 — 빠른 탐색용 HTML 표시층
3. `~/.codex/state_5.sqlite` — 스레드 메타데이터 (보조)
4. `~/.codex/history.jsonl` — 사용자 메시지 로그 (보조)

## Recovery 읽기 순서

1. **current urgent state** 확인
2. **sessions/ 폴더**에서 관련 세션 archive를 찾아 전체 대화를 읽음
3. **sessions_html/**로 빠른 탐색 (필요 시)
4. **sqlite / history.jsonl**에서 추가 확인 (부족할 때)
5. **summary/current quest**로 압축 (마지막 정리)

## 실행 절차

### Step 1: sessions/에서 관련 세션 찾기

```bash
ls -lt sessions/ | head -5
ls sessions/YYYY-MM-DD/
```

또는 sessions_html/index.html에서 최근 세션 목록 확인.

### Step 2: 세션 archive 읽기

찾은 세션의 .md 파일을 열어 다음을 확인:
- **Metadata**: 세션 ID, 시간, Agent
- **Summary**: 짧은 요약 (보조)
- **Dialogue**: 전체 대화 흐름 (메인)
- **Transcript**: 원시 기록 (필요 시)

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

## 추가 확인 필요한 주제
- {주제명} — 이유
```

## 출력 형식

- 한국어로 출력
- 원문 출처 명시 (sessions archive / sqlite / history.jsonl / human context)
- assistant 응답이 없으면 반드시 명시

## 3층 구조 원칙

이 스킬은 다음을 구분해야 한다:

1. **원문층**: sessions/ archive (전체 대화 + transcript)
2. **복원층**: 주제별 요약, 현재 상태, 남은 것, 다음 액션
3. **표시층**: sessions_html/ (원문 대체물이 아님)

**중요**: 요약을 원문으로 오해하지 말 것. 전체 archive를 먼저 읽고 요약은 보조로만 사용할 것.

## 실패/누락 시 fallback

| 상황 | fallback |
|------|----------|
| sessions/ 접근 불가 | sqlite/history.jsonl로 복원 시도 |
| sqlite 접근 불가 | history.jsonl만으로 복원 시도 |
| history.jsonl 세션 없음 | "해당 세션 메시지를 찾을 수 없음" 안내 |
| 메시지가 너무 적음 | "대화 복원에 필요한 메시지가 부족합니다" 안내 |
| 주제 분류 곤란 | "명확한 주제 패턴을 찾을 수 없습니다" 안내 |

## 관련 파일

- `sessions/` — 전체 세션 archive (최우선 소스)
- `sessions_html/` — HTML 표시층 (빠른 탐색용)
- `~/.codex/state_5.sqlite` — 스레드 메타데이터
- `~/.codex/history.jsonl` — 사용자 대화 로그
- `~/.codex/log/codex-tui.log` — 시스템 로그 (참조용)
- `docs/skills/session-recovery-skill/01-session-architecture-prompt.md` — 아키텍처 원칙
- `docs/skills/session-recovery-skill/02-codex-session-skill.md` — 스킬 설계

## 제한 사항

- 이 스킬은 **Codex** 전용이다 (Claude Code, Kilo 아님)
- assistant 응답은 직접 저장되지 않음 → 항상 "assistant 응답 없음" 명시
- 원문 vs 요약을 구분하여 출력할 것
- HTML은 보기용이지 원문 대체물이 아님
