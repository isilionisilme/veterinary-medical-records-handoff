# Plan: Split Implementation Plan into Backlog Item Files

> **Operational rules:** See [plan-execution-protocol.md](../../03-ops/plan-execution-protocol.md) for execution protocol, hard gates, and completion integrity.

**Branch:** `codex/veterinary-medical-records/docs/split-implementation-plan-backlog`  
**PR:** `#239`  
**User Story:** `US-67` (documentation governance) + `IMP-04` (plan/content migration hygiene)  
**Prerequisite:** `main` up to date and clean working tree  
**Worktree:** `D:/Git/veterinary-medical-records`  
**CI Mode:** `2) Pipeline depth-1 gate` (default)  
**Automation Mode:** `Supervisado` (default until explicit user selection)

---

## Context

`docs/projects/veterinary-medical-records/04-delivery/implementation-plan.md` currently centralizes release sequencing plus all detailed User Stories (`US-*`) and Improvements (`IMP-*`). The file is too large for maintainability and navigation.

Target outcome:
- Keep `implementation-plan.md` as release sequencing authority.
- Move each `US` and each `IMP` detail block into its own file under `04-delivery/Backlog/`.
- Provide a central backlog index and migrate legacy links.

---

## Objective

1. Create a normalized backlog structure where every `US-*` and `IMP-*` has one dedicated Markdown file.
2. Reduce `implementation-plan.md` to release plan + backlog links only.
3. Preserve traceability by updating internal references and router-facing documentation pointers.
4. Deliver changes in five logical commits (English commit messages).

## Scope Boundary

**In scope**
- Documentation refactor under `docs/projects/veterinary-medical-records/04-delivery/`.
- Link migration for references that point to old `implementation-plan.md` story anchors.
- Backlog index creation.

**Out of scope**
- Product/code behavior changes.
- Story content rewrites beyond minimal normalization needed for extraction.
- PR creation and merge actions.

**Documentation task (§3 compliance):** This plan is inherently a documentation task — every step produces or modifies documentation. No separate doc task or `no-doc-needed` rationale is required.

---

## PR Roadmap

Estimated PRs: **1** (`PR-1`), with 5 commits.

### PR partition gate (mandatory assessment)

**Semantic risk axes:** documentation-only — no backend, frontend, or schema runtime changes.
**Size guardrails:** expected to exceed 15 files and may exceed 400 changed lines.

Options presented to user at plan approval:
- **Option A:** keep one PR because changes are mechanical, traceable, and docs-only.
- **Option B:** split into multiple PRs by phase (extraction, links, router/doc-updates propagation).

**User decision:** Option A — single PR. ✅ Confirmed by user (2026-03-08).
**Rationale:** one cohesive docs migration with deterministic validation and no runtime risk. All changes are mechanical documentation extraction/relink with no mixed semantic risk axes.

> Execution-time safeguard: P4-A will re-evaluate thresholds against the real diff before PR preparation. If thresholds are exceeded beyond the original estimate, the hard gate in P4-B reopens.

---

## Design decisions

- File naming convention: `us-XX-slug.md` and `imp-XX-slug.md`.
- Backlog root index: `Backlog/README.md` with a single consolidated table.
- `implementation-plan.md` remains authoritative for release sequencing only.
- Historical references should be migrated to direct `Backlog/*` links where feasible.
- **Batched extraction (P1):** items extracted in 4 batches of ~20 with per-batch validation checkpoints to catch drift early and reduce context pressure.
- **Dry-run link migration (P3-A):** replacement list generated and reviewed before any file is modified, preventing cascading link errors.

---

## Commit recommendations (inline, non-blocking)

1. **When:** after P0-B (discovery complete) and P1-A1→P1-A4 + P1-B (batched extraction + index done).
   **Scope:** `04-delivery/Backlog/*.md`, `04-delivery/Backlog/README.md`.
   **Suggested message:** `docs(backlog): create backlog folder and extract US/IMP item files`
   **Expected validation:** all 80 items exist as individual files (verified per-batch); `Backlog/README.md` table has 80 rows.

