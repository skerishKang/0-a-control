# 18. 대시보드 정보 구조 및 화면 레이아웃

이 문서는 `0-a-control`의 `board-v2` 대시보드를 실제 운영판으로 고도화하기 위한 정보 구조와 화면 기준을 정의한다. 현재 구현을 부정하지 않고, 이미 존재하는 화면/API를 기준으로 다음 개선 방향을 정리한다.

## 현재 확인된 구조

### 진입점

- 서버: `scripts/server.py`
- 기본 URL: `http://localhost:4310`
- 루트 리다이렉트: `/` → `/board-v2.html`
- 화면 파일: `public/board-v2.html`

### 주요 프론트 파일

- `public/board-v2.html`
- `public/board-v2.js`
- `public/board-v2-render.js`
- `public/board-v2-render-morning.js`
- `public/board-v2-render-progress.js`
- `public/board-v2-render-eod.js`
- `public/board-v2-render-completed.js`
- `public/board-v2-phase.js`
- `public/board-v2-selectors.js`
- `public/board-v2-shared.js`
- `public/board-v2-*.css`

### 현재 로드하는 API

`board-v2.js` 기준 초기 로드에서 다음 API를 가져온다.

- `/api/current-state`
- `/api/briefs/latest?limit=3`
- `/api/sessions/recent?limit=50`
- `/api/quests`
- `/api/plans`

추가로 사용자 액션에서 다음 API를 사용한다.

- `/api/quests/report`
- `/api/quests/evaluate`
- `/api/current-quest/start`
- `/api/current-quest/defer`
- `/api/tomorrow-first-quest/confirm`
- `/api/tomorrow-first-quest/promote`
- `/api/tomorrow-first-quest/clear`
- `/api/bridge/quick-input`

## 대시보드의 역할

대시보드는 단순 목록이 아니라 다음 질문에 답해야 한다.

1. 지금 가장 중요한 작업은 무엇인가?
2. 오늘 이어서 처리할 작업은 무엇인가?
3. 막힌 작업은 무엇이고 왜 막혔는가?
4. 최근 어떤 세션과 결정이 있었는가?
5. 검증이 필요한 항목은 무엇인가?
6. 외부 동기화나 설정에 문제가 있는가?
7. 다음 행동을 바로 시작할 수 있는가?

## 권장 화면 구조

### 1. 상단 상태 바

목적: 현재 대시보드 상태와 시간, 운영 모드를 한눈에 보여준다.

표시 항목:

- 현재 날짜/시간
- 현재 phase
- 전체 상태 라벨
- 로컬/원격 접근 상태
- 설정 경고 수
- 수동 새로고침 버튼

현재 구현:

- 시간 표시 있음
- phase tabs 있음
- status label 있음
- Classic 보기 링크 있음

개선 필요:

- Settings/Guardrails 상태 요약
- GitHub/Telegram 외부 데이터 상태
- 마지막 새로고침 시각

### 2. 오늘의 주 임무 패널

목적: 사용자가 바로 시작해야 할 핵심 작업을 보여준다.

표시 항목:

- 주 임무 제목
- 현재 퀘스트
- 현재 상태
- 시작/보류/미루기/보고 액션
- blocker 또는 다음 시작점

현재 구현:

- current-state 기반 주 임무/퀘스트 표시 흐름 존재
- 퀘스트 시작/보고/판정/미루기 액션 존재

개선 필요:

- blocker를 별도 시각 요소로 분리
- 현재 작업과 다음 작업의 경계 명확화
- 검증 필요 상태를 명확한 배지로 표시

### 3. 작업 큐 패널

목적: `Now`, `Next`, `Blocked`, `Later`, `Done` 같은 실행 순서를 보여준다.

표시 항목:

- Now: 지금 처리할 항목
- Next: 다음 후보
- Blocked: 막힌 항목
- Later: 나중에 처리할 항목
- Done/Recent: 최근 완료 항목

현재 구현:

- plans API와 priority candidates API 기반으로 확장 가능
- overdue action 버튼 일부 존재

개선 필요:

- 큐 구분이 화면에서 충분히 명확하지 않음
- drag/reorder 또는 priority override 없음
- GitHub issue/PR 기반 작업 큐와 아직 연결되지 않음

### 4. 검증 상태 패널

목적: 실행/빌드/테스트/브라우저 확인이 필요한 항목을 별도 표시한다.

표시 항목:

- 검증 필요 항목
- 검증 체크리스트
- 마지막 검증 시각
- PASS/FAIL/SKIPPED/NOT APPLICABLE
- 실패 메모

현재 구현:

- quest verdict는 있으나 checklist 구조는 없음

개선 필요:

- #7의 검증 체크리스트 모델 필요
- PR/Issue별 검증 결과 저장 필요
- READY와 NEEDS_VALIDATION 상태 구분 필요

### 5. 최근 세션 패널

목적: 최근 작업 맥락과 에이전트 활동을 보여준다.

표시 항목:

- 최근 세션 제목
- agent name
- status
- 시작/종료 시각
- 상세 보기 링크

현재 구현:

- `/api/sessions/recent?limit=50` 로드
- compact session list 렌더링 존재

개선 필요:

