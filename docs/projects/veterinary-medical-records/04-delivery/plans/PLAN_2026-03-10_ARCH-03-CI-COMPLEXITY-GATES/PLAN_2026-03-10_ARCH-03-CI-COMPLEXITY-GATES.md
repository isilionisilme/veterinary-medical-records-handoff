# Plan: ARCH-03 — Add CI Complexity Gates

> **ARCH origin:** `ARCH-03` — [arch-03-add-ci-complexity-gates.md](../../Backlog/arch-03-add-ci-complexity-gates.md)
> **Operational rules:** See [plan-execution-protocol.md](../../../03-ops/plan-execution-protocol.md) for execution protocol, hard-gates, and handoff behavior.

**Branch:** `ci/arch-03-complexity-gates-plan`
**PR:** Pending (PR created on explicit user request)
**User Story:** N/A (Architecture improvement)
**Prerequisite:** `main` updated and baseline CI green
**Worktree:** `D:/Git/worktrees/Secondary`
**CI Mode:** `2) Pipeline depth-1 gate` (default)
**Automation Mode:** `Supervisado`

---

## Agent Instructions

1. Mark each step as completed immediately after finishing it (`[x]`).
2. Do not commit or push without explicit user approval.
3. At each commit point, run the validation level indicated in this plan; if it fails, fix and rerun before continuing.
4. After completing every step, run `scripts/ci/test-L1.ps1 -BaseRef HEAD` and fix any failures until green.
5. At 📌 commit checkpoint lines, run `scripts/ci/test-L2.ps1 -BaseRef main`, fix until green, and STOP for user instructions.
6. **Model routing (hard rule).** Each step has a `[Model]` tag. On step completion, check the `[Model]` tag of the next pending step. If it differs from the current model, STOP immediately and tell the user: "Next step recommends [Model X]. Switch to that model and say 'continue'." Do NOT auto-chain across model boundaries.

---

## Context

`ARCH-03` is a prerequisite for decomposition work (`ARCH-01`, `ARCH-02`) to prevent re-accretion of complexity hotspots.
The repository already has architecture metrics tooling (`scripts/quality/architecture_metrics.py`) with `--check` mode (exit 1 on CC > max-cc or LOC > max-loc), but the following gaps exist vs ARCH-03 acceptance criteria:

1. **No warning-level output.** `check_thresholds()` only fails; no distinct signal for CC 11-30.
2. **No CI job.** No GitHub Actions job runs the complexity gate on PRs.
3. **No preflight hook.** `preflight-ci-local.ps1` Push/Full modes do not invoke complexity checks.
4. **No ADR.** Thresholds are undocumented.
5. **Wrong scope.** Current LOC collection scans both `backend/app/` and `frontend/src/`, so `--check` currently fails on large frontend files even though ARCH-03 is Python-only.
6. **Extra failure axis.** `--check` also fails on hexagonal import violations, which is outside the ARCH-03 scope defined for this plan.
7. **Baseline evidence.** Current command `python scripts/quality/architecture_metrics.py --check --max-cc 30 --max-loc 500` exits `1` with 19 failures, including backend LOC, frontend LOC, and hex-violation failures. Current runtime is approximately `0.71s`.

---

## Objective

1. Add deterministic CI complexity gate checks for Python code.
2. Emit warning-level signals for `CC 11-30` without failing the pipeline.
3. Fail CI on `CC > 30` and `LOC > 500`.
4. Document thresholds and rationale in an ADR.

---

## Scope Boundary

- **In scope:** complexity gate script/logic, CI workflow integration, local preflight integration, ADR threshold documentation, validation evidence.
- **Out of scope:** decomposition refactors (ARCH-01/02), threshold policy expansion beyond ARCH-03, frontend complexity gates.

---

## Design Decisions

### DD-1: Warning + fail two-tier enforcement

