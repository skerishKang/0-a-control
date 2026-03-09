@echo off
setlocal
cd /d %~dp0

set "PROJECT=0-a-control"
set "TITLE=resume smoke test"

if not "%~1"=="" (
  set "TITLE=%*"
)

bash scripts/codex-work.sh "%PROJECT%" "%TITLE%"
pause
