# scripts/docs

Scripts de validación, generación y sincronización de documentación.

## Qué hace cada script

| Script | Qué hace |
|---|---|
| `check_doc_test_sync.py` | Verifica sincronización doc→tests/guards según `docs/agent_router/01_WORKFLOW/DOC_UPDATES/test_impact_map.json`. |
| `check_doc_router_parity.py` | Verifica paridad source-doc→router modules según `docs/agent_router/01_WORKFLOW/DOC_UPDATES/router_parity_map.json`. |
| `check_router_directionality.py` | Bloquea cambios en módulos router protegidos sin cambios en su fuente canónica correspondiente. |
| `check_no_canonical_router_refs.py` | Falla si docs canónicos referencian `docs/agent_router/*` (con excepciones permitidas). |
| `check_docs_links.mjs` | Ejecuta verificación de enlaces Markdown en alcance canónico (`docs/README.md`, `docs/project`, `docs/shared`). |
| `classify_doc_change.py` | Clasifica cambios docs en Rule / Clarification / Navigation y genera `doc_change_classification.json`. |
| `generate-router-files.py` | Regenera mini-archivos router desde `docs/agent_router/MANIFEST.yaml` (modo normal o `--check`). |
| `sync_docs_to_wiki.py` | Sincroniza documentación a GitHub Wiki y genera estructura de páginas/navegación. |
| `docs-local-preview.ps1` | Construye preview local de wiki docs y opcionalmente levanta servidor local. |
| `docs-local-preview.bat` | Wrapper CMD para `docs-local-preview.ps1`. |
| `router_directionality_guard_config.json` | Configuración de soporte para `check_router_directionality.py`. |

## Notas rápidas

- La mayoría de guards aceptan `--base-ref` para comparar contra `main` u otra base.
- Ejecuta estos scripts desde la raíz del repositorio.
