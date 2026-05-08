# 18. 대시보드 정보 구조 및 화면 레이아웃

이 문서는 `0-a-control`의 `board-v2` 대시보드를 실제 운영판으로 고도화하기 위한 정보 구조와 화면 기준을 정의한다.

## 현재 구조

- 진입점: `public/board-v2.html`
- 서버: `scripts/server.py`
- 기본 URL: `http://localhost:4310`
- 루트 리다이렉트: `/` → `/board-v2.html`

초기 로드 API:

- `/api/current-state`
- `/api/briefs/latest?limit=3`
- `/api/sessions/recent?limit=50`
- `/api/quests`
- `/api/plans`

사용자 액션 API:

- `/api/quests/report`
- `/api/quests/evaluate`
- `/api/current-quest/start`
- `/api/current-quest/defer`
- `/api/tomorrow-first-quest/confirm`
- `/api/tomorrow-first-quest/promote`
- `/api/tomorrow-first-quest/clear`
- `/api/bridge/quick-input`

## 대시보드가 답해야 할 질문

1. 지금 가장 중요한 작업은 무엇인가?
2. 오늘 이어서 처리할 작업은 무엇인가?
3. 막힌 작업은 무엇이고 왜 막혔는가?
4. 최근 세션과 결정은 무엇인가?
5. 검증이 필요한 항목은 무엇인가?
6. 외부 동기화나 설정에 문제가 있는가?
7. 다음 행동을 바로 시작할 수 있는가?

## 권장 화면 구조

### 상단 상태 바

- 현재 날짜/시간
- 현재 phase
- 전체 상태 라벨
- 로컬/원격 접근 상태
- 설정 경고 수
- 마지막 새로고침 시각
- 수동 새로고침 버튼

### 오늘의 주 임무 패널

- 주 임무 제목
- 현재 퀘스트
- 현재 상태
- 시작/보류/미루기/보고 액션
- blocker 또는 다음 시작점

### 작업 큐 패널

- Now
- Next
- Blocked
- Later
- Done/Recent

### 검증 상태 패널

- 검증 필요 항목
- 체크리스트
- 마지막 검증 시각
- PASS/FAIL/SKIPPED/NOT APPLICABLE
- 실패 요약

### 최근 세션 패널

- 세션 제목
- agent
- status
- 시작/종료 시각
- 상세 보기
- stale session 강조

### 외부 소스 상태 패널

- Telegram 설정/동기화 상태
- GitHub repository summary
- open issue/PR count
- rate-limit 또는 token 설정 여부

### 빠른 입력 패널

- quick input textarea
- 처리 결과 미리보기
- 실패 시 구체적 오류 표시
- 입력 예시

### Settings/Guardrails 패널

- `HOST`, `PORT`, `DEBUG`
- Telegram env 상태
- 세션 파일 존재 여부
- 로컬 전용/LAN 노출/원격 접근 위험
- 백업 확인 상태

## 정보 우선순위

### P0

- 현재 주 임무
- 현재 작업
- blocker
- 지금 할 일
- 검증 필요 여부
- critical 설정 경고

### P1

- Next 작업
- 최근 세션
- 최근 결정
- Telegram/GitHub 상태 요약
- pending 판정

### P2

- 장기 계획
- 완료 항목 전체 목록
- 오래된 브리프
- 세부 로그
- raw API 데이터

## 레이아웃 원칙

데스크톱:

- 상단: 상태 바
- 좌측: 오늘의 주 임무 + 작업 큐
- 우측: 검증 상태 + 외부 소스 + 최근 세션
- 하단/접힘: 긴 목록과 아카이브

모바일:

1. 상태 바
2. 현재 주 임무
3. 지금 할 일
4. 빠른 입력
5. blocker/검증 필요
6. Next 작업
7. 외부 소스 상태
8. 최근 세션
9. 완료/아카이브

## 상태와 배지

- `READY`
- `IN_PROGRESS`
- `BLOCKED`
- `NEEDS_IMPLEMENTATION`
- `NEEDS_REVIEW`
- `NEEDS_VALIDATION`
- `DONE`
- `NO_ACTION`
- `LOCAL_ONLY_SAFE`
- `LAN_EXPOSED`
- `REMOTE_REQUIRES_FRONTDOOR`
- `TELEGRAM_NOT_CONFIGURED`
- `DEBUG_ENABLED`
- `VALIDATION_REQUIRED`

## 오류 UI 기준

오류는 다음처럼 구분한다.

- API unreachable
- API returned non-200
- JSON parse failure
- partial source failure
- Telegram optional failure
- GitHub optional failure
- settings warning

핵심 API 실패는 주요 화면에 표시하고, 선택 소스 실패는 해당 패널에만 경고한다.

## 후속 구현 순서

1. GitHub summary service 연결
2. operational state classifier 연결
3. `/api/github/summary` 또는 `/api/operations/summary` 추가
4. board-v2 외부 소스 상태 패널 추가
5. 상태/배지 렌더링 정리
6. 검증 체크리스트 패널 추가
7. Settings/Guardrails 패널 추가
8. 모바일 레이아웃 점검
