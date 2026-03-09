@echo off
setlocal
cd /d "%~dp0"

if "%~1"=="" goto usage
if "%~2"=="" goto usage

bash -c "\"$0\" \"$@\"" "scripts/gemini-cli-work.sh" %*
set EXIT_CODE=%ERRORLEVEL%
pause
exit /b %EXIT_CODE%

:usage
echo Usage: gemini-cli-work.bat ^<project-or-path^> ^<session title^>
echo Example: gemini-cli-work.bat 0-a-control "candidate review session"
pause
exit /b 1
