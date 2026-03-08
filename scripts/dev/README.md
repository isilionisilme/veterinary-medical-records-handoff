# scripts/dev

Scripts de soporte para desarrollo local y entorno Docker.

## Uso recomendado (rápido)

- **Reset local completo (DB + storage + backend + frontend):**
  - `./scripts/dev/reset-local-dev-env.ps1`
- **Reset Docker dev completo (compose down/up + wipe DB + health checks):**
  - `./scripts/dev/reset-docker-dev-env.ps1`
- **Arranque local de backend + frontend sin reset:**
  - `./scripts/dev/start-all.ps1`

---

## Estructura por capas

- **Entradas públicas (usar estos):**
  - `reset-local-dev-env.*`
  - `reset-docker-dev-env.*`
  - `start-all.*`
- **Capa interna (no llamar directamente salvo mantenimiento):**
  - `lib/reset-local-core.ps1`
  - `lib/reset-docker-core.ps1`

---

## Scripts PowerShell (`.ps1`)

| Script | Qué hace | Parámetros |
|---|---|---|
| `start-all.ps1` | Arranca entorno local de desarrollo en dos consolas: backend (`uvicorn --reload`) + frontend (`npm run dev`). También prepara `.venv` y dependencias si faltan. | `-NoBrowser` (actualmente sin efecto visible). |
| `reset-local-dev-env.ps1` | Orquestador local: primero intenta `docker compose down` del proyecto (si Docker está disponible), luego ejecuta reset local interno (`lib/reset-local-core.ps1`) y arranca backend + frontend con `start-all.ps1`. | `-NoStart` para hacer solo reset sin arrancar servicios. |
| `reset-docker-dev-env.ps1` | Orquestador Docker: detiene procesos locales de FE/BE, garantiza que Docker esté listo (arranca Docker Desktop en Windows si hace falta), y ejecuta reset/restart de Docker dev con health checks. | `-NoBuild`. |
| `reload-vscode-window.ps1` | Enfoca VS Code y ejecuta `Developer: Reload Window` vía atajos de teclado. | `-FocusDelayMs` (default `250`). |
| `lib/reset-local-core.ps1` | Capa interna: detiene el stack Docker del proyecto (best-effort), detiene procesos locales y limpia DB/storage local (`backend/data`, `backend/storage`). | Sin flags públicos. |
| `lib/reset-docker-core.ps1` | Capa interna: detiene procesos locales, asegura Docker disponible (auto-start en Windows), ejecuta `docker compose down/up`, wipe de DB y health checks backend/frontend. | `-NoBuild`. |

## Scripts batch (`.bat`)

| Script | Qué hace |
|---|---|
| `start-all.bat` | Wrapper de `start-all.ps1`. |
| `reset-local-dev-env.bat` | Wrapper de `reset-local-dev-env.ps1` (`nostart` -> `-NoStart`). |
| `reset-docker-dev-env.bat` | Wrapper de `reset-docker-dev-env.ps1` (`nobuild` -> `-NoBuild`). |
| `reload-vscode-window.bat` | Wrapper de `reload-vscode-window.ps1`. |
| `clear-documents.bat` | Limpia registros de documentos (tablas principales) y `backend/storage`; detiene procesos en `8000/5173`. Útil para limpiar dataset sin borrar toda la base. |

## Scripts Python (`.py`)

| Script | Qué hace |
|---|---|
| `interpretation_debug_snapshot.py` | Genera snapshot determinista de depuración de interpretación para un documento (estado de artefactos, schema normalizado, etc.). |
| `ab_compare_pdf_extractors.py` | Ejecuta comparación A/B del extractor PDF (`fitz` vs `fallback`) y guarda salidas + diff en archivos. |
