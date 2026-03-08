# 0-a-Control: Local-First Control Tower

이 프로젝트는 로컬 개발 및 업무 흐름을 관리하는 **로컬 우선 컨트롤 타워** 시스템입니다. SQLite를 중심 저장소로 하며, CMD 기반의 세션 관리와 UI 기반의 상황판을 제공합니다.

## 🚀 철학
- **CMD 본체, UI 보조**: 실제 작업과 실행은 터미널(CMD/Shell)에서 이루어지며, UI는 현재 상태와 우선순위를 한눈에 파악하는 상황판 역할을 합니다.
- **파일 기반 파이프라인**: 퀘스트 보고 및 AI 판정은 파일 시스템(`quest_reports/`, `quest_verdicts/`)을 통해 외부 에이전트와 유기적으로 연동됩니다.
- **로컬 우선**: 모든 데이터는 로컬 SQLite DB에 저장되어 독립적으로 동작합니다.

## 🛠️ 주요 구성
- **scripts/server.py**: 대시보드 UI를 위한 백엔드 API 서버 (기본 포트: 8000)
- **scripts/queue_worker.py**: 외부 AI 판정 파일을 감시하고 DB에 자동 반영하는 워커
- **scripts/agent-work.sh**: 다양한 에이전트 환경(Windsurf, Gemini-CLI 등)을 통합 관리하는 래퍼 스크립트
- **public/**: 상태 가시화를 위한 대시보드 UI 소스

## 🏃 실행 방법

### 1. 컨트롤 타워 시작
루트 폴더에서 배치 파일을 실행하여 서버와 워커를 동시에 가동합니다.
```cmd
start-control-tower.bat
```

### 2. 업무 세션 시작 (CLI)
작업할 프로젝트 폴더로 이동하여 래퍼 스크립트를 통해 세션을 엽니다.
```bash
# 예: windsurf 에이전트 사용
./scripts/windsurf-work.sh [프로젝트명]
```

### 3. 대시보드 확인
브라우저에서 `http://localhost:8000`에 접속하여 주 임무, 진행률, AI 판정 결과를 확인합니다.

## 📂 저장소 구조
- `data/`: SQLite DB 및 로컬 데이터
- `docs/`: 시스템 설계 및 규약 문서
- `quest_reports/`: UI/CLI에서 생성된 퀘스트 보고서 (JSON)
- `quest_verdicts/`: 외부 에이전트가 작성한 판정 결과 (JSON)
- `scripts/`: 서버, DB 관리, 에이전트 연동 로직
- `public/`: 대시보드 웹 UI

## 📝 라이선스
개인 업무 자동화 및 제어 시스템으로 자유롭게 확장하여 사용 가능합니다.
