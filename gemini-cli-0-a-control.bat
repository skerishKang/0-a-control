@echo off
setlocal
cd /d %~dp0

set "PROJECT=0-a-control"
set "TITLE=0-a-control session"

bash scripts/gemini-cli-work.sh "%PROJECT%" "%TITLE%"
pause
