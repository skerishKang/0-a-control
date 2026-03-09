# 0-a-Control: 로컬-퍼스트 개인 컨트롤 타워

로컬 SQLite와 파일 기반 파이프라인을 통해 개인 작업의 전략적 continuity를 유지하는 컨트롤 타워입니다. 현재 시스템은 로컬 운영을 위한 프로토타입 상태이며, 일부 파이프라인 기능은 테스트 검증 단계를 거치고 있습니다.

## 핵심 기능

*   **CMD 기반 작업**: `scripts/` 내 래퍼 스크립트를 통한 세션 로그 기록
*   **파일 기반 파이프라인**: `report` 생성 → 외부 에이전트 `verdict` 생성 → 서버 `ingest` 및 DB 갱신
*   **상황판 UI**: 현재 주 임무와 퀘스트 상태 실시간 확인
*   **전략적 Aide**: `AGENTS.md`의 운영 원칙에 따라 주 임무와 퀘스트 관리

## 빠른 시작

1.  **환경 설정**:
    ```bash
    pip install -r requirements.txt
    ```
    선택 사항: `.env.example`를 참고해 환경변수를 맞출 수 있습니다.

2.  **실행**:
    *   **Windows**: `start-control-tower.bat`로 서버/큐 워커를 바로 띄울 수 있습니다. 별도의 에이전트 래퍼 실행은 일부 launcher가 WSL/bash를 전제로 합니다.
    *   **macOS/Linux/WSL**: `start-control-tower.sh` 실행
    *   **에이전트 작업 래퍼**: `scripts/agent-work.sh` 가 공통 진입점이고, `scripts/codex-work.sh`, `scripts/gemini-cli-work.sh` 같은 얇은 래퍼가 이를 감쌉니다.

3.  **접속**: 브라우저에서 `http://localhost:4310` 접속

## 운영 구조 (핵심)

*   **AGENTS.md**: 역할(User, Head Agent, Background Agents) 및 운영 원칙
*   **docs/08-file-verdict-pipeline.md**: 파일 기반 퀘스트 판정 파이프라인 상세
*   **docs/00-startup-routine.md**: 일일 시작 및 종료 루틴
*   **scripts/_archive/**: 현재는 사용하지 않지만 보존 중인 마이그레이션/백필 스크립트

## 테스트 및 검증

기능 검증을 위해 `tests/` 디렉토리의 스크립트를 활용합니다. 주요 `unittest` 케이스는 테스트마다 임시 DB/큐/작업 디렉터리를 만들어 운영 데이터와 분리하며, 셸 스크립트나 수동 검증 절차는 별도 환경 구성이 필요할 수 있습니다.

*   `python -m unittest discover -s tests -p "test_*.py"`: 전체 테스트 스위트 실행.

## 저장소 구조 요약

*   `data/`: 데이터베이스, 런타임 상태 및 파일 큐 (`data/queue/`)
*   `docs/`: 운영/설계 문서
*   `launchers/`: Windows용 보조 launcher들. 일부는 WSL/bash 환경을 전제로 함
*   `public/`: 웹 프론트엔드 자산
*   `scripts/`: 주요 운영 스크립트, 통합 세션 래퍼, 보조 CLI
*   `tests/`: 테스트 스크립트
