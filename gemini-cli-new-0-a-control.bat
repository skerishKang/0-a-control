@echo off
setlocal
cd /d %~dp0

set "CONTROL_TOWER_RESUME_MODE=fresh"
set "PROJECT=0-a-control"
set "TITLE=0-a-control new session"

if not "%~1"=="" (
  set "TITLE=%*"
)

set "CONTROL_TOWER_SESSION_ID="
set "TEMP_OUT=%TEMP%\gemini_start_%RANDOM%.txt"
call bash scripts/workon.sh gemini-cli cmd "%PROJECT%" "%TITLE%" > "%TEMP_OUT%"
if errorlevel 1 (
  if exist "%TEMP_OUT%" type "%TEMP_OUT%"
  del "%TEMP_OUT%" 2>nul
  pause
  exit /b 1
)
type "%TEMP_OUT%"
for /f "tokens=2" %%i in ('type "%TEMP_OUT%" ^| findstr /C:"started: "') do set "CONTROL_TOWER_SESSION_ID=%%i"
del "%TEMP_OUT%" 2>nul

if "%CONTROL_TOWER_SESSION_ID%"=="" (
  echo Failed to parse session ID.
  pause
  exit /b 1
)

if not exist "data\runtime\transcripts" mkdir "data\runtime\transcripts"
set "TRANSCRIPT_FILE=data\runtime\transcripts\%CONTROL_TOWER_SESSION_ID%.log"

echo Session started: %CONTROL_TOWER_SESSION_ID%

bash -c "gemini 2>&1 | tee '%TRANSCRIPT_FILE%'"
set "EXIT_CODE=%ERRORLEVEL%"

call bash scripts/import-current-transcript.sh gemini-cli "%TRANSCRIPT_FILE%" "%CONTROL_TOWER_SESSION_ID%"

set "SUMMARY=gemini-cli session closed"
if not "%EXIT_CODE%"=="0" set "SUMMARY=gemini-cli session exited with code %EXIT_CODE%"

call bash scripts/workdone.sh "%CONTROL_TOWER_SESSION_ID%" "%SUMMARY%"
pause
exit /b %EXIT_CODE%
