# Plan: Fix preflight L3 PowerShell compatibility (Windows)

**Rama:** `chore/fix-preflight-l3-powershell`
**PR:** [#200](https://github.com/isilionisilme/veterinary-medical-records/pull/200)
**Tipo:** `chore/ci`

## Context

There is a CI tooling bug in Windows PowerShell when running local preflight wrappers (`test-L1/L2/L3.ps1` → `preflight-ci-local.ps1`).

Observed error:

- `No se encuentra ningún parámetro de posición que acepte el argumento '..'`

Root cause candidate is the repository root resolution using `Join-Path` with multiple positional child segments in scripts executed from `powershell.exe` (Windows PowerShell 5.1).

## Scope boundary (strict)

- **In scope:** local CI tooling scripts under `scripts/ci/` (and `.bat` wrappers only if strictly required by the same flow).
- **Out of scope:** product/backend/frontend logic and unrelated docs.
- **Goal:** make L1/L2/L3 wrappers work on Windows PowerShell with minimal focused changes.

---

## Estado de ejecución

- [x] C1 🔄 — Fix PowerShell 5.1 compatibility in affected `scripts/ci/*.ps1` root-path resolution logic (Codex) — ✅ `2c52f3db`
- [x] C2 🔄 — Validate local preflight execution: `scripts/ci/test-L1.ps1`, `scripts/ci/test-L2.ps1`, `scripts/ci/test-L3.ps1` (Codex) — ✅ `2c52f3db`

---

## Commit strategy

Planned commit set for this iteration:

1. `fix(ci): make local preflight scripts PowerShell 5.1 compatible`
   - Includes only the minimal CI script edits required to remove the positional-argument failure.

2. `docs(plan): mark plan execution status`
   - Plan-only status update after validation evidence is available.

> Operational protocol (`push`, PR creation/update, CI verification in GitHub) follows repository execution rules and is not modeled as plan steps.

---

## Evidence to collect

- Terminal outputs for successful runs of:
  - `scripts/ci/test-L1.ps1`
  - `scripts/ci/test-L2.ps1`
  - `scripts/ci/test-L3.ps1`
- `git diff` limited to CI tooling files.
- PR body includes root cause + files changed + command results.
