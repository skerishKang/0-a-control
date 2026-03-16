@echo off
setlocal
cd /d "%~dp0.."

set "PROJECT=0-a-control"
set "TITLE=0-a-control session"

if not "%~1"=="" (
  set "TITLE=%*"
)

call "%~dp0agent-direct-launch.bat" kilo "%CD%" "%TITLE%"
exit /b %ERRORLEVEL%
