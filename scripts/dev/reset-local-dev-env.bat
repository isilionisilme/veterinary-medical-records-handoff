@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "EXITCODE=0"

if /I "%~1"=="nostart" (
    powershell -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%reset-local-dev-env.ps1" -NoStart
) else (
    powershell -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%reset-local-dev-env.ps1"
)

set "EXITCODE=%ERRORLEVEL%"
if not "%EXITCODE%"=="0" (
    echo.
    echo reset-local-dev-env failed with exit code %EXITCODE%.
    echo Check the error above and retry.
    pause
)

endlocal & exit /b %EXITCODE%
