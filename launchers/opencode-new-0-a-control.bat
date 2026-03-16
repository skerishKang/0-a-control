@echo off
setlocal
cd /d "%~dp0.."

set "CONTROL_TOWER_RESUME_MODE=fresh"
set "PROJECT=0-a-control"
set "TITLE=0-a-control new opencode session"

if not "%~1"=="" (
  set "TITLE=%*"
)

call "%~dp0agent-direct-launch.bat" opencode "%CD%" "%TITLE%"
exit /b %ERRORLEVEL%
