# ARCH-10 — Write Missing ADRs

**Status:** Planned

**Type:** Architecture Improvement (documentation)

**Target release:** Release 20 — Architecture hardening

**Origin:** [Architecture Review 2026-03-09](../../02-tech/audits/architecture-review-2026-03-09.md) — Phase 1 (GAP-008)

**Severity:** HIGH  
**Effort:** M (2-4h per ADR)

## Problem Statement

Key architectural decisions lack formal ADR documentation.

## Action

Create ADRs for at least:

- ADR-ARCH-0006: Frontend stack (React + TanStack Query + Vite)
- ADR-ARCH-0008: Confidence scoring algorithm design

Implementation note (2026-03-11): `ADR-ARCH-0005` was already used by complexity gate thresholds and `ADR-ARCH-0007`
was later assigned to re-accretion prevention governance, so the missing ADRs for this item were recorded as `0006`
and `0008`.

## Acceptance Criteria

- Both ADRs exist in the ADR directory following existing format
- Each ADR includes context, decision, consequences, and status
- Consistent with existing ADRs (0001-0005)

## Dependencies

- None.
