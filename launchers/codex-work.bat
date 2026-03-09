@echo off
setlocal
cd /d "%~dp0.."

if "%~1"=="" goto usage
if "%~2"=="" goto usage

bash -c "\"$0\" \"$@\"" "scripts/codex-work.sh" %*
set EXIT_CODE=%ERRORLEVEL%
pause
exit /b %EXIT_CODE%

:usage
echo Usage: codex-work.bat ^<project-or-path^> ^<session title^>
echo Example: codex-work.bat 0-a-control "morning control tower session"
pause
exit /b 1
