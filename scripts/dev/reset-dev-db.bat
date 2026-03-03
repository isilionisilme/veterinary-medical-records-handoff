@echo off
setlocal

set "SCRIPT_DIR=%~dp0"

if /I "%~1"=="nostart" (
    powershell -ExecutionPolicy Bypass -File "%SCRIPT_DIR%reset-dev-db.ps1" -NoStartBackend
) else (
    powershell -ExecutionPolicy Bypass -File "%SCRIPT_DIR%reset-dev-db.ps1"
)

endlocal
