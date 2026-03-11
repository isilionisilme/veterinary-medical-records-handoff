# Plan: Router and DOC_UPDATES Contract Synchronization

> **Operational rules:** See [plan-execution-protocol.md](../../../03-ops/plan-execution-protocol.md) for agent execution protocol, SCOPE BOUNDARY template, commit conventions, and handoff messages.

**Branch:** Pending (created at execution start)
**PR:** Pending (PR created on explicit user request)
**User Story:** [IMP-02](../../Backlog/completed/imp-02-router-and-doc-updates-contract-synchronization.md)
**Prerequisite:** IMP-01 canonical policy alignment merged or finalized in branch scope
**Worktree:** `8420/veterinary-medical-records`
**CI Mode:** Pipeline depth-1 gate (mode 2, default)
**Agents:** Planning agent + Execution agent
**Automation Mode:** Supervisado

## Agent execution rules (plan-specific)

1. **Mark tasks completed immediately.** After finishing each step, update its checkbox in `## Execution Status` to `[x]` before moving to the next step.
2. **L2 gate at commit recommendations.** When a prompt includes a commit recommendation, run `scripts/ci/test-L2.ps1 -BaseRef main` before yielding. If L2 fails, diagnose and fix the issue, then re-run until green. Once L2 is green, **stop and wait for user instructions** — do not proceed to the next step automatically.
3. **No commit or push without approval.** Never run `git commit`, `git push`, or any variant without explicit user confirmation. Present the proposed commit scope and message, then wait.

## Context

After canonical policy changes (e.g., consolidation of `execution-rules.md` into `plan-execution-protocol.md`, plan-creation updates, implementation-plan restructuring), derived router files and DOC_UPDATES contract maps can retain stale references. This causes:

- Assistant routing to obsolete policy semantics.
- False pass/fail in documentation guardrails (`check_doc_test_sync.py`, `check_doc_router_parity.py`, `check_router_directionality.py`).
- Drift between canonical source-of-truth and derived modules.

**Current state (2026-03-09):**
- `generate-router-files.py --check` passes (router files in sync).
- `execution-rules.md` exists as a compatibility stub routing to `plan-execution-protocol.md`.
- Both `test_impact_map.json` and `router_parity_map.json` contain explicit rules for `execution-rules.md` stub.
- IMPLEMENTATION_PLAN owner modules exist under `docs/agent_router/04_PROJECT/IMPLEMENTATION_PLAN/` with 60+ mini-files.
- All four guard scripts pass against `main` currently, but mappings may become stale after IMP-01 changes.

## Objective

Propagate canonical policy updates (from IMP-01) into router modules and DOC_UPDATES contract maps so that assistants and guardrails evaluate the same source-of-truth semantics with no legacy drift.

## Scope Boundary (strict)

- **In scope:**
  - Router mini-files under `docs/agent_router/` (regeneration from canonical sources).
  - DOC_UPDATES contract maps: `test_impact_map.json`, `router_parity_map.json`.
  - `MANIFEST.yaml` updates if canonical sources changed paths or sections.
  - IMPLEMENTATION_PLAN owner modules propagation.
  - Removal/replacement of stale `execution-rules.md` mapping references if IMP-01 deprecates the stub.
- **Out of scope:**
  - New CI guard scripts or execution guard implementation.
  - Migration of active plan files.
  - Backend/frontend product code.
  - Historical rewrite of completed plans.
  - Canonical doc content changes (those belong to IMP-01).

## Design decisions

1. **Single regeneration pass:** Run `generate-router-files.py` once after all canonical changes from IMP-01 are finalized, then review only touched families.
2. **Contract map updates are manual and targeted:** Each rule in `test_impact_map.json` / `router_parity_map.json` is reviewed individually — no bulk replacement.
3. **Stub handling depends on IMP-01 outcome:** If IMP-01 removes the `execution-rules.md` stub, remove its contract map rules. If it keeps the stub, update required terms to match current content.

## Execution Status — update on completion of each step

### Phase 1 — Pre-flight validation