2. **When:** after P2-A + P2-B (implementation-plan reduction done).
   **Scope:** `04-delivery/implementation-plan.md`.
   **Suggested message:** `docs(implementation-plan): keep release plan and link to backlog items`
   **Expected validation:** no `## US-*` or `## IMP-*` detail sections remain; release plan links resolve to `Backlog/` files.

3. **When:** after P3-A-APPLY (legacy link migration applied and confirmed).
   **Scope:** `docs/` files that referenced `implementation-plan.md#us-*` or `#imp-*` anchors.
   **Suggested message:** `docs(links): migrate legacy story/improvement references to backlog paths`
   **Expected validation:** `grep -r 'implementation-plan.md#us-\|implementation-plan.md#imp-' docs/` returns zero matches (excluding the plan itself).

4. **When:** after P3-B (router/module propagation done).
   **Scope:** `docs/agent_router/`, owner-module files, `docs/README.md`.
   **Suggested message:** `docs(router): align project/router references for implementation plan split`
   **Expected validation:** `python scripts/docs/check_doc_router_parity.py` passes; `python scripts/docs/generate-router-files.py --check` passes.

5. **When:** after P4-A (validation pass done).
   **Scope:** any files touched by normalization.
   **Suggested message:** `docs(normalization): run final doc-updates normalization and consistency pass`
   **Expected validation:** `npm run docs:lint` passes; all doc scripts in "How to test" pass.

---

## Execution Status

**Legend**
- 🔄 auto-chain: executable by agent
- 🚧 hard-gate: explicit user decision/confirmation required

### Phase 0 - Discovery and extraction contract

- [x] P0-A 🔄 **[PR-1]** Inventory all `US-*` and `IMP-*` sections in `implementation-plan.md` and map IDs to target filenames.
- [x] P0-B 🔄 **[PR-1]** Validate backlink impact (`implementation-plan.md` references and anchor-style links in delivery plans/docs).

### Phase 1 - Backlog creation and item extraction (batched)

- [x] P1-A1 🔄 **[PR-1]** Create `04-delivery/Backlog/` and extract items 1–20 (US-01 through US-20).
- [x] P1-A1-V 🔄 **[PR-1]** Validate batch 1: 20 files exist, headings are `#`-level, content matches source.
- [x] P1-A2 🔄 **[PR-1]** Extract items 21–40 (US-21 through US-40).
- [x] P1-A2-V 🔄 **[PR-1]** Validate batch 2: cumulative 40 files, spot-check 2 random items.
- [x] P1-A3 🔄 **[PR-1]** Extract items 41–60 (US-41 through US-60).
- [x] P1-A3-V 🔄 **[PR-1]** Validate batch 3: cumulative 60 files, spot-check 2 random items.
- [x] P1-A4 🔄 **[PR-1]** Extract items 61–80 (US-61 through US-75 + IMP-01 through IMP-05).
- [x] P1-A4-V 🔄 **[PR-1]** Validate batch 4: cumulative 80 files, full count verification.
- [x] P1-B 🔄 **[PR-1]** Create `Backlog/README.md` with consolidated index table (ID, title, release, link).

### Phase 2 - Implementation plan reduction

- [x] P2-A 🔄 **[PR-1]** Remove `User Story Details` and `Improvement Details` blocks from `implementation-plan.md`.
- [x] P2-B 🔄 **[PR-1]** Keep release plan sections and insert links to backlog index/items.

### Phase 3 - Link and routing propagation (dry-run + apply)

- [x] P3-A-DRY 🔄 **[PR-1]** Generate replacement list: scan all docs for `implementation-plan.md#us-*` / `#imp-*` anchors; output a table of (file, line, old link, new link) without modifying any file.
- [x] P3-A-REVIEW 🚧 **[PR-1]** Present replacement list for user review; confirm before applying.
- [x] P3-A-APPLY 🔄 **[PR-1]** Apply confirmed link replacements across all affected files.
- [x] P3-B 🔄 **[PR-1]** Propagate any required router/owner-module alignment caused by the new detail location.

### Phase 4 - Validation and closeout

