@echo off
setlocal

set "SCRIPT_DIR=%~dp0"

if /I "%~1"=="nostart" (
    powershell -ExecutionPolicy Bypass -File "%SCRIPT_DIR%reset-local-dev-env.ps1" -NoStart
) else (
    powershell -ExecutionPolicy Bypass -File "%SCRIPT_DIR%reset-local-dev-env.ps1"
)

endlocal