- [x] S1-A 🚧 — Confirm IMP-01 is merged or finalized; identify exact canonical changes (file renames, section changes, removed files) (Planning agent) — ✅ finalized on `main` via `2836eaca7` (`docs: align canonical execution policy and PR workflow (#241)`)
- [x] S1-B 🔄 — Snapshot current guard state: run all four guard scripts and record baseline output (Execution agent) — ✅ all four baseline guards pass

### Phase 2 — Router regeneration

- [x] S2-A 🔄 — Update `MANIFEST.yaml` if any canonical source paths or extracted sections changed in IMP-01 (Execution agent) — ✅ no manifest edits required (`MANIFEST.yaml` unchanged)
- [x] S2-B 🔄 — Regenerate router files: `python scripts/docs/generate-router-files.py` (Execution agent) — ✅ generated without errors
- [x] S2-C 🔄 — Verify regeneration: `python scripts/docs/generate-router-files.py --check` (Execution agent) — ✅ in sync

### Phase 3 — Contract map synchronization

- [x] S3-A 🔄 — Audit `test_impact_map.json`: remove/update rules referencing deprecated paths; add rules for new canonical sources from IMP-01 (Execution agent) — ✅ no stale/deprecated path from IMP-01 delta; file unchanged
- [x] S3-B 🔄 — Audit `router_parity_map.json`: remove/update stale source_doc entries; verify required_terms match current router module content (Execution agent) — ✅ required terms verified; file unchanged
- [x] S3-C 🔄 — If `execution-rules.md` stub is deprecated by IMP-01, remove its rules from both maps; if retained, verify required_terms accuracy (Execution agent) — ✅ Path C (`execution-rules.md` unchanged in IMP-01); mappings retained as-is

### Phase 4 — IMPLEMENTATION_PLAN owner propagation

- [x] S4-A 🔄 — Verify IMPLEMENTATION_PLAN owner modules reflect current `implementation-plan.md` structure (sections, releases, user stories) (Execution agent) — ✅ drift detected (missing Release 15-18 and US-61..US-78 modules)
- [x] S4-B 🔄 — If owner modules are out of sync, regenerate via MANIFEST or manual update (Execution agent) — ✅ manual owner-module propagation applied

### Phase 5 — Validation and close-out

- [x] S5-A 🔄 — Run `python scripts/docs/generate-router-files.py --check` — must pass (Execution agent) — ✅ pass
- [x] S5-B 🔄 — Run `python scripts/docs/check_doc_test_sync.py --base-ref main` — must pass with no unmapped gaps (Execution agent) — ✅ pass (after targeted DOC_UPDATES map rule text update)
- [x] S5-C 🔄 — Run `python scripts/docs/check_doc_router_parity.py --base-ref main` — must pass with required terms present (Execution agent) — ✅ pass
- [x] S5-D 🔄 — Run `python scripts/docs/check_router_directionality.py --base-ref main` — must pass (Execution agent) — ✅ pass
- [x] S5-E 🚧 — User validates no stale reference remains; reviews diff (Planning agent) — ✅ approved in chat

### Phase 6 — Documentation task

- [x] S6-A 🔄 — `no-doc-needed`: This is an infrastructure/derived-docs-only change. No user-facing documentation is affected. Rationale: all changes are to auto-generated router files and internal contract maps that are not part of the canonical wiki (Execution agent) — ✅ recorded

## PR Roadmap

### PR partition gate assessment

| Criterion | Assessment |
|---|---|
| **Estimated changed files** | ~5–20 (2 JSON maps + MANIFEST.yaml + regenerated router mini-files) |
| **Estimated changed lines** | ~100–300 (map rule edits + regenerated content) |
| **Semantic risk axes** | None mixed — all derived docs, no backend/frontend, no schema changes |
| **Size guardrail (>400 lines / >15 files)** | May approach file count threshold due to router regeneration, but all changes are mechanical |

**Decision:** Single PR (Option A).
**Rationale:** All changes are mechanical/derived — router regeneration is a single deterministic command, and contract map edits are targeted corrections. No mixed semantic risk axes. If regeneration touches >15 files, the diff is fully mechanical and reviewable in isolation.

### PR-1: Router and DOC_UPDATES contract sync

