# IMP-01 — Canonical Operational Execution Policy Alignment

**Status:** Done

**Type:** Technical Improvement (non-user-facing)

**Target release:** Release 17 — Engineering quality and project governance

**PR strategy:** Single dedicated PR (policy-only; low semantic risk)

**Technical Outcome**
Establish a single, consistent, and non-ambiguous canonical operational policy for plan execution so any new chat/agent can execute the workflow deterministically without legacy rule drift.

**Problem Statement**
Current operational guidance still contains conflicting semantics in canonical docs (especially around auto-commit conditions), which enables inconsistent execution behavior across chats/agents and weakens governance predictability.

**Scope**
- Update canonical operational policy to remove `CT-*` as an auto-commit prerequisite.
- Consolidate git behavior by automation mode:
  - `Supervisado`: explicit confirmation required before commit.
  - `Semiautomatico` and `Automatico`: automatic commit allowed.
  - `push`: always manual.
- Keep PR policy explicit: PR creation/update is user-triggered only.
- Add an explicit pre-PR hard rule: commit history review before opening PR.
- Add an explicit plan-start rule: mandatory automation mode selection at plan start (text fallback when no option selector is available).
- Keep the rule that operational actions are not executable plan checklist items.

**Out of Scope**
- No new CI/scripts/guards implementation in this item.
- No active plan migrations in this item.
- No router regeneration/mapping propagation in this item.
- No backend/frontend product behavior changes.

**Acceptance Criteria**
- Canonical policy no longer requires `CT-*`/`commit-task` for automatic commits.
- Commit/push/PR behavior by mode is documented once and without contradictions.
- Canonical docs include an explicit `Pre-PR Commit History Review` hard rule.
- Canonical docs include an explicit plan-start automation mode selection rule.
- The resulting policy is deterministic and self-sufficient for an implementer chat with no prior context.

**Validation Checklist**
- Static content checks confirm no canonical rule states that auto-commit depends on `CT-*`.
- Static content checks confirm `push` is manual in all modes.
- Static content checks confirm PR creation/update is user-triggered only.
- Internal consistency review confirms no contradictory policy clauses remain in canonical operational docs.

**Risks and Mitigations**
- Risk: residual legacy phrasing leaves hidden ambiguity.
  - Mitigation: perform a final "old rule -> final rule" cross-check before closing the item.
- Risk: policy PR grows too broad.
  - Mitigation: keep this PR canonical-policy-only; defer propagation/enforcement to subsequent IMPs.

**Dependencies**
- None to start this item.
- This item is the dependency baseline for router/guards propagation IMPs.

---