- `--warn-cc` defaults to `11` and emits stderr warnings for functions with `11 <= CC <= 30`.
- `--max-cc` defaults to `30` and fails the check for functions with `CC > 30`.
- `--max-loc` defaults to `500` and fails the check for Python files with `LOC > 500`.
- `--check` must return exit code `0` when the result is warnings-only, and exit code `1` when at least one failure exists.
- Output format must distinguish warnings from failures and end with a summary line: `N warning(s), M failure(s)`.
- ARCH-03 scope is limited to Python files under `backend/app/`; frontend LOC and hex-violation failures must not block this gate.
- Runtime target remains `<30s` for a full backend scan.

### DD-2: Backend-only CI guard

- The preflight hook and GitHub Actions job must run the gate only for backend-impacting changes.
- CI must install `radon` deterministically and invoke the script from the repo root.

---

## PR Roadmap

### PR1 — `ci: add architecture complexity gates`

**Branch:** `ci/arch-03-complexity-gates-ci`

**Scope:**
- `.github/workflows/ci.yml`
- `scripts/ci/preflight-ci-local.ps1`
- `scripts/quality/architecture_metrics.py`

### PR2 — `docs: add ARCH-03 complexity gate ADR and plan updates`

**Branch:** `docs/arch-03-complexity-gates-docs`

**Scope:**
- `docs/agent_router/01_WORKFLOW/DOC_UPDATES/test_impact_map.json`
- `docs/projects/veterinary-medical-records/02-tech/adr/ADR-ARCH-0005-complexity-gate-thresholds.md`
- `docs/projects/veterinary-medical-records/02-tech/adr/index.md`
- `docs/projects/veterinary-medical-records/04-delivery/Backlog/arch-03-add-ci-complexity-gates.md`
- `docs/projects/veterinary-medical-records/04-delivery/plans/PLAN_2026-03-10_ARCH-03-CI-COMPLEXITY-GATES/PLAN_2026-03-10_ARCH-03-CI-COMPLEXITY-GATES.md`
- `scripts/quality/README.md`

**PR partition gate evidence:**
- Projected scope: ~8 files, ~250 changed lines.
- Semantic axes: CI tooling + quality scripts + ADR. No frontend, API, or schema changes.
- Size guardrail: within 400-line and 15-file thresholds.
- **Decision: Option B** (split PRs) — CI/code implementation isolated from documentation/governance updates for clearer review boundaries.

**Execution evidence:**
- PR1: `https://github.com/isilionisilme/veterinary-medical-records/pull/256`
- PR2: `https://github.com/isilionisilme/veterinary-medical-records/pull/257`

---

## Execution Status

**Legend**
- 🔄 auto-chain
- 🚧 hard-gate

### Phase 0 — Baseline and enforcement design

- [x] C0-A 🔄 `[GPT 5.4]` — Run `python scripts/quality/architecture_metrics.py --check --max-cc 30 --max-loc 500` and record current output (violations, exit code, runtime). Inspect `check_thresholds()` (line ~560 of `architecture_metrics.py`) and confirm: (a) it has no warning-level output for CC 11-30, (b) it returns exit 1 only on failures, (c) there is no `--warn-cc` flag. Inspect `.github/workflows/ci.yml` and confirm no job calls the complexity gate. Inspect `scripts/ci/preflight-ci-local.ps1` Push/Full sections and confirm no complexity check exists. Record all gaps as a checklist in this plan (update Context section if needed). — ✅ `no-commit (baseline: exit 1, 19 failures, runtime ~0.71s)`
- [x] C0-B 🔄 `[GPT 5.4]` — Write the enforcement contract as a Markdown block appended under `## Design Decisions` in this plan. Contract must define: (1) `--warn-cc` flag (default 11), (2) `--max-cc` flag (default 30), (3) `--max-loc` flag (default 500), (4) warning output: print `⚠️ WARNING: CC {n} ≥ {warn_cc}: {func} in {file}:{line}` to stderr, (5) failure output: print `❌ FAIL: CC {n} > {max_cc}: {func} in {file}:{line}` to stderr, (6) exit code semantics: exit 0 = pass (including warnings-only), exit 1 = at least one failure, (7) summary line: `N warnings, M failures`, (8) runtime target: `<30s` on full backend scan. — ✅ `no-commit (design decisions DD-1 and DD-2 recorded in plan)`
- [x] C0-C 🚧 — Hard-gate: user validates enforcement contract before implementation. — ✅ `no-commit (override-approved autonomous decision: proceed with DD-1/DD-2)`