- **Phases:** S1 through S6
- **Content:** MANIFEST.yaml edits, regenerated router files, contract map corrections
- **Validation:** All four guard scripts pass

## Prompt Queue

### Prompt for S1-A (Planning agent — hard gate)

> **Goal:** Confirm IMP-01 readiness and build the delta inventory that drives Phases 2–4.
>
> **Steps:**
>
> 1. Read the IMP-01 backlog item at `docs/projects/veterinary-medical-records/04-delivery/Backlog/completed/imp-01-canonical-operational-execution-policy-alignment.md`. Check its `Status` field.
> 2. Search for any IMP-01 plan folder under `docs/projects/veterinary-medical-records/04-delivery/plans/` (e.g., `PLAN_*IMP-01*` or `PLAN_*POLICY*`). If found, read its Execution Status to determine completion.
> 3. If IMP-01 is not merged or finalized: **STOP**. Report to user that IMP-02 is blocked. Record the blocker in this plan and yield.
> 4. If IMP-01 is merged or finalized, build the **delta inventory** by running:
>    - `git diff --name-status main...HEAD -- docs/` (if IMP-01 is on current branch)
>    - Or `git log --oneline --name-status <imp01-merge-commit>` (if merged to main)
> 5. Classify each changed canonical file into one of: **renamed**, **new sections added**, **sections removed/rewritten**, **file deleted**, **file added**.
> 6. Pay special attention to:
>    - `docs/projects/veterinary-medical-records/03-ops/execution-rules.md` — was it deleted, modified, or left as-is?
>    - `docs/projects/veterinary-medical-records/03-ops/plan-execution-protocol.md` — what sections changed?
>    - `docs/projects/veterinary-medical-records/03-ops/plan-creation.md` — any structural changes?
>    - `docs/projects/veterinary-medical-records/04-delivery/implementation-plan.md` — any section/release/story changes?
>    - `docs/shared/03-ops/way-of-working.md` — any operational policy changes?
> 7. Record the delta inventory as a structured table in `## Active Prompt` or as an annex, with columns: `File | Change type | Detail | Affects manifest? | Affects contract maps?`.
>
> **Exit gate:** Delta inventory recorded. If empty (no canonical changes), report to user that IMP-02 has no work to do and recommend closing the plan.

### Prompt for S1-B (Execution agent — auto-chain)

> **Goal:** Capture baseline guard state before any changes.
>
> **Steps:**
>
> 1. Run each guard script and capture full output:
>    ```
>    python scripts/docs/generate-router-files.py --check
>    python scripts/docs/check_doc_test_sync.py --base-ref main
>    python scripts/docs/check_doc_router_parity.py --base-ref main
>    python scripts/docs/check_router_directionality.py --base-ref main
>    ```
> 2. Record each output (pass/fail, warnings, unmapped docs) as the **baseline snapshot**.
> 3. If any script fails at baseline, flag it — this is a pre-existing issue, not an IMP-02 regression. Note it for S5-E review.
>
> **Exit gate:** Four baseline outputs recorded. Proceed to Phase 2.

### Prompt for S2-A (Execution agent — auto-chain)

> **Goal:** Update `MANIFEST.yaml` to reflect any canonical source path or section changes from IMP-01.
>
> **Steps:**
>
> 1. Read `docs/agent_router/MANIFEST.yaml` fully.
> 2. Cross-reference with the S1-A delta inventory. For each canonical file that was **renamed**:
>    - Find all `source:` entries referencing the old path.
>    - Update to the new path.
> 3. For each canonical file that had **sections removed or renamed**:
>    - Find all `sections:` lists in manifest entries for that source.
>    - Update section names to match current headings (match heading text case-sensitively after `##` / `###`).
>    - If a section was removed entirely, remove the corresponding `target:` entry.
> 4. For each canonical file that was **added** by IMP-01 and needs router representation:
>    - Add appropriate manifest entries following the existing pattern (index entry + content entries per section).
>    - Use the naming convention: `<NN>_<slug>.md` with sequential numbering within the target directory.
> 5. For each canonical file that was **deleted**:
>    - Remove all manifest entries that referenced it as `source:`.
>    - Note: the generated target files will be cleaned up in S2-B.
> 6. If no manifest changes are needed (delta inventory shows no path/section changes affecting manifest), skip edits and note "MANIFEST.yaml unchanged".
>
> **Commit recommendation:** After S2-C completes (not here). Scope: MANIFEST.yaml + regenerated files.

