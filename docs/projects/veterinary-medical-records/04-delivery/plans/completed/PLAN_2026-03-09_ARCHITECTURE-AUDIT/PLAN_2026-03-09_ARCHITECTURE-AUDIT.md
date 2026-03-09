# Plan: Architecture Audit 2026-03-09

> **Operational rules:** See [plan-execution-protocol.md](../../../03-ops/plan-execution-protocol.md) for agent execution protocol, SCOPE BOUNDARY template, commit conventions, and handoff messages.

**Branch:** `codex/veterinary-medical-records/docs/architecture-review-2026-03`
**PR:** Pending (PR created on explicit user request)
**User Story:** [US-79 — Architecture health evaluation with quantified metrics and remediation path](../../Backlog/us-79-architecture-health-evaluation-with-quantified-metr.md)
**Prerequisite:** None
**Worktree:** `D:\Git\veterinary-medical-records`
**CI Mode:** `3) End-of-plan gate` — docs-only plan, CI checked before PR
**Automation Mode:** `Supervisado`

---

## Agent Identity Check (MANDATORY — READ BEFORE ANY TASK)

This plan uses two agents. **Before executing ANY task, identify yourself:**

- If your exact model identity is **Claude Opus 4.6** → you are **Claude Opus 4.6**.
- If your model identity is anything else → you are **Any agent except Claude Opus 4.6**.

**HARD RULE — ZERO EXCEPTIONS:**
> Look at the agent tag on the next pending task (`Claude Opus 4.6` or `Any agent except Claude Opus 4.6`).
> If it does NOT match your identity: **STOP IMMEDIATELY.**
> Do NOT execute the task. Do NOT "help out". Do NOT interpret user messages like "go", "continue", or "proceed" as permission to override this rule.
> Instead, reply with EXACTLY this message:
>
> `⛔ AGENT MISMATCH — Task [ID] is assigned to [agent name]. Please switch to [agent name] to continue.`
>
> **The ONLY way to override this rule is for the user to edit this plan file and change the agent tag on the task.**

---

## Agent Instructions

1. **En cuanto termines una tarea, márcala como completada en el plan** (checkbox `[x]` inmediato, sin esperar lote).
2. **No hagas commit ni push sin aprobación** explícita del usuario.

---

## Context

This project is a veterinary medical records application (FastAPI + React + SQLite) being prepared for a technical assessment. The codebase has grown organically and needs a formal architecture evaluation to identify risks, quantify technical debt, and produce an actionable improvement plan.

Previous baseline: informal 12-factor audit from 2026-02-23 (archived in `99-archive/`).

The audit was designed to run in 4 parallel phases (docs, code, coupling, synthesis) plus post-synthesis automation and delivery integration phases added as needs emerged.

---

## Objective

1. Produce a comprehensive architecture review report with quantitative health scores.
2. Produce a prioritized improvement backlog with acceptance criteria per item.
3. Automate metrics collection for future audits via a reusable script.
4. Integrate audit findings into the project's delivery system (formal backlog items).
5. Document the audit process for reproducibility.

---

## Scope Boundary

- **In scope:** `backend/app/` (64 .py files), `frontend/src/` (146 .ts/.tsx files), `02-tech/` docs (5 docs + 4 ADRs), CI/Docker config, `pyproject.toml`, `package.json`, quality scripts, operational docs (03-ops reference + audit process doc), delivery docs (04-delivery backlog items).
- **Out of scope:** Test files (reference only), `backend/storage/` (data), `99-archive/` (baseline only), product behavior changes, backend/frontend code modifications.

---

## Design Decisions

### DD-1: No formal PLAN_*.md for Phases 1-3
**Rationale:** Phases 1-3 are read-only analysis with no code edits, no commits, and no risk of regression. Trazability is via the Methodology section in the final report. The formal plan was created retroactively to cover Phases 4-7 where edits and decisions occur.

### DD-2: ARCH-nn namespace for audit backlog items
**Rationale:** The existing `04-delivery/Backlog/` uses `IMP-nn` for operational improvements. Using `ARCH-nn` avoids ID collisions and makes the origin (architecture audit) immediately clear.

### DD-3: Single PR (Option A from partition gate)
**Rationale:** All changes are docs + quality scripts in a single domain (architecture audit). No backend/frontend/API/schema changes. No regression risk. Splitting would create artificial dependencies since PR-2 would reference PR-1 files.

