# IMP-13 — Operational Runbook Architecture

**Status:** Planned

**Type:** Technical Improvement (non-user-facing)

**Target release:** Release 22 — Operational governance redesign

**PR strategy:** 4 sequential PRs, each with its own plan. Hard-gate between PRs.

**Plans (execution order):**

| # | Plan | Scope | Branch |
|---|---|---|---|
| PR-1 | [IMP-13-PR1-CREATE-RUNBOOK-LAYER](../plans/PLAN_2026-03-10_IMP-13-PR1-CREATE-RUNBOOK-LAYER.md) | Fase A — Create `.prompt.md`, `.instructions.md`, `plan-start-check.py` | `docs/imp-13-operational-runbook-architecture` |
| PR-2 | [IMP-13-PR2-ACTIVATE-RUNBOOK-ROUTING](../plans/PLAN_2026-03-10_IMP-13-PR2-ACTIVATE-RUNBOOK-ROUTING.md) | Fase B — Rewire AGENTS.md | `refactor/imp-13-activate-runbook-routing` |
| PR-3 | [IMP-13-PR3-MIGRATE-ROUTER-RULES-TO-RUNBOOKS](../plans/PLAN_2026-03-11_IMP-13-PR3-MIGRATE-ROUTER-RULES-TO-RUNBOOKS.md) | Migrate all operational rules from router into self-contained runbooks | Pending |
| PR-4 | [IMP-13-PR4-RETIRE-ROUTER-OPERATIONAL](../plans/PLAN_2026-03-10_IMP-13-PR3-RETIRE-ROUTER-OPERATIONAL.md) | Fases C+D — Retire router, cleanup | Pending |

**Technical Outcome**
Replace the multi-level agent router operational layer with self-contained `.prompt.md` runbooks, pattern-triggered `.instructions.md` context files, and executable enforcement scripts. Reduce the agent's operational burden from navigating ~1000 lines of fragmented protocol to loading a single 20–40 line runbook per intent.

**Problem Statement**
The current operational governance system relies on a 5-level routing chain (AGENTS.md → 00_AUTHORITY.md → 01_WORKFLOW/\* or 03_SHARED/EXECUTION_PROTOCOL/\* → 12 sub-modules) backed by a ~700-line plan execution protocol. This architecture treats agent misbehavior as an information-deficit problem and responds by adding more text. The actual problem is information overload: agents saturate their context navigating conditional prose and fail to follow plan-start rules, checkpoint procedures, and commit governance deterministically.

Evidence:
- Agents skip mandatory plan-start questions in fresh chats.
- Agents ask inconsistent questions when forced through the plan-start flow.
- Agents recover the wrong subset of rules from the routing and protocol stack.
- Behavior varies across chat sessions despite identical protocol text.

These failures are symptoms of context saturation, not missing instructions.

**Scope**

### Fase A — Create without destroying (low risk, high immediate value)

Create the new operational layer alongside the existing one. No existing files are modified.

#### A1 — Plan-start enforcement script

Create `scripts/dev/plan-start-check.py` that:
1. Finds the active plan file (glob `PLAN_*.md` outside `completed/`).
2. Reads the four mandatory fields (`Branch`, `Worktree`, `Execution Mode`, `Model Assignment`).
3. Reports which are resolved and which are not.
4. Outputs the exact next action as structured text the agent can follow.

#### A2 — Operational prompts (`.prompt.md`)

Create self-contained runbooks in `.github/prompts/`:

| File | Intent trigger | Content source |
|---|---|---|
| `plan-create.prompt.md` | "create a plan", "new plan" | plan-creation.md essentials |
| `plan-start.prompt.md` | "go" / "continue" on unresolved plan | plan-execution-protocol.md §4, §7 (plan-start choices), preflight gate |
| `plan-resume.prompt.md` | "go" / "continue" on active plan | plan-execution-protocol.md §4, §5, §10 (decision table) |
| `plan-closeout.prompt.md` | "merge", "close plan" | plan-execution-protocol.md §14 (closeout), §13 SCOPE BOUNDARY |
| `code-review.prompt.md` | "review", "code review" | code-review operational rules |
| `scope-boundary.prompt.md` | commit/push during active plan | plan-execution-protocol.md §13 SCOPE BOUNDARY |

