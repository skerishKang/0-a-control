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

if /I "%AGENT%"=="kilo" (
  rem Keep the main Kilo data store on G:\kilo, while config/cache/state stay on G:\KiloProfile.
  set "XDG_DATA_HOME=G:\"
  set "XDG_CONFIG_HOME=G:\KiloProfile\.config"
  set "XDG_CACHE_HOME=G:\KiloProfile\.cache"
  set "XDG_STATE_HOME=G:\KiloProfile\.local\state"

  if not exist "%XDG_DATA_HOME%\kilo" mkdir "%XDG_DATA_HOME%\kilo"
  if not exist "%XDG_CONFIG_HOME%\kilo" mkdir "%XDG_CONFIG_HOME%\kilo"
  if not exist "%XDG_CACHE_HOME%\kilo" mkdir "%XDG_CACHE_HOME%\kilo"
  if not exist "%XDG_STATE_HOME%\kilo" mkdir "%XDG_STATE_HOME%\kilo"

  rem One-time bootstrap: carry over settings and session DB, but skip large snapshot data.
  if exist "%USERPROFILE%\.config\kilo" (
    robocopy "%USERPROFILE%\.config\kilo" "%XDG_CONFIG_HOME%\kilo" /E /XO /R:1 /W:1 /NFL /NDL /NJH /NJS /NP >nul
  )

  if exist "%USERPROFILE%\.local\share\kilo\kilo.db" if not exist "%XDG_DATA_HOME%\kilo\kilo.db" copy /Y "%USERPROFILE%\.local\share\kilo\kilo.db" "%XDG_DATA_HOME%\kilo\kilo.db" >nul
  if exist "%USERPROFILE%\.local\share\kilo\kilo.db-shm" if not exist "%XDG_DATA_HOME%\kilo\kilo.db-shm" copy /Y "%USERPROFILE%\.local\share\kilo\kilo.db-shm" "%XDG_DATA_HOME%\kilo\kilo.db-shm" >nul
  if exist "%USERPROFILE%\.local\share\kilo\kilo.db-wal" if not exist "%XDG_DATA_HOME%\kilo\kilo.db-wal" copy /Y "%USERPROFILE%\.local\share\kilo\kilo.db-wal" "%XDG_DATA_HOME%\kilo\kilo.db-wal" >nul
  if exist "%USERPROFILE%\.local\share\kilo\auth.json" if not exist "%XDG_DATA_HOME%\kilo\auth.json" copy /Y "%USERPROFILE%\.local\share\kilo\auth.json" "%XDG_DATA_HOME%\kilo\auth.json" >nul
  if exist "%USERPROFILE%\.local\share\kilo\telemetry-id" if not exist "%XDG_DATA_HOME%\kilo\telemetry-id" copy /Y "%USERPROFILE%\.local\share\kilo\telemetry-id" "%XDG_DATA_HOME%\kilo\telemetry-id" >nul
)

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