- [x] P4-A 🔄 **[PR-1]** Run link/consistency checks and router/doc sync checks required by docs workflow.
- [x] P4-B 🚧 **[PR-1]** Re-evaluate PR partition thresholds against real diff; confirm with user if thresholds exceed original estimate.
- [x] P4-C 🔄 **[PR-1]** Prepare evidence summary (`How to test`, changed counts, residual gaps).

---

## Prompt Queue

### Prompt 1 — P0-A + P0-B: Discovery and extraction contract

**Steps:** P0-A, P0-B

**Objective:** Build the complete inventory of items to extract and assess backlink impact.

**Instructions:**

1. Open `docs/projects/veterinary-medical-records/04-delivery/implementation-plan.md`.
2. Scan for every `## US-*` and `## IMP-*` heading (expected: 75 US + 5 IMP = 80 items).
3. For each item, record:
   - ID (e.g., `US-01`, `IMP-04`)
   - Full title (text after the ID and dash)
   - Target filename using convention `us-XX-slug.md` or `imp-XX-slug.md` (slug derived from title, lowercase, hyphens, max ~50 chars)
   - Line range in source file (start line of `## US/IMP-*` heading to line before next `## US/IMP-*` or EOF)
   - Release assignment (which `## Release N` section lists this item)
4. Output the inventory as a Markdown table in a session note or temporary artifact for use by subsequent prompts.
5. Search all `.md` files under `docs/` for references to `implementation-plan.md#us-` or `implementation-plan.md#imp-` anchors. Record each match: file path, line number, anchor target.
6. Also search for plain references to `implementation-plan.md` (without anchor) that mention specific US/IMP IDs in surrounding context.
7. Produce a backlink impact summary: list of files that need link migration in P3-A.

**Validation:** Inventory has exactly 80 rows. Backlink list is complete.

---

### Prompt 2 — P1-A + P1-B: Batched backlog creation and item extraction

**Steps:** P1-A1, P1-A1-V, P1-A2, P1-A2-V, P1-A3, P1-A3-V, P1-A4, P1-A4-V, P1-B

**Objective:** Create the `Backlog/` folder, extract items in batches of 20 with per-batch validation, and create the index.

**Instructions:**

1. Create directory `docs/projects/veterinary-medical-records/04-delivery/Backlog/`.

**Batch 1 (P1-A1): items 1–20 (US-01 → US-20)**
2. For each item in this batch from the P0-A inventory:
   a. Create the target file (e.g., `Backlog/us-01-upload-document-api.md`).
   b. Copy the full content of the `## US-*` section from `implementation-plan.md` into the new file.
   c. Adjust the heading level: `## US-*` → `# US-*`.
   d. Preserve text as-is except heading level.
   e. Leave internal cross-links for P3-A.
3. **Checkpoint (P1-A1-V):** verify 20 files exist in `Backlog/`, each has a `# US-*` heading, and content matches the source line range ±0 lines.

**Batch 2 (P1-A2): items 21–40 (US-21 → US-40)**
4. Repeat step 2 for items 21–40.
5. **Checkpoint (P1-A2-V):** cumulative count = 40 files. Spot-check 2 random items: heading, content length, and release assignment match inventory.

**Batch 3 (P1-A3): items 41–60 (US-41 → US-60)**
6. Repeat step 2 for items 41–60.
7. **Checkpoint (P1-A3-V):** cumulative count = 60 files. Spot-check 2 random items.

**Batch 4 (P1-A4): items 61–80 (US-61 → US-75 + IMP-01 → IMP-05)**
8. Repeat step 2 for items 61–80. For IMP items, adjust heading `## IMP-*` → `# IMP-*`.
9. **Checkpoint (P1-A4-V):** cumulative count = 80 files. Full verification: list all files, confirm 75 `us-*.md` + 5 `imp-*.md`.

**Index (P1-B)**
10. Create `Backlog/README.md` with:
   a. Title: `# Backlog Index`
   b. Brief intro explaining this is the consolidated backlog for the project.
   c. A Markdown table with columns: `ID`, `Title`, `Release`, `File`.
   d. One row per item, sorted by ID (US first numerically, then IMP numerically).
   e. The `File` column links to the relative path of each item file.
   f. The `Release` column shows the release number(s) where the item is scheduled.
