@echo off
setlocal
cd /d "%~dp0.."

set "CONTROL_TOWER_RESUME_MODE=fresh"
set "PROJECT=0-a-control"
set "TITLE=0-a-control new session"

if not "%~1"=="" (
  set "TITLE=%*"
)

call "%~dp0codex-wsl-launch.bat" "%PROJECT%" "%TITLE%" "fresh"