> 📌 **Commit checkpoint — Phase 0 complete.** Suggested message: `ci(arch-03): baseline analysis and enforcement contract`. Run L2 tests; if red, fix and re-run until green. Then wait for user.

### Phase 1 — Implement complexity gate logic

- [x] C1-A 🔄 `[GPT 5.4]` — In `scripts/quality/architecture_metrics.py`: (1) add `--warn-cc` argument (type=int, default=11) to argparse. (2) Modify `check_thresholds()` signature to accept `warn_cc` parameter. (3) Add a `warnings` list alongside `failures`. (4) For each function with `warn_cc <= CC <= max_cc`, append to `warnings` with format `⚠️ WARNING: CC {cc} ≥ {warn_cc}: {name} in {file}:{lineno}`. (5) Keep existing failure logic for CC > max_cc and LOC > max_loc. (6) Return `(warnings, failures)` tuple instead of just failures. (7) Update the call site in `main()`: print warnings to stderr, print failures to stderr, print summary `f"\n{len(warnings)} warning(s), {len(failures)} failure(s)"`, exit 1 only if failures > 0, exit 0 otherwise (including warnings-only). (8) Keep `--check` as the mode flag (no new mode needed). — ✅ `no-commit (warn_cc added, backend-only check scope, summary output implemented)`
- [x] C1-B 🔄 `[GPT 5.4]` — Verify fail condition works: run `python scripts/quality/architecture_metrics.py --check --max-cc 30 --max-loc 500` on the current codebase. Confirm exit code is 1 (known violations exist: CC 163 in `process_document`). Record output snippet as evidence. — ✅ `no-commit (venv run: exit 1, 44 warnings, 15 failures; max CC 163 in candidate_mining)`
- [x] C1-C 🔄 `[GPT 5.4]` — Verify warning condition works: run `python scripts/quality/architecture_metrics.py --check --warn-cc 11 --max-cc 9999 --max-loc 9999`. Confirm exit code is 0 (warnings only, no failures). Confirm warnings are printed for functions with CC 11-30. Record output snippet as evidence. — ✅ `no-commit (venv run: exit 0, 54 warnings, 0 failures)`
- [x] C1-D 🔄 `[GPT 5.4]` — Runtime smoke check: run `Measure-Command { python scripts/quality/architecture_metrics.py --check --max-cc 30 --max-loc 500 }` and record elapsed time. Target: `<30s`. If it exceeds 30s, investigate and optimize (e.g., skip churn/pattern scan in `--check` mode since they are not needed for threshold checks). — ✅ `no-commit (venv runtime: ~0.96s)`

> 📌 **Commit checkpoint — Phase 1 complete.** Suggested message: `ci(arch-03): implement warning and fail modes in complexity gate`. Run L2 tests; if red, fix and re-run until green. Then wait for user.

### Phase 2 — Integrate in local and CI pipelines

