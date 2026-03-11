---
title: "Architecture Decision Records (ADR) Index"
type: reference
status: active
audience: all
last-updated: 2026-03-11
---

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [Architecture Decision Records (ADR) Index](#architecture-decision-records-adr-index)
  - [ADR table](#adr-table)
  - [Usage](#usage)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Architecture Decision Records (ADR) Index

This directory stores architecture decisions that shape the current system design.

## ADR table

| ID                                                                         | Title                                                | Status   | Date       |
| -------------------------------------------------------------------------- | ---------------------------------------------------- | -------- | ---------- |
| [ADR-ARCH-0001](ADR-ARCH-0001-modular-monolith.md)                         | Modular Monolith over Microservices                  | Accepted | 2026-02-24 |
| [ADR-ARCH-0002](ADR-ARCH-0002-sqlite-database.md)                          | SQLite as Primary Database                           | Accepted | 2026-02-24 |
| [ADR-ARCH-0003](ADR-ARCH-0003-raw-sql-repository-pattern.md)               | Raw SQL with Repository Pattern (No ORM)             | Accepted | 2026-02-24 |
| [ADR-ARCH-0004](ADR-ARCH-0004-in-process-async-processing.md)              | In-Process Async Processing (No External Task Queue) | Accepted | 2026-02-24 |
| [ADR-ARCH-0005](ADR-ARCH-0005-complexity-gate-thresholds.md)               | Complexity Gate Thresholds for CI Enforcement        | Accepted | 2026-03-10 |
| [ADR-ARCH-0006](ADR-ARCH-0006-frontend-stack-react-tanstack-query-vite.md) | Frontend Stack (React + TanStack Query + Vite)       | Accepted | 2026-03-11 |
| [ADR-ARCH-0007](ADR-ARCH-0007-re-accretion-prevention-governance.md)       | Re-accretion Prevention Governance                   | Accepted | 2026-03-11 |
| [ADR-ARCH-0008](ADR-ARCH-0008-confidence-scoring-algorithm.md)             | Confidence Scoring Algorithm Design                  | Accepted | 2026-03-11 |

## Usage

- Read architecture ADRs first for high-level technical trade-offs.
- Use [`docs/README.md`](../../../README.md) for full documentation reading order.
