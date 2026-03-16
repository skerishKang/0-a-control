@echo off
setlocal
cd /d "%~dp0.."

set "PROJECT=0-a-control"
set "TITLE=0-a-control session"

call "%~dp0agent-direct-launch.bat" gemini "%CD%" "%TITLE%"
exit /b %ERRORLEVEL%
