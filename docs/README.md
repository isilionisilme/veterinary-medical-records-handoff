---
title: "Wiki — Documentation Index"
type: index
status: active
audience: all
last-updated: 2026-03-02
---

# Wiki — Documentation Index


**Breadcrumbs:** Docs

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->


- [Folder structure](#folder-structure)
- [Sitemap](#sitemap)
- [Documentation governance (normative)](#documentation-governance-normative)
- [Shared Documentation](#shared-documentation)
- [Projects](#projects)
- [Evaluator first-pass (recommended, 10-15 min)](#evaluator-first-pass-recommended-10-15-min)
- [Tooling (optional)](#tooling-optional)
- [Authority & precedence](#authority--precedence)
- [Contribution and quality gates](#contribution-and-quality-gates)
- [Dependency justification (Technical Design Appendix E3)](#dependency-justification-technical-design-appendix-e3)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

Human-oriented index for all canonical documentation in this repository.

## Folder structure
```
docs/
├── shared/           ← standards and guidelines shared across all projects
├── projects/         ← per-initiative documentation
│   └── veterinary-medical-records/
└── metrics/          ← tooling data (llm_benchmarks)
```

## Sitemap

- `docs/README.md`
- `docs/shared/`
  - `01-product/brand-guidelines.md`
  - `01-product/ux-guidelines.md`
  - `02-tech/coding-standards.md`
  - `02-tech/documentation-guidelines.md`
  - `02-tech/llm-benchmarks.md`
  - `03-ops/way-of-working.md`
- `docs/projects/veterinary-medical-records/`
  - `01-product/design-system.md`
  - `01-product/product-design.md`
  - `01-product/ux-design.md`
  - `02-tech/architecture.md`
  - `02-tech/backend-implementation.md`
  - `02-tech/extraction-quality.md`
  - `02-tech/frontend-implementation.md`
  - `02-tech/technical-design.md`
  - `03-ops/execution-rules.md` (compatibility stub)
  - `03-ops/manual-qa-regression-checklist.md`
  - `03-ops/plan-execution-protocol.md`
  - `03-ops/plan-e2e-test-coverage.md`
  - `04-delivery/copilot-usage.md`
  - `04-delivery/delivery-summary.md`
  - `04-delivery/future-improvements.md`
  - `04-delivery/implementation-history.md`
  - `04-delivery/implementation-plan.md`

## Documentation governance (normative)

- **Canonical source docs (human SoT):** `docs/shared/*` and `docs/projects/*`.
- **Directionality rule:** canonical docs are human-facing sources and should remain self-contained.
- Human-readable documentation → `docs/shared/` or `docs/projects/`.

## Shared Documentation

Standards that apply across all initiatives:

- [coding-standards.md](shared/02-tech/coding-standards.md) — code style, architecture, contracts, naming, and technical standards.
- [documentation-guidelines.md](shared/02-tech/documentation-guidelines.md) — documentation rules, change classification, and verification.
- [way-of-working.md](shared/03-ops/way-of-working.md) — branch→commit→PR→review→merge lifecycle and working agreements.
- [ux-guidelines.md](shared/01-product/ux-guidelines.md) — global UX principles.
- [brand-guidelines.md](shared/01-product/brand-guidelines.md) — global brand rules.
- [llm-benchmarks.md](shared/02-tech/llm-benchmarks.md) — LLM benchmarks system explanation.

## Projects

- [veterinary-medical-records](projects/veterinary-medical-records/) — AI-assisted veterinary clinical records processing.

See [projects/README.md](projects/README.md) for the full initiative listing.

## Evaluator first-pass (recommended, 10-15 min)

1. [README.md](../README.md) — Docker-first quickstart, smoke path, and repository overview.
2. [product-design.md](projects/veterinary-medical-records/01-product/product-design.md) — problem framing and intended outcomes.
3. [technical-design.md](projects/veterinary-medical-records/02-tech/technical-design.md) — architecture, contracts, and invariants.
4. [ADR index](projects/veterinary-medical-records/02-tech/adr/index.md) — architecture decision records and trade-off rationale.
5. [ux-design.md](projects/veterinary-medical-records/01-product/ux-design.md) — review workflow and UX interaction guarantees.
6. [backend-implementation.md](projects/veterinary-medical-records/02-tech/backend-implementation.md) and [frontend-implementation.md](projects/veterinary-medical-records/02-tech/frontend-implementation.md) — implementation details.

## Tooling (optional)

- [metrics/llm_benchmarks/README.md](../metrics/llm_benchmarks/README.md) — assistant usage benchmarks.

## Authority & precedence

If documents conflict, resolve in this order:

1. [technical-design.md](projects/veterinary-medical-records/02-tech/technical-design.md) — contracts and invariants
2. [ux-design.md](projects/veterinary-medical-records/01-product/ux-design.md) — interaction contract
3. [product-design.md](projects/veterinary-medical-records/01-product/product-design.md) — system meaning and governance boundary
4. [implementation-plan.md](projects/veterinary-medical-records/04-delivery/implementation-plan.md) — sequencing and acceptance criteria
5. [backend-implementation.md](projects/veterinary-medical-records/02-tech/backend-implementation.md) and [frontend-implementation.md](projects/veterinary-medical-records/02-tech/frontend-implementation.md) — implementation notes

Shared docs (`docs/shared/*`) apply globally within their scope.

## Contribution and quality gates

For daily development and pull-request readiness checks, use the local quality-gate commands listed in [README.md](../README.md#local-quality-gates-before-pushing).

## Dependency justification (Technical Design Appendix E3)

PDF text extraction uses **PyMuPDF** because it provides strong extraction quality for "digital text" PDFs with a small dependency footprint and straightforward integration.
