@echo off
setlocal

cd /d "%~dp0\..\.."

where python >nul 2>nul
if errorlevel 1 (
  echo [0-a-control] Python 실행 파일을 PATH에서 찾지 못했습니다.
  exit /b 1
)

python scripts\telegram_cli.py sync-core