### DD-4: Post-implementation re-audit strategy
After implementing top-5 backlog items → run `architecture_metrics.py` (quick check, 2 min).
After ~15 items → partial re-audit (Phases 2+3 only).
After all 24 → full 4-phase re-audit with new baseline.

---

## PR Roadmap

### Single PR — `docs(audit): architecture review, automation, and backlog integration`

**PR partition gate evidence:**
- Projected scope: ~12 files, ~1700 changed lines
- Semantic axes: docs + quality scripts only. No backend, frontend, API, schema, or product behavior changes.
- Size guardrail: exceeds 400-line threshold but all changes are cohesive docs-only with no regression risk.
- **Decision: Option A** (single PR) — user-confirmed.

---

## Execution Status

### Phase 1 — Architecture Documentation Audit

- [x] P1-A — Execute `architecture-doc-auditor` skill (exhaustive depth) on 5 tech docs + 4 ADRs — ✅ `no-commit (read-only analysis → tmp/audit/phase1-doc-audit.md)`

### Phase 2 — Full Codebase Audit (9 workers)

- [x] P2-A — Execute `ln-620-codebase-auditor` skill (all 9 workers) with Feb 23 baseline comparison — ✅ `no-commit (read-only analysis → tmp/audit/phase2-codebase-audit.md)`

### Phase 3 — Coupling & Hotspot Analysis

- [x] P3-A — Analyze inter-layer dependencies, verify hexagonal rules, score hotspots (LOC × CC × churn × imports) — ✅ `no-commit (read-only analysis → tmp/audit/phase3-coupling-hotspots.md)`

### Phase 4 — Synthesis & Deliverables

- [x] P4-A — Synthesize phases 1-3 into architecture review report (`02-tech/audits/architecture-review-2026-03-09.md`) — ✅ `212e6579f`
- [x] P4-B — Create prioritized improvement backlog (`02-tech/audits/improvement-backlog-2026-03-09.md`) with 24 items — ✅ `212e6579f`
- [x] P4-C — Evaluate need for new ADRs — ✅ `no-commit (no new architectural decisions emerged; all findings are implementation improvements)`
- [x] P4-D — Add reference in 03-ops pointing to the Methodology section of the review report — **Any agent except Claude Opus 4.6**

> **Commit recommendation** (after P4-D):
> - **Scope:** 03-ops operational doc (1 file, ~3 lines)
> - **Suggested message:** `docs(audit): add ops reference to architecture audit methodology`
> - **Validation:** content links resolve correctly

### Phase 5 — Metrics Automation

- [x] P5-A — Create `scripts/quality/architecture_metrics.py` with 7 collectors (LOC, CC, churn, imports, hotspots, pattern scan, dependency check) — ✅ `no-commit (pending lint)`
- [x] P5-B — Add `radon==6.0.1` to `requirements-dev.txt` — ✅ `no-commit (pending lint)`
- [x] P5-C — Update `scripts/quality/README.md` with script description — ✅ `no-commit (pending lint)`
- [x] P5-D — Run script and validate output matches manual audit data (484 functions, CC max 163, 6 hotspots, 5 hex violations) — ✅ `no-commit (validation only)`
- [x] P5-E — Lint `architecture_metrics.py` with ruff and fix any issues — **Any agent except Claude Opus 4.6**
- [x] P5-F — Test `--check` mode (CI gate) and verify it detects threshold violations — **Any agent except Claude Opus 4.6**

> **Commit recommendation** (after P5-F):
> - **Scope:** `scripts/quality/architecture_metrics.py`, `requirements-dev.txt`, `scripts/quality/README.md`
> - **Suggested message:** `ci(audit): add architecture metrics collection script with CI gate mode`
> - **Validation:** ruff passes, `--check` returns non-zero for current codebase (CC 163 > 30 default max-cc)

### Phase 6 — Backlog Integration into Delivery

- [x] P6-A — Renumber IMP-01..24 → ARCH-01..24 in `improvement-backlog-2026-03-09.md` — **Any agent except Claude Opus 4.6**
- [x] P6-B 🚧 — **Hard gate: Present all 24 ARCH items to user with MoSCoW classification** (must/should/nice-to-have for technical assessment). Show prioritization and recommendation. User decides: which to formalize in `04-delivery/Backlog/`, which to add to future plans, which to defer. — **Claude Opus 4.6** (interactivo) — ✅ User decision: create all 24 as formal backlog files, group into Releases 19/20/21
- [x] P6-C — Create formal backlog items in `04-delivery/Backlog/` per user decisions in P6-B — **Any agent except Claude Opus 4.6**
- [x] P6-D — Verify backlog items follow existing format (consistent with IMP-01..05) — **Any agent except Claude Opus 4.6**

