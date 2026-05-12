# 11. 구조 개선 후속 과제

이 문서는 현재 코드 상태를 부정하지 않고, 바로 뜯지 않을 구조 개선 과제를 분리해 적는다.

## 현재 사실

- `scripts/` 아래에는 DB, 서버, 큐, Telegram, import, wrapper 스크립트가 함께 있다.
- 공통 세션 진입점은 이미 `scripts/agent-work.sh` 와 `scripts/agent_registry.py` 로 존재한다.
- 파일 기반 verdict 파이프라인에는 `processed`, `failed`, `duplicates`, `archive/revisions` 처리가 이미 있다.
- GitHub Actions CI는 `.github/workflows/python-tests.yml` 로 연결되어 있다.
- 현재 CI는 Ubuntu + Python 3.11에서 `requirements.txt` 와 `pytest`를 설치하고, 임시 데이터/DB/워크다이어리 경로와 테스트 환경을 준비한 뒤 `python -m pytest tests/ -q` 를 실행한다.

## 지금 당장 하지 않는 이유

- 폴더 구조를 크게 나누면 import 경로, wrapper, 문서, 런처를 함께 손봐야 한다.
- 현재 우선순위는 동작 안정성과 운영 문서 정합성 유지이지, 대규모 패키지 리팩터링이 아니다.
- launcher와 wrapper는 Windows/WSL 경로 의존이 있어 성급한 통합이 회귀를 만들 수 있다.

## 향후 과제

### 1. scripts 역할 경계 재정리
- `scripts/db_*`, `scripts/server.py`, `scripts/queue_worker.py`, Telegram 관련 스크립트, import 스크립트, wrapper 스크립트를 더 명확한 서브패키지 또는 디렉토리로 나누는 방안 검토
- 목표는 “지금 기능 삭제”가 아니라 책임 경계 명확화

### 2. 파일 파이프라인 운영 절차 보강
- failed verdict 재처리 CLI 또는 운영 스크립트 추가
- report/verdict 쌍 단위 보관 및 정리 정책 명문화
- 중복/실패/재시도 통계 조회 지점 추가

### 3. 온보딩 문서 분리
- README는 개요와 빠른 시작 중심으로 유지
- 설치, 트러블슈팅, Windows/WSL 실행 차이, 운영 점검 절차는 별도 문서로 분리

### 4. CI 운영 보강
- 기본 CI는 연결되어 있으므로, 이후에는 테스트 범위, 캐시, 실패 로그 가독성을 점진적으로 보강
- CI 환경 준비가 운영 데이터에 의존하지 않도록 임시 경로와 테스트 fixture 기준을 유지

### 5. Windows 지원 명확화
- 현재는 부분 지원 상태이므로, launcher별로 “네이티브 CMD 가능 / WSL 필요” 표를 문서화
- 필요 시 Windows 전용 wrapper 또는 PowerShell 진입점 검토
