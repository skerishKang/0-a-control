@echo off
setlocal
cd /d "%~dp0.."

set "CONTROL_TOWER_RESUME_MODE=resume"
set "PROJECT=0-a-control"
set "TITLE=0-a-control pre opencode session"

if not "%~1"=="" (
  set "TITLE=%*"
)

:: 1. Start session via bash script
call bash scripts/workon.sh opencode cmd "%PROJECT%" "%TITLE%"
if errorlevel 1 (
  pause
  exit /b %ERRORLEVEL%
)

:: 2. Run opencode in the same window using cmd /c for reliable return
cmd /c opencode
set "EXIT_CODE=%ERRORLEVEL%"

:: 3. Post-session cleanup and import
call bash scripts/import-current-opencode-session.sh

set "SUMMARY=opencode session closed"
if not "%EXIT_CODE%"=="0" set "SUMMARY=opencode session exited with code %EXIT_CODE%"

call bash scripts/workdone.sh "%SUMMARY%"
pause
exit /b %EXIT_CODE%
