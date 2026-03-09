@echo off
setlocal
cd /d "%~dp0.."

set "CONTROL_TOWER_RESUME_MODE=resume"
set "PROJECT=0-a-control"
set "TITLE=0-a-control pre session"

if not "%~1"=="" (
  set "TITLE=%*"
)

bash scripts/codex-work.sh "%PROJECT%" "%TITLE%"
pause