- stale session 강조
- 세션 상세 drill-down 연결 강화
- 실패/중단 세션 구분 표시

### 6. 외부 소스 상태 패널

목적: Telegram, GitHub 등 외부 데이터 수집 상태를 보여준다.

표시 항목:

- Telegram 설정 상태
- Telegram sync 상태
- GitHub repository summary
- GitHub open issues/PRs counts
- rate-limit 또는 token 설정 여부

현재 구현:

- Telegram 관련 API 존재
- GitHub 수집 레이어는 #16에서 draft PR로 진행 중

개선 필요:

- GitHub summary API/UI 연결
- 외부 소스별 상태 배너
- 설정 누락을 정보/경고/차단으로 구분

### 7. 빠른 입력 패널

목적: 사용자가 자연어로 작업, 아이디어, 기한, 상태 변경을 빠르게 입력한다.

현재 구현:

- quick input textarea 존재
- `/api/bridge/quick-input` 연결 존재
- overdue item action이 quick input으로 연결됨

개선 필요:

- 처리 결과 미리보기
- 실패 시 더 구체적인 오류 표시
- 입력 예시 제공

### 8. Settings/Guardrails 패널

목적: 현재 운영 설정과 위험 상태를 표시한다.

표시 항목:

- `HOST`, `PORT`, `DEBUG`
- Telegram env 설정 상태
- 세션 파일 존재 여부
- 로컬 전용/LAN 노출/원격 접근 위험
- 백업 확인 상태
- 검증 필요 상태

현재 구현:

- Telegram status API는 존재
- 중앙 settings/guardrails 패널은 없음

개선 필요:

- #9 기준의 상태명 UI 반영
- `/api/settings/status` 또는 유사 endpoint 필요
- 위험 상태별 색상 체계 필요

## 권장 정보 우선순위

### P0: 항상 보여야 함

- 현재 주 임무
- 현재 퀘스트/작업
- blocker
- 지금 할 일
- 검증 필요 여부
- critical 설정 경고

### P1: 한 화면 안에서 보여야 함

- Next 작업
- 최근 세션
- 최근 결정
- Telegram/GitHub 상태 요약
- pending 판정

### P2: 접거나 상세로 보내도 됨

- 장기 계획
- 완료 항목 전체 목록
- 오래된 브리프
- 세부 로그
- raw API 데이터

## 레이아웃 원칙

### 데스크톱

권장 구조:

- 상단: 상태 바
- 좌측 큰 영역: 오늘의 주 임무 + 작업 큐
- 우측 보조 영역: 검증 상태 + 외부 소스 + 최근 세션
- 하단 또는 접힘 영역: 긴 목록/아카이브

### 모바일

권장 순서:

1. 상태 바
2. 현재 주 임무
3. 지금 할 일
4. 빠른 입력
5. blocker/검증 필요
6. Next 작업
7. 외부 소스 상태
8. 최근 세션
9. 완료/아카이브

모바일 기준:

- 한 카드에 하나의 판단만 담는다.
- 중요한 액션은 카드 하단에 배치한다.
- 긴 설명은 모달 또는 상세 화면으로 보낸다.

## 상태와 배지 체계

권장 배지:

- `READY`
- `IN_PROGRESS`
- `BLOCKED`
- `NEEDS_IMPLEMENTATION`
- `NEEDS_REVIEW`
- `NEEDS_VALIDATION`
- `DONE`
- `NO_ACTION`

위험/설정 배지:

- `LOCAL_ONLY_SAFE`
- `LAN_EXPOSED`
- `REMOTE_REQUIRES_FRONTDOOR`
- `TELEGRAM_NOT_CONFIGURED`
- `DEBUG_ENABLED`
- `VALIDATION_REQUIRED`

## 오류 UI 기준

현재 `board-v2.js`는 초기 데이터 로드 실패 시 `데이터 로드 실패`만 표시한다. 운영판으로 쓰려면 오류를 구분해야 한다.

권장 오류 구분:

- API unreachable
- API returned non-200
- JSON parse failure
- partial source failure
- Telegram optional failure
- GitHub optional failure
- settings warning

UI 기준:

- 핵심 API 실패: 주요 화면에 오류 표시
- 선택 소스 실패: 해당 패널에만 경고 표시
- 기존 데이터가 있으면 유지하고 상단에 stale warning 표시

## 후속 구현 순서

1. #2 GitHub summary service 로컬 테스트 통과
2. #3 operational state classifier 로컬 테스트 통과
3. `/api/github/summary` 또는 `/api/operations/summary` 추가
4. board-v2에 외부 소스 상태 패널 추가
5. 상태/배지 렌더링 컴포넌트 정리
6. 검증 체크리스트 패널 추가
7. Settings/Guardrails 패널 추가
8. 모바일 레이아웃 점검

## 완료 기준

#4가 완료되려면 다음 조건을 만족해야 한다.

- 현재 `board-v2`의 정보 흐름이 문서화되어 있다.
- 대시보드가 답해야 할 운영 질문이 정의되어 있다.
- 주요 패널과 우선순위가 정의되어 있다.
- 데스크톱/모바일 레이아웃 원칙이 정의되어 있다.
- 후속 UI 구현자가 무엇을 어디에 넣을지 판단할 수 있다.
