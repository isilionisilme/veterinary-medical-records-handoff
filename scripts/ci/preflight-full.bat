@echo off
setlocal

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0preflight-full.ps1" %*
set EXIT_CODE=%ERRORLEVEL%

if not "%EXIT_CODE%"=="0" (
  echo preflight-full: FAILED (exit code %EXIT_CODE%)
  exit /b %EXIT_CODE%
)

echo preflight-full: PASS
exit /b 0
