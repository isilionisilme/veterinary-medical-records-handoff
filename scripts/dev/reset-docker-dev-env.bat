@echo off
setlocal

set "SCRIPT_DIR=%~dp0"

if /I "%~1"=="nobuild" (
    powershell -ExecutionPolicy Bypass -File "%SCRIPT_DIR%reset-docker-dev-env.ps1" -NoBuild
) else (
    powershell -ExecutionPolicy Bypass -File "%SCRIPT_DIR%reset-docker-dev-env.ps1"
)

endlocal

