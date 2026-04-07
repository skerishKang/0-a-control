@echo off
setlocal

cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
  echo [0-a-control] Python executable not found in PATH.
  echo Please install Python or add it to PATH, then run again.
  pause
  exit /b 1
)

echo [0-a-control] Starting local server...
echo.
echo Browser URL:
echo   Default: http://localhost:4310
echo   If 4310 is unavailable, check the actual URL printed by the server below.
echo.
echo Telegram:
echo   If TELEGRAM_API_ID / TELEGRAM_API_HASH are configured, sync works directly in 0-a-control.
echo.

python scripts\server.py

echo.
echo [0-a-control] Server stopped.
pause
