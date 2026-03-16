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
  echo [0-a-control] Python 실행 파일을 PATH에서 찾지 못했습니다.
  pause
  exit /b 1
)

set "COUNT_ARGS=%SOURCE_ID%"
set "FILL_ARGS=%SOURCE_ID% --limit 50"
set "LIMIT_LABEL=제한 없음"
if defined MAX_FILE_SIZE_MB (
  set "COUNT_ARGS=%SOURCE_ID% %MAX_FILE_SIZE_MB%"
  set "FILL_ARGS=%SOURCE_ID% --limit 50 --max-file-size-mb %MAX_FILE_SIZE_MB%"
  set "LIMIT_LABEL=%MAX_FILE_SIZE_MB%MB 이하"
)

echo [0-a-control] %LABEL% 첨부 반복 작업을 시작합니다.
echo [0-a-control] Source ID: %SOURCE_ID%
echo [0-a-control] Batch size: 50
echo [0-a-control] 파일 크기 조건: %LIMIT_LABEL%
echo [0-a-control] 배치 간격: %INTERVAL_SEC%초
echo [0-a-control] 실패 재시도 대기: %RETRY_WAIT_SEC%초
echo [0-a-control] 중지하려면 Ctrl+C를 누르십시오.
echo.

:loop
set "REMAINING="
for /f %%R in ('%PYTHON_BIN% scripts\telegram_missing_attachment_count.py %COUNT_ARGS%') do set "REMAINING=%%R"

if defined MAX_FILE_SIZE_MB (
  echo [%date% %time%] 남은_누락첨부_%MAX_FILE_SIZE_MB%mb_이하=%REMAINING%
) else (
  echo [%date% %time%] 남은_누락첨부=%REMAINING%
)

if not defined REMAINING (
  echo [0-a-control] DB에서 남은 누락 첨부 수를 읽지 못했습니다.
  pause
  exit /b 1
)
if "%REMAINING%"=="0" (
  echo [0-a-control] 조건에 맞는 누락 첨부가 더 이상 없습니다. 종료합니다.
  goto :end
)

%PYTHON_BIN% scripts\telegram_cli.py fill-missing-attachments %FILL_ARGS%
if errorlevel 1 (
  echo [0-a-control] 첨부 채우기에 실패했습니다. %RETRY_WAIT_SEC%초 후 다시 시도합니다.
  %PYTHON_BIN% scripts\telegram_attachment_status.py %COUNT_ARGS%
  timeout /t %RETRY_WAIT_SEC%
  goto :loop
)

set "REMAINING="
for /f %%R in ('%PYTHON_BIN% scripts\telegram_missing_attachment_count.py %COUNT_ARGS%') do set "REMAINING=%%R"
if defined MAX_FILE_SIZE_MB (
  echo [%date% %time%] 배치후_남은_누락첨부_%MAX_FILE_SIZE_MB%mb_이하=%REMAINING%
) else (
  echo [%date% %time%] 배치후_남은_누락첨부=%REMAINING%
)

if "%REMAINING%"=="0" (
  echo [0-a-control] 조건에 맞는 누락 첨부가 더 이상 없습니다. 종료합니다.
  goto :end
)

echo [0-a-control] %INTERVAL_SEC%초 후 다음 배치를 시작합니다...
timeout /t %INTERVAL_SEC%
goto :loop

:usage
echo 사용법: 첨부채우기-반복.bat SOURCE_ID LABEL [MAX_FILE_SIZE_MB] [INTERVAL_SEC]
pause
exit /b 1

:end
echo [0-a-control] 반복 작업을 마쳤습니다.
pause