Each `.prompt.md` is:
- Self-contained (no external loads required to complete the process).
- Under 50 lines.
- Structured as a numbered checklist the agent executes sequentially.
- Includes the termination criterion (when the process is done).

#### A3 — Pattern-triggered instructions (`.instructions.md`)

Create passive context files in `.github/instructions/`:

| File | `applyTo` | Content |
|---|---|---|
| `plan-files.instructions.md` | `**/plans/PLAN_*.md` | 5 critical rules: atomic iterations, mark `[x]` with SHA, no scope mixing, checkpoint pause, evidence block |
| `backlog-files.instructions.md` | `**/Backlog/*.md` | Status lifecycle, naming convention, link format |

These load automatically when the agent touches matching files. No routing required.

#### A4 — Dry-run validation

Perform a documented dry-run using the new operational layer:
1. Simulate plan creation from a cold chat using `plan-create.prompt.md`.
2. Simulate plan-start with unresolved metadata using `plan-start.prompt.md` + `plan-start-check.py`.
3. Simulate plan resume using `plan-resume.prompt.md`.
4. Document results. If any dry-run fails, iterate on the prompts before proceeding.

### Fase B — Rewire AGENTS.md (medium risk)

Rewrite `AGENTS.md` to use the new operational layer as primary path.

#### B1 — Rewrite AGENTS.md

New AGENTS.md (~20–30 lines):
- Global rules (no commits to main, branch naming).
- Operational processes: intent → `.prompt.md` mapping.
- Reference: pointers to remaining router reference modules.
- Plan execution: "run `scripts/dev/plan-start-check.py` before any plan step."

#### B2 — Update test_doc_router_contract.py

Adapt the router contract tests to validate the new AGENTS.md structure instead of the old routing chain.

**🚧 Hard-gate after Fase B:** User validates that the new operational layer works in real usage before proceeding to router retirement.

### Fase C — Retire router operational layer (high risk, mechanical)

Remove the router modules that are now replaced by `.prompt.md` files.

#### C1 — Remove operational router directories

Delete:
- `docs/agent_router/01_WORKFLOW/START_WORK/`
- `docs/agent_router/01_WORKFLOW/PULL_REQUESTS/`
- `docs/agent_router/01_WORKFLOW/CODE_REVIEW/`
- `docs/agent_router/01_WORKFLOW/TESTING/`
- `docs/agent_router/01_WORKFLOW/BRANCHING/`
- `docs/agent_router/03_SHARED/EXECUTION_PROTOCOL/`
- `docs/agent_router/03_SHARED/WAY_OF_WORKING/`

Preserve:
- `docs/agent_router/01_WORKFLOW/DOC_UPDATES/` (contains map JSONs — relocated in Fase D).
- `docs/agent_router/03_SHARED/CODING_STANDARDS/`
- `docs/agent_router/03_SHARED/DOCUMENTATION_GUIDELINES/`
- `docs/agent_router/03_SHARED/BRAND_GUIDELINES/`
- `docs/agent_router/03_SHARED/UX_GUIDELINES/`
- `docs/agent_router/02_PRODUCT/`
- `docs/agent_router/04_PROJECT/`
- `docs/agent_router/extraction/` and `extraction-tracking/`

#### C2 — Update 00_AUTHORITY.md

Remove intent entries that now route to `.prompt.md`. Keep entries for reference materials only.

#### C3 — Update CI scripts

Update scripts that reference removed paths:
- `scripts/docs/check_router_directionality.py` — remove `01_WORKFLOW/` from protected prefixes or adjust.
- `scripts/docs/check_doc_router_parity.py` — update if DOC_UPDATES path changes.
- `scripts/docs/check_no_canonical_router_refs.py` — no change expected (validates canonical docs).
- `metrics/llm_benchmarks/scripts/backfill_daily.py` — update router path references.

