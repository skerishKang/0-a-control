# 초기실행bat

이 폴더는 `0-a-control`의 Windows 실행 배치를 모아 둔 곳이다.

## 역할
- `codex-*.bat`, `gemini-cli-*.bat`, `kilo-*.bat`, `opencode-*.bat`: 사용자가 직접 실행하는 에이전트 배치
- `agent-direct-launch.bat`, `codex-wsl-launch.bat`: 공통 내부 호출 배치
- `텔레그램/`: Telegram 동기화 관련 보조 배치

## 원칙
- 사용자는 보통 이 폴더의 에이전트별 배치 또는 루트의 `auto.bat`를 사용한다. `start-control-tower.bat`는 호환용 별칭이다.
- 실행 동작을 바꿀 때는 공통 호출 배치와 에이전트별 배치를 구분해서 수정한다.
- `agent-direct-launch.bat`, `codex-wsl-launch.bat`는 직접 실행보다 내부 호출 용도로 본다.
