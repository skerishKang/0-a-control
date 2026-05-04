# 20. 작업 큐 및 우선순위 보드 모델

이 문서는 `0-a-control`에서 지금 처리할 작업, 다음 작업, 막힌 작업, 나중 작업, 완료 작업을 한 화면에서 판단하기 위한 작업 큐와 우선순위 보드 기준을 정의한다.

## 목적

현재 대시보드는 `plans`, `quests`, `workdiary`, `sessions` 데이터를 이미 갖고 있다. 그러나 운영판으로 쓰려면 단순 목록이 아니라 “지금 무엇을 해야 하는가”를 더 명확히 보여줘야 한다.

작업 큐의 목적은 다음과 같다.

- 지금 바로 실행 가능한 작업을 분리한다.
- 막힌 작업을 실행 가능한 작업과 섞지 않는다.
- 오래 방치된 작업을 드러낸다.
- 수동 override와 자동 분류를 함께 반영한다.
- 로컬 필요 작업과 원격 가능 작업을 구분한다.
- 작업 완료 후 다음 후보를 바로 볼 수 있게 한다.

## 현재 활용 가능한 데이터

### 기존 API

- `/api/plans`
- `/api/quests`
- `/api/workdiary/top-level`
- `/api/workdiary/priority-candidates`
- `/api/sessions/recent`
- `/api/current-state`

### 진행 중인 후속 데이터

- #2 GitHub data summary service
- #3 operational state classifier
- #5 manual ops override model
- #7 validation checklist model

## 큐 상태

작업 큐는 다음 상태를 기본으로 사용한다.

| Queue | 의미 | 기본 행동 |
|---|---|---|
| `NOW` | 지금 바로 처리할 작업 | 즉시 시작 또는 보고 |
| `NEXT` | 지금 작업 이후 후보 | 준비 상태 유지 |
| `BLOCKED` | 막힌 작업 | blocker와 재개 조건 확인 |
| `LOCAL_NEEDED` | 로컬 실행/브라우저/모델 확인 필요 | 사용자 로컬 실행 요청 |
| `REVIEW_NEEDED` | 검토 필요 | 범위/결과 확인 |
| `VALIDATION_NEEDED` | 검증 필요 | 테스트/빌드/브라우저 확인 |
| `LATER` | 나중 작업 | 낮은 우선순위로 보관 |
| `DONE` | 완료 | 최근 완료로만 표시 |
| `NO_ACTION` | 지금 조치 없음 | 기본 보드에서는 숨김 가능 |

## 우선순위

| Priority | 의미 | 예시 |
|---|---|---|
| `P0` | 오늘 즉시 처리해야 함 | 대시보드가 안 뜸, 데이터 손상 위험 |
| `P1` | 가까운 시점에 처리해야 함 | 검증 필요 PR, blocked 해소 |
| `P2` | 일반 작업 | 문서 보강, UI 개선 |
| `P3` | 낮은 우선순위 | 아카이브, 참고, 장기 개선 |

## 작업 항목 모델

권장 normalized work item 형태:

```json
{
  "id": "github-pr-16",
  "source": "github",
  "source_type": "pr",
  "source_id": "16",
  "title": "feat: add GitHub data summary service",
  "queue": "VALIDATION_NEEDED",
  "priority": "P1",
  "automatic_status": "IN_PROGRESS",
  "manual_status": null,
  "effective_status": "NEEDS_VALIDATION",
  "reason": "Python runtime code and tests were added.",
  "next_action": "Run unit tests locally before ready/merge.",
  "guards": ["VALIDATION_REQUIRED"],
  "is_local_needed": true,
  "updated_at": "2026-05-04T02:06:27Z",
  "links": [
    {"label": "PR", "url": "https://github.com/skerishKang/0-a-control/pull/16"}
  ]
}
```

## 큐 산출 규칙

### 1. 완료/조치 없음 먼저 제외

- `DONE` → `DONE` 큐 또는 최근 완료 영역
- `NO_ACTION` → 기본 보드에서 숨김 가능

### 2. 금지/차단 guard 우선

- `DO_NOT_MERGE`
- `DO_NOT_CLOSE`
- `BLOCKED`
- `CONFIGURATION_MISSING`

위 항목은 `BLOCKED` 또는 별도 위험 영역에 둔다.

### 3. 로컬 필요 작업 분리

다음 조건이면 `LOCAL_NEEDED` 또는 `VALIDATION_NEEDED`로 보낸다.