11. Final verify: 80 files + 1 README = 81 files in `Backlog/`.

**Commit recommendation:** commit 1 after this prompt.

---

### Prompt 3 — P2-A + P2-B: Implementation plan reduction

**Steps:** P2-A, P2-B

**Objective:** Remove detail blocks from `implementation-plan.md` and insert links to backlog items.

**Instructions:**

1. Open `implementation-plan.md`.
2. Identify the boundary between "release sequencing" content and "detail" content:
   - Release sequencing = everything from the start of the file through the last `## Release N` section (including the lists of US/IMP IDs within each release).
   - Detail content = all `## US-*` and `## IMP-*` sections that follow the release plan.
3. Remove all `## US-*` and `## IMP-*` detail sections (the entire block from each heading to the next, approximately lines 657–3181).
4. In each `## Release N` section, where US/IMP items are listed:
   - Convert each item reference to a link pointing to its `Backlog/` file.
   - Example: `US-01 — Upload document (API)` → `[US-01 — Upload document (API)](Backlog/us-01-upload-document-api.md)`
5. After the last release section, add a brief pointer:
   ```
   ---
   > For detailed User Story and Improvement specifications, see [Backlog Index](Backlog/README.md).
   ```
6. Verify: no `## US-*` or `## IMP-*` headings remain in the file. Release sections still list all items with working links.

**Commit recommendation:** commit 2 after this prompt.

---

### Prompt 4 — P3-A + P3-B: Link and routing propagation (dry-run + apply)

**Steps:** P3-A-DRY, P3-A-REVIEW, P3-A-APPLY, P3-B

**Objective:** Migrate legacy links using a dry-run/review/apply cycle, then propagate routing/module alignment.

**Instructions:**

**Dry-run (P3-A-DRY):**
1. Scan all `.md` files under `docs/` for references matching `implementation-plan.md#us-*` or `implementation-plan.md#imp-*`.
2. For each match, compute the replacement link using the P0-A inventory (ID → target filename mapping).
3. Also scan for plain references to `implementation-plan.md` (without anchor) that mention specific US/IMP IDs in surrounding context.
4. For context-only references, classify:
   - **story-detail context** → replacement points to `Backlog/` file or index.
   - **release-sequencing context** → keep `implementation-plan.md` link unchanged.
5. Output a replacement table:
   | File | Line | Old link/reference | New link/reference | Action |
   |------|------|--------------------|--------------------|--------|
   Known files to include:
   - `docs/projects/veterinary-medical-records/04-delivery/plans/PLAN_2026-03-07_PROCESSING-HISTORY-UI.md` (line 7: `#us-78`)
   - `docs/README.md` (lines 69, 114)
   - `docs/projects/veterinary-medical-records/02-tech/backend-implementation.md` (line 392)
   - `docs/projects/veterinary-medical-records/02-tech/technical-design.md` (lines 317, 561, 628)
   - `docs/projects/veterinary-medical-records/03-ops/plan-execution-protocol.md` (line 535 — §18 "How to Add a New User Story")
   - `docs/projects/veterinary-medical-records/99-archive/cto-review-verdict.md` (line 121 — archive)
   - Any additional files found in P0-B.

**Review (P3-A-REVIEW) — hard gate:**
6. Present the replacement table to the user for confirmation.
7. User may approve all, reject specific rows, or request modifications.

**Apply (P3-A-APPLY):**
8. Apply only the confirmed replacements.
9. For `plan-execution-protocol.md` §18 ("How to Add a New User Story"): update to reflect the new structure — new stories should be added as `Backlog/` files AND registered in `implementation-plan.md` release sections.
10. Verify: re-run the scan from step 1 — zero matches expected (excluding this plan itself).

**Router propagation (P3-B):**
11. Check if any router/owner-module files under `docs/agent_router/` reference `implementation-plan.md` story anchors and update if needed.
12. Run `python scripts/docs/generate-router-files.py --check` to verify router parity after any protocol changes.