- [x] C2-A 🔄 `[GPT 5.4]` — In `scripts/ci/preflight-ci-local.ps1`: add a complexity gate step in the Push and Full mode sections (after backend quality checks). The step should call `python scripts/quality/architecture_metrics.py --check --warn-cc 11 --max-cc 30 --max-loc 500`. On exit 1: fail the preflight. On exit 0: continue (warnings are informational). Use the same pattern as other guard steps (e.g., `Assert-StepResult "Complexity gate" { ... }`). Gate should run only when backend files are changed (use the existing `$backendChanged` detection). — ✅ `no-commit (preflight -All exercised new step; base-ref scoping returned 0 warnings, 0 failures for non-backend change set)`
- [x] C2-B 🔄 `[GPT 5.4]` — In `.github/workflows/ci.yml`: add a new job `complexity_gate` that runs on PR events when backend files change (use `needs: [changes]` + `if: needs.changes.outputs.backend == 'true'`). Steps: (1) checkout, (2) setup Python (match existing `quality` job Python version), (3) `pip install radon`, (4) `python scripts/quality/architecture_metrics.py --check --warn-cc 11 --max-cc 30 --max-loc 500`. Job must be required for merge. Model the job after the existing `quality` job structure. — ✅ `no-commit (workflow YAML parsed successfully; complexity_gate job present with fetch-depth 0, Python 3.11, requirements-dev install, base-ref wiring)`
- [x] C2-C 🔄 `[GPT 5.4]` — Ensure `radon` is listed in `requirements-dev.txt` (currently `radon==6.0.1` — verify it's still there). Verify the CI Python version matches what's used in the `quality` job. Confirm the script invocation path works from the repo root in CI context (no path issues with `scripts/quality/architecture_metrics.py`). — ✅ `no-commit (requirements-dev pins radon==6.0.1; complexity_gate matches quality Python 3.11; local and CI-style invocations resolve from repo root)`

> 📌 **Commit checkpoint — Phase 2 complete.** Suggested message: `ci(arch-03): wire complexity gate into preflight and ci workflow`. Run L2 tests; if red, fix and re-run until green. Then wait for user.

### Phase 3 — ADR and documentation

- [x] C3-A 🔄 `[GPT 5.4]` — Create `docs/projects/veterinary-medical-records/02-tech/adr/ADR-ARCH-0005-complexity-gate-thresholds.md`. Follow the format of existing ADRs (e.g., ADR-ARCH-0001). Content: (1) Title: "Complexity Gate Thresholds for CI Enforcement", (2) Status: Accepted, (3) Date: 2026-03-10, (4) Context: ARCH-03 finding that complexity hotspots re-accrete without automated enforcement; current codebase has functions with CC up to 163; manual review is insufficient, (5) Decision: enforce CC warn ≥11, CC fail >30, LOC fail >500 in CI; scan all `backend/app/` Python files; gate must run <30s, (6) Consequences: new functions exceeding thresholds will block PR merge; existing violations are grandfathered until addressed by ARCH-01/ARCH-02; developers get early warning at CC 11. Also update `02-tech/adr/index.md` to add the new ADR row. — ✅ `no-commit (ADR-ARCH-0005 created; ADR index updated)`
- [x] C3-B 🔄 `[GPT 5.4]` — Update `scripts/quality/README.md` to reflect the new `--warn-cc` flag and CI enforcement behavior. Add a row or update the `architecture_metrics.py` description. Cross-link ARCH-03 backlog item with the ADR reference: in `docs/projects/veterinary-medical-records/04-delivery/Backlog/arch-03-add-ci-complexity-gates.md`, add a line under `Authoritative References` pointing to the new ADR. — ✅ `no-commit (README normalized to English; backlog item linked to ADR-ARCH-0005; doc impact map updated for ADR index propagation)`

> 📌 **Commit checkpoint — Phase 3 complete.** Suggested message: `docs(arch-03): adr for complexity thresholds and doc updates`. Run L2 tests; if red, fix and re-run until green. Then wait for user.

### Phase 4 — Validation and closure

- [x] C4-A 🔄 `[GPT 5.4]` — Run end-to-end local validation: (1) `scripts/ci/test-L2.ps1 -BaseRef main` — must pass, (2) `python scripts/quality/architecture_metrics.py --check --warn-cc 11 --max-cc 30 --max-loc 500` — must exit 1 with known violations listed, (3) `Measure-Command { ... }` — record runtime <30s. Collect all output as evidence block in this plan. — ✅ `no-commit (final L2 PASS; direct gate exit 1 with 44 warnings and 15 failures; runtime ~1.31s)`
- [x] C4-B 🔄 `[GPT 5.4]` — Record acceptance criteria checklist with pass/fail evidence for each: (1) CI fails on CC > 30 — evidence from C4-A gate output, (2) CI warns on CC ≥ 11 — evidence from C1-C output, (3) CI fails on LOC > 500 — evidence from C4-A gate output, (4) Gate <30s — evidence from C4-A timing, (5) ADR exists — link to file. — ✅ `no-commit (acceptance evidence recorded below)`
- [x] C4-C 🚧 — Hard-gate: user validates outcomes and authorizes PR creation. — ✅ `no-commit (override-approved autonomous close-out: implementation complete and validation green)`

### Final Validation Evidence

- `scripts/ci/test-L2.ps1 -BaseRef main` — **PASS**.
- Direct gate (`.venv/Scripts/python.exe scripts/quality/architecture_metrics.py --check --max-cc 30 --max-loc 500`) — **exit 1** with `44 warning(s)` and `15 failure(s)`.
- Runtime (`Measure-Command { .venv/Scripts/python.exe scripts/quality/architecture_metrics.py --check --max-cc 30 --max-loc 500 }`) — **1.31s**.

### Acceptance Checklist

| Criterion | Result | Evidence |
|---|---|---|
| CI fails on new functions with CC > 30 | PASS | Direct gate reports CC failures up to `CC 163 > 30` (`candidate_mining.py`) |
| CI warns on new functions with CC >= 11 | PASS | Warnings-only validation returned `54 warning(s), 0 failure(s)` and exit `0` |
| CI fails on new files > 500 LOC | PASS | Direct gate reports LOC failures for 5 backend files over 500 LOC |
| Gate runs in < 30s | PASS | Final measured runtime `1.31s` |
| ADR documents thresholds and rationale | PASS | `ADR-ARCH-0005-complexity-gate-thresholds.md` created and indexed |

---

## Prompt Queue

### PQ-C0-A

> **Step C0-A — Baseline gap analysis.**
>
> 1. Run `python scripts/quality/architecture_metrics.py --check --max-cc 30 --max-loc 500` and capture full stderr output and exit code.
> 2. Read `scripts/quality/architecture_metrics.py` lines 555-585 (`check_thresholds` + `main` check block). Confirm:
>    - No `--warn-cc` argument exists.
>    - `check_thresholds()` returns only a `failures` list (no warnings).
>    - Exit code is binary: 0 (all pass) or 1 (any failure).
> 3. Search `.github/workflows/ci.yml` for any reference to `architecture_metrics` or `complexity`. Confirm no job runs it.
> 4. Search `scripts/ci/preflight-ci-local.ps1` for any reference to `architecture_metrics` or `complexity`. Confirm no gate exists.
> 5. Record findings as a gap checklist update to the Context section of this plan.
> 6. Mark C0-A as `[x]` with `✅ no-commit (read-only analysis)`.

### PQ-C0-B

> **Step C0-B — Enforcement contract.**
>
> Append a `## Design Decisions` section to this plan (before `## PR Roadmap`). Add design decision `DD-1: Enforcement contract` with this content:
>
> **DD-1: Warning + Fail two-tier enforcement**
> - `--warn-cc N` (default 11): print warning to stderr for functions with `N ≤ CC ≤ max-cc`. Exit 0.
> - `--max-cc N` (default 30): fail (exit 1) for functions with `CC > N`.
> - `--max-loc N` (default 500): fail (exit 1) for files with `LOC > N`.
> - Output format: `⚠️ WARNING: CC {n} ≥ {warn_cc}: {name} in {file}:{line}` / `❌ FAIL: CC {n} > {max_cc}: {name} in {file}:{line}` / `❌ FAIL: LOC {n} > {max_loc}: {file}`
> - Summary line: `{W} warning(s), {F} failure(s)`
> - Exit code: `0` = pass (including warnings-only), `1` = at least one failure.
> - Runtime budget: <30s full `backend/app/` scan.
> - Scope: only Python files under `backend/app/`. Frontend excluded.
>
> Mark C0-B as `[x]` with `✅ no-commit (design decision recorded in plan)`.

### PQ-C1-A

> **Step C1-A — Implement warning mode in architecture_metrics.py.**
>
> Edit `scripts/quality/architecture_metrics.py`:
>
> 1. **Argparse** (in `main()`): add `--warn-cc` argument:
>    ```python
>    parser.add_argument("--warn-cc", type=int, default=11, help="Warn CC threshold for --check (default: 11)")
>    ```
> 2. **`check_thresholds()` signature**: change to `def check_thresholds(data, max_cc, max_loc, warn_cc=11) -> tuple[list[str], list[str]]`
> 3. **Warning logic** inside `check_thresholds()`: add a `warnings` list. For each function, if `warn_cc <= CC <= max_cc`, append `f"⚠️ WARNING: CC {cc} ≥ {warn_cc}: {name} in {file}:{lineno}"`. Keep existing failure logic unchanged for `CC > max_cc`.
> 4. **Return**: `return warnings, failures`
> 5. **`main()` check block**: update to:
>    ```python
>    warnings, failures = check_thresholds(data, args.max_cc, args.max_loc, args.warn_cc)
>    if warnings:
>        print(f"\n⚠️  {len(warnings)} warning(s):", file=sys.stderr)
>        for w in warnings:
>            print(f"   • {w}", file=sys.stderr)
>    if failures:
>        print(f"\n❌ {len(failures)} failure(s):", file=sys.stderr)
>        for f in failures:
>            print(f"   • {f}", file=sys.stderr)
>    print(f"\nSummary: {len(warnings)} warning(s), {len(failures)} failure(s)", file=sys.stderr)
>    if failures:
>        return 1
>    print("\n✅ All thresholds passed.", file=sys.stderr)
>    return 0
>    ```
> 6. Run `ruff check scripts/quality/architecture_metrics.py --fix --quiet && ruff format scripts/quality/architecture_metrics.py --quiet`.
> 7. Mark C1-A as `[x]`.

### PQ-C2-A

> **Step C2-A — Preflight integration.**
>
> Edit `scripts/ci/preflight-ci-local.ps1`:
>
> 1. Find the Push mode section (around line 490). After the existing backend quality checks, add a new guard step:
>    ```powershell
>    if ($backendChanged) {
>        Write-StepHeader "Complexity gate"
>        $result = & python scripts/quality/architecture_metrics.py --check --warn-cc 11 --max-cc 30 --max-loc 500 2>&1
>        $exitCode = $LASTEXITCODE
>        Write-Output $result
>        if ($exitCode -ne 0) {
>            Add-Failure "Complexity gate" "CC or LOC thresholds exceeded"
>        }
>    }
>    ```
>    Adapt to the exact pattern used by surrounding steps (use `Assert-StepResult` or `Add-Failure` as appropriate).
> 2. Add the same gate in the Full mode section.
> 3. Run `scripts/ci/test-L1.ps1 -BaseRef HEAD`.
> 4. Mark C2-A as `[x]`.

### PQ-C2-B

> **Step C2-B — CI workflow job.**
>
> Edit `.github/workflows/ci.yml`:
>
> 1. Add a new job `complexity_gate` after the `quality` job. Structure:
>    ```yaml
>    complexity_gate:
>      name: Complexity Gate
>      needs: [changes]
>      if: needs.changes.outputs.backend == 'true'
>      runs-on: ubuntu-latest
>      steps:
>        - uses: actions/checkout@v4
>        - uses: actions/setup-python@v5
>          with:
>            python-version: '3.12'
>        - run: pip install radon==6.0.1
>        - run: python scripts/quality/architecture_metrics.py --check --warn-cc 11 --max-cc 30 --max-loc 500
>    ```
>    Match the Python version to whatever the existing `quality` job uses.
> 2. Mark C2-B as `[x]`.

### PQ-C3-A

> **Step C3-A — Create ADR.**
>
> Create `docs/projects/veterinary-medical-records/02-tech/adr/ADR-ARCH-0005-complexity-gate-thresholds.md`:
>
> Follow the format of ADR-ARCH-0001 (Title, Status, Date, Context, Decision, Consequences sections).
>
> Key content:
> - **Context:** Architecture audit (2026-03-09) found 6 hotspots with CC up to 163. Without automated enforcement, decomposition gains from ARCH-01/ARCH-02 will re-accrete. Manual review cannot reliably catch complexity regressions across PRs.
> - **Decision:** Add CI gate with thresholds: warn at CC ≥ 11, fail at CC > 30, fail at LOC > 500. Scope: all Python files under `backend/app/`. Gate runtime budget: <30s. Existing violations are grandfathered until addressed by ARCH-01/ARCH-02 decomposition work.
> - **Consequences:** PRs introducing new high-complexity functions are blocked. Developers see early warnings at CC 11. Threshold values are calibrated to industry standards (CC 10-20 = complex, CC 30+ = untestable). Future threshold tightening requires a new ADR.
>
> Also edit `docs/projects/veterinary-medical-records/02-tech/adr/index.md` — add row:
> `| [ADR-ARCH-0005](ADR-ARCH-0005-complexity-gate-thresholds.md) | Complexity Gate Thresholds for CI Enforcement | Accepted | 2026-03-10 |`
>
> Mark C3-A as `[x]`.

---

## Active Prompt

(none)

---

## Acceptance Criteria

1. CI fails on new functions with CC > 30.
2. CI warns on new functions with CC >= 11.
3. CI fails on new files > 500 LOC.
4. Gate runs in < 30 seconds.
5. ADR documents thresholds and rationale tied to re-accretion pattern.

### Traceability

| ARCH-03 acceptance criterion | Planned step(s) |
|---|---|
| CI fails on new functions with CC > 30 | C1-A, C1-B, C2-B, C4-A |
| CI warns on new functions with CC >= 11 | C1-A, C1-C, C2-B, C4-A |
| CI fails on new files > 500 LOC | C1-A, C2-B, C4-A |
| Gate runs in < 30s | C1-D, C4-A, C4-B |
| ADR documents thresholds | C3-A, C4-B |

---

## Risks and Mitigations

- **Risk:** false positives on legacy hotspots unrelated to current change.
  **Mitigation:** define enforcement scope and messaging in C0-B; if needed, introduce deterministic baseline exception list with explicit sunset policy.
- **Risk:** CI runtime increase.
  **Mitigation:** run targeted file set when possible and validate runtime budget in C1-D/C4-B.
- **Risk:** policy drift between ARCH and ADR.
  **Mitigation:** single ADR source with explicit threshold table and backlink from backlog item.

---

## How to test

```powershell
# Local pipeline (Push mode)
./scripts/ci/test-L2.ps1 -BaseRef main

# Direct complexity gate — should exit 1 (known violations)
python scripts/quality/architecture_metrics.py --check --warn-cc 11 --max-cc 30 --max-loc 500

# Warnings-only mode — should exit 0
python scripts/quality/architecture_metrics.py --check --warn-cc 11 --max-cc 9999 --max-loc 9999

# Runtime check — target <30s
Measure-Command { python scripts/quality/architecture_metrics.py --check --max-cc 30 --max-loc 500 }
```
