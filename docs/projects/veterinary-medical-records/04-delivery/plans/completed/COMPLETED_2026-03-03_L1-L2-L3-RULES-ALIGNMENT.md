# Plan: L1/L2/L3 Rules Alignment

**Fecha:** 2026-03-03
**Rama:** `chore/execution-rules-preflight-integration`
**PR:** #192
**Objetivo:** Cerrar el gap entre los scripts de preflight L1/L2/L3 y `execution-rules.md`, que es el documento que los agentes AI siguen paso a paso.

## Contexto

Los scripts `test-L1.ps1`, `test-L2.ps1`, `test-L3.ps1` ya existen y están documentados en el Engineering Playbook (`docs/shared/03-ops/engineering-playbook.md`). Sin embargo:

- `execution-rules.md` no los referencia en ninguna línea.
- La tabla de "local validation commands" en §CI-PIPELINE usa comandos ad-hoc (`pytest`, `vitest`, `playwright`) sin conectarlos con L1/L2/L3.
- Los agentes siguen `execution-rules.md` → nunca ven la instrucción de ejecutar L1/L2/L3.

La rama ya tiene 8 commits con scripts, hooks, docs y tests. Falta integrar L1/L2/L3 en `execution-rules.md` y abrir PR.

## Inventario de commits existentes

| # | SHA corto | Mensaje | Veredicto |
|---|-----------|---------|-----------|
| 1 | `00a0d66a` | `docs(code-review): strengthen review policy and router guidance` | ⚠️ Fuera de alcance L1/L2/L3 — decidir en P1-A |
| 2 | `8f441820` | `chore(ci): add local preflight runner and bat launcher` | ✅ Conservar |
| 3 | `9a2ce6dd` | `chore(preflight): make L2/L3 frontend checks path-scoped with force overrides` | ✅ Conservar |
| 4 | `1e8946c3` | `chore(preflight): broaden frontend impact scope and log skip rationale` | ✅ Conservar |
| 5 | `e3b4f636` | `docs(preflight): require L3 -ForceFull before merge to main for relevant changes` | ✅ Conservar |
| 6 | `3fd2f42e` | `test(docs-contract): enforce relevant-change and ForceFull policy terms` | ✅ Conservar |
| 7 | `1a094b55` | `chore(preflight): add L1/L2/L3 script entrypoints with legacy aliases` | ✅ Conservar |
| 8 | `218f6795` | `docs(preflight): adopt L1/L2/L3 naming in docs and contract tests` | ✅ Conservar |

## Estado de ejecución

### Fase 1 — Preparación de rama

- [x] P1-A 🚧 — Decisión: conservar o separar commit `00a0d66a` (code-review) (Claude) — ✅ Moot: los 8 commits ya están en main via PR #187 squash-merge
- [x] P1-B 🔄 — Rebase interactivo sobre `origin/main`, resolver conflictos (Claude) — ✅ Nueva rama `chore/execution-rules-preflight-integration` creada desde main actual

### Fase 2 — Integrar L1/L2/L3 en execution-rules.md

- [x] P2-A 🔄 — **Commit 1:** Actualizar §CI-PIPELINE §4 — reemplazar tabla de comandos ad-hoc por referencia a L1/L2/L3 (Claude) — ✅ `845fef9d`
  - Archivo: `docs/projects/veterinary-medical-records/03-ops/execution-rules.md`
  - Cambio: la tabla "Local validation command" pasa a ser "run the targeted preflight level" con referencia al Engineering Playbook
  - Mantener los comandos específicos como ejemplos bajo los niveles, no como la fuente primaria
- [x] P2-B 🔄 — **Commit 2:** Actualizar §Format-before-commit — integrar con L1 (Claude) — ✅ `dfb2fe89`
  - Archivo: `docs/projects/veterinary-medical-records/03-ops/execution-rules.md`
  - Cambio: anotar que L1 cubre format + lint + doc guards, por lo que el agente puede ejecutar `test-L1.ps1` en lugar de los 2 comandos manuales
- [x] P2-C 🔄 — **Commit 3:** Añadir §"Local preflight integration" en execution-rules.md (Claude) — ✅ `2fa4ac0d`
  - Archivo: `docs/projects/veterinary-medical-records/03-ops/execution-rules.md`
  - Nuevo bloque que mapea momentos del SCOPE BOUNDARY a niveles de preflight:

    | Momento SCOPE BOUNDARY | Nivel mínimo | Comando |
    |---|---|---|
    | Antes de STEP A (commit) | L1 | `scripts/ci/test-L1.ps1 -BaseRef HEAD` |
    | Antes de STEP C (push) | L2 | `scripts/ci/test-L2.ps1 -BaseRef main` |
    | Antes de crear/actualizar PR | L3 | `scripts/ci/test-L3.ps1 -BaseRef main` |
    | Antes de merge a main (cambio relevante) | L3 -ForceFull | `scripts/ci/test-L3.ps1 -BaseRef main -ForceFull` |

### Fase 3 — Tests de contrato y validación

- [x] P3-A 🔄 — **Commit 4:** Añadir test de contrato: execution-rules.md referencia L1/L2/L3 (Claude) — ✅ `2f8cef65`
  - Archivo: `backend/tests/unit/test_doc_updates_contract.py`
  - Nuevo test: `test_execution_rules_reference_preflight_levels`
  - Assertions: execution-rules.md contiene `test-L1`, `test-L2`, `test-L3`, `L1 —`, `L2 —`, `L3 —`, `ForceFull`
- [x] P3-B 🔄 — **Commit 5:** Ejecutar L1 preflight, corregir fallos si los hay (Claude) — ✅ PASS (no fixes needed)

### Fase 4 — PR

- [x] P4-A 🔄 — Push + crear PR draft + ejecutar L3 (Claude) — ✅ PR #192 created

## Riesgos

| Riesgo | Mitigación |
|---|---|
| Inconsistencia entre tabla ad-hoc y L1/L2/L3 | No eliminar la tabla ad-hoc — anotar que L1/L2/L3 la sustituyen y dejar los comandos como referencia interna |