#### C4 — Update MANIFEST.yaml

Remove entries for deleted operational modules. Keep entries for reference modules.

#### C5 — Regenerate router files

Run `python scripts/docs/generate-router-files.py` to confirm no drift.

#### C6 — Full test suite

Run L2 validation to confirm nothing is broken.

### Fase D — Cleanup

#### D1 — Relocate DOC_UPDATES map JSONs

Move `router_parity_map.json` and `test_impact_map.json` from `docs/agent_router/01_WORKFLOW/DOC_UPDATES/` to a neutral location (e.g., `scripts/docs/` or `docs/shared/03-ops/`). Update all references.

#### D2 — Update copilot-instructions.md

Create `.github/copilot-instructions.md` with the minimal global rules that should always be in context (the subset of AGENTS.md global rules that VS Code auto-loads).

#### D3 — Final L3 validation

Run full L3 suite. Confirm all tests pass. Confirm router generation has no drift.

**Out of Scope**
- No changes to the product, API, or UI.
- No rewrite of the canonical plan-execution-protocol.md (it remains as reference specification).
- No changes to reference router modules (CODING_STANDARDS, UX_GUIDELINES, etc.).
- No changes to extraction or extraction-tracking router modules.
- No removal of canonical operational docs — only their router-derived operational fragments.

**Acceptance Criteria**
- All operational processes (plan create, plan start, plan resume, plan closeout, code review, commit/push) have a self-contained `.prompt.md` under 50 lines.
- AGENTS.md is under 30 lines and routes to `.prompt.md` files for operational processes.
- `.instructions.md` files auto-load critical rules when touching plan or backlog files.
- `scripts/dev/plan-start-check.py` deterministically detects unresolved plan-start fields.
- The agent can complete a plan-start flow from a cold chat using only `plan-start.prompt.md` + the enforcement script, without loading the full protocol.
- Router operational directories (`01_WORKFLOW/START_WORK`, `EXECUTION_PROTOCOL`, etc.) are removed.
- All CI scripts, contract tests, and router generation pass after changes.

**Validation Checklist**
- Dry-run plan creation from a cold chat using `plan-create.prompt.md` → agent follows the checklist deterministically.
- Dry-run plan-start with unresolved metadata → `plan-start-check.py` reports missing fields → agent follows `plan-start.prompt.md` to resolve them.
- Dry-run plan resume → agent loads `plan-resume.prompt.md` and executes the correct next step.
- Dry-run plan closeout → agent follows `plan-closeout.prompt.md` lifecycle.
- Edit a plan file in VS Code → `plan-files.instructions.md` loads automatically (verify via Copilot context).
- Confirm no stale references to deleted router paths in any file.
- L3 test suite passes.
- Router generation (`generate-router-files.py --check`) passes.

**Risks and Mitigations**
- Risk: `.prompt.md` content doesn't capture edge cases from the full protocol.
  - Mitigation: Fase A dry-runs validate coverage before Fase B activation. The canonical protocol remains as reference for edge cases.
- Risk: CI scripts break when router directories are removed.
  - Mitigation: Fase C updates scripts before deleting directories. L2 gate validates.
- Risk: agents ignore `.prompt.md` routing from AGENTS.md.
  - Mitigation: `plan-start-check.py` provides a deterministic backstop independent of agent instruction-following.
- Risk: `.instructions.md` `applyTo` patterns don't trigger as expected.
  - Mitigation: Fase A includes explicit verification that VS Code loads them.

**Dependencies**
- Supersedes and replaces IMP-10 (PLANFLOW-L1), IMP-11 (PLANFLOW-L2), and IMP-12 (PLANFLOW-L3).
- Should be coordinated with IMP-09 (Rationalize Documentation Governance Tests) for test cleanup.
- Canonical docs (`plan-execution-protocol.md`, `plan-creation.md`, `way-of-working.md`) are read as source material but not modified.