- Python 런타임 코드 변경
- 테스트 추가/수정
- 서버 실행 확인 필요
- 브라우저 렌더링 확인 필요
- Telegram 인증/동기화 필요
- 로컬 모델 또는 CLI agent 실행 필요

### 4. 검토 필요 작업 분리

다음 조건이면 `REVIEW_NEEDED`로 보낸다.

- 문서 전용 PR
- non-draft PR
- scope 확인 필요
- stale item 검토 필요

### 5. 실행 가능 작업 산출

blocker가 없고 검증/리뷰 조건이 충족된 작업 중 가장 높은 우선순위를 `NOW`에 둔다.

### 6. 장기/낮은 우선순위 보관

- P3
- archive
- recurring이지만 오늘 대상 아님
- watch 상태
- ignore until 조건이 아직 안 된 항목

## 정렬 규칙

권장 정렬 순서:

1. Queue 우선순위
   - `NOW`
   - `LOCAL_NEEDED`
   - `VALIDATION_NEEDED`
   - `REVIEW_NEEDED`
   - `BLOCKED`
   - `NEXT`
   - `LATER`
   - `DONE`
   - `NO_ACTION`
2. Priority
   - `P0`
   - `P1`
   - `P2`
   - `P3`
3. 오래 방치된 항목
4. 최근 업데이트 항목
5. source별 tie-breaker

## UI 요구사항

### 홈 요약

대시보드 홈에는 다음만 짧게 보여준다.

- NOW 1~3개
- LOCAL_NEEDED 1~3개
- BLOCKED 1~3개
- VALIDATION_NEEDED 1~3개
- NEXT 3개 이하

### 상세 보드

별도 상세 영역에서는 다음 컬럼 또는 섹션을 제공한다.

- Now
- Local Needed
- Validation Needed
- Review Needed
- Blocked
- Next
- Later
- Done

### 카드 필드

각 카드에는 다음을 표시한다.

- 제목
- source badge
- queue badge
- priority badge
- effective status
- reason 요약
- next action
- local-needed 여부
- 마지막 업데이트
- 링크

### 카드 액션

1차 액션:

- Open source
- Mark override
- Add note
- Copy local prompt
- Mark validation result

주의:

- merge/close/delete 같은 destructive action은 이 보드에서 바로 실행하지 않는다.
- 외부 시스템 write 작업은 별도 확인 플로우가 필요하다.

## 로컬 필요 작업 표시

`LOCAL_NEEDED` 카드는 반드시 실행 명령 또는 보고 형식을 함께 제공해야 한다.

예시:

- `python -m unittest tests.test_github_service`
- `python -m unittest tests.test_operational_state`
- `python scripts/server.py`
- `curl http://localhost:4310/api/health`

보고 형식:

- 실행한 명령
- PASS/FAIL
- 실패 로그 요약
- OS/Shell/Python
- 다음 조치

## 자동 상태와 수동 override 반영

작업 큐는 다음 순서로 상태를 계산한다.

1. source data 수집
2. automatic classifier 적용
3. manual override 적용
4. validation status 적용
5. queue 산출
6. priority 산출
7. UI 표시

manual override가 있으면 자동 상태와 함께 표시한다.

## 오류와 빈 상태

### 빈 상태

- NOW가 비어 있으면 “지금 바로 처리할 작업 없음” 표시
- BLOCKED가 비어 있으면 숨김 가능
- LOCAL_NEEDED가 비어 있으면 숨김 가능

### 오류 상태

- source API 실패: 해당 source 섹션만 경고
- classifier 실패: 자동 상태 대신 raw item 표시
- override 저장소 오류: manual layer 비활성화 경고
- validation 데이터 오류: validation 상태 unknown 표시

## 후속 구현 순서

1. #2 GitHub summary service 테스트 통과
2. #3 operational classifier 테스트 통과
3. #5 manual override 저장 모델 구현
4. work item normalize 함수 추가
5. queue assignment 함수 추가
6. queue assignment 단위 테스트 추가
7. `/api/work-queue` endpoint 추가
8. board-v2에 작업 큐 패널 추가
9. local-needed prompt copy 기능 추가
10. validation checklist와 연결

## 완료 기준

#6이 완료되려면 다음 조건을 만족해야 한다.

- 큐 상태와 우선순위가 정의되어 있다.
- 작업 항목 normalized 모델이 정의되어 있다.
- 자동/수동/검증 상태를 반영하는 산출 규칙이 있다.
- UI 카드와 상세 보드 요구사항이 정리되어 있다.
- 로컬 필요 작업을 별도 표시하는 기준이 있다.
- 후속 구현자가 `/api/work-queue`를 설계할 수 있다.
