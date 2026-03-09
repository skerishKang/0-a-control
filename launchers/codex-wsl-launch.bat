@echo off
setlocal EnableExtensions
cd /d "%~dp0.."

if "%~1"=="" goto usage
if "%~2"=="" goto usage

set "PROJECT=%~1"
set "TITLE=%~2"
set "RESUME_MODE=%~3"
set "EXIT_CODE=1"

for /f "delims=" %%i in ('wsl wslpath "%CD%"') do set "WSL_ROOT=%%i"
if not defined WSL_ROOT (
  echo Failed to resolve WSL path for %CD%.
  goto end
)

set "WSL_PREFIX="
if defined RESUME_MODE set "WSL_PREFIX=export CONTROL_TOWER_RESUME_MODE=%RESUME_MODE%; "

wsl bash -lc "%WSL_PREFIX%cd \"$1\" && bash scripts/codex-work.sh \"$2\" \"$3\"" -- "%WSL_ROOT%" "%PROJECT%" "%TITLE%"
set "EXIT_CODE=%ERRORLEVEL%"
goto end

:usage
echo Usage: codex-wsl-launch.bat ^<project-or-path^> ^<session title^> [resume-mode]
echo Example: codex-wsl-launch.bat 0-a-control "morning control tower session" resume

:end
pause
exit /b %EXIT_CODE%