**Commit recommendations:** commit 3 (links) after step 10, then commit 4 (router) after step 12.

---

### Prompt 5 — P4-A + P4-B + P4-C: Validation and closeout

**Steps:** P4-A, P4-B, P4-C

**Objective:** Run all validation checks, re-evaluate PR sizing, and prepare evidence.

**Instructions:**

1. Run all validation scripts:
   - `python scripts/docs/generate-router-files.py --check`
   - `python scripts/docs/check_doc_test_sync.py`
   - `python scripts/docs/check_doc_router_parity.py`
   - `python scripts/docs/check_router_directionality.py`
   - `npm run docs:lint`
2. Fix any failures that are directly caused by this plan's changes. Pre-existing failures should be reported but not fixed.
3. **P4-B (hard gate):** Re-evaluate PR partition thresholds:
   - Run `git diff --stat origin/main` and report: changed files count, total changed lines.
   - Compare against the thresholds (>400 lines or >15 files).
   - If both are within thresholds (or the exceedance matches the original estimate and Option A rationale holds), confirm Option A.
   - If thresholds are significantly exceeded beyond the original estimate, present Option A / Option B to the user for re-confirmation.
4. **P4-C:** Prepare evidence summary:
   - Total files created/modified/deleted.
   - Backlog items extracted (target: 80).
   - Validation script results (pass/fail per script).
   - Residual gaps (links not migrated, if any, with rationale).
   - `How to test` section for PR description.

**Commit recommendation:** commit 5 (normalization) after validation fixes.

## Active Prompt

Pending explicit user start signal for execution.

---

## Acceptance criteria

1. Every `US-*` and `IMP-*` section from source exists as exactly one file in `04-delivery/Backlog/`.
2. `implementation-plan.md` no longer contains detailed US/IMP bodies and keeps release sequencing authority.
3. `Backlog/README.md` exists and links to all extracted items.
4. Legacy links to old story/improvement anchors are migrated or explicitly reported as gaps.
5. Docs validation checks pass without unresolved blocking parity/sync issues.

## Risks and limitations

- Large link-migration surface across historical plan files may require staged cleanup.
- Router parity requirements can force additional owner-module updates beyond delivery docs.
- If scope expands into rule changes, extra DOC_UPDATES propagation may be required.
- **Mitigated by batching:** extraction errors caught at batch boundaries rather than after all 80 files, reducing rework scope.
- **Mitigated by dry-run:** link migration errors caught before file modification, avoiding partial/inconsistent states.

## Execution evidence

- Diff vs `origin/main`: 102 changed files, 3302 insertions, 2956 deletions.
- File status counts: 82 added, 20 modified, 0 deleted.
- Backlog extraction result: 80 backlog item files plus `Backlog/README.md` index.
- Validation results:
   - `python scripts/docs/generate-router-files.py --check` ✅
   - `python scripts/docs/check_doc_test_sync.py --base-ref main` ✅
   - `python scripts/docs/check_doc_router_parity.py --base-ref main` ✅
   - `python scripts/docs/check_router_directionality.py --base-ref main` ✅
   - `scripts/ci/test-L2.ps1 -BaseRef main` ✅
   - `scripts/ci/test-L3.ps1 -BaseRef main` ✅
   - `npm run docs:lint` ⚠️ blocked by local missing `markdownlint-cli2`; fallback `npx markdownlint-cli2 ...` reports pre-existing lint failures in historical files under `docs/projects/veterinary-medical-records/04-delivery/plans/completed/`.
- Residual link gaps: none found by the P3 re-scan; the only real legacy story anchor replacement was migrated.
- PR partition decision: keep Option A (single PR). The diff is larger than the numeric thresholds, but that exceedance matches the approved docs-only extraction/relink scope and does not introduce mixed runtime risk axes.

## How to test

- `git diff --name-status`
- `python scripts/docs/generate-router-files.py --check`
- `python scripts/docs/check_doc_test_sync.py`
- `python scripts/docs/check_doc_router_parity.py`
- `python scripts/docs/check_router_directionality.py`
- `npm run docs:lint`
