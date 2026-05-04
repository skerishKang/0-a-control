# 19. 수동 운영 메모 및 판단 Override 모델

이 문서는 `0-a-control`에서 자동 분류만으로는 표현하기 어려운 운영 판단을 수동으로 기록하고 override하는 기준을 정의한다. 현재 구현을 바로 바꾸기 전에 데이터 모델, UI 요구사항, API 요구사항, 안전 기준을 먼저 고정한다.

## 목적

자동 상태는 객관적인 입력을 기반으로 빠르게 계산할 수 있지만, 실제 운영에서는 다음과 같은 수동 판단이 필요하다.

- 지금은 일부러 보류한다.
- 자동 분류는 READY지만 실제로는 검증이 필요하다.
- 이 이슈는 다음 주까지 건드리지 않는다.
- 특정 PR은 병합하지 않고 참고용으로 둔다.
- blocker가 외부 상황에 의존한다.
- 사용자의 직접 판단으로 우선순위를 바꾼다.

수동 override는 자동 분류를 삭제하지 않고, 그 위에 사용자의 운영 판단을 명시적으로 덧씌우는 계층이어야 한다.

## 기본 원칙

1. 자동 상태와 수동 override 상태를 분리한다.
2. override에는 반드시 이유가 있어야 한다.
3. override 작성자와 작성/수정 시각을 남긴다.
4. override는 제거 가능해야 한다.
5. destructive action을 자동으로 실행하지 않는다.
6. 수동 override는 UI에서 자동 상태보다 더 눈에 띄게 표시한다.
7. 오래된 override는 stale 상태로 표시한다.

## 대상 객체

수동 메모와 override는 다음 대상에 붙을 수 있다.

| 대상 | 예시 |
|---|---|
| GitHub issue | `issue:5` |
| GitHub PR | `pr:16` |
| 내부 quest | `quest:<id>` |
| 내부 plan | `plan:<id>` |
| session | `session:<id>` |
| external source | `source:telegram` 또는 `source:github` |
| global dashboard | `global:dashboard` |

## 데이터 모델

권장 저장 형태는 JSON 또는 SQLite 테이블이다. 1차 구현에서는 로컬 JSON 파일로 시작해도 된다.

### Override record

필드:

| 필드 | 필수 | 설명 |
|---|---:|---|
| `id` | yes | override 고유 ID |
| `target_type` | yes | `issue`, `pr`, `quest`, `plan`, `session`, `source`, `global` |
| `target_id` | yes | 대상 식별자 |
| `manual_status` | yes | 수동 상태 |
| `reason` | yes | override 이유 |
| `note` | no | 추가 메모 |
| `priority` | no | `P0`, `P1`, `P2`, `P3` |
| `expires_at` | no | 자동 stale 판단 또는 만료 기준 |
| `created_at` | yes | 생성 시각 |
| `updated_at` | yes | 수정 시각 |
| `created_by` | no | 로컬 사용자/agent 이름 |
| `source` | yes | `manual`, `local-agent`, `imported` 등 |
| `is_active` | yes | 현재 적용 여부 |

예시:

```json
{
  "id": "override_20260504_001",
  "target_type": "pr",
  "target_id": "16",
  "manual_status": "NEEDS_VALIDATION",
  "reason": "Python runtime code was added and local tests have not been run yet.",
  "note": "Run tests.test_github_service before ready/merge.",
  "priority": "P1",
  "expires_at": null,
  "created_at": "2026-05-04T02:30:00+09:00",
  "updated_at": "2026-05-04T02:30:00+09:00",
  "created_by": "user",
  "source": "manual",
  "is_active": true
}
```

## 수동 상태 값

자동 분류 상태와 같은 상태명을 우선 재사용한다.

- `READY`
- `IN_PROGRESS`
- `BLOCKED`
- `NEEDS_IMPLEMENTATION`
- `NEEDS_REVIEW`
- `NEEDS_VALIDATION`
- `DONE`
- `NO_ACTION`

추가 수동 전용 상태:

- `PINNED`: 대시보드 상단 고정
- `WATCH`: 당장 작업하지 않지만 관찰
- `IGNORE_UNTIL`: 특정 시점까지 숨김 또는 낮은 우선순위
- `DO_NOT_MERGE`: 병합 금지 판단
- `DO_NOT_CLOSE`: 닫기 금지 판단

