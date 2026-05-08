# 20. 작업 큐 및 우선순위 보드 모델

이 문서는 `0-a-control`에서 지금 처리할 작업, 다음 작업, 막힌 작업, 나중 작업, 완료 작업을 한 화면에서 판단하기 위한 작업 큐와 우선순위 보드 기준을 정의한다.

## 목적

- 지금 바로 실행 가능한 작업을 분리한다.
- 막힌 작업을 실행 가능한 작업과 섞지 않는다.
- 오래 방치된 작업을 드러낸다.
- 수동 override와 자동 분류를 함께 반영한다.
- 로컬 필요 작업과 원격 가능 작업을 구분한다.
- 작업 완료 후 다음 후보를 바로 볼 수 있게 한다.

## 활용 가능한 데이터

기존 API:

- `/api/plans`
- `/api/quests`
- `/api/workdiary/top-level`
- `/api/workdiary/priority-candidates`
- `/api/sessions/recent`
- `/api/current-state`

후속 데이터:

- GitHub data summary service
- operational state classifier
- manual ops override model
- validation checklist model

## 큐 상태

| Queue | 의미 | 기본 행동 |
|---|---|---|
| `NOW` | 지금 바로 처리할 작업 | 즉시 시작 또는 보고 |
| `NEXT` | 지금 작업 이후 후보 | 준비 상태 유지 |
| `BLOCKED` | 막힌 작업 | blocker와 재개 조건 확인 |
| `LOCAL_NEEDED` | 로컬 실행/브라우저/모델 확인 필요 | 로컬 실행 요청 |
| `REVIEW_NEEDED` | 검토 필요 | 범위/결과 확인 |
| `VALIDATION_NEEDED` | 검증 필요 | 테스트/빌드/브라우저 확인 |
| `LATER` | 나중 작업 | 낮은 우선순위 보관 |
| `DONE` | 완료 | 최근 완료로만 표시 |
| `NO_ACTION` | 지금 조치 없음 | 기본 보드에서 숨김 가능 |

## 우선순위

| Priority | 의미 |
|---|---|
| `P0` | 즉시 처리 |
| `P1` | 가까운 시점 처리 |
| `P2` | 일반 작업 |
| `P3` | 낮은 우선순위 |

## normalized work item

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
  "next_action": "Run unit tests locally before review.",
  "guards": ["VALIDATION_REQUIRED"],
  "is_local_needed": true,
  "updated_at": "2026-05-04T02:06:27Z",
  "links": [{"label": "PR", "url": "https://github.com/skerishKang/0-a-control/pull/16"}]
}
```

## 큐 산출 규칙

1. 완료/조치 없음 항목은 먼저 분리한다.
2. 금지/차단 guard를 우선 처리한다.
3. 로컬 필요 작업은 `LOCAL_NEEDED` 또는 `VALIDATION_NEEDED`로 보낸다.
4. 문서/범위 검토 작업은 `REVIEW_NEEDED`로 보낸다.
5. blocker가 없고 검증 조건이 충족된 가장 높은 우선순위 작업을 `NOW`에 둔다.
6. 낮은 우선순위, watch, ignore-until 항목은 `LATER`로 둔다.

## 정렬 규칙

1. Queue 우선순위
2. Priority
3. 오래 방치된 항목
4. 최근 업데이트 항목
5. source별 tie-breaker

## UI 요구사항

홈 요약:

- NOW 1~3개
- LOCAL_NEEDED 1~3개
- BLOCKED 1~3개
- VALIDATION_NEEDED 1~3개
- NEXT 3개 이하

상세 보드:

- Now
- Local Needed
- Validation Needed
- Review Needed
- Blocked
- Next
- Later
- Done

카드 필드:

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

카드 액션:

- Open source
- Mark override
- Add note
- Copy local prompt
- Mark validation result

merge/close/delete 같은 외부 destructive action은 이 보드에서 바로 실행하지 않는다.

## 로컬 필요 작업 표시

`LOCAL_NEEDED` 카드는 실행 명령 또는 보고 형식을 함께 제공해야 한다.

예:

- `python -m unittest tests.test_github_service`
- `python -m unittest tests.test_operational_state`
- `python scripts/server.py`
- `curl http://localhost:4310/api/health`

## 상태 계산 순서

1. source data 수집
2. automatic classifier 적용
3. manual override 적용
4. validation status 적용
5. queue 산출
6. priority 산출
7. UI 표시

## 오류와 빈 상태

- source API 실패: 해당 source 섹션 경고
- classifier 실패: raw item 표시
- override 저장소 오류: manual layer 비활성화 경고
- validation 데이터 오류: validation unknown 표시
- NOW가 비어 있으면 “지금 바로 처리할 작업 없음” 표시

## 후속 구현 순서

1. work item normalize 함수
2. queue assignment 함수
3. queue assignment 단위 테스트
4. `/api/work-queue` endpoint
5. board-v2 작업 큐 패널
6. local-needed prompt copy
7. validation checklist 연결
