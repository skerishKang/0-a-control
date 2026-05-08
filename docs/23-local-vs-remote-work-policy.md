# 23. 로컬 필요 작업과 원격 처리 가능 작업 구분 기준

이 문서는 `0-a-control` 운영에서 어떤 작업을 원격으로 처리할 수 있고, 어떤 작업은 GitHub 웹모델 또는 로컬 실행자가 필요한지 구분하는 기준을 정의한다.

## 목적

- 원격에서 가능한 작업은 사용자를 기다리지 않고 진행한다.
- GitHub UI로 가능한 작업은 로컬 실행자보다 GitHub 웹모델에 먼저 배정한다.
- 로컬에서만 검증 가능한 작업은 명확히 분리한다.
- 로컬 실행자에게 줄 명령과 보고 형식을 표준화한다.
- 검증하지 않은 내용을 PASS로 처리하지 않는다.
- 민감 정보가 원격 대화나 공개 저장소에 노출되지 않게 한다.

## 처리 순서

1. 현재 에이전트가 GitHub API로 직접 처리 가능한 작업은 직접 처리한다.
2. GitHub API connector 한계로 실패했지만 GitHub UI로 가능한 작업은 GitHub-capable web model에 넘긴다.
3. 실제 머신 실행, localhost, 로컬 모델, 세션, OS 설정 확인이 필요한 작업만 로컬 실행자에게 넘긴다.

## 원격 처리 가능 작업

### GitHub API/파일 작업

- issue 생성/수정/댓글
- PR 생성/설명 작성/상태 확인
- changed files 확인
- 브랜치 생성
- 문서 파일 생성/수정
- 정적 코드 리뷰
- open/closed issue 및 PR 목록 확인

### 문서 및 정책 정리

- README 보강
- 운영 문서 추가
- 체크리스트 작성
- 아키텍처/데이터 모델 문서화
- 실행자 프롬프트 작성
- 이슈별 진행 상황 기록

### 안전한 코드 준비

조건:

- 변경 범위가 작고 명확함
- 로컬 데이터나 세션 파일에 접근하지 않음
- secret 값이 필요하지 않음
- 테스트 명령을 명확히 제시 가능
- 실행 결과를 직접 검증한 것처럼 주장하지 않음

예:

- 순수 함수 모듈 추가
- mocked unit test 추가
- 정적 template 추가
- API route 초안 추가

## GitHub 웹모델 필요 작업

다음 작업은 GitHub API가 실패했거나 브라우저 UI 확인이 필요한 경우 GitHub 웹모델에 먼저 넘긴다.

- draft PR ready-for-review 전환
- GitHub UI 상태 확인
- GitHub Actions UI 확인
- PR setting 확인
- API connector가 제한된 UI 작업

## 로컬 필요 작업

### 서버 및 브라우저

- `python scripts/server.py` 실행
- `start-control-tower.bat` 실행
- `./start-control-tower.sh` 실행
- `http://localhost:4310` 접속
- `/board-v2.html` 렌더링 확인
- 브라우저 콘솔 오류 확인
- 스크린샷 확인

### 테스트 및 빌드

- `python -m unittest ...`
- 전체 test discovery
- Node/JS syntax check
- OS별 launcher 확인
- 포트 충돌 확인
- requirements 설치 확인

### 로컬 데이터 및 세션

- SQLite DB 상태 확인
- `data/runtime/` 파일 확인
- Telegram 세션 생성
- Telegram sync 실행
- 로컬 queue 파일 처리 확인
- 민감 파일 존재 여부 확인

### 로컬 모델 및 에이전트

- 로컬 모델 실행
- CLI agent 실행
- Kilo/OpenCode/Codex/Gemini CLI launcher 확인
- agent session 기록 확인
- 모델 응답 품질 확인

### 네트워크/배포

- LAN 접근 확인
- reverse proxy 실제 연결 확인
- TLS 인증서 적용 확인
- firewall 규칙 확인
- process manager 확인

## 혼합 작업 기준

