@echo off
setlocal
cd /d "%~dp0.."

set "PROJECT=0-a-control"
set "TITLE=0-a-control session"

bash scripts/codex-work.sh "%PROJECT%" "%TITLE%"
pause
