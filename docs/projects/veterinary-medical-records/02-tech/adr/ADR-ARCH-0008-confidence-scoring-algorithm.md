---
title: "ADR-ARCH-0008: Confidence Scoring Algorithm Design"
type: adr
status: active
audience: contributor
last-updated: 2026-03-11
---

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [ADR-ARCH-0008: Confidence Scoring Algorithm Design](#adr-arch-0008-confidence-scoring-algorithm-design)
  - [Status](#status)
  - [Context](#context)
  - [Decision Drivers](#decision-drivers)
  - [Considered Options](#considered-options)
    - [Option A — Deterministic composed confidence (candidate + bounded history adjustment)](#option-a--deterministic-composed-confidence-candidate--bounded-history-adjustment)
    - [Option B — Pure candidate confidence only (no calibration)](#option-b--pure-candidate-confidence-only-no-calibration)
    - [Option C — Learned model confidence (online/offline ML model)](#option-c--learned-model-confidence-onlineoffline-ml-model)
  - [Decision](#decision)
  - [Rationale](#rationale)
  - [Consequences](#consequences)
    - [Positive](#positive)
    - [Negative](#negative)
    - [Risks](#risks)
  - [Code Evidence](#code-evidence)
  - [Related Decisions](#related-decisions)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# ADR-ARCH-0008: Confidence Scoring Algorithm Design

## Status

- Accepted
- Date: 2026-03-11

## Context

The review payload includes confidence signals that drive veterinarian prioritization and explainability. The system
needs deterministic behavior, bounded outputs, and an incremental way to incorporate reviewer feedback without
introducing non-reproducible model behavior.

The confidence design must support:

- Stable field-level confidence values in range `[0, 1]`.
- Explicit separation between extraction signal and historical calibration signal.
- Safe defaults when policy configuration is absent or invalid.
- Human edit flows that preserve prior confidence when possible.

## Decision Drivers

- Deterministic and testable behavior for evaluator reproducibility.
- Incremental calibration based on observed accept/edit history.
- Strong guardrails against invalid numeric inputs and drift.
- Backward-compatible payload semantics for frontend confidence bands.

## Considered Options

### Option A — Deterministic composed confidence (candidate + bounded history adjustment)

#### Pros

- Transparent formula and bounded outputs.
- Easy to test and reason about in unit/integration tests.
- Supports calibration without external ML infrastructure.

#### Cons

- Less expressive than full probabilistic or learned ranking models.
- Requires manual policy/version governance over time.

### Option B — Pure candidate confidence only (no calibration)

#### Pros

- Simplest implementation and explanation.

#### Cons

- Ignores valuable reviewer feedback loops.
- No adaptation for recurring context/mapping behavior.

### Option C — Learned model confidence (online/offline ML model)

#### Pros

- Potentially higher ranking quality with sufficient training data.

#### Cons

- Adds model lifecycle, observability, and reproducibility complexity.
- Harder to justify and audit for current single-clinic scope.

## Decision

Adopt **Option A: deterministic composed confidence** with this structure:

1. Compute `field_candidate_confidence` from candidate signal, sanitized and clamped to `[0,1]`.
2. Compute review-history adjustment in percentage points (pp) with minimum volume and bounded max absolute
   adjustment.
3. Compose `field_mapping_confidence = clamp(candidate_confidence + adjustment_pp/100, 0, 1)`.
4. Expose confidence policy metadata only when explicit policy environment configuration is valid.
5. For human edits, preserve prior candidate confidence when available; fallback to mapping confidence or neutral
   baseline.

## Rationale

1. `backend/app/application/processing/confidence_scoring.py` sanitizes candidate confidence and composes mapping
   confidence with explicit clamping.
2. `backend/app/application/confidence_calibration.py` computes bounded review-history adjustment with
   `min_volume=3` and `max_abs_adjustment_pp=15.0`.
3. `backend/app/application/processing/interpretation.py` includes/omits `confidence_policy` payload based on explicit
   configuration diagnostics.
4. `backend/app/config.py` defines defaults and environment parsing for policy version, band cutoffs, and human-edit
   neutral confidence.
5. `backend/app/application/documents/_edit_helpers.py` preserves confidence semantics during edit flows through
   deterministic fallback logic.

## Consequences

### Positive

- Confidence values remain bounded, deterministic, and auditable.
- Reviewer feedback affects ranking behavior without external model dependencies.
- Frontend confidence-band rendering can rely on a stable payload contract.

### Negative

- Calibration sensitivity is limited to configured bounded adjustments.
- Policy evolution requires explicit versioning and follow-up ADR updates.

### Risks

- Over- or under-calibrated confidence if environment policy values are misconfigured.
- Mitigation: explicit config diagnostics, safe defaults, and bounded formulas with test coverage.

## Code Evidence

- `backend/app/application/processing/confidence_scoring.py`
- `backend/app/application/confidence_calibration.py`
- `backend/app/application/processing/interpretation.py`
- `backend/app/application/documents/_edit_helpers.py`
- `backend/app/config.py`
- `backend/tests/unit/test_confidence_calibration.py`
- `backend/tests/unit/test_confidence_config_and_fallback.py`

## Related Decisions

- [ADR-ARCH-0003: Raw SQL with Repository Pattern](ADR-ARCH-0003-raw-sql-repository-pattern.md)
- [ADR-ARCH-0004: In-Process Async Processing](ADR-ARCH-0004-in-process-async-processing.md)
- [ADR-ARCH-0006: Frontend Stack (React + TanStack Query + Vite)](ADR-ARCH-0006-frontend-stack-react-tanstack-query-vite.md)
