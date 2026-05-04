# 21. 검증 체크리스트 및 결과 기록 모델

이 문서는 `0-a-control`에서 작업별 검증 상태를 기록하고 운영판에 표시하기 위한 체크리스트 모델을 정의한다. 기존 quest verdict는 “작업 결과 판정”에 가깝고, 이 문서의 validation checklist는 “실행/빌드/테스트/브라우저 확인 증거”를 별도 기록하는 계층이다.

## 목적

검증 체크리스트는 다음 질문에 답해야 한다.

- 이 작업은 실제로 실행되었는가?
- 어떤 명령을 실행했는가?
- 결과는 PASS/FAIL/SKIPPED 중 무엇인가?
- 실패했다면 요약 로그와 다음 조치가 무엇인가?
- 로컬 실행이 필요한데 아직 실행되지 않은 상태인가?
- 브라우저 확인 또는 스크린샷 확인이 필요한가?
- 검증이 완료되지 않았는데 READY로 보이는 것을 막을 수 있는가?

## 기본 원칙

1. 검증 결과는 작업 상태와 별도로 저장한다.
2. 실행하지 않은 검증은 `not_started` 또는 `not_applicable`로 명확히 표시한다.
3. `skipped`는 반드시 이유가 있어야 한다.
4. 실패 로그는 요약만 저장하고 민감 정보는 기록하지 않는다.
5. 로컬 환경에서만 가능한 검증은 `local_needed`로 표시한다.
6. 검증이 필요한 작업은 검증 완료 전 `READY`로 보이지 않아야 한다.
7. 검증 기록은 나중에 재현 가능한 명령과 환경 정보를 포함해야 한다.

## 검증 대상

검증 체크리스트는 다음 대상에 붙을 수 있다.

| 대상 | 예시 |
|---|---|
| GitHub PR | `pr:16` |
| GitHub issue | `issue:7` |
| 내부 quest | `quest:<id>` |
| 내부 plan | `plan:<id>` |
| global dashboard | `global:dashboard` |
| release/deploy task | `deploy:<id>` |

## 검증 항목 종류

기본 항목:

| Key | 의미 | 로컬 필요 여부 |
|---|---|---:|
| `install` | 의존성 설치 확인 | yes |
| `lint` | lint 또는 정적 검사 | yes |
| `typecheck` | 타입 검사 | yes |
| `unit_test` | 단위 테스트 | yes |
| `integration_test` | 통합 테스트 | yes |
| `build` | 빌드 확인 | yes |
| `server_start` | 서버 실행 확인 | yes |
| `api_smoke` | 주요 API smoke test | yes |
| `browser_smoke` | 브라우저 렌더링 확인 | yes |
| `manual_review` | 문서/범위 수동 검토 | no |
| `security_review` | 민감정보/노출 위험 확인 | no 또는 yes |
| `docs_review` | 문서 정확성 검토 | no |

## 상태 값

| 상태 | 의미 |
|---|---|
| `not_started` | 아직 실행하지 않음 |
| `passed` | 통과 |
| `failed` | 실패 |
| `skipped` | 의도적으로 건너뜀 |
| `not_applicable` | 해당 작업에 필요 없음 |
| `blocked` | 선행 조건 때문에 실행 불가 |

## 데이터 모델

### Validation checklist

필드:

| 필드 | 필수 | 설명 |
|---|---:|---|
| `id` | yes | checklist 고유 ID |
| `target_type` | yes | `pr`, `issue`, `quest`, `plan`, `global`, `deploy` |
| `target_id` | yes | 대상 ID |
| `required_items` | yes | 필요한 검증 항목 목록 |
| `overall_status` | yes | 종합 상태 |
| `created_at` | yes | 생성 시각 |
| `updated_at` | yes | 수정 시각 |

### Validation result item

필드:

| 필드 | 필수 | 설명 |
|---|---:|---|
| `key` | yes | 검증 항목 key |
| `label` | yes | 사용자 표시 이름 |
| `status` | yes | 상태 값 |
| `command` | no | 실행 명령 |
| `environment` | no | OS/Shell/Python/Node 등 |
| `summary` | no | 결과 요약 |
| `log_excerpt` | no | 실패 로그 일부. 민감 정보 제외 |
| `evidence_url` | no | PR 댓글, 파일, 스크린샷 등 링크 |
| `run_at` | no | 실행 시각 |
| `runner` | no | 사용자, 로컬 모델, agent 이름 |
| `skip_reason` | no | skipped일 때 필수 |
| `is_local_needed` | yes | 로컬 실행 필요 여부 |

예시:

```json
{
  "id": "validation_pr_16",
  "target_type": "pr",
  "target_id": "16",
  "overall_status": "blocked",
  "required_items": [
    {
      "key": "unit_test",
      "label": "GitHub service unit tests",
      "status": "not_started",
      "command": "python -m unittest tests.test_github_service",
      "summary": "Local execution required before ready/merge.",
      "is_local_needed": true
    }
  ],
  "created_at": "2026-05-04T02:40:00+09:00",
  "updated_at": "2026-05-04T02:40:00+09:00"
}
```

## overall_status 산출 규칙

| 조건 | overall_status |
|---|---|
| 필수 항목 중 `failed` 있음 | `failed` |
| 필수 항목 중 `blocked` 있음 | `blocked` |
| 필수 항목 중 `not_started` 있음 | `not_started` |
| 필수 항목이 모두 `passed` 또는 `not_applicable` | `passed` |
| 모든 필수 항목이 `skipped`이고 이유가 있음 | `skipped` |

## 작업 유형별 기본 체크리스트

### 문서 전용 PR

필수:

- `docs_review`
- `manual_review`

일반적으로 불필요:

- `install`
- `unit_test`
- `build`
- `browser_smoke`

### Python 런타임 코드 PR

필수:

- `unit_test`
- `integration_test` 또는 관련 smoke test
- `manual_review`

상황별:

- `server_start`
- `api_smoke`

### 프론트엔드 UI PR

필수:

- `browser_smoke`
- `manual_review`
- JS syntax check 또는 관련 정적 검사

상황별:

- `api_smoke`
- screenshot evidence

### 배포/접근 경로 PR

필수:

- `security_review`
- `docs_review`
- `manual_review`

상황별:

- `server_start`
- reverse proxy smoke test

## UI 요구사항

### 목록 카드

작업 카드에는 다음을 표시한다.

- overall validation status
- required item count
- failed count
- local-needed count
- last run time
- 다음 필요한 검증 명령

### 상세 모달

상세 모달에는 다음을 표시한다.

- 전체 checklist
- 항목별 status
- command
- runner
- run_at
- summary
- 실패 로그 요약
- skipped reason
- evidence link

### 입력 UI

검증 결과 입력 시 필수:

- target
- item key
- status
- summary

조건부 필수:

- failed: log excerpt 또는 failure summary
- skipped: skip reason
- passed: command 또는 review evidence 중 하나

## API 요구사항

### GET `/api/validation-checklists`

쿼리:

- `target_type`
- `target_id`
- `status`

반환:

- checklist 목록

### POST `/api/validation-checklists`

목적:

- 대상에 필요한 checklist 생성

필수 body:

- `target_type`
- `target_id`
- `required_items`

### PATCH `/api/validation-checklists/<id>/items/<key>`

목적:

- 특정 검증 항목 결과 갱신

수정 가능:

- `status`
- `command`
- `environment`
- `summary`
- `log_excerpt`
- `evidence_url`
- `runner`
- `skip_reason`

### POST `/api/validation-checklists/<id>/recompute`

목적:

- 항목 상태를 기준으로 `overall_status` 재계산

## 저장 방식

### 1차 구현 권장

- `data/runtime/validation_checklists.json`
- Git 커밋 대상 아님
- 로컬 검증 결과 저장소로 사용

### 후속 구현 권장

- SQLite 테이블
- validation_checklists
- validation_results
- validation_history

## 안전 기준

- 실패 로그에는 토큰, 세션, 개인 정보가 들어가면 안 된다.
- 환경변수 전체 dump를 저장하지 않는다.
- 세션 파일 경로는 필요 시 존재 여부만 기록한다.
- screenshot은 민감 화면이 포함되지 않았는지 확인한다.
- 검증 결과는 merge/close를 자동 실행하지 않는다.

## work queue와의 연결

validation checklist는 #6 작업 큐에 다음 영향을 준다.

- overall_status가 `not_started` → `VALIDATION_NEEDED`
- overall_status가 `failed` → `VALIDATION_NEEDED` 또는 `BLOCKED`
- local-needed 항목 존재 → `LOCAL_NEEDED`
- all passed → 자동 상태에 따라 `REVIEW_NEEDED` 또는 `READY`

## 후속 구현 순서

1. JSON 기반 validation storage 모듈 추가
2. checklist/item 상태 산출 함수 추가
3. 단위 테스트 추가
4. `/api/validation-checklists` GET/POST 추가
5. item PATCH endpoint 추가
6. board-v2 상세 모달에 validation 표시
7. work queue 산출에 validation status 반영
8. 로컬 실행자 프롬프트 생성과 연결

## 완료 기준

#7이 완료되려면 다음 조건을 만족해야 한다.

- 검증 항목 종류와 상태 값이 정의되어 있다.
- checklist와 result item 데이터 모델이 정의되어 있다.
- 작업 유형별 기본 체크리스트가 정의되어 있다.
- overall_status 산출 규칙이 있다.
- UI/API/저장 방식 요구사항이 있다.
- work queue와 연결 기준이 명확하다.