### Prompt for S2-B (Execution agent — auto-chain)

> **Goal:** Regenerate all derived router files from updated manifest.
>
> **Steps:**
>
> 1. Run: `python scripts/docs/generate-router-files.py`
> 2. Review console output for errors or warnings.
> 3. If the script reports orphaned target files (targets in filesystem but not in manifest), delete them.
> 4. If the script reports missing source sections (section name in manifest not found in canonical doc), go back and fix the manifest section name in S2-A.
> 5. Check `git diff --stat` to see which router files changed and how many.
>
> **Exit gate:** Regeneration completed without errors.

### Prompt for S2-C (Execution agent — auto-chain)

> **Goal:** Verify router files are now in sync.
>
> **Steps:**
>
> 1. Run: `python scripts/docs/generate-router-files.py --check`
> 2. Expected output: "Router files are in sync with canonical sources."
> 3. If check fails, identify the drifted file(s) from the output and fix either the manifest entry or re-run regeneration.
> 4. Do not proceed to Phase 3 until this check passes.
>
> **Commit recommendation:** After S2-C passes. Scope: `MANIFEST.yaml` (if changed) + all regenerated files under `docs/agent_router/`. Message: `chore(docs): regenerate router files after IMP-01 canonical changes`. Validation: `generate-router-files.py --check` passes.

### Prompt for S3-A (Execution agent — auto-chain)