## 자동 상태와 수동 상태 결합 규칙

### 우선순위

1. `DO_NOT_MERGE`, `DO_NOT_CLOSE` 같은 금지성 override
2. active manual status
3. automatic status
4. default fallback

### 결합 결과 필드

UI와 API는 다음 형태를 반환하는 것이 좋다.

```json
{
  "automatic": {
    "status": "READY",
    "reason": "Open non-draft PR has no blocking marker."
  },
  "manual": {
    "status": "NEEDS_VALIDATION",
    "reason": "Local tests have not been run."
  },
  "effective": {
    "status": "NEEDS_VALIDATION",
    "source": "manual",
    "reason": "Manual override requires local tests before review."
  }
}
```

## UI 요구사항

### 목록 카드/행

각 항목은 다음을 보여준다.

- 제목
- 자동 상태 배지
- 수동 override 배지, 있으면 더 강조
- override 이유 요약
- priority
- 마지막 업데이트 시각
- override 만료 또는 stale 여부

### 상세 모달

상세 모달은 다음을 보여준다.

- 자동 분류 결과
- 수동 override 결과
- override 변경 이력
- 메모
- 현재 적용 중인 effective status
- override 생성/수정/해제 버튼

### 생성/수정 폼

필수 입력:

- 대상
- 수동 상태
- 이유

선택 입력:

- 메모
- 우선순위
- 만료일

검증 규칙:

- 이유가 비어 있으면 저장 불가
- `DONE`으로 override할 때는 완료 근거가 필요
- `NO_ACTION`으로 override할 때는 이유가 필요
- 금지성 override는 눈에 띄는 확인을 요구

## API 요구사항

후속 구현 시 다음 endpoint를 고려한다.

### GET `/api/ops-overrides`

쿼리:

- `target_type`
- `target_id`
- `active_only=true|false`

반환:

- override 목록

### POST `/api/ops-overrides`

목적:

- 새 override 생성

필수 body:

- `target_type`
- `target_id`
- `manual_status`
- `reason`

### PATCH `/api/ops-overrides/<id>`

목적:

- override 수정

수정 가능:

- `manual_status`
- `reason`
- `note`
- `priority`
- `expires_at`
- `is_active`

### DELETE 또는 POST deactivate

권장:

- 실제 삭제보다 `is_active=false` 비활성화
- 이력 보존 우선

## 저장 방식

### 1차 구현 권장

- `data/runtime/ops_overrides.json`
- Git 커밋 대상 아님
- 로컬 런타임 상태로 취급

### 후속 구현 권장

- SQLite 테이블
- 변경 이력 테이블 분리
- backup 대상 포함

## stale override 기준

다음 경우 stale로 표시한다.

- `updated_at`이 14일 이상 지남
- `expires_at`이 지났는데 active 상태임
- 대상 issue/PR이 이미 닫혔는데 override가 active임
- manual status가 자동 상태와 장기간 충돌함

stale 상태는 자동 삭제하지 않고 사용자에게 검토를 요구한다.

## 안전 기준

- override는 GitHub issue/PR을 직접 닫거나 병합하지 않는다.
- override는 로컬 판단 레이어다.
- 외부 시스템에 쓰기 작업을 하려면 별도 확인이 필요하다.
- 민감 정보는 reason/note에 넣지 않는다.
- token, session, 개인 식별 정보는 override note에 기록하지 않는다.

## 후속 구현 순서

1. JSON 기반 저장 모듈 추가
2. override CRUD 단위 테스트 추가
3. `/api/ops-overrides` GET/POST 추가
4. 상세 모달에 override 표시 추가
5. 항목 리스트에 effective status 배지 추가
6. stale override 경고 추가
7. 필요 시 SQLite로 이전

## 완료 기준

#5가 완료되려면 다음 조건을 만족해야 한다.

- 수동 운영 메모와 override의 목적이 정의되어 있다.
- 데이터 모델이 정의되어 있다.
- 자동 상태와 수동 상태 결합 규칙이 정의되어 있다.
- UI와 API 요구사항이 정리되어 있다.
- 안전 기준과 stale 기준이 명확하다.
- 후속 구현자가 JSON 또는 DB 기반으로 바로 구현할 수 있다.
