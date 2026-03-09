@echo off
setlocal
cd /d "%~dp0.."

set "PROJECT=0-a-control"
set "TITLE=0-a-control session"

call "%~dp0codex-wsl-launch.bat" "%PROJECT%" "%TITLE%"
