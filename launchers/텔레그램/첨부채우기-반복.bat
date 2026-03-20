@echo off
setlocal

if "%~1"=="" goto :usage
if "%~2"=="" goto :usage

set "SOURCE_ID=%~1"
set "LABEL=%~2"
set "MAX_FILE_SIZE_MB=%~3"
set "INTERVAL_SEC=%~4"
if not defined INTERVAL_SEC set "INTERVAL_SEC=30"
set "RETRY_WAIT_SEC=60"

cd /d "%~dp0\..\.."

set "PYTHON_BIN="
where python >nul 2>nul
if not errorlevel 1 (
  set "PYTHON_BIN=python"
)
if not defined PYTHON_BIN (
  where py >nul 2>nul
  if not errorlevel 1 (
    set "PYTHON_BIN=py"
  )
)
if not defined PYTHON_BIN (
  echo [0-a-control] Python executable not found in PATH.
  pause
  exit /b 1
)

set "COUNT_ARGS=%SOURCE_ID%"
set "FILL_ARGS=%SOURCE_ID% --limit 50"
set "LIMIT_LABEL=no-limit"
if defined MAX_FILE_SIZE_MB (
  set "COUNT_ARGS=%SOURCE_ID% %MAX_FILE_SIZE_MB%"
  set "FILL_ARGS=%SOURCE_ID% --limit 50 --max-file-size-mb %MAX_FILE_SIZE_MB%"
  set "LIMIT_LABEL=%MAX_FILE_SIZE_MB%MB-or-less"
)

echo [0-a-control] Starting attachment fill loop for %LABEL%.
echo [0-a-control] Source ID: %SOURCE_ID%
echo [0-a-control] Batch size: 50
echo [0-a-control] File size limit: %LIMIT_LABEL%
echo [0-a-control] Batch interval: %INTERVAL_SEC%s
echo [0-a-control] Retry wait: %RETRY_WAIT_SEC%s
echo [0-a-control] Press Ctrl+C to stop.
echo.

:loop
set "REMAINING="
for /f %%R in ('%PYTHON_BIN% scripts\telegram_missing_attachment_count.py %COUNT_ARGS%') do set "REMAINING=%%R"

if defined MAX_FILE_SIZE_MB (
  echo [%date% %time%] remaining_missing_%MAX_FILE_SIZE_MB%mb_or_less=%REMAINING%
) else (
  echo [%date% %time%] remaining_missing=%REMAINING%
)

if not defined REMAINING (
  echo [0-a-control] Failed to read remaining missing attachment count from DB.
  pause
  exit /b 1
)
if "%REMAINING%"=="0" (
  echo [0-a-control] No more matching missing attachments. Exiting.
  goto :end
)

%PYTHON_BIN% scripts\telegram_cli.py fill-missing-attachments %FILL_ARGS%
if errorlevel 1 (
  echo [0-a-control] Attachment fill failed. Retrying after %RETRY_WAIT_SEC%s.
  %PYTHON_BIN% scripts\telegram_attachment_status.py %COUNT_ARGS%
  timeout /t %RETRY_WAIT_SEC%
  goto :loop
)

set "REMAINING="
for /f %%R in ('%PYTHON_BIN% scripts\telegram_missing_attachment_count.py %COUNT_ARGS%') do set "REMAINING=%%R"
if defined MAX_FILE_SIZE_MB (
  echo [%date% %time%] remaining_after_batch_%MAX_FILE_SIZE_MB%mb_or_less=%REMAINING%
) else (
  echo [%date% %time%] remaining_after_batch=%REMAINING%
)

if "%REMAINING%"=="0" (
  echo [0-a-control] No more matching missing attachments. Exiting.
  goto :end
)

echo [0-a-control] Starting next batch after %INTERVAL_SEC%s...
timeout /t %INTERVAL_SEC%
goto :loop

:usage
echo Usage: attachment-fill-loop.bat SOURCE_ID LABEL [MAX_FILE_SIZE_MB] [INTERVAL_SEC]
pause
exit /b 1

:end
echo [0-a-control] Attachment fill loop finished.
pause
