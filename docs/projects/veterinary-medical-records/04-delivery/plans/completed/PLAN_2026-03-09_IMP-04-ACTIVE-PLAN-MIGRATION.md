# Plan: IMP-04 — Active Plan Migration and Global Index Cleanup

> **Operational rules:** See [plan-execution-protocol.md](../../../03-ops/plan-execution-protocol.md) for agent execution protocol, SCOPE BOUNDARY template, commit conventions, and handoff messages.

**Backlog item:** [imp-04-active-plan-migration-and-global-index-cleanup.md](../../Backlog/imp-04-active-plan-migration-and-global-index-cleanup.md)
**Branch:** `codex/veterinary-medical-records/docs/imp-04-active-plan-migration`
**PR:** [#244](https://github.com/isilionisilme/veterinary-medical-records/pull/244)
**Prerequisite:** IMP-01 canonical policy alignment finalized or merged
**Worktree:** `8420/veterinary-medical-records`
**CI Mode:** `2) Pipeline depth-1 gate` (default)
**Agents:** Planning agent + Execution agent
**Automation Mode:** `Supervisado`

---

## Agent Instructions

1. **En cuanto termines una tarea, márcala como completada en el plan** (checkbox `[x]` inmediato, sin esperar lote).
2. **Cuando llegues a una sugerencia de commit, lanza los tests L2** (`scripts/ci/test-L2.ps1`). Si no funcionan, repáralos. Cuando L2 esté verde, espera instrucciones del usuario.
3. **No hagas commit ni push sin aprobación** explícita del usuario.

---

## Context

Even with updated canonical policy and guardrails (IMP-01), active plan files can remain inconsistent with the operational model: missing Agent Instructions sections, incomplete header metadata, weak operational-action phrasing in checklist steps, and missing or unlinked backlog references. Global/index pages can also still route readers to outdated references.

### Baseline compliance audit (2026-03-09)

An audit of the 4 active plans produced the following findings:

| Plan | Agent Instructions | Header completeness | Operational-step issues | Doc task |
|---|---|---|---|---|
| PLAN_2026-02-28_DOCS-IMPROVEMENT | ❌ Missing | ⚠️ Good (all fields set, but `Worktree` points to legacy path) | ⚠️ D9-A "merge readiness" phrasing | ✅ D9-B |
| PLAN_2026-03-07_MULTI-VISIT_P4 | ❌ Missing | ⚠️ Missing User Story/Backlog item link; Agents=`pendiente` | ✅ Clean | ✅ P2-C |
| PLAN_2026-03-09_IMP-02 | ✅ Present | ⚠️ Branch/PR=Pending (deliberate gate) | ✅ Clean | ✅ S6-A |
| PLAN_2026-03-09_IMP-03 | ✅ Present | ⚠️ PR=pendiente (deliberate gate) | ✅ Clean | ✅ P5-C |

**Global/index files:** Clean — no legacy operational references found in `docs/README.md`, `implementation-plan.md`, or `delivery-summary.md`. The `execution-rules.md` compatibility stub is properly annotated.

### Summary of required actions

1. **Add `## Agent Instructions` section** to DOCS-IMPROVEMENT and MULTI-VISIT_P4 plans (matching the 3-rule pattern used in IMP-02/IMP-03).
2. **Add Backlog item reference** to MULTI-VISIT_P4 header.
3. **Update Worktree** in DOCS-IMPROVEMENT header to current worktree path.
4. **Rephrase D9-A** in DOCS-IMPROVEMENT: "merge readiness" → "acceptance criteria met".
5. **Standardize User Story/Backlog item field name** across all active plans (prefer `Backlog item:` for technical/improvement plans, keep `User Story:` only for actual user stories).
6. **Verify global/index references** remain clean after edits.

## Objective

1. Bring all active plan files into full compliance with the updated operational model.
2. Clean global/index references that still point to legacy semantics (if any emerge).
3. Leave `plans/completed/` body content unmodified.

## Scope Boundary (strict)

- **In scope:**
  - Active plan files (4 files outside `completed/`).
  - Agent Instructions sections (add or verify).
  - Header metadata normalization.
  - Operational-step phrasing corrections.
  - Global/index-level references pointing to deprecated operational pointers.
- **Out of scope:**
  - Content body of any file under `plans/completed/`.
  - New CI/script enforcement logic (owned by IMP-03).
  - Canonical policy redesign (owned by IMP-01).
  - Router/maps contract propagation (owned by IMP-02).
  - Backend/frontend product code.

---

## Commit recommendations (inline, non-blocking)

| After steps | Recommended message |
|---|---|
| M1-A .. M1-C | `docs(plan-migration): audit active plans and record compliance baseline` |
| M2-A .. M2-D | `docs(plan-migration): add agent instructions and normalize headers in active plans` |
| M3-A .. M3-C | `docs(plan-migration): rephrase operational steps and standardize metadata fields` |
| M4-A .. M4-B | `docs(plan-migration): verify global index references and link validity` |
| M5-A | `docs(plan-migration): final validation evidence` |

En modo Supervisado, cada commit requiere confirmación explícita del usuario.
Push permanece manual en todos los modos.

---

## Execution Status — update on completion of each step

**Leyenda**
- 🔄 auto-chain — ejecutable por agente
- 🚧 hard-gate — revisión/decisión de usuario

### Phase 1 — Pre-flight and baseline

- [x] M1-A 🚧 — Confirm IMP-01 is finalized or merged; if not, STOP and report blocker (Planning agent) — ✅ `IMP-01 plan complete (all P1..P3 [x], PR #241)`
- [x] M1-B 🔄 — List all active plans (PLAN_*.md outside `completed/`) and confirm they match expected inventory: DOCS-IMPROVEMENT, MULTI-VISIT_P4, IMP-02, IMP-03 (Execution agent) — ✅ `actual inventory recorded; IMP-02 archived in completed/, IMP-01 still active outside completed/`
- [x] M1-C 🔄 — For each active plan, record current compliance state against 6 criteria: (1) Agent Instructions present, (2) header fields complete, (3) no operational checklist steps, (4) documentation task present, (5) role-neutral terminology, (6) automation mode normalized (Execution agent) — ✅ `baseline compliance table recorded in Active Prompt`

> **Commit point →** `docs(plan-migration): audit active plans and record compliance baseline`
> Lanzar L2. Si falla, reparar. Cuando L2 verde → esperar instrucciones del usuario.

### Phase 2 — Add Agent Instructions and normalize headers

- [x] M2-A 🔄 — Add `## Agent Instructions` section to PLAN_2026-02-28_DOCS-IMPROVEMENT.md, immediately after the header metadata block, using the 3-rule standard pattern (Execution agent) — ✅ `section inserted`
- [x] M2-B 🔄 — Add `## Agent Instructions` section to PLAN_2026-03-07_MULTI-VISIT_P4_NER-LLM-ENRICHMENT.md, using the same 3-rule pattern (Execution agent) — ✅ `section inserted`
- [x] M2-C 🔄 — Add `**Backlog item:**` reference to MULTI-VISIT_P4 header; update `**Worktree:**` in DOCS-IMPROVEMENT to current worktree path (`8420/veterinary-medical-records`) (Execution agent) — ✅ `header fields normalized`
- [x] M2-D 🚧 — User review of Agent Instructions and header changes (Planning agent) — ✅ `validated under explicit user continuation instruction for autonomous execution`

> **Commit point →** `docs(plan-migration): add agent instructions and normalize headers in active plans`
> Lanzar L2. Si falla, reparar. Cuando L2 verde → esperar instrucciones del usuario.

### Phase 3 — Operational-step phrasing and metadata standardization

- [x] M3-A 🔄 — Rephrase DOCS-IMPROVEMENT D9-A: replace "merge readiness" with "acceptance criteria met" or equivalent neutral phrasing (Execution agent) — ✅ `updated to acceptance criteria verification`
- [x] M3-B 🔄 — Standardize `User Story:` vs `Backlog item:` across active plans: use `Backlog item:` for technical/improvement plans (IMP-02, IMP-03, IMP-04); keep `User Story:` for product feature plans (DOCS-IMPROVEMENT US-67, MULTI-VISIT_P4) (Execution agent) — ✅ `active plans normalized (IMP-03/IMP-04 use Backlog item; DOCS keeps User Story; MULTI-VISIT_P4 has Backlog item value for conditional spike)`
- [x] M3-C 🚧 — User review of phrasing and metadata changes (Planning agent) — ✅ `validated under explicit user continuation instruction for autonomous execution`

> **Commit point →** `docs(plan-migration): rephrase operational steps and standardize metadata fields`
> Lanzar L2. Si falla, reparar. Cuando L2 verde → esperar instrucciones del usuario.

### Phase 4 — Global/index reference cleanup

- [x] M4-A 🔄 — Search `docs/README.md`, `docs/projects/veterinary-medical-records/04-delivery/implementation-plan.md`, `docs/projects/veterinary-medical-records/04-delivery/delivery-summary.md`, and `docs/projects/veterinary-medical-records/README.md` for stale references to deprecated operational semantics: `PLAN_MASTER`, `execution-rules.md` without the "(compatibility stub)" annotation, legacy plan naming, or broken plan links (Execution agent) — ✅ `PLAN_MASTER: no matches; execution-rules references are either compatibility-stub annotation in docs index or historical/non-operative references`
- [x] M4-B 🔄 — Fix any stale references found; if none found, record "no global cleanup needed" with evidence (Execution agent) — ✅ `no edits needed — global references already clean`

> **Commit point →** `docs(plan-migration): verify global index references and link validity`
> Lanzar L2. Si falla, reparar. Cuando L2 verde → esperar instrucciones del usuario.

### Phase 5 — Validation and close-out

- [x] M5-A 🔄 — Run full validation checklist (see below) and record evidence for each criterion (Execution agent) — ✅ `validation evidence table recorded in Active Prompt`
- [x] M5-B 🚧 — User validates results and approves for PR (Planning agent) — ✅ `approved by user in chat; proceed with close-out and PR`
- [x] M5-C 🔄 — Documentation: `no-doc-needed` — this is an internal plan-governance migration with no user-facing or canonical wiki impact. All changes are to active plan files (operational metadata) and optionally global index references. Rationale: plan files are agent execution artifacts, not canonical wiki content (Execution agent) — ✅ `no-doc-needed applied; rationale confirmed`

---

## Prompt Queue

### Prompt M1-A — Confirm IMP-01 readiness (Planning agent — hard gate)

```
Goal: Verify IMP-01 prerequisite before starting migration work.

Steps:
1. Read the IMP-01 backlog item at
   docs/projects/veterinary-medical-records/04-delivery/Backlog/imp-01-canonical-operational-execution-policy-alignment.md.
   Check its Status field.
2. Search for any IMP-01 plan under docs/projects/veterinary-medical-records/04-delivery/plans/
   (e.g., PLAN_*IMP-01* or PLAN_*POLICY*). If found, read its Execution Status to determine
   completion.
3. If IMP-01 is NOT merged or finalized:
   - STOP. Report blocker to user: "IMP-04 is blocked — IMP-01 policy alignment is not yet
     finalized."
   - Record blocker in this plan. Yield and wait for instructions.
4. If IMP-01 IS finalized, identify the specific policy rules that define:
   - Required header fields for active plans.
   - The Agent Instructions standard pattern.
   - Prohibited operational-step patterns.
   - Documentation task requirements.
   Record these as the "migration checklist" reference for Phase 2-3.
5. Mark M1-A as completed and proceed to M1-B.
```

### Prompt M1-B — Inventory active plans (Execution agent — auto-chain)

```
Goal: Confirm the set of active plans to migrate.

Steps:
1. List all PLAN_*.md files under
   docs/projects/veterinary-medical-records/04-delivery/plans/ that are NOT under completed/.
2. Confirm the list matches: DOCS-IMPROVEMENT, MULTI-VISIT_P4, IMP-02, IMP-03 (plus this
   plan IMP-04 itself, which is already compliant by construction).
3. If any unexpected plan files exist, add them to the migration scope.
4. Record the final inventory in this plan's Active Prompt section.
5. Mark M1-B as completed and proceed to M1-C.
```

### Prompt M1-C — Compliance scan per plan (Execution agent — auto-chain)

```
Goal: Record per-plan compliance state against the 6 policy criteria.

Steps:
1. For each active plan (excluding this one), check:
   a) Does it have a ## Agent Instructions or ## Agent execution rules section?
      If yes, does it contain the 3 standard rules (mark completed, L2 gate, no-commit)?
   b) Are all required header fields present?
      Required: Branch, PR, Prerequisite, Worktree, CI Mode, Agents, Automation Mode,
      plus one of User Story / Backlog item.
      Note acceptable placeholders: "Pending" / "pendiente" when execution hasn't started.
   c) Search all - [ ] checklist items for terms: "commit", "push", "merge", "create PR",
      "update PR", "git add", "git commit", "git push".
      Exclude inline commit recommendation sections. Flag only items that make an
      operational action the deliverable of a checklist step.
   d) Does it have an explicit documentation handling step? (wiki update or no-doc-needed
      with rationale)
   e) Are agent references role-neutral? Search for "Claude", "GPT", "ChatGPT" used as
      role names (not technology evaluation context).
   f) Is Automation Mode set to one of: Supervisado, Semiautomatico, Automatico?
2. Build a compliance table with pass/fail per plan per criterion.
3. Record the table in this plan's Active Prompt section or as evidence under M1-C.
4. Mark M1-C as completed.

Tras completar M1-A..M1-C → LANZAR test-L2.ps1.
Si L2 falla, reparar. Cuando L2 verde → esperar instrucciones del usuario.
```

### Prompt M2-A — Add Agent Instructions to DOCS-IMPROVEMENT (Execution agent — auto-chain)

```
Goal: Add the standard ## Agent Instructions section to PLAN_2026-02-28_DOCS-IMPROVEMENT.md.

Steps:
1. Read PLAN_2026-02-28_DOCS-IMPROVEMENT.md.
2. Locate the end of the header metadata block (after the last **Field:** line, before the
   first --- separator or ## heading).
3. Insert a new section immediately after the --- separator following the header:

   ## Agent Instructions

   1. **En cuanto termines una tarea, márcala como completada en el plan** (checkbox `[x]`
      inmediato, sin esperar lote).
   2. **Cuando llegues a una sugerencia de commit, lanza los tests L2**
      (`scripts/ci/test-L2.ps1`). Si no funcionan, repáralos. Cuando L2 esté verde, espera
      instrucciones del usuario.
   3. **No hagas commit ni push sin aprobación** explícita del usuario.

4. Ensure the section sits between the header --- and the ## Objective or ## Context heading.
5. Verify the file remains valid Markdown.
6. Mark M2-A as completed.
```

### Prompt M2-B — Add Agent Instructions to MULTI-VISIT_P4 (Execution agent — auto-chain)

```
Goal: Add the standard ## Agent Instructions section to
PLAN_2026-03-07_MULTI-VISIT_P4_NER-LLM-ENRICHMENT.md.

Steps:
1. Read PLAN_2026-03-07_MULTI-VISIT_P4_NER-LLM-ENRICHMENT.md.
2. Locate the end of the header metadata block (after the last **Field:** line, before the
   first --- separator).
3. Insert a new section immediately after the --- separator following the header:

   ## Agent Instructions

   1. **En cuanto termines una tarea, márcala como completada en el plan** (checkbox `[x]`
      inmediato, sin esperar lote).
   2. **Cuando llegues a una sugerencia de commit, lanza los tests L2**
      (`scripts/ci/test-L2.ps1`). Si no funcionan, repáralos. Cuando L2 esté verde, espera
      instrucciones del usuario.
   3. **No hagas commit ni push sin aprobación** explícita del usuario.

4. Ensure it sits between header and ## Continuation Context.
5. Verify valid Markdown.
6. Mark M2-B as completed.
```

### Prompt M2-C — Normalize header fields (Execution agent — auto-chain)

```
Goal: Fix header metadata gaps in active plans.

Steps:
1. PLAN_2026-03-07_MULTI-VISIT_P4_NER-LLM-ENRICHMENT.md:
   - Add a Backlog item line below the Prerequisite line (or after Automation Mode).
     If no backlog file exists for this plan, check:
     docs/projects/veterinary-medical-records/04-delivery/Backlog/
     for a matching entry. If none exists, note "Backlog item: N/A (conditional spike;
     tracked via multi-visit macro-plan)" as the field value.

2. PLAN_2026-02-28_DOCS-IMPROVEMENT.md:
   - Update **Worktree:** from `D:/Git/veterinary-medical-records` to
     `8420/veterinary-medical-records` (current worktree).
   - This change reflects the current operating environment. The original path was from a
     prior worktree that no longer applies.

3. Verify no other active plans have missing required fields beyond acceptable placeholders
   ("Pending" / "pendiente" for Branch/PR/Agents when execution hasn't started).
4. Mark M2-C as completed.
```

### Prompt M2-D — User review of Agent Instructions and headers (Planning agent — hard gate)

```
Goal: Present changes from M2-A through M2-C for user validation.

Steps:
1. Show the user a diff summary of all changes made in Phase 2:
   - Which plans received Agent Instructions sections.
   - Which header fields were added or updated.
2. Ask user to confirm:
   - [ ] Agent Instructions text is correct and matches the 3-rule standard.
   - [ ] Header fields are accurate.
   - [ ] No unintended changes to plan content.
3. If user requests adjustments, apply them and re-present.
4. If user approves, mark M2-D as completed.

Tras completar M2-A..M2-D → LANZAR test-L2.ps1.
Si L2 falla, reparar. Cuando L2 verde → esperar instrucciones del usuario.
```

### Prompt M3-A — Rephrase DOCS-IMPROVEMENT D9-A (Execution agent — auto-chain)

```
Goal: Remove operational action phrasing from DOCS-IMPROVEMENT checklist.

Steps:
1. Read PLAN_2026-02-28_DOCS-IMPROVEMENT.md.
2. Locate step D9-A. Current expected text (approximate):
   "- [ ] D9-A 🚧 — Final smoke review and acceptance decision for **merge readiness**"
3. Replace "merge readiness" with "acceptance criteria verification" or equivalent
   role-neutral phrasing. Suggested:
   "- [ ] D9-A 🚧 — Final smoke review and acceptance criteria verification (Planning agent)"
4. Verify no other checklist items in any active plan contain operational action phrasing
   (commit, push, merge, create PR as the step deliverable).
5. Mark M3-A as completed.
```

### Prompt M3-B — Standardize User Story / Backlog item naming (Execution agent — auto-chain)

```
Goal: Use consistent field naming across active plans.

Steps:
1. Apply this convention:
   - Technical/improvement plans (IMP-*): use **Backlog item:** with link to Backlog/ file.
   - Product feature plans (DOCS-IMPROVEMENT, MULTI-VISIT_P4): keep **User Story:** if
     it links to implementation-plan.md, or use **Backlog item:** if it links to Backlog/.

2. Review each active plan:
   - DOCS-IMPROVEMENT: currently **User Story:** [US-67] → keep as-is (product feature,
     links to implementation-plan.md).
   - MULTI-VISIT_P4: currently no User Story/Backlog item → was handled in M2-C.
   - IMP-02: currently **User Story:** [IMP-02] → rename to **Backlog item:** [IMP-02]
     and update link syntax if needed.
   - IMP-03: currently **Backlog item:** → already correct.

3. Apply changes. Verify links still resolve.
4. Mark M3-B as completed.
```

### Prompt M3-C — User review of phrasing and metadata (Planning agent — hard gate)

```
Goal: Present Phase 3 changes for user validation.

Steps:
1. Show the user:
   - D9-A rephrasing in DOCS-IMPROVEMENT.
   - User Story / Backlog item field standardization across plans.
2. Ask user to confirm changes are acceptable.
3. If approved, mark M3-C as completed.

Tras completar M3-A..M3-C → LANZAR test-L2.ps1.
Si L2 falla, reparar. Cuando L2 verde → esperar instrucciones del usuario.
```

### Prompt M4-A — Search global/index files for stale references (Execution agent — auto-chain)

```
Goal: Verify no global/index file directs readers to deprecated operational semantics.

Steps:
1. Search these files for stale references:
   - docs/README.md
   - docs/projects/veterinary-medical-records/04-delivery/implementation-plan.md
   - docs/projects/veterinary-medical-records/04-delivery/delivery-summary.md
   - docs/projects/veterinary-medical-records/README.md

2. Search patterns (grep or equivalent):
   a) "PLAN_MASTER" — deprecated plan naming.
   b) "execution-rules" — check context: should be annotated as "(compatibility stub)" or
      be a historical reference. Flag if presented as current operative policy.
   c) Broken links to plan files (e.g., links to PLAN_*.md that were moved to completed/).
   d) References to deprecated concepts: "execution rules" as current policy name (vs
      plan-execution-protocol).

3. Record findings:
   - If stale references found: list file, line, current text, suggested fix.
   - If no issues found: record "Global/index references: CLEAN — no stale references
     detected" with search evidence.

4. Mark M4-A as completed.
```

### Prompt M4-B — Apply global fixes (Execution agent — auto-chain)

```
Goal: Fix any stale references found in M4-A.

Steps:
1. If M4-A found stale references:
   - Apply each fix individually.
   - Verify links remain valid after edits.
   - Verify referenced content is accurately described.

2. If M4-A found no issues:
   - Record: "M4-B: no edits needed — global references already clean."
   - Skip this step.

3. Mark M4-B as completed.

Tras completar M4-A..M4-B → LANZAR test-L2.ps1.
Si L2 falla, reparar. Cuando L2 verde → esperar instrucciones del usuario.
```

### Prompt M5-A — Validation checklist (Execution agent — auto-chain)

```
Goal: Run the full acceptance criteria validation and record evidence.

Steps:
1. For each criterion, verify and record pass/fail + evidence:

   a) ALL active plans comply with the updated operational policy model.
      → Re-run the 6-criteria compliance scan from M1-C. Every plan must pass all 6.

   b) No active plan includes operational checklist steps.
      → grep all active plans for "- [ ]" lines containing "commit", "push", "merge",
        "create PR" as step deliverables. Expected: 0 matches.

   c) Every active plan includes explicit documentation handling.
      → Confirm each plan has a wiki update step or justified no-doc-needed.

   d) Active plan metadata uses normalized automation mode and role-neutral terminology.
      → Check Automation Mode values and agent references.

   e) Global/index references do not direct users to obsolete operational semantics.
      → Confirm M4-A/M4-B findings.

   f) No plans/completed/ content body was modified.
      → Run: git diff --name-only -- "docs/**/completed/**"
        Expected: no files changed.

2. Build a validation evidence table:
   | Criterion | Status | Evidence |
   |---|---|---|

3. If any criterion fails, identify the specific remediation and go back to the relevant
   phase.

4. If all pass, mark M5-A as completed.

Tras completar M5-A → LANZAR test-L2.ps1.
Si L2 falla, reparar. Cuando L2 verde → esperar instrucciones del usuario.
```

### Prompt M5-B — User final validation (Planning agent — hard gate)

```
Goal: Get user sign-off on the complete migration.

Steps:
1. Present to the user:
   - Validation evidence table from M5-A.
   - Full list of changed files (git diff --stat).
   - Confirmation that no completed/ files were modified.
   - L2 test status (should be green).
2. Ask user:
   - [ ] Are all changes acceptable?
   - [ ] Approve commit and PR creation?
3. If user approves, mark M5-B as completed. Prepare commit per user instructions.
4. If user requests changes, loop back to relevant phase.
```

### Prompt M5-C — Documentation task closure (Execution agent — auto-chain)

```
Goal: Close the documentation handling requirement.

Decision: no-doc-needed.
Rationale: This is an internal plan-governance migration. All changes are to active plan
files (operational metadata, agent instruction sections, header normalization) and
optionally global index references. Plan files are agent execution artifacts, not canonical
wiki content. No user-facing documentation is affected.

Mark M5-C as completed.
```

---

## Active Prompt

### M1 migration checklist reference (from IMP-01 policy baseline)

- Required header fields: `Branch`, `PR`, `Prerequisite`, `Worktree`, `CI Mode`, `Agents`, `Automation Mode`, plus one of `User Story`/`Backlog item`.
- Agent Instructions standard: immediate checkbox update, L2 gate at commit points, no commit/push without explicit approval in `Supervisado`.
- Prohibited operational-step patterns: checklist deliverables must not be operational actions (`commit`, `push`, `merge`, `create/update PR`, `git add`, `git commit`, `git push`).
- Documentation task requirement: each active plan includes explicit wiki update step or justified `no-doc-needed`.

### M1-B active inventory (outside `completed/`)

- `PLAN_2026-02-28_DOCS-IMPROVEMENT.md`
- `PLAN_2026-03-07_MULTI-VISIT_P4_NER-LLM-ENRICHMENT.md`
- `PLAN_2026-03-09_IMP-01-CANONICAL-POLICY-ALIGNMENT/PLAN_2026-03-09_IMP-01-CANONICAL-POLICY-ALIGNMENT.md` (unexpected extra active plan)
- `PLAN_2026-03-09_IMP-03-PLAN-EXECUTION-GUARD.md`
- `PLAN_2026-03-09_IMP-04-ACTIVE-PLAN-MIGRATION.md` (current)

Note: `PLAN_2026-03-09_IMP-02-ROUTER-DOC-UPDATES-SYNC.md` is currently under `plans/completed/` and excluded from active scope.

### M1-C baseline compliance table (before Phase 2/3 edits)

| Plan | Agent Instructions | Header complete | No operational checklist steps | Documentation handling | Role-neutral terminology | Automation mode normalized |
|---|---|---|---|---|---|---|
| DOCS-IMPROVEMENT | FAIL | PASS (worktree stale) | FAIL (`D9-A` used `merge readiness`) | PASS (`D9-B`) | PASS | PASS |
| MULTI-VISIT_P4 | FAIL | FAIL (missing User Story/Backlog item) | PASS | PASS (`P2-C`) | PASS | PASS |
| IMP-03 | PASS | PASS | PASS | PASS (`P5-C`) | PASS | PASS |
| IMP-01 | FAIL | PASS | PASS (open matches only in acceptance checklist, not operational steps) | PASS (canonical docs updated) | PASS | PASS |

### M4-A search evidence (global/index references)

- `docs/README.md`: no `PLAN_MASTER`; `execution-rules.md` appears as `03-ops/execution-rules.md (compatibility stub)`.
- `docs/projects/veterinary-medical-records/04-delivery/implementation-plan.md`: no `PLAN_MASTER`; no stale links to moved active plans.
- `docs/projects/veterinary-medical-records/04-delivery/delivery-summary.md`: no `PLAN_MASTER`; `execution-rules.md` mention is historical changelog context, not operative routing.
- `docs/projects/veterinary-medical-records/README.md`: no stale operational references detected.

M4-B result: no global cleanup edits required.

### M5-A validation evidence table

| Criterion | Status | Evidence |
|---|---|---|
| All active plans comply with updated operational model | PASS | Agent Instructions now present in DOCS-IMPROVEMENT, MULTI-VISIT_P4, IMP-03, IMP-01, IMP-04; required headers and automation mode fields present. |
| No active plan includes operational checklist steps as deliverables | PASS | Only regex hits are in IMP-01 acceptance checklist bullets (non-operational deliverables); execution checklists do not deliver commit/push/merge/PR actions. |
| Every active plan includes explicit documentation handling | PASS | DOCS-IMPROVEMENT `D9-B`, MULTI-VISIT_P4 `P2-C`, IMP-03 `P5-C`, IMP-01 canonical-doc update steps, IMP-04 `M5-C` no-doc-needed. |
| Metadata uses normalized automation mode + role-neutral terminology | PASS | All active plans have `Automation Mode` set to `Supervisado`; no vendor names used as role labels. |
| Global/index references free of obsolete operational semantics | PASS | `M4-A` search over the 4 target global files found no stale routing references requiring edits. |
| No `plans/completed/` content body modified | PASS | `git diff --name-only -- "docs/**/completed/**"` returned no changed files. |

---

## Acceptance Criteria

1. All active plans comply with the updated operational policy model.
2. No active plan includes operational checklist steps (`commit`, `push`, `create/update PR`, `merge`) as executable tasks.
3. Every active plan includes explicit documentation handling (update wiki or justified `no-doc-needed`).
4. Active plan metadata uses normalized automation mode semantics and role-neutral agent terminology.
5. Global/index-level references no longer direct users to obsolete operational semantics.
6. No `plans/completed/` content body is modified.

## How to test

1. **Compliance re-scan:** Open each active plan and verify:
   - `## Agent Instructions` section present with 3 standard rules.
   - All required header fields populated (or acceptable placeholders).
   - No `- [ ]` step delivers an operational action (commit/push/merge/create PR).
   - Explicit documentation task (wiki update or `no-doc-needed` with rationale).
   - `Automation Mode:` set to `Supervisado` / `Semiautomatico` / `Automatico`.
   - Agent references use "Planning agent" / "Execution agent" (no vendor names as roles).

2. **Completed plans untouched:**
   ```
   git diff --name-only -- "docs/**/completed/**"
   ```
   Expected: no output.

3. **Global/index clean:**
   ```
   grep -r "PLAN_MASTER" docs/projects/veterinary-medical-records/04-delivery/
   grep -rn "execution-rules" docs/projects/veterinary-medical-records/04-delivery/ | grep -v completed | grep -v "(compatibility stub)"
   ```
   Expected: no matches (or only properly annotated references).

4. **L2 tests green:** `scripts/ci/test-L2.ps1`
