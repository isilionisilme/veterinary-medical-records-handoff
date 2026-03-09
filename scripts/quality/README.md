# scripts/quality

Guardrails de calidad visual y consistencia de diseño.

## Qué hace cada script

| Script | Qué hace |
|---|---|
| `check_brand_compliance.py` | Revisa líneas añadidas en `frontend/` y valida cumplimiento de brand (paleta hex permitida y reglas de tipografía). |
| `check_design_system.mjs` | Detecta violaciones de design system en frontend (tokens, estilos inline, icon buttons sin label, bypasses no permitidos, etc.). |
| `architecture_metrics.py` | Recolecta métricas de arquitectura (CC, LOC, churn, hex violations, hotspots, scans) y genera `tmp/audit/metrics.json` + `tmp/audit/metrics-report.md`. Soporta modo `--check` para CI. |

## Notas rápidas

- Están orientados a cambios frontend y suelen ejecutarse en preflight/CI.
- Ejecuta desde la raíz del repositorio.
