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
    *   **Windows**: `start-control-tower.bat`로 서버와 큐 워커를 시작할 수 있습니다. 다만 `launchers/`와 일부 에이전트 래퍼는 WSL/bash 환경을 전제로 하므로 Windows 지원은 부분적입니다.
    *   **macOS/Linux/WSL**: `start-control-tower.sh` 실행
    *   **에이전트 작업 래퍼**: `scripts/agent-work.sh` 가 공통 진입점이고, `scripts/agent_registry.py` 가 에이전트 이름과 실행 파일을 해석합니다. `scripts/codex-work.sh`, `scripts/gemini-cli-work.sh` 같은 얇은 래퍼는 이 진입점을 감싸는 편의 스크립트입니다.

3.  **접속**: 브라우저에서 `http://localhost:4310` 접속

## 운영 구조 (핵심)

*   **AGENTS.md**: 역할(User, Head Agent, Background Agents) 및 운영 원칙
*   **docs/08-file-verdict-pipeline.md**: 파일 기반 퀘스트 판정 파이프라인 상세
*   **docs/00-startup-routine.md**: 일일 시작 및 종료 루틴
*   **scripts/_archive/**: 현재는 사용하지 않지만 보존 중인 마이그레이션/백필 스크립트

## 테스트 및 검증

이 프로젝트는 자동화된 단위 테스트와 수동 검증 스크립트를 구분하여 관리합니다. 자세한 내용은 `tests/README.md`를 참고하십시오.

### 자동 테스트 (CI 범위)
GitHub Actions(Ubuntu)에서 푸시/PR 시 자동으로 실행되는 테스트입니다.
*   **실행**: `python -m unittest discover -s tests -p "test_*.py"`
*   **특징**: `tempfile` 기반의 임시 환경을 사용하여 운영 데이터와 격리된 상태에서 수행됩니다.

### 수동 검증 및 시드 (로컬 범위)
로컬 개발 및 운영 중 상태 확인을 위해 사용하는 스크립트입니다. CI에서는 실행되지 않습니다.
*   **데이터 시드**: `tests/seed/` 내의 스크립트로 샘플 데이터를 생성합니다. (예: `python tests/seed/seed_dummy_inbox.py`)
*   **파이프라인 검증**: `tests/manual/run_pipeline_test.sh`를 통해 전체 파일 큐 흐름을 수동으로 확인할 수 있습니다.
*   **DB 무결성 확인**: `tests/manual/db_verify/`의 스크립트를 사용하여 DB 상태를 직접 점검합니다.

> **주의**: CI 환경은 현재 Ubuntu Linux 기반이며, `launchers/` 내의 일부 Windows 전용 기능이나 복잡한 에이전트 연동 시나리오는 자동 테스트 범위에 포함되지 않을 수 있습니다.

## 현재 한계와 다음 문서

*   `scripts/` 아래에는 DB, 서버, 큐, Telegram, import, wrapper 스크립트가 함께 있어 역할 경계가 완전히 분리된 상태는 아닙니다.
*   파일 기반 판정 파이프라인은 중복 판정, 손상 JSON 격리, stale revision 보관은 구현되어 있지만, 자동 재처리 정책과 운영 절차는 아직 문서/자동화가 더 필요합니다.
*   구조 개선 과제는 [docs/11-structure-followups.md](/mnt/g/Ddrive/BatangD/task/workdiary/0-a-control/docs/11-structure-followups.md)에 따로 정리했습니다.

## 저장소 구조 요약

*   `data/`: 데이터베이스, 런타임 상태 및 파일 큐 (`data/queue/`)
*   `docs/`: 운영/설계 문서
*   `launchers/`: Windows용 보조 launcher들. 일부는 WSL/bash 환경을 전제로 함
*   `public/`: 웹 프론트엔드 자산
*   `scripts/`: 주요 운영 스크립트, 통합 세션 래퍼, 보조 CLI
*   `tests/`: 테스트 스크립트
