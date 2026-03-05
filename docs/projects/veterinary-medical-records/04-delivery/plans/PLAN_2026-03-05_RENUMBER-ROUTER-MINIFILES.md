# Plan: Renumber Router Mini-files

> **Operational rules:** See [plan-execution-protocol.md](../../03-ops/plan-execution-protocol.md) for agent execution protocol, SCOPE BOUNDARY template, commit-task schema, and handoff rules.

**Rama:** `chore/router-directionality-protection`
**PR:** #205 (draft)
**Prerequisito:** ENGINEERING_PLAYBOOK eliminado.
**Worktree:** `D:/Git/veterinary-medical-records`
**CI Mode:** `1) Strict step gate`
**Agents:** `Claude Opus 4.6 + Codex 5.3`

## Context

La eliminación de ENGINEERING_PLAYBOOK dejó gaps en la numeración de 2 directorios de router:
- **CODING_STANDARDS**: gaps en 90 y 150 (heredados del monolito original).
- **UX_GUIDELINES**: gap en 10 (archivos empezaban en 20).

Los demás directorios (BRAND_GUIDELINES, DOCUMENTATION_GUIDELINES, WAY_OF_WORKING) ya tienen numeración limpia.

## Objective

- Cerrar gaps de numeración en CODING_STANDARDS y UX_GUIDELINES.
- Todos los directorios router quedan con secuencias consecutivas sin huecos.

## Scope

- **In scope:** renumerar archivos derivados vía MANIFEST.yaml + regeneración.
- **Out of scope:** contenido canónico, tests, JSON maps (todos usan globs `*.md`, no paths con número).
- `metrics/llm_benchmarks/runs.jsonl` es histórico — no tocar.

## Renumbering tables

### CODING_STANDARDS (6 archivos cambian)

| Viejo | Nuevo | Slug |
|-------|-------|------|
| 10 | 10 | `preamble` |
| 20 | 20 | `change-discipline` |
| 30 | 30 | `code-style-consistency` |
| 40 | 40 | `structure-separation-of-concerns` |
| 50 | 50 | `explicit-contracts-schemas` |
| 60 | 60 | `state-management-workflow-safety` |
| 70 | 70 | `traceability-human-control` |
| 80 | 80 | `error-handling-observability` |
| **100 → 90** | | `testing-discipline` |
| **110 → 100** | | `data-handling-safety` |
| **120 → 110** | | `configuration-environment-separation` |
| **130 → 120** | | `versioning-evolution` |
| **140 → 130** | | `dependency-management` |
| **160 → 140** | | `naming-conventions` |

### UX_GUIDELINES (9 archivos cambian)

| Viejo | Nuevo | Slug |
|-------|-------|------|
| **20 → 10** | | `scope-and-authority` |
| **30 → 20** | | `core-ux-principles` |
| **40 → 30** | | `human-in-the-loop-shared-principle` |
| **50 → 40** | | `confidence-uncertainty-shared-principle` |
| **60 → 50** | | `accessibility-usability` |
| **70 → 60** | | `role-specific-workflows` |
| **80 → 70** | | `governance-review-shared-boundary` |
| **90 → 80** | | `delegation-rule-mandatory` |
| **100 → 90** | | `final-rule` |

## Commit plan

| # | Commit message | Files touched | Step |
|---|---|---|---|
| C1 | `docs(router): renumber CODING_STANDARDS and UX_GUIDELINES — close numbering gaps` | `MANIFEST.yaml`, `03_SHARED/CODING_STANDARDS/*`, `03_SHARED/UX_GUIDELINES/*` | F1-A through F1-D |

## Operational override steps

### CT-1 — Commit renumbering bundle

- `type`: `commit-task`
- `trigger`: after F1-A, F1-B, F1-C, F1-D are `[x]`
- `preconditions`: `python scripts/docs/generate-router-files.py --check` passes; targeted contract tests green (61 tests)
- `commands`:
  - `git add docs/agent_router/MANIFEST.yaml docs/agent_router/03_SHARED/CODING_STANDARDS/ docs/agent_router/03_SHARED/UX_GUIDELINES/`
  - `git commit -m "docs(router): renumber CODING_STANDARDS and UX_GUIDELINES — close numbering gaps"`
  - `git push origin chore/router-directionality-protection`
- `approval`: `auto`
- `fallback`: if commit fails, check for unstaged orphans and retry with explicit file list

---

## Estado de ejecución

### Phase 1 — Renumber router mini-files

- [x] F1-A 🔄 — **Update MANIFEST.yaml** — Cambiar los 15 targets afectados (6 CODING_STANDARDS + 9 UX_GUIDELINES) a sus nuevos números según las tablas de renumeración. — ✅ `0140262c`
- [x] F1-B 🔄 — **Regenerate router files** — Ejecutar `python scripts/docs/generate-router-files.py`. Verificar que crea archivos con nuevos nombres. — ✅ `0140262c`
- [x] F1-C 🔄 — **Delete orphan files** — Eliminar los 6 archivos huérfanos de CODING_STANDARDS y los 9 de UX_GUIDELINES (los renumerados que quedan con nombre viejo en disco). — ✅ `0140262c`
- [x] F1-D 🔄 — **Validate** — Ejecutar drift check + 61 contract tests. Todos deben pasar. — ✅ `0140262c`
- [x] F1-E 🔄 — **Commit-task CT-1** — Ejecutar CT-1 (SCOPE BOUNDARY: commit code, commit plan update, push). — ✅ `0140262c`

