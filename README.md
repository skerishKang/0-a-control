# 0-a-Control: Local-First Control Tower

이 프로젝트는 로컬 개발 및 업무 흐름을 관리하는 **로컬 우선 컨트롤 타워** 시스템입니다. SQLite를 중심 저장소로 하며, CMD 기반의 세션 관리와 UI 기반의 상황판을 제공합니다.

## 🚀 철학
- **CMD 본체, UI 보조**: 실제 작업과 실행은 터미널(CMD/Shell)에서 이루어지며, UI는 현재 상태와 우선순위를 한눈에 파악하는 상황판 역할을 합니다.
- **파일 기반 파이프라인**: 퀘스트 보고 및 AI 판정은 파일 시스템(`quest_reports/`, `quest_verdicts/`)을 통해 외부 에이전트와 유기적으로 연동됩니다.
- **로컬 우선**: 모든 데이터는 로컬 SQLite DB에 저장되어 독립적으로 동작합니다.

## 🛠️ 주요 구성
- **scripts/server.py**: 대시보드 UI를 위한 백엔드 API 서버 (기본 포트: **4310**)
- **scripts/queue_worker.py**: `quest_verdicts/`를 감시해 판정 JSON을 ingest하고 SQLite 상태를 갱신하는 워커
- **scripts/agent-work.sh**: 다양한 에이전트 환경(Windsurf, Gemini-CLI 등)을 통합 관리하는 래퍼 스크립트
- **AGENTS.md**: 주 임무/퀘스트 운영 원칙과 역할 정의를 담은 헌장
- **public/**: 상태 가시화를 위한 대시보드 UI 소스

## 🏃 실행 방법

### 1. 컨트롤 타워 시작
루트 폴더에서 환경에 맞는 실행 파일을 실행하여 서버와 워커를 동시에 가동합니다.

**Windows:**
- `start-control-tower.bat` 실행

**macOS / Linux:**
```bash
chmod +x start-control-tower.sh
./start-control-tower.sh
```

*(참고: 수동 기동이 필요한 경우, 각각의 터미널에서 `python scripts/queue_worker.py`와 `python scripts/server.py`를 실행하십시오.)*

### 2. 업무 세션 시작 (CLI)
작업할 프로젝트 폴더로 이동하여 래퍼 스크립트를 통해 세션을 엽니다.
```bash
# 예: windsurf 에이전트 사용
./scripts/windsurf-work.sh [프로젝트명]
```

### 3. 대시보드 확인
브라우저에서 `http://localhost:4310`에 접속하여 주 임무, 진행률, AI 판정 결과를 확인합니다.

### 4. 테스트 (tests/)
`tests/` 폴더에 파일 기반 점검 스크립트가 배치되어 있으나, 정식 테스트 실행 절차는 아직 확정되지 않았습니다. 현재는 필요한 스크립트를 직접 `python tests/<파일명>.py` 형태로 실행해 수동 검증합니다.

## 📂 저장소 구조
- `data/`: SQLite DB 및 로컬 데이터
- `docs/`: 시스템 설계 및 규약 문서
- `docs/00-startup-routine.md`: 일일 기동 루틴 및 start-control-tower.bat 동작 설명
- `quest_reports/`: UI/CLI에서 생성된 퀘스트 보고서 (JSON)
- `quest_verdicts/`: 외부 에이전트가 작성한 판정 결과 (JSON)
- `scripts/`: 서버, DB 관리, 에이전트 연동 로직
- `public/`: 대시보드 웹 UI

## 📝 라이선스
개인 업무 자동화 및 제어 시스템으로 자유롭게 확장하여 사용 가능합니다.
