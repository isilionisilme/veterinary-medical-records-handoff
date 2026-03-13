@echo off
setlocal

set "ROOT=%~dp0..\.."
for %%I in ("%ROOT%") do set "ROOT=%%~fI"

set "DB=%ROOT%\backend\data\documents.db"
set "STORAGE=%ROOT%\backend\storage"
set "VENV_PY=%ROOT%\.venv\Scripts\python.exe"

echo.
echo === Limpiando documentos locales ===
echo Repo: %ROOT%
echo.

echo [1/3] Deteniendo procesos en puertos de desarrollo (8000/5173)...
call :kill_port 8000
call :kill_port 5173

echo [2/3] Limpiando base de datos...
if not exist "%DB%" (
  echo - No existe DB en %DB%
) else (
  if exist "%VENV_PY%" (
    "%VENV_PY%" -c "import sqlite3; db=r'%DB%'; conn=sqlite3.connect(db); conn.execute('PRAGMA foreign_keys = OFF'); [conn.execute('DELETE FROM ' + t) for t in ('artifacts','processing_runs','document_status_history','documents')]; conn.commit(); conn.close(); print('- DB limpiada')"
  ) else (
    py -3 -c "import sqlite3; db=r'%DB%'; conn=sqlite3.connect(db); conn.execute('PRAGMA foreign_keys = OFF'); [conn.execute('DELETE FROM ' + t) for t in ('artifacts','processing_runs','document_status_history','documents')]; conn.commit(); conn.close(); print('- DB limpiada')"
  )
  if errorlevel 1 (
    echo - ERROR limpiando DB. Cierra procesos que usen backend/data/documents.db y vuelve a ejecutar.
    exit /b 1
  )
)

echo [3/3] Limpiando storage...
if exist "%STORAGE%" (
  rmdir /s /q "%STORAGE%"
)
mkdir "%STORAGE%" >nul 2>&1
echo - Storage limpiado.

echo.
echo OK: documentos e historial locales eliminados.
echo Puedes volver a arrancar con scripts\dev\start-all.bat
echo.

endlocal
exit /b 0

:kill_port
set "TARGET_PORT=%~1"
for /f "tokens=5" %%P in ('netstat -ano ^| findstr /r /c:":%TARGET_PORT% .*LISTENING"') do (
  if not "%%P"=="0" (
    taskkill /PID %%P /T /F >nul 2>&1
    echo - detenido PID %%P (puerto %TARGET_PORT%)
  )
)
exit /b 0
