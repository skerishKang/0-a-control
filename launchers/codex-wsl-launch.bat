@echo off
setlocal EnableExtensions
cd /d "%~dp0.."

if "%~1"=="" goto usage
if "%~2"=="" goto usage

set "PROJECT=%~1"
set "TITLE=%~2"
set "RESUME_MODE=%~3"
set "EXIT_CODE=1"

for /f "delims=" %%i in ('wsl wslpath "%CD%\scripts\codex-work.sh"') do set "WSL_CODEX_WORK=%%i"
if not defined WSL_CODEX_WORK (
  echo Failed to resolve codex-work.sh path.
  goto end
)

if defined RESUME_MODE (
  wsl env CONTROL_TOWER_RESUME_MODE=%RESUME_MODE% bash "%WSL_CODEX_WORK%" "%PROJECT%" "%TITLE%"
) else (
  wsl bash "%WSL_CODEX_WORK%" "%PROJECT%" "%TITLE%"
)
set "EXIT_CODE=%ERRORLEVEL%"
goto end

:usage
echo Usage: codex-wsl-launch.bat ^<project-or-path^> ^<session title^> [resume-mode]
echo Example: codex-wsl-launch.bat 0-a-control "morning control tower session" resume

:end
pause
exit /b %EXIT_CODE%
