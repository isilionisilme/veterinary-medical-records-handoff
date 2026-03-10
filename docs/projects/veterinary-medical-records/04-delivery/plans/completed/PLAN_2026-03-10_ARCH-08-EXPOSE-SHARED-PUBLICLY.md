# Plan: ARCH-08 — Expose `_shared` Functions Publicly

> **Operational rules:** See [plan-execution-protocol.md](../../../03-ops/plan-execution-protocol.md) for agent execution protocol, SCOPE BOUNDARY template, commit conventions, and handoff messages.

**Backlog item:** [arch-08-expose-shared-functions-publicly.md](../../Backlog/completed/arch-08-expose-shared-functions-publicly.md)
**Branch:** `refactor/arch-08-expose-shared-publicly`
**PR:** `#264`
**Prerequisite:** `main` actualizado y tests verdes
**Worktree:** `D:\Git\worktrees\segundo`
**CI Mode:** `1) Local-only`
**Execution Mode:** `Autonomous`
**Model Assignment:** `Custom`
**Agents:** `GitHub Copilot (GPT-5.4)`

---

## Agent Instructions

1. **En cuanto termines una tarea, márcala como completada en el plan** (checkbox `[x]` inmediato, sin esperar lote).
2. **Cuando llegues a una sugerencia de commit, lanza los tests L2** (`scripts/ci/test-L2.ps1`). Si no funcionan, repáralos. Cuando L2 esté verde, espera instrucciones del usuario.
3. **No hagas commit ni push sin aprobación** explícita del usuario.

---

## Context

`api/routes_review.py` (line 30) imports `_locate_visit_date_occurrences_from_raw_text` directly from the private module `application/documents/_shared.py`. This breaks encapsulation: the API layer reaches into a `_`-prefixed internal module instead of consuming the public interface exposed by `application/documents/__init__.py`.

### Current state

| File | Relevant detail |
|---|---|
| `backend/app/application/documents/_shared.py` | Defines `_locate_visit_date_occurrences_from_raw_text` (line 284) |
| `backend/app/application/documents/__init__.py` | Already re-exports `_normalize_visit_date_candidate` from `_shared`; does NOT re-export `_locate_visit_date_occurrences_from_raw_text` |
| `backend/app/api/routes_review.py` | Line 30: `from backend.app.application.documents._shared import _locate_visit_date_occurrences_from_raw_text` |

### Target state

1. `application/documents/__init__.py` re-exports `_locate_visit_date_occurrences_from_raw_text`.
2. `api/routes_review.py` imports it from `application/documents` (public API), not from `_shared`.
3. No `api/` file imports from any `_`-prefixed module.

---

## Scope Boundary

- **In scope:** `backend/app/application/documents/__init__.py`, `backend/app/api/routes_review.py`.
- **Out of scope:** renaming the function (still starts with `_` — that's a separate concern), refactoring other `_`-prefixed re-exports already in `__init__.py`, any frontend or docs changes.

---

## Commit recommendations (inline, non-blocking)

| After steps | Recommended message |
|---|---|
| P1-A .. P1-C | `refactor(api): re-export _locate_visit_date_occurrences via public documents API` |
| P2-A | `refactor(api): add validation evidence for ARCH-08` |

En modo Supervisado, cada commit requiere confirmación explícita del usuario.
Push permanece manual en todos los modos.

---

## Execution Status

**Leyenda**
- 🔄 auto-chain — ejecutable por agente
- 🚧 hard-gate — revisión/decisión de usuario

### Phase 1 — Re-export and update import

- [x] P1-A 🔄 — In `backend/app/application/documents/__init__.py`: add `_locate_visit_date_occurrences_from_raw_text` to the import from `_shared` (line 1) and add it to the `__all__` list in alphabetical order. — `no-commit (pending commit point)`
- [x] P1-B 🔄 — In `backend/app/api/routes_review.py`: change line 30 from `from backend.app.application.documents._shared import _locate_visit_date_occurrences_from_raw_text` to `from backend.app.application.documents import _locate_visit_date_occurrences_from_raw_text`. — `no-commit (pending commit point)`
- [x] P1-C 🔄 — Run grep across `backend/app/api/` to confirm zero remaining imports from any `_`-prefixed module. Document result as evidence. — `no-commit (pending commit point)`

Evidence P1-C: `grep_search` on `backend/app/api/**/*.py` with pattern `from .*\._` returned no matches after the import update.

> **Commit point →** `refactor(api): re-export _locate_visit_date_occurrences via public documents API`
> Lanzar L2. Si falla, reparar. Cuando L2 verde → esperar instrucciones del usuario.

### Phase 2 — Validation & closure

- [x] P2-A 🔄 — Run full test suite (L2). Document pass evidence. — `no-commit (pending commit point)`
- [x] P2-B 🚧 — Hard-gate: usuario valida resultados y aprueba para commit + PR.

Evidence P2-A: `scripts/ci/test-L2.ps1` passed after repairing the public package export syntax, resolving required plan metadata fields (`**Execution Mode:**`, `**Model Assignment:**`), and extracting review debug/scoping helpers so backend complexity checks passed. Final L2 result: backend `831 passed, 2 xfailed`; frontend `53 passed / 345 passed`; `preflight-ci-local: PASS`.

Evidence P2-B: usuario aprobó commit y push tras validar resultados. Confirmatory validation beyond plan minimum also passed with `scripts/ci/test-L3.ps1`: backend `831 passed, 2 xfailed`; frontend unit/integration `53 files / 345 tests`; Playwright `18 passed, 1 skipped`; final result `preflight-ci-local: PASS`.

> **Commit point →** (si el usuario solicita un commit separado de evidencia, usar: `refactor(api): add validation evidence for ARCH-08`)

---

## How to test

1. After the change, verify the import works: `python -c "from backend.app.application.documents import _locate_visit_date_occurrences_from_raw_text; print('OK')"`.
2. Run `scripts/ci/test-L2.ps1` — all tests must pass.
3. Grep: `Select-String -Path backend/app/api/*.py -Pattern 'from.*\._' -Recurse` should return zero matches from `_shared` or any `_`-prefixed application module.