---

## Relevant files

- `docs/agent_router/MANIFEST.yaml` — 15 target lines to edit (only file manually changed)
- `docs/agent_router/03_SHARED/CODING_STANDARDS/` — 6 orphans to delete after regeneration
- `docs/agent_router/03_SHARED/UX_GUIDELINES/` — 9 orphans to delete after regeneration

---

## Cola de prompts

### F1-A — Update MANIFEST.yaml

```text
Update `docs/agent_router/MANIFEST.yaml`:

CODING_STANDARDS — change these 6 targets:
  100_testing-discipline.md → 90_testing-discipline.md
  110_data-handling-safety.md → 100_data-handling-safety.md
  120_configuration-environment-separation.md → 110_configuration-environment-separation.md
  130_versioning-evolution.md → 120_versioning-evolution.md
  140_dependency-management.md → 130_dependency-management.md
  160_naming-conventions.md → 140_naming-conventions.md

UX_GUIDELINES — change these 9 targets:
  20_scope-and-authority.md → 10_scope-and-authority.md
  30_core-ux-principles.md → 20_core-ux-principles.md
  40_human-in-the-loop-shared-principle.md → 30_human-in-the-loop-shared-principle.md
  50_confidence-uncertainty-shared-principle.md → 40_confidence-uncertainty-shared-principle.md
  60_accessibility-usability.md → 50_accessibility-usability.md
  70_role-specific-workflows.md → 60_role-specific-workflows.md
  80_governance-review-shared-boundary.md → 70_governance-review-shared-boundary.md
  90_delegation-rule-mandatory.md → 80_delegation-rule-mandatory.md
  100_final-rule.md → 90_final-rule.md

Do not change any other fields (source, sections, type, title, description).
```

⚠️ AUTO-CHAIN → F1-B

### F1-B — Regenerate router files

```text
Run: python scripts/docs/generate-router-files.py

Verify that the new files exist:
  CODING_STANDARDS: 90_*, 100_*, 110_*, 120_*, 130_*, 140_*
  UX_GUIDELINES: 10_*, 20_*, 30_*, 40_*, 50_*, 60_*, 70_*, 80_*, 90_*
```

⚠️ AUTO-CHAIN → F1-C

### F1-C — Delete orphan files

```text
Delete these orphan files (old numbers still on disk after regeneration):

CODING_STANDARDS:
  docs/agent_router/03_SHARED/CODING_STANDARDS/100_testing-discipline.md
  docs/agent_router/03_SHARED/CODING_STANDARDS/110_data-handling-safety.md
  docs/agent_router/03_SHARED/CODING_STANDARDS/120_configuration-environment-separation.md
  docs/agent_router/03_SHARED/CODING_STANDARDS/130_versioning-evolution.md
  docs/agent_router/03_SHARED/CODING_STANDARDS/140_dependency-management.md
  docs/agent_router/03_SHARED/CODING_STANDARDS/160_naming-conventions.md

UX_GUIDELINES:
  docs/agent_router/03_SHARED/UX_GUIDELINES/20_scope-and-authority.md
  docs/agent_router/03_SHARED/UX_GUIDELINES/30_core-ux-principles.md
  docs/agent_router/03_SHARED/UX_GUIDELINES/40_human-in-the-loop-shared-principle.md
  docs/agent_router/03_SHARED/UX_GUIDELINES/50_confidence-uncertainty-shared-principle.md
  docs/agent_router/03_SHARED/UX_GUIDELINES/60_accessibility-usability.md
  docs/agent_router/03_SHARED/UX_GUIDELINES/70_role-specific-workflows.md
  docs/agent_router/03_SHARED/UX_GUIDELINES/80_governance-review-shared-boundary.md
  docs/agent_router/03_SHARED/UX_GUIDELINES/90_delegation-rule-mandatory.md
  docs/agent_router/03_SHARED/UX_GUIDELINES/100_final-rule.md

CAUTION: Only delete files whose numbers have CHANGED. Do not delete files that kept the same number.
```

⚠️ AUTO-CHAIN → F1-D

### F1-D — Validate

```text
Run both validation commands:

1. python scripts/docs/generate-router-files.py --check
2. python -m pytest backend/tests/unit/test_doc_router_contract.py backend/tests/unit/test_doc_updates_contract.py backend/tests/unit/test_doc_router_parity_contract.py backend/tests/unit/test_doc_test_sync_guard.py --tb=short --no-header -p no:cacheprovider --no-cov

Expected: drift check OK + 61 tests passing.
If any fail: diagnose and fix before proceeding to CT-1.
```

⚠️ AUTO-CHAIN → F1-E

## Active Prompt

_(empty — populated at execution time)_
