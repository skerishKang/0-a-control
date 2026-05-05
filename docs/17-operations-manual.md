# 17. 운영 사용법 매뉴얼

이 문서는 `0-a-control`을 매일 사용하는 관점에서 정리한 운영 매뉴얼이다. 설치나 내부 구조보다 “켜고, 보고, 판단하고, 기록하고, 종료하는 흐름”에 집중한다.

## 대상 사용자

- `0-a-control`을 개인 컨트롤 타워로 직접 운영하는 사용자
- 로컬 모델, CLI 에이전트, Telegram 동기화, 작업 로그를 함께 쓰는 사용자
- 기존 README를 읽었지만 실제 하루 운영 흐름이 아직 분명하지 않은 사용자

## 기본 원칙

1. 기본값은 로컬 전용 운영이다.
2. 대시보드는 현재 상태를 확인하는 중심 화면이다.
3. 작업 기록은 가능한 한 세션/퀘스트/보고서 형태로 남긴다.
4. 민감한 세션 파일, 토큰, 개인 데이터는 공개 저장소에 올리지 않는다.
5. 원격 접근은 별도 접근 제어를 갖춘 뒤에만 사용한다.

## 하루 운영 흐름

### 1. 시작 전 확인

확인 항목:

- 오늘 사용할 머신이 맞는가
- 저장소 위치가 맞는가
- 이전 세션이 비정상 종료되지 않았는가
- Telegram 동기화가 필요한 날인가
- 로컬 모델 또는 CLI 에이전트를 사용할 계획이 있는가

필요 시 확인 명령:

- `git status --short`
- `git branch --show-current`
- `python --version`

### 2. 서버 시작

Windows:

- `start-control-tower.bat`

macOS/Linux/WSL:

- `./start-control-tower.sh`

직접 실행:

- `python scripts/server.py`

정상 기준:

- 서버가 `http://localhost:4310` 또는 `http://127.0.0.1:4310`에서 열린다.
- `/api/health`가 `{ "ok": true }`를 반환한다.
- 루트 URL `/`가 `/board-v2.html`로 이동한다.

### 3. 대시보드 확인

브라우저에서 접속:

- `http://localhost:4310`

먼저 볼 항목:

- 현재 주 임무
- 현재 퀘스트 상태
- 우선 검토 후보
- 최근 세션
- 에이전트 상태
- Telegram 상태 배너

판단 기준:

- 오늘 바로 할 작업이 있는가
- pending 상태로 남은 작업이 있는가
- stale session이 있는가
- Telegram 설정이 필요한데 누락되어 있는가
- 현재 화면만으로 다음 행동이 명확한가

### 4. 작업 시작

작업은 가능한 한 세션 단위로 시작한다.

사용 가능한 진입점 예:

- 루트의 `open-*.bat`
- `scripts/agent-work.sh`
- `scripts/codex-work.sh`
- `scripts/gemini-cli-work.sh`
- `scripts/telegram_cli.py`

운영 기준:

- 루트의 `open-*.bat`는 사용자 진입점이다.
- 실제 실행 구현은 `launchers/`와 `scripts/`를 기준으로 확인한다.
- 새 작업을 시작할 때는 작업 목적과 범위를 명확히 한다.
- 작업 완료 후에는 요약, 남은 일, blocker를 기록한다.

### 5. 작업 중 기록

작업 중에는 아래 내용을 남긴다.

- 무엇을 하려 했는가
- 어떤 파일이나 데이터에 접근했는가
- 어떤 결정을 했는가
- 무엇이 완료되었는가
- 무엇이 남았는가
- 다음 시작점은 무엇인가

기록 기준:

- 짧아도 좋지만, 다음 세션에서 이어갈 수 있어야 한다.
- 성공/실패만 쓰지 말고 이유를 남긴다.
- blocker가 있으면 명확히 분리한다.

### 6. 퀘스트 보고와 판정

퀘스트 단위 작업은 보고와 판정 흐름을 따른다.

흐름:

1. 작업 진행 상황을 보고한다.
2. report 파일 또는 DB 상태가 갱신된다.
3. 외부 에이전트 또는 판정 흐름이 verdict를 만든다.
4. 대시보드가 `done`, `partial`, `hold`, `pending` 등 상태를 반영한다.

판정 기준:

- `done`: 목표가 충족됨
- `partial`: 일부 완료, 후속 작업 필요
- `hold`: 지금은 계속 진행하지 않음
- `pending`: 보고는 되었지만 판정 또는 반영 대기

### 7. Telegram 동기화

Telegram 동기화는 선택 기능이다.

수동 실행:

- `python scripts/telegram_cli.py sync-core`
- `python scripts/telegram_cli.py sync-status`
- `python scripts/telegram_cli.py telegram-status`

필요 설정:

- `TELEGRAM_API_ID`
- `TELEGRAM_API_HASH`
- 선택: `CONTROL_TOWER_TELEGRAM_SESSION_PATH`