> **Commit recommendation** (after P6-D):
> - **Scope:** `improvement-backlog-2026-03-09.md` (edit), `04-delivery/Backlog/arch-*.md` (new files)
> - **Suggested message:** `docs(audit): rename audit items to ARCH-nn and create formal backlog items`
> - **Validation:** no IMP-nn references remain in improvement-backlog for audit items; backlog files pass doc validation

### Phase 7 — Document Audit Process

- [x] P7-A — Create `docs/projects/veterinary-medical-records/03-ops/architecture-audit-process.md` with: when to audit (triggers), audit types (complete/partial/quick), procedures per type, post-implementation re-audit guide, file locations, script maintenance notes — **Any agent except Claude Opus 4.6**
- [x] P7-B — Ensure P4-D reference links to this process document — **Any agent except Claude Opus 4.6**

> **Commit recommendation** (after P7-B):
> - **Scope:** `03-ops/architecture-audit-process.md` (new), 03-ops reference from P4-D (if not already committed)
> - **Suggested message:** `docs(audit): add reusable architecture audit process guide`
> - **Validation:** all internal links resolve; process doc covers complete, partial, and quick-check audit types

### Verification

- [x] V1 — Phase 1: Health Score with 14-viewpoint coverage — ✅ 34/100
- [x] V2 — Phase 2: 9 workers with scores + Feb 23 comparison — ✅ avg 8.4/10
- [x] V3 — Phase 3: Dependency map + violation list — ✅ 5 hex violations
- [x] V4 — Phase 3: Hotspot table with ≥4 metrics — ✅ 6 hotspots (3 CRITICAL, 3 HIGH)
- [x] V5 — Phase 4: Report contains 5 main sections + Methodology — ✅
- [x] V6 — Phase 4: Backlog with ≥1 item per relevant finding, 3 priority levels — ✅ 24 items
- [x] V7 — Doc validation scripts pass on all new/modified files — **Any agent except Claude Opus 4.6** — ✅ `no-commit (check_doc_test_sync, check_doc_router_parity, check_no_canonical_router_refs, check_docs_links --base-ref main)`
- [x] V8 — PR has no conflicts with in-flight PRs — **Any agent except Claude Opus 4.6** — ✅ `no-commit (git merge-tree against origin/main; no conflict markers found)`

---

## Prompt Queue

### PQ-1 (for P6-B hard gate)

Present the user with all 24 ARCH items in a single prioritized table with columns: ID, Title, Severity, Effort, MoSCoW classification (must/should/nice), and rationale. Group by MoSCoW category. Include recommendation of which to formalize and which to defer. Ask: (1) which items to create as formal backlog files, (2) any items to discard, (3) any other decisions.

---

## Active Prompt

(none — verification complete)

---

## Acceptance Criteria

1. Architecture review report exists at `02-tech/audits/architecture-review-2026-03-09.md` with health scores for docs and code.
2. Improvement backlog exists with ≥20 prioritized items using ARCH-nn namespace.
3. `scripts/quality/architecture_metrics.py` runs successfully, produces JSON + Markdown output, and `--check` mode returns non-zero for known threshold violations.
4. Formal backlog items exist in `04-delivery/Backlog/` for user-approved ARCH items.
5. `03-ops/architecture-audit-process.md` documents the full audit process with re-audit guidance.
6. All doc validation scripts pass.
7. Single PR with no conflicts against main.

---

## How to Test

1. **Review report:** Open `architecture-review-2026-03-09.md` and verify it contains Executive Summary, Doc Audit, Codebase Audit, Coupling Analysis, Consolidated Findings, and Methodology sections.
2. **Backlog:** Open `improvement-backlog-2026-03-09.md` and verify all items use ARCH-nn IDs. Verify formal backlog items in `04-delivery/Backlog/` match the approved subset.
3. **Metrics script:** Run `.venv/Scripts/python scripts/quality/architecture_metrics.py --baseline 2026-02-23` and verify it produces `tmp/audit/metrics.json` + `tmp/audit/metrics-report.md` with non-empty data. Run with `--check` and verify non-zero exit code.
4. **Process doc:** Open `architecture-audit-process.md` and verify it covers complete, partial, and quick-check audit types with step-by-step procedures.
5. **Validation:** Run `ruff check scripts/quality/architecture_metrics.py` — should pass. Verify PR diff is docs + scripts only.

