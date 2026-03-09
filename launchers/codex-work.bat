@echo off
setlocal
cd /d "%~dp0.."

if "%~1"=="" goto usage
if "%~2"=="" goto usage

call "%~dp0codex-wsl-launch.bat" "%~1" "%~2"
exit /b %ERRORLEVEL%

:usage
echo Usage: codex-work.bat ^<project-or-path^> ^<session title^>
echo Example: codex-work.bat 0-a-control "morning control tower session"
pause
exit /b 1
