# 22. 실행자용 작업 프롬프트 생성 모델

이 문서는 `0-a-control`에서 로컬 모델, CLI 에이전트, 외부 실행자에게 전달할 작업 프롬프트를 일관되게 생성하기 위한 기준을 정의한다.

## 목적

작업 지시를 매번 수동으로 작성하면 다음 문제가 생긴다.

- 작업 범위 누락
- 외부 프로젝트 혼입
- 완료 기준 불명확
- 로컬 필요 작업과 원격 가능 작업 혼동
- 검증 명령 누락
- 보고 형식 불일치
- 민감 정보 출력 위험

프롬프트 생성 기능은 작업 항목의 상태, 검증 필요 여부, 수동 override, 로컬 필요 여부를 반영해 실행자가 바로 수행할 수 있는 지시문을 만들어야 한다.

## 기본 원칙

1. 프롬프트는 단일 작업 단위로 생성한다.
2. 대상 저장소와 범위를 명확히 적는다.
3. 제외 범위를 반드시 포함한다.
4. 완료 기준을 검증 가능한 형태로 적는다.
5. 로컬 필요 작업에는 명령과 보고 형식을 포함한다.
6. 원격 가능 작업에는 GitHub/문서/정적 리뷰 범위를 명확히 한다.
7. 민감 정보 출력 금지 규칙을 항상 포함한다.
8. 사용자가 이미 준 정보는 다시 묻지 않는다.
9. 실행하지 못한 검증은 `미실행`으로 보고하게 한다.

## 입력 데이터

프롬프트 생성기는 다음 데이터를 받을 수 있다.

| 입력 | 설명 |
|---|---|
| `work_item` | #6 normalized work item |
| `classification` | #3 automatic/effective status |
| `manual_override` | #5 manual override |
| `validation_checklist` | #7 validation checklist |
| `repository` | 대상 저장소 |
| `changed_files` | 관련 파일 목록 |
| `local_needed` | 로컬 실행 필요 여부 |
| `guards` | 위험/금지/주의 플래그 |
| `links` | issue/PR/doc 링크 |

## 프롬프트 유형

### 1. 구현 프롬프트

목적:

- 코드 또는 문서 변경을 수행한다.

포함 항목:

- 목표
- 대상 저장소
- 대상 브랜치
- 작업 범위
- 제외 범위
- 구현 기준
- 검증 명령
- 보고 형식

### 2. 로컬 검증 프롬프트

목적:

- 사용자의 로컬 머신에서 서버 실행, 테스트, 브라우저 확인, 로컬 모델 확인을 수행한다.

포함 항목:

- 실행 환경 확인 명령
- 실행 명령
- 기대 결과
- PASS/FAIL 기준
- 실패 로그 요약 방식
- 민감 정보 출력 금지

### 3. 문서 리뷰 프롬프트

목적:

- 문서 변경의 범위, 정확성, 충돌 가능성, 누락을 검토한다.

포함 항목:

- 읽을 문서
- 확인할 기준
- 링크 정확성
- 외부 프로젝트 혼입 여부
- 중복/충돌 여부
- 수정 제안

### 4. PR 리뷰 프롬프트

목적:

- PR의 변경 범위와 merge readiness를 판단한다.

포함 항목:

- PR 링크
- 변경 파일
- 관련 이슈
- 검증 결과
- merge blocking condition
- ready/merge 금지 조건

### 5. 상태 점검 프롬프트

목적:

- 이슈/PR/작업 큐 상태를 갱신한다.

포함 항목:

- 현재 상태
- 자동 분류
- 수동 override
- 검증 상태
- 다음 액션
- stale 여부

## 공통 프롬프트 구조

모든 프롬프트는 다음 구조를 따른다.

1. 제목
2. 목표
3. 대상
4. 현재 상태
5. 작업 범위
6. 제외 범위
7. 실행 절차
8. 검증 기준
9. 금지 사항
10. 보고 형식
11. 완료 기준

## 공통 금지 사항

모든 프롬프트에 포함한다.

- 대상 저장소 외부 프로젝트를 작업 범위에 포함하지 마십시오.
- 요청되지 않은 대규모 리팩터링을 하지 마십시오.
- 로컬 비밀값, 토큰, 세션 파일 내용을 출력하지 마십시오.
- 검증 없이 `정상`, `완료`, `통과`라고 쓰지 마십시오.
- 실패 로그에는 민감 정보를 포함하지 마십시오.
- merge, close, delete 같은 destructive action은 별도 명시 없이 실행하지 마십시오.

## 로컬 검증 프롬프트 템플릿

아래는 로컬 검증용 기본 템플릿이다. 중첩 Markdown 코드블록을 피하기 위해 명령은 inline 또는 목록 형태로 제공한다.

```text
로컬 검증 프롬프트 — <작업 제목>

목표:
<검증 목표>

대상:
- 저장소: <owner/repo>
- 브랜치: <branch>
- 관련 PR/Issue: <links>

현재 상태:
- 자동 상태: <automatic_status>
- 수동 override: <manual_status or none>
- 검증 상태: <validation_status>
- 로컬 필요 여부: <yes/no>

작업 범위:
- <scope item>

제외 범위:
- <excluded item>

실행 절차:
1. 저장소 상태 확인
   - git status --short
   - git branch --show-current
   - git log -1 --oneline
2. 환경 확인
   - python --version
   - pip --version
3. 검증 명령 실행
   - <command>

PASS 기준:
- <pass criteria>

FAIL 기준:
- <fail criteria>

금지 사항:
- 비밀값, 토큰, 세션 파일 내용을 출력하지 마십시오.
- 검증하지 않은 항목을 PASS로 쓰지 마십시오.

보고 형식:
- OS:
- Shell:
- Branch:
- HEAD:
- Commands run:
- Result: PASS/FAIL
- Failure summary:
- Next action:
```

