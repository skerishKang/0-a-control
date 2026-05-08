# 19. 수동 운영 메모 및 판단 Override 모델

이 문서는 자동 분류만으로 표현하기 어려운 운영 판단을 수동으로 기록하고 override하는 기준을 정의한다.

## 목적

수동 override는 자동 상태를 삭제하지 않고, 그 위에 사용자의 운영 판단을 명시적으로 덧씌우는 계층이다.

필요한 경우:

- 자동 분류는 READY지만 실제로는 검증이 필요함
- 특정 작업을 보류함
- blocker가 외부 상황에 의존함
- 특정 PR/issue를 관찰만 함
- 사용자가 직접 우선순위를 조정함

## 기본 원칙

1. 자동 상태와 수동 override 상태를 분리한다.
2. override에는 이유가 있어야 한다.
3. 작성자와 작성/수정 시각을 남긴다.
4. override는 비활성화 가능해야 한다.
5. 외부 destructive action을 자동 실행하지 않는다.
6. 오래된 override는 stale로 표시한다.

## 대상 객체

| 대상 | 예시 |
|---|---|
| GitHub issue | `issue:5` |
| GitHub PR | `pr:16` |
| 내부 quest | `quest:<id>` |
| 내부 plan | `plan:<id>` |
| session | `session:<id>` |
| external source | `source:telegram` |
| global dashboard | `global:dashboard` |

## Override record

권장 필드:

| 필드 | 필수 | 설명 |
|---|---:|---|
| `id` | yes | override 고유 ID |
| `target_type` | yes | `issue`, `pr`, `quest`, `plan`, `session`, `source`, `global` |
| `target_id` | yes | 대상 식별자 |
| `manual_status` | yes | 수동 상태 |
| `reason` | yes | override 이유 |
| `note` | no | 추가 메모 |
| `priority` | no | `P0`, `P1`, `P2`, `P3` |
| `expires_at` | no | 만료 기준 |
| `created_at` | yes | 생성 시각 |
| `updated_at` | yes | 수정 시각 |
| `created_by` | no | 사용자/agent 이름 |
| `source` | yes | `manual`, `local-agent`, `imported` |
| `is_active` | yes | 현재 적용 여부 |

## 수동 상태 값

자동 분류 상태를 우선 재사용한다.

- `READY`
- `IN_PROGRESS`
- `BLOCKED`
- `NEEDS_IMPLEMENTATION`
- `NEEDS_REVIEW`
- `NEEDS_VALIDATION`
- `DONE`
- `NO_ACTION`

추가 수동 전용 상태:

- `PINNED`
- `WATCH`
- `IGNORE_UNTIL`
- `DO_NOT_MERGE`
- `DO_NOT_CLOSE`

## 결합 규칙

우선순위:

1. 금지성 override
2. active manual status
3. automatic status
4. default fallback

UI/API는 `automatic`, `manual`, `effective`를 함께 반환하는 구조가 좋다.

## UI 요구사항

목록 카드/행:

- 제목
- 자동 상태 배지
- 수동 override 배지
- override 이유 요약
- priority
- 마지막 업데이트 시각
- stale 여부

상세 모달:

- 자동 분류 결과
- 수동 override 결과
- 변경 이력
- 메모
- effective status
- override 생성/수정/해제 버튼

폼 검증:

- 이유가 비어 있으면 저장 불가
- `DONE`은 완료 근거 필요
- `NO_ACTION`은 이유 필요
- 금지성 override는 명확히 표시

## API 요구사항

- `GET /api/ops-overrides`
- `POST /api/ops-overrides`
- `PATCH /api/ops-overrides/<id>`
- 실제 삭제보다 `is_active=false` 비활성화 권장

## 저장 방식

1차:

- `data/runtime/ops_overrides.json`
- Git 커밋 대상 아님

후속:

- SQLite 테이블
- 변경 이력 테이블 분리
- backup 대상 포함

## stale 기준

- 14일 이상 갱신 없음
- `expires_at` 경과
- 대상 issue/PR이 닫혔는데 active 상태
- manual status와 automatic status가 장기간 충돌

## 안전 기준

- override는 외부 시스템을 직접 변경하지 않는다.
- 민감 정보는 reason/note에 넣지 않는다.
- token, session, 개인 식별 정보는 기록하지 않는다.

## 후속 구현 순서

1. JSON 저장 모듈
2. CRUD 단위 테스트
3. `/api/ops-overrides` GET/POST
4. 상세 모달 표시
5. effective status 배지
6. stale 경고
7. SQLite 이전
