@echo off
setlocal

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0test-L3.ps1" %*
set EXIT_CODE=%ERRORLEVEL%

if not "%EXIT_CODE%"=="0" (
  echo test-L3: FAILED (exit code %EXIT_CODE%)
  exit /b %EXIT_CODE%
)

echo test-L3: PASS
exit /b 0