## 문서 리뷰 프롬프트 템플릿

```text
문서 리뷰 프롬프트 — <문서/PR 제목>

목표:
문서가 현재 저장소 기준과 맞는지 검토하십시오.

대상:
- 저장소: <owner/repo>
- 파일: <files>
- 관련 이슈/PR: <links>

확인 항목:
- 문서가 대상 저장소 기준으로 작성되었는가
- 외부 프로젝트 언급이 섞이지 않았는가
- 현재 README/기존 docs와 충돌하지 않는가
- 링크가 실제 파일과 맞는가
- 후속 구현자가 실행 가능한 수준으로 구체적인가

금지 사항:
- 문서 범위를 넘어 코드 변경을 제안하지 마십시오.
- 검증하지 않은 링크를 정상이라고 쓰지 마십시오.

보고 형식:
- Result: PASS/FAIL
- Issues found:
- Suggested edits:
- Blocking concerns:
```

## PR 리뷰 프롬프트 템플릿

```text
PR 리뷰 프롬프트 — <PR 번호/제목>

목표:
PR의 변경 범위, 검증 상태, merge readiness를 판단하십시오.

대상:
- 저장소: <owner/repo>
- PR: <url>
- 관련 이슈: <links>

확인 항목:
- 변경 파일이 PR 설명과 일치하는가
- 관련 이슈 범위를 벗어나지 않는가
- 검증 결과가 충분한가
- 로컬 필요 검증이 남아 있는가
- 문서/코드 충돌 위험이 있는가

판정:
- READY
- NEEDS_REVIEW
- NEEDS_VALIDATION
- BLOCKED
- NO_ACTION

보고 형식:
- Result:
- Scope check:
- Validation check:
- Blocking issues:
- Recommended next action:
```

## 프롬프트 생성 규칙

### local_needed가 true인 경우

반드시 포함:

- 로컬 실행 명령
- 환경 정보 수집 명령
- PASS/FAIL 기준
- 실패 로그 요약 방식
- “로컬 비밀값 출력 금지”

### validation_required guard가 있는 경우

반드시 포함:

- 검증 항목 목록
- 실행 명령
- 어떤 결과가 READY 조건인지
- 실행하지 못한 경우 `미실행`으로 보고하라는 지시

### manual override가 있는 경우

반드시 포함:

- override 상태
- override 이유
- override가 자동 상태보다 우선한다는 설명
- override 해제 조건, 있는 경우

### blocked 상태인 경우

반드시 포함:

- blocker
- 재개 조건
- 지금 실행 가능한 대체 작업이 있는지

### docs-only 작업인 경우

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
- `Copy PR review prompt`
- `Copy status check prompt`

버튼은 현재 상태에 따라 노출한다.

예:

- `LOCAL_NEEDED` → local validation prompt 우선
- `NEEDS_REVIEW` → PR review 또는 document review prompt 우선
- `BLOCKED` → status check prompt 우선
- `NEEDS_IMPLEMENTATION` → implementation prompt 우선

## API 요구사항

후속 구현 시 다음 endpoint를 고려한다.

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

목적:

- 사용 가능한 prompt type과 템플릿 목록 반환

## 저장 방식

1차 구현은 생성형으로 충분하다.

- 프롬프트를 DB에 저장하지 않고, 현재 source data에서 즉시 생성
- 사용자가 복사한 뒤 실행자에게 전달

후속 구현:

- 생성 이력 저장
- 어떤 prompt가 어떤 결과 보고로 이어졌는지 연결
- validation checklist와 자동 연결

## 안전 기준

- 프롬프트에 secret 값을 넣지 않는다.
- 환경변수명은 포함할 수 있지만 값은 포함하지 않는다.
- 세션 파일 경로는 필요 시 경로명만 포함하고 내용은 포함하지 않는다.
- 외부 write action은 명시적 사용자 승인 없이는 지시하지 않는다.
- merge/close/delete는 기본 프롬프트에서 제외한다.

## 후속 구현 순서

1. prompt template constants 추가
2. work item → prompt context 변환 함수 추가
3. prompt generator 단위 테스트 추가
4. `/api/executor-prompts/generate` endpoint 추가
5. board-v2 상세 모달에 copy prompt 버튼 추가
6. local-needed 카드에 local validation prompt 우선 노출
7. validation result 보고 형식과 연결

## 완료 기준

#8이 완료되려면 다음 조건을 만족해야 한다.

- 프롬프트 유형이 정의되어 있다.
- 공통 구조와 금지 사항이 정의되어 있다.
- 로컬 검증/문서 리뷰/PR 리뷰 템플릿이 있다.
- local-needed, validation-required, manual override, blocked 상태별 생성 규칙이 있다.
- UI/API 요구사항이 있다.
- 후속 구현자가 prompt generator를 만들 수 있다.
