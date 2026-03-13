@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "EXITCODE=0"

if /I "%~1"=="nobuild" (
    powershell -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%reset-docker-dev-env.ps1" -NoBuild
) else (
    powershell -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%reset-docker-dev-env.ps1"
)

set "EXITCODE=%ERRORLEVEL%"
if not "%EXITCODE%"=="0" (
    echo.
    echo reset-docker-dev-env failed with exit code %EXITCODE%.
    echo Check the error above. If Docker is not running, start Docker Desktop and retry.
    pause
)

endlocal & exit /b %EXITCODE%
