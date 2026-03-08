# Execution Rules (Compatibility Stub)

This file is kept for compatibility. Canonical operational behavior lives in
[plan-execution-protocol.md](plan-execution-protocol.md).

## Step eligibility rule

On continuation intent, select the first `[ ]` step and apply the decision table
from the canonical protocol. This compatibility stub keeps the Step eligibility
rule and decision table reference discoverable for legacy tooling.

## Semi-unattended execution

See canonical protocol section: `Semi-Unattended Execution (Default Mode)`.

## CI GATE

Before commit/push/PR, use local preflight levels:
- L1 — Quick: `scripts/ci/test-L1.ps1 -BaseRef HEAD`
- L2 — Push: `scripts/ci/test-L2.ps1 -BaseRef main`
- L3 — Full: `scripts/ci/test-L3.ps1 -BaseRef main`

## AUTO-CHAIN

Use the canonical next-step decision table and hard-gates behavior.

## SCOPE BOUNDARY

Use the canonical `SCOPE BOUNDARY Procedure`.

## Plan-edit-last

Apply plan-edit-last governance from the canonical protocol.

## Commit conventions

Use canonical commit convention:
`<type>(plan-<id>): <short description>`.

## Token efficiency

Use `iterative-retrieval` before each step and `strategic-compact` at step close.
