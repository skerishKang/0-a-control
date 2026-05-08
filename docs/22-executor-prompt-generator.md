# 22. 실행자용 작업 프롬프트 생성 모델

이 문서는 로컬 모델, CLI 에이전트, GitHub 가능 웹모델, 로컬 실행자에게 전달할 작업 프롬프트를 일관되게 생성하기 위한 기준을 정의한다.

## 목적

작업 프롬프트는 다음 문제를 줄여야 한다.

- 작업 범위 누락
- 외부 프로젝트 혼입
- 완료 기준 불명확
- 로컬 필요 작업과 원격 가능 작업 혼동
- 검증 명령 누락
- 보고 형식 불일치
- 민감 정보 노출 위험

## 원칙

1. 프롬프트는 단일 작업 단위로 생성한다.
2. 대상 저장소와 범위를 명확히 적는다.
3. 제외 범위를 포함한다.
4. 완료 기준을 검증 가능한 형태로 적는다.
5. 로컬 필요 작업에는 명령과 보고 형식을 포함한다.
6. GitHub 웹모델 가능 작업은 로컬 실행자보다 먼저 배정한다.
7. 검증하지 못한 항목은 미실행으로 보고하게 한다.

## 입력 데이터

| 입력 | 설명 |
|---|---|
| `work_item` | normalized work item |
| `classification` | automatic/effective status |
| `manual_override` | 수동 override |
| `validation_checklist` | 검증 체크리스트 |
| `repository` | 대상 저장소 |
| `changed_files` | 관련 파일 목록 |
| `execution_context` | remote, github_web, local |
| `guards` | 위험/주의 플래그 |
| `links` | issue/PR/doc 링크 |

## 프롬프트 유형

### 구현 프롬프트

- 코드 또는 문서 변경 수행
- 목표, 대상 저장소, 브랜치, 범위, 제외 범위, 구현 기준, 검증 명령, 보고 형식 포함

### 로컬 검증 프롬프트

- 서버 실행, 테스트, 브라우저 확인, 로컬 모델 확인 수행
- 환경 확인 명령, 실행 명령, 기대 결과, PASS/FAIL 기준, 실패 요약 방식 포함

### GitHub 웹모델 프롬프트

- GitHub UI 또는 브라우저 기반 GitHub 조작 수행
- API connector가 실패한 draft 해제, 상태 확인, UI 확인 작업에 사용
- merge, close, branch update 같은 고위험 작업은 별도 승인 기준이 있을 때만 포함

### 문서 리뷰 프롬프트

- 문서 변경의 범위, 정확성, 충돌 가능성, 누락 검토
- 읽을 문서, 링크 정확성, 외부 프로젝트 혼입 여부, 중복/충돌 여부 포함

### PR 리뷰 프롬프트

- PR 변경 범위와 merge readiness 판단
- PR 링크, 변경 파일, 관련 이슈, 검증 결과, blocking condition 포함

### 상태 점검 프롬프트

- 이슈/PR/작업 큐 상태 갱신
- 현재 상태, 자동 분류, 수동 override, 검증 상태, 다음 액션, stale 여부 포함

## 공통 구조

1. 제목
2. 목표
3. 대상
4. 현재 상태
5. 작업 범위
6. 제외 범위
7. 실행 절차
8. 검증 기준
9. 주의 사항
10. 보고 형식
11. 완료 기준

## 실행 컨텍스트 선택 규칙

### `REMOTE_DOABLE`

- GitHub API와 파일 변경으로 처리 가능
- 문서/정책/정적 리뷰 중심

### `GITHUB_WEB_MODEL_NEEDED`

- GitHub API connector가 실패했지만 GitHub UI로 가능한 작업
- draft 해제, GitHub UI 상태 확인, Actions UI 확인 등

### `LOCAL_NEEDED`

- 서버 실행, 테스트, 브라우저 렌더링, 로컬 모델, Telegram 세션, OS 설정 확인 필요

### `MIXED_REMOTE_CODE_LOCAL_VALIDATION`

- 원격에서 PR 생성 가능
- 실제 실행 검증은 로컬 필요

## 생성 규칙

### local-needed 작업

포함:

- 로컬 실행 명령
- 환경 정보 수집 명령
- PASS/FAIL 기준
- 실패 요약 방식
- 민감 정보 값 출력 금지

### validation-required 작업

포함:

- 검증 항목 목록
- 실행 명령
- READY 조건
- 미실행 보고 규칙

### manual override가 있는 작업

포함:

- override 상태
- override 이유
- override 해제 조건

### blocked 작업

포함:

- blocker
- 재개 조건
- 지금 실행 가능한 대체 작업 여부

### docs-only 작업

포함:

- 문서 리뷰 기준
- 링크 검토
- 기존 문서와 중복/충돌 확인

제외:

- 불필요한 서버 실행
- 불필요한 브라우저 검증

## UI 요구사항

작업 상세 화면 또는 카드에서 다음 기능을 제공한다.

- `Copy implementation prompt`
- `Copy local validation prompt`
- `Copy GitHub web prompt`
- `Copy PR review prompt`
- `Copy status check prompt`

상태별 우선 노출:

- `LOCAL_NEEDED` → local validation prompt
- `GITHUB_WEB_MODEL_NEEDED` → GitHub web prompt
- `NEEDS_REVIEW` → PR/document review prompt
- `BLOCKED` → status check prompt
- `NEEDS_IMPLEMENTATION` → implementation prompt

## API 요구사항

### POST `/api/executor-prompts/generate`

입력:

- `target_type`
- `target_id`
- `prompt_type`
- 선택: `include_validation`, `include_override`, `include_links`

출력:

- `prompt_title`
- `prompt_body`
- `warnings`
- `source_data`

### GET `/api/executor-prompts/templates`

- 사용 가능한 prompt type과 템플릿 목록 반환

## 저장 방식

1차 구현:

- 프롬프트를 저장하지 않고 현재 source data에서 즉시 생성

후속 구현:

- 생성 이력 저장
- prompt와 결과 보고 연결
- validation checklist와 자동 연결

## 안전 기준

- 실제 민감 값은 prompt context에 넣지 않는다.
- 환경변수명은 포함할 수 있지만 값은 포함하지 않는다.
- 세션 파일 경로는 필요 시 경로명만 포함하고 내용은 포함하지 않는다.
- 외부 시스템 변경 작업은 별도 승인 기준을 따른다.

## 후속 구현 순서

1. prompt template constants
2. work item to prompt context 변환 함수
3. prompt generator 단위 테스트
4. `/api/executor-prompts/generate`
5. board-v2 copy prompt 버튼
6. GitHub web prompt 단계 추가
7. validation result 보고 형식과 연결
