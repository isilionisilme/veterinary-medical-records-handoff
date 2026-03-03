@echo off
setlocal

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0preflight-quick.ps1" %*
set EXIT_CODE=%ERRORLEVEL%

if not "%EXIT_CODE%"=="0" (
  echo preflight-quick: FAILED (exit code %EXIT_CODE%)
  exit /b %EXIT_CODE%
)

echo preflight-quick: PASS
exit /b 0
