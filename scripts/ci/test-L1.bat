@echo off
setlocal

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0test-L1.ps1" %*
set EXIT_CODE=%ERRORLEVEL%

if not "%EXIT_CODE%"=="0" (
  echo test-L1: FAILED (exit code %EXIT_CODE%)
  exit /b %EXIT_CODE%
)

echo test-L1: PASS
exit /b 0