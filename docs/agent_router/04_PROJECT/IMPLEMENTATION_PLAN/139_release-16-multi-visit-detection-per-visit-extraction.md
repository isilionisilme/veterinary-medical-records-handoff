# Release 16 — Multi-visit detection & per-visit extraction

## Goal
Detect all visits in a medical document from raw text boundaries and assign clinical data to each specific visit, with observability for debugging assignment problems.

## Scope
- Multi-visit detection from raw text boundaries
- Per-visit field extraction from segment text
- Visit scoping observability and documentation (conditional)

## User Stories (in order)
- US-64 — Detect all visits in the document even when dates are not in explicit fields
- US-65 — View clinical data assigned to each specific visit
- US-66 — Diagnose visit-to-data assignment problems (conditional)

---
