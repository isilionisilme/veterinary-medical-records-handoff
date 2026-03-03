@echo off
setlocal

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0preflight-ci-local.ps1" %*
set EXIT_CODE=%ERRORLEVEL%

if not "%EXIT_CODE%"=="0" (
  echo preflight-ci-local: FAILED (exit code %EXIT_CODE%)
  exit /b %EXIT_CODE%
)

echo preflight-ci-local: PASS
exit /b 0