주의:

- Telegram 세션 파일은 민감 파일이다.
- 설정이 없어도 대시보드 핵심 기능은 계속 쓸 수 있어야 한다.
- 동기화 실패는 전체 시스템 실패와 구분한다.

### 8. 종료 전 정리

종료 전 확인 항목:

- 현재 작업이 완료/보류/진행 중 중 어디인지 정리했는가
- 다음 시작점이 남아 있는가
- stale session이 없는가
- 중요한 blocker가 기록되었는가
- 민감 파일이 Git에 잡히지 않았는가

확인 명령:

- `git status --short`

서버 종료:

- 서버 터미널에서 `Ctrl + C`
- Windows 창은 필요한 경우 닫아도 된다.

## 상태 해석 기준

### 오늘 볼 상태

| 상태 | 의미 | 권장 행동 |
|---|---|---|
| active | 현재 진행 중 | 이어서 진행하거나 보고 작성 |
| pending | 판정/반영 대기 | verdict 또는 큐 상태 확인 |
| done | 완료 | 기록 확인 후 다음 작업으로 이동 |
| hold | 보류 | 이유와 재개 조건 확인 |
| stale | 비정상 잔존 가능성 | 세션 정리 또는 cleanup 실행 |

### 우선순위 판단

우선순위는 아래 순서로 본다.

1. 지금 막힌 작업
2. 오늘 반드시 끝낼 작업
3. 현재 주 임무와 직접 연결된 작업
4. 오래 방치된 미완료 작업
5. 참고/아카이브 성격의 작업

## 문제 발생 시 처리

### 서버가 뜨지 않음

확인:

- Python 설치 여부
- 현재 디렉터리가 저장소 루트인지
- 포트 `4310` 사용 중인지
- `requirements.txt` 설치 여부

조치:

- `python scripts/server.py`로 직접 실행해 에러 메시지를 확인한다.
- 포트 충돌이면 `PORT`를 바꾼다.

### 화면이 깨짐

확인:

- `/board-v2.html` 직접 접속
- 정적 CSS/JS 파일이 200으로 로드되는지 확인
- 브라우저 콘솔 에러 확인

조치:

- 서버 재시작
- 캐시 새로고침
- 최근 변경 파일 확인

### API는 되는데 화면 데이터가 이상함

확인:

- `/api/current-state`
- `/api/quests`
- `/api/plans`
- `/api/sessions/recent`

판단:

- API 데이터 문제인지
- 프론트 렌더링 문제인지
- 데이터 자체가 비어 있는 정상 상태인지 구분한다.

### Telegram이 동작하지 않음

확인:

- `python scripts/telegram_cli.py telegram-status`
- `TELEGRAM_API_ID`
- `TELEGRAM_API_HASH`
- 세션 파일 경로

판단:

- Telegram 미설정은 전체 대시보드 장애가 아니다.
- Telegram sync만 별도 조치한다.

## 로컬 필요 작업과 원격 가능 작업

### 로컬 필요

- 서버 실행
- 브라우저 화면 확인
- Telegram 인증/세션 생성
- 로컬 모델 실행
- DB 상태 직접 확인
- OS별 launcher 실행 확인

### 원격 가능

- 문서 수정
- 이슈/PR 정리
- 정적 코드 리뷰
- 운영 기준 정리
- 실행자 프롬프트 작성
- GitHub 메타데이터 확인

## 변경 작업 보고 기준

변경 작업을 마친 뒤에는 아래 항목을 보고한다.

- 변경한 파일
- 변경한 이유
- 실행한 명령
- 검증 결과
- 남은 위험
- 다음 작업

검증 없이 `완료`라고 쓰지 않는다. 실행하지 못한 검증은 `미실행`으로 명확히 표시한다.

## 관련 문서

- `README.md`: 프로젝트 개요와 빠른 시작
- `AGENTS.md`: 역할과 운영 원칙
- `docs/00-startup-routine.md`: 매일 시작 루틴
- `docs/08-file-verdict-pipeline.md`: report/verdict 파이프라인
- `docs/11-structure-followups.md`: 구조 개선 후속 과제
- `docs/14-kilo-mode-skill-guide.md`: Kilo mode/skill 가이드
- `docs/15-deployment-and-access.md`: 배포와 접근 경로 체크리스트
- `docs/16-settings-and-guardrails.md`: 설정과 안전 가드레일

## 완료 기준

이 매뉴얼은 다음 조건을 만족해야 한다.

- 처음 보는 사용자가 하루 운영 흐름을 이해할 수 있다.
- 서버 시작, 대시보드 확인, 작업 기록, 종료 절차가 연결되어 있다.
- 문제 발생 시 어디를 확인해야 하는지 명확하다.
- 로컬 필요 작업과 원격 가능 작업이 구분되어 있다.
- README가 너무 길어지지 않도록 상세 운영 흐름을 별도 문서로 분리한다.
