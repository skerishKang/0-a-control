# 21. 검증 체크리스트 및 결과 기록 모델

이 문서는 작업별 검증 상태를 기록하고 운영판에 표시하기 위한 체크리스트 모델을 정의한다.

## 목적

검증 체크리스트는 다음 질문에 답해야 한다.

- 이 작업은 실제로 실행되었는가?
- 어떤 명령을 실행했는가?
- 결과는 무엇인가?
- 실패했다면 요약과 다음 조치는 무엇인가?
- 로컬 실행이나 브라우저 확인이 필요한가?
- 검증이 끝나지 않았는데 READY로 보이는 것을 막을 수 있는가?

## 원칙

1. 검증 결과는 작업 상태와 별도로 저장한다.
2. 실행하지 않은 검증은 `not_started` 또는 `not_applicable`로 표시한다.
3. `skipped`는 이유가 있어야 한다.
4. 실패 로그는 요약만 저장하고 민감 정보는 기록하지 않는다.
5. 로컬 검증은 `local_needed`로 표시한다.
6. 검증이 필요한 작업은 검증 완료 전 READY로 보이지 않아야 한다.

## 검증 대상

| 대상 | 예시 |
|---|---|
| GitHub PR | `pr:16` |
| GitHub issue | `issue:7` |
| 내부 quest | `quest:<id>` |
| 내부 plan | `plan:<id>` |
| global dashboard | `global:dashboard` |
| deploy task | `deploy:<id>` |

## 검증 항목 종류

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

- `not_started`
- `passed`
- `failed`
- `skipped`
- `not_applicable`
- `blocked`

## 데이터 모델

### Validation checklist

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

## overall_status 산출 규칙

| 조건 | overall_status |
|---|---|
| 필수 항목 중 `failed` 있음 | `failed` |
| 필수 항목 중 `blocked` 있음 | `blocked` |
| 필수 항목 중 `not_started` 있음 | `not_started` |
| 필수 항목이 모두 `passed` 또는 `not_applicable` | `passed` |
| 모든 필수 항목이 `skipped`이고 이유가 있음 | `skipped` |

## 작업 유형별 기본 체크리스트

문서 전용 PR:

- `docs_review`
- `manual_review`

Python 런타임 코드 PR:

- `unit_test`
- 관련 smoke test
- `manual_review`

프론트엔드 UI PR:

- `browser_smoke`
- `manual_review`
- JS syntax check

배포/접근 경로 PR:

- `security_review`
- `docs_review`
- `manual_review`

## UI 요구사항

목록 카드:

- overall validation status
- required item count
- failed count
- local-needed count
- last run time
- 다음 필요한 검증 명령

상세 모달:

- 전체 checklist
- 항목별 status
- command
- runner
- run_at
- summary
- 실패 로그 요약
- skipped reason
- evidence link

입력 UI 조건:

- failed: failure summary 필요
- skipped: skip reason 필요
- passed: command 또는 review evidence 필요

## API 요구사항

- `GET /api/validation-checklists`
- `POST /api/validation-checklists`
- `PATCH /api/validation-checklists/<id>/items/<key>`
- `POST /api/validation-checklists/<id>/recompute`

## 저장 방식

1차:

- `data/runtime/validation_checklists.json`
- Git 커밋 대상 아님

후속:

- SQLite 테이블
- validation history 분리

## 안전 기준

- 실패 로그에 토큰, 세션, 개인 정보를 넣지 않는다.
- 환경변수 전체 dump를 저장하지 않는다.
- 세션 파일은 존재 여부만 기록한다.
- 검증 결과는 외부 작업을 자동 실행하지 않는다.

## work queue 연결

- `not_started` → `VALIDATION_NEEDED`
- `failed` → `VALIDATION_NEEDED` 또는 `BLOCKED`
- local-needed 항목 존재 → `LOCAL_NEEDED`
- all passed → automatic status에 따라 `REVIEW_NEEDED` 또는 `READY`

## 후속 구현 순서

1. JSON validation storage
2. status 산출 함수
3. 단위 테스트
4. `/api/validation-checklists` endpoint
5. board-v2 상세 모달 표시
6. work queue 연결
7. 로컬 실행자 프롬프트 연결
