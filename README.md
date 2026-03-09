# 0-a-Control: 로컬-퍼스트 개인 컨트롤 타워

로컬 SQLite와 파일 기반 파이프라인을 통해 개인 작업의 전략적 continuity를 유지하는 컨트롤 타워입니다. 체크리스트 앱이 아닌, 전략적 의사결정을 돕는 Aide를 지향합니다.

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

2.  **실행**:
    *   **Windows**: `start-control-tower.bat` 실행 (서버 및 큐 워커 자동 구동)
    *   **macOS/Linux**: `start-control-tower.sh` 실행

3.  **접속**: 브라우저에서 `http://localhost:4310` 접속

## 운영 구조 (핵심)

*   **AGENTS.md**: 역할(User, Head Agent, Background Agents) 및 운영 원칙
*   **docs/08-file-verdict-pipeline.md**: 파일 기반 퀘스트 판정 파이프라인 상세
*   **docs/00-startup-routine.md**: 일일 시작 및 종료 루틴

## 테스트 및 검증

기능 검증을 위해 `tests/` 디렉토리의 스크립트를 활용합니다.

*   `python tests/test_01_pipeline_flow.py`: 전체 파이프라인 검증
*   `python tests/test_02_quests_basic.py`: DB 데이터 정합성 검증
*   `python tests/test_session_resume.py`: 세션 연속성 및 상태 복원 검증

## 저장소 구조 요약

*   `data/`: 데이터베이스, 런타임 상태 및 파일 큐 (`data/queue/`)
*   `docs/`: 운영/설계 문서
*   `public/`: 웹 프론트엔드 자산
*   `scripts/`: 주요 운영 스크립트 및 CLI 래퍼
*   `tests/`: 테스트 스크립트