| 작업 | 원격 처리 | 후속 필요 |
|---|---|---|
| Python service 추가 | 코드/테스트 PR 작성 | unit test 실행 |
| server route 추가 | 코드 PR 작성 | 서버 실행 + curl 확인 |
| board-v2 UI 추가 | 코드 PR 작성 | 브라우저 렌더링 확인 |
| 문서 추가 | PR 작성 | 보통 불필요 |
| 배포 문서 추가 | PR 작성 | 실제 배포 검증은 로컬/서버 필요 |
| Telegram 기능 수정 | 코드 PR 작성 가능 | 인증/동기화 실행 필요 |
| GitHub UI 조작 | 웹모델 가능 | 실패 시 로컬/수동 확인 |

## 작업 분류 라벨

- `REMOTE_DOABLE`
- `GITHUB_WEB_MODEL_NEEDED`
- `LOCAL_NEEDED`
- `MIXED_REMOTE_CODE_LOCAL_VALIDATION`
- `DOCS_ONLY_REMOTE_SAFE`
- `BROWSER_VALIDATION_REQUIRED`
- `LOCAL_MODEL_REQUIRED`
- `SECRET_OR_SESSION_SENSITIVE`
- `DEPLOYMENT_ENV_REQUIRED`

## 로컬 필요 판정 규칙

다음 조건 중 하나라도 해당하면 `LOCAL_NEEDED`로 본다.

- 명령 실행 결과가 필요하다.
- 브라우저 화면 확인이 필요하다.
- 로컬 데이터 파일을 읽어야 한다.
- 세션 파일이나 token 존재 여부가 관련된다.
- 로컬 모델/agent가 관련된다.
- 네트워크, firewall, TLS, reverse proxy가 관련된다.
- OS별 launcher 동작이 관련된다.

## 원격 처리 가능 판정 규칙

다음 조건을 모두 만족하면 원격 처리 가능으로 본다.

- GitHub에서 필요한 파일을 읽고 쓸 수 있다.
- secret 값이 필요하지 않다.
- 실행 결과를 직접 검증하지 않아도 되는 문서/정책 작업이다.
- 코드 변경이라면 로컬 검증 명령을 명확히 제공할 수 있다.
- 사용자가 이미 제공한 범위 내에서 결정 가능하다.

## 보고 형식

원격 처리 완료 보고:

- 생성/수정한 PR 또는 issue 링크
- 변경 파일
- 변경 요약
- 로컬 검증 필요 여부
- 다음 작업

로컬 필요 보고 요청:

- 목표
- 대상 브랜치/PR
- 실행 명령
- 기대 결과
- PASS/FAIL 기준
- 주의 사항
- 보고 형식

## 주의 사항

- 로컬 검증 없이 PASS라고 쓰지 않는다.
- secret, token, session file 내용을 출력하지 않는다.
- 사용자의 로컬 환경에만 있는 파일 내용을 임의로 추정하지 않는다.
- 원격에서 할 수 있는 작업을 불필요하게 사용자에게 넘기지 않는다.
- 로컬에서만 가능한 작업을 원격에서 완료했다고 말하지 않는다.
- 외부 시스템 변경 작업은 별도 승인 기준을 따른다.

## 현재 PR/이슈 적용 예시

문서 전용 PR:

- `DOCS_ONLY_REMOTE_SAFE`
- 로컬 실행 검증 불필요

Python 코드 PR:

- `MIXED_REMOTE_CODE_LOCAL_VALIDATION`
- PR 생성은 원격 가능
- unit test 실행은 로컬 필요

GitHub UI 작업:

- `GITHUB_WEB_MODEL_NEEDED`
- API 실패 시 웹모델 단계에서 먼저 재시도

## 후속 구현 순서

1. work item에 `execution_context` 필드 추가
2. local-needed 판정 함수 추가
3. GitHub-web-needed 판정 함수 추가
4. validation checklist와 연결
5. executor prompt generator와 연결
6. board-v2 카드에 execution context 배지 표시
7. `/api/work-queue`에서 분류 결과 제공
