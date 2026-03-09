@echo off
setlocal
cd /d "%~dp0.."

set "PROJECT=0-a-control"
set "TITLE=resume smoke test"

if not "%~1"=="" (
  set "TITLE=%*"
)

call "%~dp0codex-wsl-launch.bat" "%PROJECT%" "%TITLE%"
