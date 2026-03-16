@echo off
setlocal EnableExtensions

if "%~2"=="" (
  echo Usage: agent-direct-launch.bat ^<agent^> ^<workspace^> [window title]
  exit /b 1
)

set "AGENT=%~1"
set "WORKSPACE=%~f2"
set "WINDOW_TITLE=%~3"

if "%WINDOW_TITLE%"=="" (
  set "WINDOW_TITLE=%AGENT% session"
)

cd /d "%WORKSPACE%" || (
  echo Failed to open workspace: %WORKSPACE%
  exit /b 1
)

title %WINDOW_TITLE%

set "CLI_CMD=%AGENT%.cmd"
set "NPM_SHIM=%AppData%\npm\%CLI_CMD%"

if exist "%NPM_SHIM%" (
  call "%NPM_SHIM%"
) else (
  call %CLI_CMD%
)

set "EXIT_CODE=%ERRORLEVEL%"
pause
exit /b %EXIT_CODE%
