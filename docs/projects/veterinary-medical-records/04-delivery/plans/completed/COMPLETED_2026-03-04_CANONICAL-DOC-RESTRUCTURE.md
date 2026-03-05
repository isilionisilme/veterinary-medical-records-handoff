# Plan: Canonical Documentation Restructuring

> **Operational rules:** See [plan-execution-protocol.md](../../03-ops/plan-execution-protocol.md) for agent execution protocol, SCOPE BOUNDARY template, commit-task schema, and handoff rules.

**Rama:** `chore/canonical-doc-restructure-ci-guards` (PR-2; PR-1 was `docs/canonical-doc-restructure`)
**PR:** [#197](https://github.com/isilionisilme/veterinary-medical-records/pull/197) (PR-1, merged), PR-2 pending
**Prerequisito:** `main` estable.
**Worktree:** `D:\Git\veterinary-medical-records`
**CI Mode:** `1) Strict step gate`
**Agents:** `Claude Opus 4.6 + Codex`

## Context

Las reglas operativas del proyecto están distribuidas en ~75 archivos bajo `docs/agent_router/` (mini-archivos optimizados para agentes) y en `docs/shared/03-ops/engineering-playbook.md` (764 líneas, monolito). Hay 35+ instancias de duplicación, el Engineering Playbook mezcla estándares técnicos con proceso operativo, y `execution-rules.md` (636 líneas) contiene reglas que no están en ningún doc human-readable.

Este plan establece 7 documentos canónicos (5 shared, 2 project) como single source of truth para todas las reglas operativas, con dirección de flujo estricta: **canonical → router, nunca al revés**.

## Objective

- Toda regla operativa vive en exactamente un documento canónico (human-readable, wiki-ready).
- Los mini-archivos del `agent_router/` son outputs derivados, nunca editados directamente.
- `engineering-playbook.md` desaparece; su contenido migra a 3 canónicos.
- CI protege la direccionalidad canonical → router.

## Scope Boundary (strict)

- **In scope:** crear canónicos, eliminar engineering-playbook.md, actualizar referencias, script de derivación, CI checks.
- **Out of scope:** cambios a brand-guidelines.md o ux-guidelines.md (salvo governance header), cambios de código, cambios a extraction-tracking run reports o field-level tracking files.

## Design decisions

| Decision | Choice | Rationale |
|---|---|---|
| Canonical doc count | 7 (5 shared + 2 project) | Natural topic clustering; each doc reads as a coherent unit |
| `contributing.md` vs `way-of-working.md` | `way-of-working.md` | More descriptive of content (branch→commit→PR→review→done lifecycle) |
| engineering-playbook.md fate | Delete after migration | Content fully covered by 3 new canonicals |
| Directionality enforcement | CI check + regeneration script | Convention alone is insufficient; automated protection required |
| brand/ux guidelines | Keep as-is, add governance header only | Already well-structured canonical docs |
| Router mini-files | Derived via script + manifest | Single source of truth; no manual edits to router |
| Derived router files strategy | Delete ~58 derived files, regenerate from scratch | Cleaner than incremental update; avoids stale content. Keep routing infra (00_AUTHORITY, 00_FALLBACK, 00_RULES_INDEX, README), DOC_UPDATES, 02_PRODUCT pointers, 04_PROJECT (out of scope), extraction ADR/ITERATIONS, extraction-tracking |

## PR Roadmap

| PR | Rama | Fases | Alcance | Depende de |
|---|---|---|---|---|
| **PR-1** | `docs/canonical-doc-restructure` | F1, F2 | Crear 5 canónicos nuevos, governance headers, eliminar engineering-playbook.md, fix refs | — |
| **PR-2** | `chore/router-directionality-protection` | F3, F4 | Regenerar router desde canónicos, manifest, CI directionality + drift checks | PR-1 merged |

## Commit plan

| # | Commit message | Files touched | Step |
|---|---|---|---|
| C1 | `docs(shared): add coding-standards.md — tech standards canonical` | `docs/shared/02-tech/coding-standards.md` | F1-A |
| C2 | `docs(shared): add documentation-guidelines.md — doc standards canonical` | `docs/shared/02-tech/documentation-guidelines.md` | F1-B |
| C3 | `docs(shared): add way-of-working.md — ops workflow canonical` | `docs/shared/03-ops/way-of-working.md` | F1-C |
| C4 | `docs(project): add plan-execution-protocol.md — agent execution canonical` | `docs/projects/.../03-ops/plan-execution-protocol.md` | F1-D |
| C5 | `docs(project): add extraction-quality.md — extraction rules canonical` | `docs/projects/.../02-tech/extraction-quality.md` | F1-E |
| C6 | `docs(shared): add governance headers to brand-guidelines and ux-guidelines` | `docs/shared/01-product/brand-guidelines.md`, `docs/shared/01-product/ux-guidelines.md` | F2-A |
| C7 | `docs(shared): delete engineering-playbook.md — replaced by 3 canonicals` | `docs/shared/03-ops/engineering-playbook.md` (delete) | F2-B |
| C8 | `docs(shared): update wiki section indexes for new canonical docs` | `docs/shared/02-tech/`, `docs/shared/03-ops/` index files | F2-C |
| C9 | `docs: fix all cross-references from engineering-playbook.md to new canonicals` | Multiple files (grep + replace) | F2-D |
| C10 | `docs(router): add MANIFEST.yaml — canonical-to-router derivation map` | `docs/agent_router/MANIFEST.yaml` | F3-A |
| C11 | `chore(scripts): add generate-router-files.py — canonical→router derivation` | `scripts/docs/generate-router-files.py` | F3-B |
| C12 | `docs(router): delete derived router files and regenerate from canonicals` | `docs/agent_router/01_WORKFLOW/{BRANCHING,CODE_REVIEW,PULL_REQUESTS,START_WORK,TESTING}/`, `docs/agent_router/03_SHARED/{ENGINEERING_PLAYBOOK,BRAND_GUIDELINES,UX_GUIDELINES}/`, `docs/agent_router/extraction/{STRATEGY,FIELD_GUARDRAILS,OBSERVABILITY}.md` | F3-C |
| C13 | `docs(router): update AGENTS.md and 00_AUTHORITY.md — remove embedded rules` | `AGENTS.md`, `docs/agent_router/00_AUTHORITY.md` | F3-D |
| C14 | `docs(router): update parity and impact maps for new canonical paths` | `docs/agent_router/01_WORKFLOW/DOC_UPDATES/router_parity_map.json`, `test_impact_map.json` | F3-E |
| C15 | `ci: add canonical→router directionality check` | `.github/workflows/` or `scripts/ci/` | F4-A |
| C16 | `ci: add router drift check — regenerate and compare` | `.github/workflows/` or `scripts/ci/` | F4-B |

## Operational override steps (commit-task schema)

### CT-1 — Commit F3 implementation bundle

- `type`: `commit-task`
- `trigger`: after F3-A, F3-B, F3-C, F3-D, F3-E are `[x]`
- `preconditions`: targeted docs/router tests green; `python scripts/docs/generate-router-files.py --check` passes
- `commands`:
   - `git add docs/agent_router/MANIFEST.yaml scripts/docs/generate-router-files.py requirements-dev.txt AGENTS.md docs/shared/03-ops/way-of-working.md docs/agent_router/00_AUTHORITY.md docs/agent_router/00_RULES_INDEX.md docs/agent_router/01_WORKFLOW/DOC_UPDATES/router_parity_map.json docs/agent_router/01_WORKFLOW/DOC_UPDATES/test_impact_map.json docs/agent_router/01_WORKFLOW/CODE_REVIEW/ docs/agent_router/01_WORKFLOW/BRANCHING/ docs/agent_router/01_WORKFLOW/PULL_REQUESTS/ docs/agent_router/01_WORKFLOW/START_WORK/ docs/agent_router/01_WORKFLOW/TESTING/ docs/agent_router/03_SHARED/ENGINEERING_PLAYBOOK/ docs/agent_router/03_SHARED/BRAND_GUIDELINES/ docs/agent_router/03_SHARED/UX_GUIDELINES/ docs/agent_router/03_SHARED/00_entry.md docs/agent_router/extraction/STRATEGY.md docs/agent_router/extraction/FIELD_GUARDRAILS.md docs/agent_router/extraction/OBSERVABILITY.md`
   - `git commit -m "docs(router): F3 canonical->router derivation, regeneration, and contract alignment"`
   - `git push origin chore/router-directionality-protection`
- `approval`: `auto`
- `fallback`: if commit fails due to scope mismatch, split into CT-1a/CT-1b in this plan before retrying

### CT-2 — Commit F4 CI protection

- `type`: `commit-task`
- `trigger`: after F4-A and F4-B are `[x]`
- `preconditions`: CI checks added and passing in branch validation run
- `commands`:
   - `git add .github/workflows/ci.yml scripts/docs/check_router_directionality.py`
   - `git commit -m "ci(plan-f4): add canonical-router directionality and drift checks"`
   - `git push origin chore/canonical-doc-restructure-ci-guards`
- `approval`: `auto`
- `fallback`: if checks fail, keep F4 steps in `🚫 BLOCKED` until focused fix is committed

---

## Estado de ejecución

**Leyenda**
- 🔄 — Codex (auto-chain)
- 🚧 — Claude (hard-gate / redacción)

### Phase 1 — Create canonical documents **[PR-1]**

- [x] F1-A 🚧 — **Create `docs/shared/02-tech/coding-standards.md`** — Migrar de engineering-playbook.md: code style, architecture, contracts, state mgmt, traceability, error handling, observability, data handling, config/env, versioning, dependencies, naming (domain/API/lifecycle/persistence). Añadir governance header. Commit C1. (Claude Opus 4.6) — ✅ `33fbf0f9`
- [x] F1-B 🚧 — **Create `docs/shared/02-tech/documentation-guidelines.md`** — Migrar de engineering-playbook.md §documentation + parte humana de DOC_UPDATES (cuándo actualizar, clasificación R/C/N, verificación). Añadir governance header. Commit C2. (Claude Opus 4.6) — ✅ `0dc88c60`
- [x] F1-C 🚧 — **Create `docs/shared/03-ops/way-of-working.md`** — Migrar de engineering-playbook.md §branch-first, §branching, §commits, §preflight, §PRs, §code-reviews, §delivery-model, §kickoff, §DoD, §execution-rule + contenido de 01_WORKFLOW/*. Añadir governance header. Commit C3. (Claude Opus 4.6) — ✅ `28e60da0`
- [x] F1-D 🚧 — **Create `docs/projects/.../03-ops/plan-execution-protocol.md`** — Absorber execution-rules.md completo, reescrito para legibilidad humana manteniendo todas las reglas operativas. Añadir governance header. Commit C4. (Claude Opus 4.6) — ✅ `e47a60d4`
- [x] F1-E 🚧 — **Create `docs/projects/.../02-tech/extraction-quality.md`** — Consolidar extraction/STRATEGY.md, FIELD_GUARDRAILS.md, OBSERVABILITY.md, extraction-tracking/INDEX.md, risk-matrix.md. Añadir governance header. Commit C5. (Claude Opus 4.6) — ✅ `b514b44b`

### Phase 2 — Update existing docs + cleanup **[PR-1]**

- [x] F2-A 🚧 — **Add governance headers** a `brand-guidelines.md` y `ux-guidelines.md`. Directiva de direccionalidad canonical → router. Commit C6. (Claude Opus 4.6) — ✅ `3b93d88b`
- [x] F2-B 🚧 — **Delete `engineering-playbook.md`** — Sustituido por coding-standards + documentation-guidelines + way-of-working. Commit C7. (Claude Opus 4.6) — ✅ `9f8c70c7`
- [x] F2-C 🔄 — **Update wiki section indexes** — Actualizar ficheros índice de `docs/shared/02-tech/` y `docs/shared/03-ops/` para que listen los nuevos documentos. Commit C8. (Codex) — ✅ `0d696664`
- [x] F2-D 🔄 — **Fix all cross-references** — Grep todos los links a engineering-playbook.md en el repo, reemplazar por el canónico correspondiente (coding-standards, documentation-guidelines, o way-of-working según la sección referenciada). Commit C9. (Codex) — ✅ `517cdec2`
- [x] F2-E 🚧 — **Hard-gate: user review** — El usuario revisa los 5 canónicos, valida contenido, tono, completitud. Go/no-go para merge PR-1. (Claude Opus 4.6) ✅ GO (2026-03-05)

### Phase 3 — Router derivation + governance **[PR-2]**

- [x] F3-A 🚧 — **Define router derivation manifest** — Crear `docs/agent_router/MANIFEST.yaml` que mapee cada canónico → secciones → mini-archivos a generar. Commit C10. (Claude Opus 4.6) — ✅ `e417b965`
- [x] F3-B 🚧 — **Create `scripts/docs/generate-router-files.py`** — Script que lee canónicos + manifest, genera mini-archivos con header AUTO-GENERATED. Commit C11. (Claude Opus 4.6) — ✅ `e417b965`
- [x] F3-C 🚧 — **Delete derived router files + regenerate** — Eliminados ~58 archivos derivados, regenerados 55 desde canónicos. Drift check OK. Commit C12. (Claude Opus 4.6) — ✅ `e417b965`
- [x] F3-D 🚧 — **Update `AGENTS.md` and `00_AUTHORITY.md`** — Reemplazar reglas embebidas por references a canónicos. Mantener AGENTS.md como entry point ligero. Commit C13. (Claude Opus 4.6) — ✅ `e417b965`
- [x] F3-E 🔄 — **Update parity and impact maps** — Ajustar `router_parity_map.json` y `test_impact_map.json` a nuevos paths canónicos. Commit C14. (Claude Opus 4.6) — ✅ `e417b965`
- [x] F3-F 🔄 — **Commit-task CT-1** — Ejecutar CT-1 (commit/push de implementación F3 según schema). (Codex) — ✅ `e417b965`

### Phase 4 — CI protection **[PR-2]**

- [x] F4-A 🔄 — **Add CI directionality check** — Step en CI que falla si archivos bajo `docs/agent_router/03_SHARED/` o `01_WORKFLOW/` son modificados sin cambio en canónico correspondiente. Commit C15. (Codex) — ✅ `c04b4a26`
- [x] F4-B 🔄 — **Add CI drift check** — Step que ejecuta `generate-router-files.py` y compara output con committed. Falla si difieren. Commit C16. (Codex) — ✅ `c04b4a26`
- [x] F4-C 🚧 — **Hard-gate: user validation of full pipeline** — Verificar ciclo canonical → generate → router → agent-use. Go/no-go para merge PR-2. (Claude Opus 4.6) — ✅ GO (2026-03-05): pipeline validado tras F4-C.fix.
- [x] F4-C.fix 🚧 — **Fix progressive discovery for 2 broken docs** — Rediseñar MANIFEST.yaml: plan-execution-protocol → 11 mini-files en nueva dir EXECUTION_PROTOCOL; documentation-guidelines → 5 mini-files. Eliminar orphaned files. Añadir bypass de directionality guard cuando MANIFEST.yaml cambia. (Claude Opus 4.6)
- [x] F4-D 🔄 — **Commit-task CT-2** — Ejecutar CT-2 (commit/push de protección CI F4). (Codex) — ✅ `c04b4a26`

---

## Cola de prompts

### F1-A — coding-standards canonical

```text
Create `docs/shared/02-tech/coding-standards.md` by extracting and normalizing the technical standards content currently spread across:
- docs/shared/03-ops/engineering-playbook.md (code-style, structure, contracts, state/workflow safety, traceability, error handling, observability, testing discipline, data handling, config/env, versioning, dependencies, naming for API/domain/lifecycle/persistence)

Requirements:
1) Human-readable canonical format (not router format), wiki-ready.
2) Keep all normative rules (MUST/NEVER style meaning) intact.
3) Add explicit governance section with directionality:
	- Canonical source of truth
	- Flow is canonical → router only
	- Router files are derived outputs and must not be manually edited
4) Include clear section headers and concise rationale per section where helpful.
5) Do not edit unrelated files.

Validation:
- Ensure internal links in the new file resolve.
- Run a quick markdown sanity pass if available.

Commit:
- `docs(shared): add coding-standards.md — tech standards canonical`
```

⚠️ AUTO-CHAIN → F1-B

### F1-B — documentation-guidelines canonical

```text
Create `docs/shared/02-tech/documentation-guidelines.md` by consolidating:
- Documentation section from docs/shared/03-ops/engineering-playbook.md
- Human-facing rules from docs/agent_router/01_WORKFLOW/DOC_UPDATES/* (triggers, R/C/N classification, normalization intent, verification checklist)

Requirements:
1) Keep operational meaning intact, remove router-specific wording.
2) Distinguish clearly:
	- Human policy/rules (canonical)
	- Agent/router mechanics (derived, references only)
3) Add governance section with canonical → router directionality.
4) Include a practical “when docs must be updated” section and a concise verification checklist.
5) Do not edit unrelated files.

Validation:
- Verify links and markdown structure.

Commit:
- `docs(shared): add documentation-guidelines.md — doc standards canonical`
```

⚠️ AUTO-CHAIN → F1-C

### F1-C — way-of-working canonical

```text
Create `docs/shared/03-ops/way-of-working.md` as the canonical human-readable operations doc by consolidating:
- workflow and delivery sections from docs/shared/03-ops/engineering-playbook.md
- duplicated operational content from docs/agent_router/01_WORKFLOW/{START_WORK,BRANCHING,PULL_REQUESTS,CODE_REVIEW,TESTING}/*

Include (in this order):
1) Starting new work (branch-first)
2) Branching strategy and naming
3) Commit discipline
4) Local preflight levels (L1/L2/L3)
5) Pull request workflow
6) Code review workflow and output expectations
7) Delivery model and user story kickoff
8) Definition of done

Requirements:
- Resolve duplicated rules into one canonical wording per rule.
- Keep all mandatory constraints intact.
- Add governance section with canonical → router directionality.

Commit:
- `docs(shared): add way-of-working.md — ops workflow canonical`
```

⚠️ AUTO-CHAIN → F1-D

### F1-D — plan-execution-protocol canonical (project)

```text
Create `docs/projects/veterinary-medical-records/03-ops/plan-execution-protocol.md` as canonical project-level execution protocol by restructuring content from:
- docs/projects/veterinary-medical-records/03-ops/execution-rules.md

Requirements:
1) Preserve all operational rules and hard gates (no semantic loss).
2) Improve human readability with a coherent structure and explicit section boundaries.
3) Keep agent names and handoff messages exactly where they are normative.
4) Add governance section indicating this is canonical and router files are derived.
5) Keep links valid and update references if needed.

Commit:
- `docs(project): add plan-execution-protocol.md — agent execution canonical`
```

⚠️ AUTO-CHAIN → F1-E

### F1-E — extraction-quality canonical (project)

```text
Create `docs/projects/veterinary-medical-records/02-tech/extraction-quality.md` by consolidating extraction operational rules from:
- docs/agent_router/extraction/STRATEGY.md
- docs/agent_router/extraction/FIELD_GUARDRAILS.md
- docs/agent_router/extraction/OBSERVABILITY.md
- docs/agent_router/extraction-tracking/INDEX.md
- docs/agent_router/extraction-tracking/risk-matrix.md

Requirements:
1) Capture only stable operational rules and guardrails (not transient run logs).
2) Keep field-level acceptance/rejection criteria explicit.
3) Keep observability and risk policy sections.
4) Add governance section with canonical → router directionality.

Commit:
- `docs(project): add extraction-quality.md — extraction rules canonical`
```

⚠️ AUTO-CHAIN → F2-A

### F2-A — governance headers in existing canonical docs

```text
Update these existing canonical docs:
- docs/shared/01-product/brand-guidelines.md
- docs/shared/01-product/ux-guidelines.md

Add a short governance header/section in both files stating:
- They are canonical sources.
- Router files are derived outputs.
- Directionality is canonical → router only.
- Direct manual edits to router files are invalid and may be overwritten/regenerated.

Keep all current content intact; make minimal targeted edits only.

Commit:
- `docs(shared): add governance headers to brand-guidelines and ux-guidelines`
```

⚠️ STOP (next steps depend on created canonicals and/or Codex tasks)

### F2-C — update wiki section indexes

```text
Update the documentation indexes to reflect the new canonical documents created in Phase 1 and the deletion of engineering-playbook.md.

Files to update:
1) docs/README.md — Sitemap section (around line 49):
   - Remove `03-ops/engineering-playbook.md`
   - Add `02-tech/coding-standards.md`
   - Add `02-tech/documentation-guidelines.md`
   - Add `03-ops/way-of-working.md`
   Also add project-level canonical docs to the sitemap under `docs/projects/veterinary-medical-records/`:
   - `02-tech/extraction-quality.md`
   - `03-ops/plan-execution-protocol.md`

2) docs/README.md — Shared Documentation section (around line 77):
   - Remove the line: `- [engineering-playbook.md](shared/03-ops/engineering-playbook.md) — engineering standards and working agreements.`
   - Add these lines:
     - `- [coding-standards.md](shared/02-tech/coding-standards.md) — code style, architecture, contracts, naming, and technical standards.`
     - `- [documentation-guidelines.md](shared/02-tech/documentation-guidelines.md) — documentation rules, change classification, and verification.`
     - `- [way-of-working.md](shared/03-ops/way-of-working.md) — branch→commit→PR→review→merge lifecycle and working agreements.`

Requirements:
- Keep all other content in these files intact.
- Ensure the sitemap ordering is consistent (01-product before 02-tech before 03-ops).
- Do not edit unrelated files.

Commit:
- `docs(shared): update wiki section indexes for new canonical docs`
```

⚠️ AUTO-CHAIN → F2-D

### F2-D — fix all cross-references to engineering-playbook.md

```text
Find and fix all remaining cross-references to engineering-playbook.md across the repository.

Known references to fix (confirmed via grep):
1) README.md (repo root, around line 132):
   Current:
     📄 **[`docs/shared/03-ops/engineering-playbook.md`](docs/shared/03-ops/engineering-playbook.md)**
     Engineering standards for implementation and changes.
   Replace with:
     📄 **[`docs/shared/02-tech/coding-standards.md`](docs/shared/02-tech/coding-standards.md)**
     Technical coding standards and architecture rules.

     📄 **[`docs/shared/03-ops/way-of-working.md`](docs/shared/03-ops/way-of-working.md)**
     Workflow lifecycle and working agreements.

2) Run a full scan to catch any other references:
   grep -r "engineering-playbook" docs/ AGENTS.md --include="*.md" | grep -v "completed/" | grep -v "PLAN_2026-03-04"
   Fix any hits found (replace with the most appropriate canonical doc based on context).

Do NOT modify:
- The PLAN file itself (PLAN_2026-03-04_CANONICAL-DOC-RESTRUCTURE.md) — historical references are fine.
- Completed plan files under `docs/projects/.../plans/completed/`.

Commit:
- `docs: fix all cross-references from engineering-playbook.md to new canonicals`
```

⚠️ STOP (F2-E is a hard-gate: user review before PR-1 merge)

### F4-A — CI directionality check

```text
Create `scripts/docs/check_router_directionality.py` and add a CI job `doc_router_directionality_guard` in `.github/workflows/ci.yml`.

Script behavior:
1. Accept `--base-ref` argument (PR base SHA).
2. Compute changed files via `git diff --name-only --diff-filter=ACMR <base-ref>...HEAD`.
3. Filter files under protected prefixes: `docs/agent_router/01_WORKFLOW/`, `docs/agent_router/03_SHARED/`.
4. Load `docs/agent_router/MANIFEST.yaml` to build router-path → canonical-source mapping.
5. For each changed protected router file, verify its canonical source is also in the diff.
6. Exit 0 if no violations; exit 1 with findings list if any router file changed without its canonical.
7. Exit 2 on infrastructure errors (missing manifest, git failures).

CI job:
- Condition: `if: github.event_name == 'pull_request'`
- Steps: checkout (fetch-depth: 0), setup Python 3.11, run script with `--base-ref "${{ github.event.pull_request.base.sha }}"`.

Validation:
- Run locally: `python scripts/docs/check_router_directionality.py --base-ref origin/main`
- Expected: passes on current branch (no unmatched router changes).

Do NOT commit — this is bundled into CT-2.
```

⚠️ AUTO-CHAIN → F4-B

### F4-B — CI drift check

```text
Add a CI job `doc_router_drift_guard` in `.github/workflows/ci.yml`.

Job behavior:
1. Checkout code (no special fetch-depth needed).
2. Setup Python 3.11.
3. Install dependency: `pip install pyyaml>=6.0`.
4. Run: `python scripts/docs/generate-router-files.py --check`.
5. The `--check` flag (already implemented in generate-router-files.py) regenerates router files to a temp dir and compares with committed files. Exits non-zero if any differ.

CI job:
- Condition: `if: github.event_name == 'pull_request'`
- Steps: checkout, setup Python 3.11, install pyyaml, run `--check`.

Validation:
- Run locally: `python scripts/docs/generate-router-files.py --check`
- Expected: "No drift detected" (exit 0).

Do NOT commit — this is bundled into CT-2.
```

⚠️ AUTO-CHAIN → F4-D (CT-2)

### F4-C — Hard-gate: user validation of full pipeline

```text
Validate the complete canonical → router → CI protection pipeline:

1. **Directionality guard test:**
   - Manually edit a router file (e.g., add a comment to `docs/agent_router/03_SHARED/CODING_STANDARDS/10_preamble.md`).
   - Run: `python scripts/docs/check_router_directionality.py --base-ref origin/main`
   - Expected: FAIL (router changed without canonical).
   - Revert the edit.

2. **Drift guard test:**
   - Manually edit a router file (same as above).
   - Run: `python scripts/docs/generate-router-files.py --check`
   - Expected: FAIL (committed differs from generated).
   - Revert the edit.

3. **Positive path test:**
   - Run both guards without modifications.
   - Expected: both PASS.

4. **CI integration:**
   - Verify `doc_router_directionality_guard` and `doc_router_drift_guard` jobs exist in `.github/workflows/ci.yml`.
   - Verify both run on `pull_request` events only.

Output:
- GO: continue to PR readiness and merge.
- NO-GO: list exact failures requiring fixes.
```

### F4-D — Commit-task CT-2

```text
Execute commit task CT-2 per SCOPE BOUNDARY:

STEP 0 — Branch Verification:
- Expected branch: `chore/canonical-doc-restructure-ci-guards`

STEP A — Commit Code:
- Run formatters (ruff for Python).
- Stage: `git add .github/workflows/ci.yml scripts/docs/check_router_directionality.py`
- Commit: `ci(plan-f4): add canonical-router directionality and drift checks`

STEP B — Commit Plan Update:
- Mark F4-A, F4-B, F4-D as `[x]` with code commit SHA.
- Clear Prompt activo.
- Stage and commit plan file only.

STEP C — Push:
- `git push origin chore/canonical-doc-restructure-ci-guards`

STEP D — Update PR description.

STEP E — CI Gate.

STEP F — Chain or Stop (F4-C is 🚧 hard-gate → STOP).
```

---

## Prompt activo

### Paso objetivo

F4-C 🚧 — Hard-gate: user validation of full pipeline.

### Prompt

```text
Validate the complete canonical → router → CI protection pipeline.
See prompt F4-C in Cola de prompts for full validation checklist.

Output:
- GO: continue to PR readiness and merge.
- NO-GO: list exact failures requiring fixes.
```

---

## Acceptance criteria

1. Toda regla operativa del repo está documentada en exactamente 1 de los 7 canónicos.
2. `engineering-playbook.md` no existe.
3. Todos los links internos que apuntaban a engineering-playbook.md resuelven correctamente.
4. La wiki muestra los nuevos documentos bajo las secciones correctas.
5. Los mini-archivos del router se generan con `generate-router-files.py` y coinciden con los committed.
6. CI falla si un router file se edita sin tocar el canónico.
7. CI falla si router files committed difieren de los generados.
8. Cada router mini-archivo lleva header `<!-- AUTO-GENERATED from ... DO NOT EDIT -->`.
9. `AGENTS.md` no contiene reglas embebidas, solo routing.

## Risks and limitations

| Risk | Mitigation |
|---|---|
| PR-1 diff grande (muchos archivos) | Contenido es move/reorganize, no creación. Review por secciones temáticas. |
| PLANs activos referenciando engineering-playbook.md | F2-D actualiza todas las refs antes del delete. |
| Script de generación introduce drift sutil | F4-B CI drift check como safety net. |
| Periodo entre PR-1 y PR-2 sin protección CI | Aceptable: PR-2 se ejecuta inmediatamente tras merge de PR-1. |
| Contenido de extraction-quality.md puede necesitar revisión de dominio | F2-E hard-gate permite al usuario validar antes de merge. |

---

## How to test

```bash
# Verify no broken links (after PR-1)
grep -r "engineering-playbook" docs/ AGENTS.md --include="*.md" | grep -v "completed/"
# Should return 0 results

# Verify wiki sync (after PR-1)
python scripts/docs/sync_docs_to_wiki.py --dry-run
# New docs should appear under shared-02-tech and shared-03-ops

# Verify router generation is idempotent (after PR-2)
python scripts/docs/generate-router-files.py
git diff --stat docs/agent_router/
# Should show 0 changed files

# Verify CI directionality check (after PR-2)
# Manually edit a router file without touching canonical → CI should fail
```
