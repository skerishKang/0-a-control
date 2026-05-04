# 23. 로컬 필요 작업과 원격 처리 가능 작업 구분 기준

이 문서는 `0-a-control` 운영에서 어떤 작업을 원격으로 바로 처리할 수 있고, 어떤 작업은 사용자 로컬 환경에서 실행해야 하는지 구분하는 기준을 정의한다.

## 목적

`0-a-control`은 로컬 대시보드, 로컬 데이터, 로컬 모델/에이전트, Telegram 세션, 브라우저 확인을 포함한다. 따라서 모든 작업을 원격에서 처리할 수 없다.

이 기준의 목적은 다음과 같다.

- 원격에서 가능한 작업은 사용자를 기다리지 않고 진행한다.
- 로컬에서만 검증 가능한 작업은 명확히 분리한다.
- 로컬 실행자에게 줄 명령과 보고 형식을 표준화한다.
- 검증하지 않은 내용을 PASS로 처리하지 않는다.
- 민감 정보가 원격 대화나 공개 저장소에 노출되지 않게 한다.

## 기본 원칙

1. GitHub에서 읽고 쓸 수 있는 문서/이슈/PR 정리는 원격 처리 가능으로 본다.
2. 실제 서버 실행, 브라우저 렌더링, 로컬 모델 실행은 로컬 필요로 본다.
3. 로컬 데이터, 세션 파일, 토큰 값은 원격으로 출력하지 않는다.
4. 기능 코드 변경은 가능한 한 PR까지 만들되, 실행 검증은 로컬 필요로 표시한다.
5. 문서 전용 변경은 원칙적으로 로컬 실행 검증이 필요 없다.
6. 검증하지 않은 항목은 `미검증` 또는 `local-needed`로 표시한다.

## 원격 처리 가능 작업

다음 작업은 원격에서 직접 처리할 수 있다.

### GitHub 운영

- issue 생성
- issue 제목/본문 수정
- issue 댓글 작성
- PR 생성
- PR 설명 작성
- PR 상태 확인
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

다음 조건을 만족하면 원격에서 코드 PR까지 만들 수 있다.

- 변경 범위가 작고 명확하다.
- 로컬 데이터나 세션 파일에 접근하지 않는다.
- secret 값이 필요하지 않다.
- 테스트 명령을 명확히 제시할 수 있다.
- 실행 결과를 PASS로 주장하지 않는다.

예:

- 순수 함수 모듈 추가
- mocked unit test 추가
- 정적 template 추가
- API route 초안 추가

## 로컬 필요 작업

다음 작업은 사용자 로컬 환경 또는 로컬 실행자가 필요하다.

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

일부 작업은 원격과 로컬이 섞인다.

| 작업 | 원격 처리 | 로컬 필요 |
|---|---|---|
| Python service 추가 | 코드/테스트 PR 작성 | unit test 실행 |
| server route 추가 | 코드 PR 작성 | 서버 실행 + curl 확인 |
| board-v2 UI 추가 | 코드 PR 작성 | 브라우저 렌더링 확인 |
| 문서 추가 | PR 작성 | 보통 불필요 |
| 배포 문서 추가 | PR 작성 | 실제 배포 검증은 로컬/서버 필요 |
| Telegram 기능 수정 | 코드 PR 작성 가능 | 인증/동기화 실행 필요 |

## 작업 분류 라벨

향후 UI/API는 다음 값을 사용할 수 있다.

- `REMOTE_DOABLE`
- `LOCAL_NEEDED`
- `MIXED_REMOTE_CODE_LOCAL_VALIDATION`
- `DOCS_ONLY_REMOTE_SAFE`
- `BROWSER_VALIDATION_REQUIRED`
- `LOCAL_MODEL_REQUIRED`
- `SECRET_OR_SESSION_SENSITIVE`
- `DEPLOYMENT_ENV_REQUIRED`

## 로컬 필요 판정 규칙

다음 조건 중 하나라도 해당하면 `LOCAL_NEEDED`를 표시한다.

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

### 원격 처리 완료 보고

포함 항목:

- 생성/수정한 PR 또는 issue 링크
- 변경 파일
- 변경 요약
- 로컬 검증 필요 여부
- 다음 작업

### 로컬 필요 보고 요청

포함 항목:

- 목표
- 대상 브랜치/PR
- 실행 명령
- 기대 결과
- PASS/FAIL 기준
- 금지 사항
- 보고 형식

## 금지 사항

- 로컬 검증 없이 `PASS`라고 쓰지 않는다.
- secret, token, session file 내용을 출력하지 않는다.
- 사용자의 로컬 환경에만 있는 파일 내용을 임의로 추정하지 않는다.
- 원격에서 할 수 있는 작업을 불필요하게 사용자에게 넘기지 않는다.
- 로컬에서만 가능한 작업을 원격에서 완료했다고 말하지 않는다.
- merge/close/delete는 별도 명시 없이 실행하지 않는다.

## 현재 PR/이슈 적용 예시

### 문서 전용 PR

예:

- #13 deployment checklist
- #14 settings guardrails checklist
- #15 operations manual
- #18 dashboard IA
- #19 manual overrides
- #20 work queue model
- #21 validation checklist model
- #22 executor prompt generator model

판정:

- `DOCS_ONLY_REMOTE_SAFE`
- 로컬 실행 검증 불필요

### Python 코드 PR

예:

- #16 GitHub data summary service
- #17 operational state classifier

판정:

- `MIXED_REMOTE_CODE_LOCAL_VALIDATION`
- PR 생성은 원격 가능
- unit test 실행은 로컬 필요

## 후속 구현 순서

1. work item에 `execution_context` 필드 추가
2. local-needed 판정 함수 추가
3. validation checklist와 연결
4. executor prompt generator와 연결
5. board-v2 카드에 `LOCAL_NEEDED` 배지 표시
6. local validation prompt copy 버튼 추가
7. `/api/work-queue`에서 분류 결과 제공

## 완료 기준

#12가 완료되려면 다음 조건을 만족해야 한다.

- 원격 처리 가능 작업과 로컬 필요 작업 기준이 명확하다.
- 혼합 작업의 처리 방식이 정의되어 있다.
- 작업 분류 라벨이 정의되어 있다.
- 로컬 필요 판정 규칙이 있다.
- 보고 형식과 금지 사항이 있다.
- 후속 구현자가 work queue와 prompt generator에 연결할 수 있다.
