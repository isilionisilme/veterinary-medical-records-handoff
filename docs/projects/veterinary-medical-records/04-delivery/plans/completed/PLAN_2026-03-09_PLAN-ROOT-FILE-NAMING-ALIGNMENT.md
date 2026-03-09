# Plan: Plan Root File Naming Alignment (IMP-05)

> **Operational rules:** See [plan-execution-protocol.md](../../03-ops/plan-execution-protocol.md)

**Branch:** `codex/veterinary-medical-records/chore/plan-root-file-naming-alignment`
**PR:** [#240](https://github.com/isilionisilme/veterinary-medical-records/pull/240)
**User Story:** [IMP-05](../Backlog/imp-05-plan-root-file-naming-alignment.md)
**Prerequisite:** None (IMP-01 dependency is soft — different sections of the same canonical docs)
**Worktree:** `d:/Git/veterinary-medical-records`
**CI Mode:** `1. Strict step gate`
**Automation Mode:** `Supervisado`

## Context

The project uses `PLAN_MASTER.md` as the canonical root file name inside every plan folder. This creates poor discoverability because all root files share the same name.

Current state after audit:
- **Canonical docs:** `plan-creation.md` (4 refs) and `plan-execution-protocol.md` (6 refs) still mandate `PLAN_MASTER.md`.
- **Active plans (4):** All already use the new folder-matching convention (`PLAN_<date>_<slug>.md`). No migration needed.
- **Completed plans:** 1 legacy plan still uses `PLAN_MASTER.md` (`PLAN_2026-03-08_SPLIT-IMPLEMENTATION-PLAN-BACKLOG/PLAN_MASTER.md`).
- **Router files (auto-generated):** 4 refs derived from canonical sources — will be regenerated.

## Objective

Replace the `PLAN_MASTER.md` convention with a deterministic root file name matching the plan folder name, update all canonical operational docs, add backward-read compatibility for legacy plans, and migrate the one remaining legacy root.

## Scope Boundary

| In scope | Out of scope |
|----------|--------------|
| Update naming rule in `plan-creation.md` | Rewrite completed plan body content |
| Update all `PLAN_MASTER.md` refs in `plan-execution-protocol.md` | Backend/frontend product changes |
| Add backward-read compatibility language for legacy plans | Unrelated plan schema/section refactors |
| Migrate the 1 remaining legacy `PLAN_MASTER.md` in completed plans | Active plan content changes |
| Regenerate router files from canonical sources | IMP-01 commit policy changes |
| Update backlog item status | |

## Commit-Point Hard Gate (Plan-Level Rule)

## Commit Authorization Rule (Plan-Level Hard Rule)

No execution agent may stage, commit, amend, or push changes for this plan without explicit user confirmation in the current chat.

Mandatory behavior:
1. When a step reaches a suggested commit point, the agent may prepare the pending scope and report the proposed commit message.
2. The agent MUST stop and ask for explicit confirmation before any `git add`, `git commit`, `git commit --amend`, or `git push`.
3. This rule survives handoff: any successor agent working on this plan MUST follow it unless the user explicitly overrides it in chat.
4. If this rule conflicts with any default automation behavior in shared protocol docs, this plan-level rule takes precedence for this plan.

When a step includes a **🔀 Suggested commit** block, the execution agent MUST:

1. Finish the step implementation and report the exact commit scope and suggested message.
2. **STOP and wait for explicit user confirmation** before staging or committing.
3. After user confirmation, stage and commit with the suggested message.
4. Run `scripts/ci/test-L2.ps1 -BaseRef main`.
5. If L2 fails: diagnose and fix until L2 is green.
6. **STOP and wait for explicit user instructions** before proceeding to the next step.

This rule overrides auto-chain behavior for all steps in this plan.

## Step Tracking Rule (Plan-Level Rule)

The execution agent MUST mark each step as completed (`[x]`) in this plan file **immediately** after finishing it — before moving to the next step or stopping. Use the extended state markers defined in the execution protocol (⏳ on start, `[x]` + ✅ SHA on completion).

## Execution Status

- [x] S1 — Update `plan-creation.md`: replace `PLAN_MASTER.md` convention with folder-matching root file name rule, add backward-read compatibility note for legacy plans — ✅ `96549997`
- [x] S2 — Update `plan-execution-protocol.md`: replace all `PLAN_MASTER.md` references with the new convention and add legacy compatibility language — ✅ `96549997`
- [x] S3 — Migrate legacy completed plan: rename `completed/PLAN_2026-03-08_SPLIT-IMPLEMENTATION-PLAN-BACKLOG/PLAN_MASTER.md` → `PLAN_2026-03-08_SPLIT-IMPLEMENTATION-PLAN-BACKLOG.md` — ✅ `96549997`
- [x] S4 — Regenerate router files: run `python scripts/docs/generate-router-files.py` and verify derived files no longer reference `PLAN_MASTER.md` — ✅ `0ae4ba8c`
  - 🔀 Suggested commit after S4: `chore(docs): replace PLAN_MASTER naming convention with folder-matching root file names`
  - Scope: `plan-creation.md`, `plan-execution-protocol.md`, renamed legacy plan, regenerated router files
   - Before any staging or commit: ask the user for explicit confirmation.
  - Run L2, fix until green, STOP and wait for user.
- [x] S5 — Validation: grep confirms zero `PLAN_MASTER` references in canonical and router docs (excluding the IMP-05 backlog item itself and this plan); verify plan discovery patterns work for both new-named and legacy roots — ✅ `no-commit (validation only)`
- [x] S6 — Update backlog item status to Implemented; update `implementation-plan.md` status — ✅ `3f7307f2`
  - 🔀 Suggested commit after S6: `chore(docs): mark IMP-05 as Implemented`
  - Scope: `imp-05-plan-root-file-naming-alignment.md`, `implementation-plan.md`
   - Before any staging or commit: ask the user for explicit confirmation.
  - Run L2, fix until green, STOP and wait for user.

## Prompt Queue

### S1 — Update plan-creation.md

Open `docs/projects/veterinary-medical-records/03-ops/plan-creation.md` and apply the following edits:

1. In **§ Naming and location**, replace:
   ```
   - Canonical root file inside the plan folder: `PLAN_MASTER.md`
   ```
   with:
   ```
   - Canonical root file inside the plan folder: `PLAN_<YYYY-MM-DD>_<SLUG>.md` (must match the folder name)
   - Legacy compatibility: plans that still use `PLAN_MASTER.md` remain readable during the transition period. New plans MUST use the folder-matching name.
   ```

2. In **§ Required plan template**, step 2, replace:
   ```
   2. Create root file: `plans/<plan-folder>/PLAN_MASTER.md`.
   ```
   with:
   ```
   2. Create root file: `plans/<plan-folder>/PLAN_<YYYY-MM-DD>_<SLUG>.md` (matching the folder name).
   ```

3. In **§ PR Roadmap** guidance, replace the two references to `PLAN_MASTER.md`:
   - `The section lives in `PLAN_MASTER.md`.` → `The section lives in the plan root file.`
   - `If a PR requires implementation detail that would bloat `PLAN_MASTER.md`` → `If a PR requires implementation detail that would bloat the plan root file`

4. Verify no other `PLAN_MASTER` references remain in the file.

### S2 — Update plan-execution-protocol.md

Open `docs/projects/veterinary-medical-records/03-ops/plan-execution-protocol.md` and apply the following edits:

1. **File Structure diagram (~line 37)** — Replace:
   ```
   │   ├── PLAN_MASTER.md              ← Active plan source of truth
   ```
   with:
   ```
   │   ├── PLAN_<date>_<slug>.md       ← Active plan source of truth (matches folder name)
   ```

2. **Active plan file paragraph (~line 43)** — Replace:
   ```
   **Active plan file:** For new plans, the agent attaches `plans/<plan-folder>/PLAN_MASTER.md` when executing a continuation-intent request
   ```
   with:
   ```
   **Active plan file:** For new plans, the agent attaches `plans/<plan-folder>/PLAN_<date>_<slug>.md` (matching the folder name) when executing a continuation-intent request
   ```
   Keep the legacy line: `For legacy plans, `PLAN_*.md` remains accepted during transition.`

3. **Worktree selection (~line 201)** — Replace:
   ```
   (`PLAN_MASTER.md` for new plans; `PLAN_*.md` for legacy plans)
   ```
   with:
   ```
   (`PLAN_<date>_<slug>.md` for new plans; `PLAN_MASTER.md` or `PLAN_*.md` for legacy plans)
   ```

4. **CI mode (~line 214)** — Same replacement as item 3.

5. **Completed plan archival (~line 467)** — Replace:
   ```
   Keep all file names unchanged (including `PLAN_MASTER.md` and `PR-X.md`) to preserve links.
   ```
   with:
   ```
   Keep all file names unchanged (including the plan root file and `PR-X.md`) to preserve links.
   ```

6. **Checkbox source of truth (~line 497)** — Replace:
   ```
   (`PLAN_MASTER.md` for new plans; `PLAN_*.md` for legacy plans)
   ```
   with:
   ```
   (`PLAN_<date>_<slug>.md` for new plans; `PLAN_MASTER.md` or `PLAN_*.md` for legacy plans)
   ```

7. Verify no other `PLAN_MASTER` references remain in the file.

### S3 — Migrate legacy plan

Run:
```powershell
git mv "docs/projects/veterinary-medical-records/04-delivery/plans/completed/PLAN_2026-03-08_SPLIT-IMPLEMENTATION-PLAN-BACKLOG/PLAN_MASTER.md" "docs/projects/veterinary-medical-records/04-delivery/plans/completed/PLAN_2026-03-08_SPLIT-IMPLEMENTATION-PLAN-BACKLOG/PLAN_2026-03-08_SPLIT-IMPLEMENTATION-PLAN-BACKLOG.md"
```

No content changes to the file.

### S4 — Regenerate router files

Run:
```powershell
python scripts/docs/generate-router-files.py
```

Then verify:
```powershell
Select-String -Path "docs/agent_router/**/*.md" -Pattern "PLAN_MASTER" -Recurse
```
Expected: zero matches.

🔀 **Suggested commit** (S1–S4 combined):
- Message: `chore(docs): replace PLAN_MASTER naming convention with folder-matching root file names`
- Scope: `plan-creation.md`, `plan-execution-protocol.md`, renamed legacy plan, regenerated router files.
- Before any staging or commit: ask the user for explicit confirmation.
- After commit: run `scripts/ci/test-L2.ps1 -BaseRef main`, fix until green, STOP and wait for user instructions.

### S5 — Validation

Run:
```powershell
Select-String -Path "docs/" -Pattern "PLAN_MASTER" -Recurse | Where-Object { $_.Path -notmatch "imp-05|PLAN_2026-03-09_PLAN-ROOT-FILE-NAMING" }
```
Expected: zero matches.

Scan active plan roots to confirm they resolve (they all already use the new convention — this is a no-op confirmation):
```powershell
Get-ChildItem "docs/projects/veterinary-medical-records/04-delivery/plans/PLAN_*.md"
```
Expected: 4 active plans + this plan file.

### S6 — Backlog and implementation-plan update

1. In `docs/projects/veterinary-medical-records/04-delivery/Backlog/imp-05-plan-root-file-naming-alignment.md`, replace:
   ```
   **Status:** Planned
   ```
   with:
   ```
   **Status:** Implemented
   ```

2. In `docs/projects/veterinary-medical-records/04-delivery/implementation-plan.md`, on the IMP-05 line, replace `(Planned)` with `(Implemented)`.

🔀 **Suggested commit**:
- Message: `chore(docs): mark IMP-05 as Implemented`
- Scope: `imp-05-plan-root-file-naming-alignment.md`, `implementation-plan.md`.
- Before any staging or commit: ask the user for explicit confirmation.
- After commit: run `scripts/ci/test-L2.ps1 -BaseRef main`, fix until green, STOP and wait for user instructions.

## Active Prompt

—

## Acceptance Criteria

1. Canonical docs (`plan-creation.md`, `plan-execution-protocol.md`) define the new root-file naming rule explicitly.
2. Active-plan resolution language supports the new file name and can still read legacy roots during transition.
3. All active plans use folder-matching root file names (already true — verified in audit).
4. No newly created plan uses `PLAN_MASTER.md`.
5. Global/index references and examples use the new naming convention.
6. Router files are regenerated and consistent with canonical sources.

## Risks and Limitations

| Risk | Mitigation |
|------|------------|
| Tooling/scripts fail to find plans after rename | Backward-read compatibility language preserved during transition |
| Partial migration leaves mixed naming | Only 1 legacy file to migrate; all active plans already comply |
| Accidental edits to completed plans | Migration limited to renaming the root file — no content change |

## PR Roadmap

### PR partition gate assessment

- **Projected scope:** ~6 files changed, ~40 changed lines (canonical docs updates + 1 rename + router regen).
- **Semantic axes:** docs-only; no backend/frontend/test changes.
- **Size guardrails:** well under 400 lines and 15 files.
- **Decision:** Option A — single PR. Low risk, cohesive docs-only change.

### Single PR

All steps (S1–S6) ship in one PR. No dependencies or ordering constraints beyond the natural sequence.

## Documentation Task

This plan IS the documentation update — it modifies canonical operational documentation directly. No separate wiki/doc task needed (`no-doc-needed`: the plan itself updates the canonical docs).

## How to Test

1. Search the repository for `PLAN_MASTER` — should appear only in the IMP-05 backlog item (historical reference) and this archived plan.
2. Verify the 4 active plans still resolve correctly (their root files already use folder-matching names).
3. Verify `plan-creation.md` and `plan-execution-protocol.md` reference the new convention with backward-read compatibility.
4. Verify router files are consistent with canonical sources (`python scripts/docs/generate-router-files.py --check`).
