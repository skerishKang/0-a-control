@echo off
setlocal

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
  exit /b 1
)

%PYTHON_BIN% scripts\telegram_cli.py sync-core