> **Goal:** Audit and update `test_impact_map.json` to remove stale references and add missing rules.
>
> **Steps:**
>
> 1. Read `docs/agent_router/01_WORKFLOW/DOC_UPDATES/test_impact_map.json` fully.
> 2. Cross-reference with the S1-A delta inventory. For each rule in the `rules` array:
>    - **`doc_glob` check:** Does the glob still match an existing canonical file? If the file was renamed by IMP-01, update the glob. If deleted, remove the entire rule.
>    - **`owner_any` check:** Do all paths in `owner_any` still exist? If a file was renamed, update the path. If deleted, remove the stale entry (keep the rule if other valid owners remain; remove the rule if no valid owners remain).
>    - **`required_any` check:** Do all paths in `required_any` still exist? Update renamed paths. Remove deleted paths (keep the rule if other valid required files remain).
> 3. For each **new** canonical file added by IMP-01 that falls under `required_doc_globs` scope:
>    - Check if it already matches an existing glob rule. If not, add a new rule with appropriate `description`, `required_any` (linking to relevant guard scripts and contract maps), and `owner_any` (if there's a corresponding router owner module).
> 4. Validate JSON syntax after edits (no trailing commas, valid structure).
> 5. Run `python scripts/docs/check_doc_test_sync.py --base-ref main` to check progress. Note: this may still show issues if parity map is not yet updated.
>
> **Key files to watch:**
> - Rule for `execution-rules.md` (line ~115): handle per S3-C decision.
> - Rules for `plan-execution-protocol.md`, `plan-creation.md`, `implementation-plan.md`: verify `owner_any` and `required_any` paths match current filesystem.

### Prompt for S3-B (Execution agent — auto-chain)

> **Goal:** Audit and update `router_parity_map.json` to remove stale source_doc references and verify required_terms.
>
> **Steps:**
>
> 1. Read `docs/agent_router/01_WORKFLOW/DOC_UPDATES/router_parity_map.json` fully.
> 2. Cross-reference with the S1-A delta inventory. For each rule in the `rules` array:
>    - **`source_doc` check:** Does the file still exist? If renamed, update the path. If deleted, remove the entire rule.
>    - **`router_modules[].path` check:** Does each target router module file still exist? (It should after S2-B regeneration.) If a router module was removed because its canonical source was deleted, remove the router_module entry.
>    - **`router_modules[].required_terms` check:** For each required term, open the target router module file and verify the term appears as a substring (case-sensitive). If a term no longer appears (e.g., because the section was renamed in IMP-01), update the term to match current content.
> 3. For each **new** canonical file added by IMP-01 that has a corresponding router owner module:
>    - Add a new parity rule with `source_doc`, `description`, and `router_modules` entries.
>    - Set `required_terms` to include the module's title heading (e.g., `"MODULE_NAME — Modules"`) and a distinctive term from the canonical source.
> 4. Validate JSON syntax after edits.
> 5. Run `python scripts/docs/check_doc_router_parity.py --base-ref main` to verify progress.
>
> **Key verification pattern for required_terms:**
> For each rule, run this mental check:
> ```
> rule.source_doc → exists on disk?
> rule.router_modules[].path → exists on disk?
> rule.router_modules[].required_terms[] → appears in target file content?
> ```
> All three must be true for the rule to be valid.

### Prompt for S3-C (Execution agent — auto-chain)

> **Goal:** Handle the `execution-rules.md` compatibility stub based on IMP-01 outcome.
>
> **Steps:**
>
> **Path A — IMP-01 deleted `execution-rules.md`:**
> 1. Remove the rule in `test_impact_map.json` where `doc_glob` is `docs/projects/veterinary-medical-records/03-ops/execution-rules.md`.
> 2. Remove the rule in `router_parity_map.json` where `source_doc` is `docs/projects/veterinary-medical-records/03-ops/execution-rules.md`.
> 3. Check `MANIFEST.yaml` for any entries referencing `execution-rules.md` as source. Remove if present.
> 4. Check `docs/agent_router/04_PROJECT/IMPLEMENTATION_PLAN/60_execution-rules.md` — if the canonical source is gone and this was derived from it, remove or update. If it was derived from `implementation-plan.md` (check manifest), it stays.
> 5. Search for orphan references: `grep -r "execution-rules" docs/agent_router/` — update or remove any remaining pointers.
>
> **Path B — IMP-01 kept `execution-rules.md` as compatibility stub:**
> 1. Read the current content of `docs/projects/veterinary-medical-records/03-ops/execution-rules.md`.
> 2. In `test_impact_map.json`, verify the rule's `required_any` paths are all valid and complete.
> 3. In `router_parity_map.json`, verify:
>    - The `router_modules[].path` exists: `docs/agent_router/03_SHARED/EXECUTION_PROTOCOL/00_entry.md`
>    - The `required_terms` (`"EXECUTION_PROTOCOL — Modules"`, `"plan-execution-protocol.md"`) appear in that file.
> 4. If IMP-01 modified the stub's content, verify terms still match. Update if needed.
>
> **Path C — IMP-01 did not touch `execution-rules.md` at all:**
> 1. Leave both rules as-is. No changes needed.
> 2. Note: the stub and its mappings remain valid as-is.
>
> **Commit recommendation:** After S3-C completes. Scope: `test_impact_map.json`, `router_parity_map.json`. Message: `chore(docs): synchronize DOC_UPDATES contract maps after IMP-01`. Validation: all four guard scripts pass.

### Prompt for S4-A (Execution agent — auto-chain)

> **Goal:** Verify IMPLEMENTATION_PLAN router owner modules reflect current `implementation-plan.md` structure.
>
> **Steps:**
>
> 1. Read `docs/projects/veterinary-medical-records/04-delivery/implementation-plan.md` — note its current heading structure (releases, user stories, sections).
> 2. Read `docs/agent_router/04_PROJECT/IMPLEMENTATION_PLAN/00_entry.md` — note the module index.
> 3. Read the corresponding MANIFEST.yaml entries for `04_PROJECT/IMPLEMENTATION_PLAN/` to understand which sections map to which mini-files.
> 4. Cross-reference:
>    - Does every release in `implementation-plan.md` have a corresponding mini-file?
>    - Does every user story have a corresponding mini-file?
>    - Does the `00_entry.md` index list all existing mini-files?
>    - Are section headings in mini-files consistent with current canonical headings?
> 5. Build a sync report:
>    - **In sync:** files that match current canonical content.
>    - **Drift detected:** files whose content doesn't match the canonical section.
>    - **Missing:** canonical sections with no corresponding mini-file.
>    - **Orphaned:** mini-files with no corresponding canonical section.
> 6. If everything is in sync, note "IMPLEMENTATION_PLAN owner modules: in sync" and skip S4-B.
>
> **Exit gate:** Sync report produced. If drift/missing/orphaned items exist, proceed to S4-B.

### Prompt for S4-B (Execution agent — auto-chain)

> **Goal:** Fix any IMPLEMENTATION_PLAN owner module drift detected in S4-A.
>
> **Steps:**
>
> 1. **Drift detected:** For each drifted mini-file:
>    - If the file is generated by `generate-router-files.py` (has `<!-- AUTO-GENERATED -->` header), confirm it was regenerated in S2-B. If still drifted, check the manifest section name mapping.
>    - If the file is manually maintained, update its content to match the canonical section.
> 2. **Missing mini-files:** For each missing entry:
>    - Add a manifest entry for the new section following naming convention (`<NN>_<slug>.md`).
>    - Regenerate: `python scripts/docs/generate-router-files.py`.
>    - Add the new file to the `00_entry.md` index.
> 3. **Orphaned mini-files:**
>    - If the canonical section was removed, remove the manifest entry and delete the orphaned mini-file.
>    - Remove the deleted file from `00_entry.md` index.
> 4. Verify: `python scripts/docs/generate-router-files.py --check` must pass.
> 5. Verify the `router_parity_map.json` rule for `implementation-plan.md` still passes:
>    - `required_terms` (e.g., `"IMPLEMENTATION_PLAN — Modules"`) must appear in `00_entry.md`.
>
> **Commit recommendation:** If changes were made, combine with S2/S3 commit or create separate commit. Scope: manifest + IMPLEMENTATION_PLAN mini-files. Message: `chore(docs): propagate implementation-plan owner modules`. Validation: `generate-router-files.py --check` passes.

### Prompt for S5-A through S5-D (Execution agent — auto-chain)

> **Goal:** Run all four guard scripts as final validation. All must pass.
>
> **Steps:**
>
> 1. Run each script sequentially and capture output:
>    ```
>    python scripts/docs/generate-router-files.py --check
>    python scripts/docs/check_doc_test_sync.py --base-ref main
>    python scripts/docs/check_doc_router_parity.py --base-ref main
>    python scripts/docs/check_router_directionality.py --base-ref main
>    ```
> 2. For each script:
>    - **Pass:** Record ✅ and move to next.
>    - **Fail:** Record the error output. Diagnose:
>      - If `generate-router-files.py --check` fails: a regeneration was missed or manifest is wrong. Go back to S2.
>      - If `check_doc_test_sync.py` fails with unmapped docs: a rule is missing in `test_impact_map.json`. Go back to S3-A.
>      - If `check_doc_router_parity.py` fails with missing terms: a `required_terms` entry is wrong or a router module is stale. Go back to S3-B.
>      - If `check_router_directionality.py` fails: a protected router file was edited without a canonical source change. Verify the canonical source was also changed, or add an exemption in `scripts/docs/router_directionality_guard_config.json`.
> 3. Do not proceed to S5-E until all four scripts pass.
> 4. Run `git diff --stat` and `git diff --name-only` to produce the final changeset summary for user review.
>
> **Exit gate:** All four guards green. Changeset summary ready for S5-E user review.

### Prompt for S5-E (Planning agent — hard gate)

> **Goal:** User validates the complete diff. No stale references remain.
>
> **Steps:**
>
> 1. Present to the user:
>    - Summary of all changed files (from `git diff --stat`).
>    - Confirmation that all four guard scripts pass.
>    - List of any pre-existing issues noted in S1-B baseline (if any).
> 2. Ask user to verify:
>    - [ ] No DOC_UPDATES mapping rule references a deprecated canonical path.
>    - [ ] `grep -r "execution-rules" docs/agent_router/01_WORKFLOW/DOC_UPDATES/*.json` returns expected results (none if stub deprecated, valid terms if retained).
>    - [ ] Diff contains only targeted corrections — no over-broad rule removal.
>    - [ ] IMPLEMENTATION_PLAN owner modules are consistent.
> 3. If user approves: proceed to commit.
> 4. If user requests changes: go back to the relevant phase.
>
> **Commit recommendation:** Final commit for PR. Scope: all changed files. Message: `chore(docs): synchronize router and DOC_UPDATES contracts (IMP-02)`. Validation: all four guard scripts pass + user approval.

### Prompt for S6-A (Execution agent — auto-chain)

> **Goal:** Close documentation task.
>
> This step records the documentation decision. No wiki or user-facing documentation is needed because:
> - All changes are to auto-generated router files (`docs/agent_router/`), which are derived assistant modules, not canonical wiki content.
> - Contract map files (`test_impact_map.json`, `router_parity_map.json`) are internal guardrail configuration, not user-facing documentation.
> - `MANIFEST.yaml` is build configuration for the router generation pipeline.
>
> **Decision:** `no-doc-needed`.
> **Rationale:** Infrastructure-only change to derived docs and internal contract maps. No canonical wiki content affected.

## Active Prompt

### S1-A Delta Inventory (IMP-01 -> `main`)

IMP-01 is finalized/merged in `main` (`2836eaca7`).

| File | Change type | Detail | Affects manifest? | Affects contract maps? |
|---|---|---|---|---|
| `docs/projects/veterinary-medical-records/03-ops/plan-execution-protocol.md` | sections removed/rewritten | Canonical policy text alignment in execution governance sections (automation/PR policy semantics) | Yes (router content regeneration) | Yes (DOC_UPDATES/parity terms can drift) |
| `docs/shared/03-ops/way-of-working.md` | sections removed/rewritten | Canonical policy text alignment in commit discipline and PR workflow semantics | Yes (router content regeneration) | Yes (DOC_UPDATES/parity terms can drift) |
| `docs/projects/veterinary-medical-records/03-ops/execution-rules.md` | unchanged | Compatibility stub retained (not deleted/renamed in IMP-01 merge commit) | No | Keep existing stub rules; re-verify terms in S3-C |
| `docs/projects/veterinary-medical-records/03-ops/plan-creation.md` | unchanged | No IMP-01 change detected in merge commit | No | No direct map change expected |
| `docs/projects/veterinary-medical-records/04-delivery/implementation-plan.md` | unchanged | No IMP-01 change detected in merge commit | No (for IMP-01) | No direct map change expected |

Notes:
- Backlog card `imp-01-canonical-operational-execution-policy-alignment.md` still shows `Status: Planned`, but execution evidence indicates completion in merged PR `#241` and IMP-01 plan shows all execution steps completed.

### S1-B Baseline Snapshot

- `python scripts/docs/generate-router-files.py --check` -> `Router files are in sync with canonical sources.`
- `python scripts/docs/check_doc_test_sync.py --base-ref main` -> `Doc/test sync guard: no markdown docs changed.`
- `python scripts/docs/check_doc_router_parity.py --base-ref main` -> `Doc/router parity guard: no mapped source docs changed.`
- `python scripts/docs/check_router_directionality.py --base-ref main` -> `Router directionality guard: no protected router files changed.`

### Phase 2 Snapshot (S2-A/S2-B/S2-C)

- `MANIFEST.yaml`: unchanged (no source path rename and no section extraction key drift requiring manifest edits).
- `python scripts/docs/generate-router-files.py` -> `Generated 73 router files.`
- `python scripts/docs/generate-router-files.py --check` -> `Router files are in sync with canonical sources.`

### Phase 3 Snapshot (S3-A/S3-B/S3-C)

- `test_impact_map.json` audited against S1-A delta: no renamed/deleted canonical paths introduced by IMP-01; no rule edits required.
- `router_parity_map.json` audited against S1-A delta: no stale `source_doc` paths from IMP-01; no rule edits required.
- Stub decision: `docs/projects/veterinary-medical-records/03-ops/execution-rules.md` retained/unchanged in IMP-01 merge (`2836eaca7`) -> keep compatibility rules.
- Required-term check for stub parity rule:
  - `docs/agent_router/03_SHARED/EXECUTION_PROTOCOL/00_entry.md` contains `EXECUTION_PROTOCOL — Modules` and `plan-execution-protocol.md`.
- Guard spot checks:
  - `python scripts/docs/check_doc_test_sync.py --base-ref main` -> no markdown docs changed.
  - `python scripts/docs/check_doc_router_parity.py --base-ref main` -> no mapped source docs changed.

### Phase 4 Sync Report (S4-A/S4-B)

- In sync before fix:
  - Existing Release 1-14 owner mini-files.
  - Existing US owner mini-files up to US-58.
  - Index/file existence integrity: `index_count=63`, `missing_count=0`, `fs_count=64` (`00_entry.md` not listed in its own index).
- Drift detected:
  - Missing release modules for Release 15, 16, 17, 18.
  - Missing story modules for US-61 through US-78.
- Applied in S4-B:
  - Added release modules: `138_release-15...md`, `139_release-16...md`, `140_release-17...md`, `141_release-18...md`.
  - Added story modules: `364_us-61...md` through `381_us-78...md`.
  - Updated `docs/agent_router/04_PROJECT/IMPLEMENTATION_PLAN/00_entry.md` index entries accordingly.
- Post-fix validation:
  - Index/file existence integrity: `index_count=85`, `missing_count=0`, `fs_count=86`.
  - `python scripts/docs/generate-router-files.py --check` -> `Router files are in sync with canonical sources.`

### Phase 5 Snapshot (S5-A..S5-D)

- Final guard run results:
  - `python scripts/docs/generate-router-files.py --check` -> `Router files are in sync with canonical sources.`
  - `python scripts/docs/check_doc_test_sync.py --base-ref main` -> pass
  - `python scripts/docs/check_doc_router_parity.py --base-ref main` -> no mapped source docs changed
  - `python scripts/docs/check_router_directionality.py --base-ref main` -> no protected router files changed
- Adjustment applied during S5-B remediation:
  - Updated description text in `docs/agent_router/01_WORKFLOW/DOC_UPDATES/test_impact_map.json` router rule to explicitly include owner-module propagation wording.
- Current staged changeset summary for S5-E review:
  - `24 files changed, 297 insertions(+), 2 deletions(-)` (IMPLEMENTATION_PLAN owner modules + plan file)
  - plus `test_impact_map.json` (1 insertion, 1 deletion)

## Acceptance criteria

1. `python scripts/docs/generate-router-files.py --check` passes.
2. `python scripts/docs/check_doc_test_sync.py --base-ref <base>` passes with no unmapped or owner propagation gaps.
3. `python scripts/docs/check_doc_router_parity.py --base-ref <base>` passes with required terms present.
4. `python scripts/docs/check_router_directionality.py --base-ref <base>` passes.
5. No DOC_UPDATES mapping rule references deprecated canonical ownership paths.
6. IMPLEMENTATION_PLAN owner modules are consistent with current `implementation-plan.md`.

## How to test

1. `python scripts/docs/generate-router-files.py --check` — expect "Router files are in sync".
2. `python scripts/docs/check_doc_test_sync.py --base-ref main` — expect pass, no unmapped docs.
3. `python scripts/docs/check_doc_router_parity.py --base-ref main` — expect pass, no missing terms.
4. `python scripts/docs/check_router_directionality.py --base-ref main` — expect pass, no directionality violations.
5. `grep -r "execution-rules" docs/agent_router/01_WORKFLOW/DOC_UPDATES/*.json` — expect no results if stub deprecated, or expect updated terms if stub retained.
6. Manual review: diff of `test_impact_map.json` and `router_parity_map.json` shows only targeted corrections, no over-broad rule removal.

## Risks and limitations

- **IMP-01 not merged:** This plan cannot execute Phase 2+ until IMP-01 canonical changes are finalized. S1-A is a hard gate.
- **Router regeneration touching many files:** Regeneration is deterministic and mechanical, but review should focus on touched owner families only.
- **Over-broad map edits:** Mitigated by reviewing each rule individually and preserving strict required-term checks.
