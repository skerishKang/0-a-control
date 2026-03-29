@echo off
setlocal
cd /d "%~dp0"

rem Backward-compatible alias. Keep a single implementation in start-control-tower.bat.
call "%~dp0start-control-tower.bat" %*
exit /b %ERRORLEVEL%
