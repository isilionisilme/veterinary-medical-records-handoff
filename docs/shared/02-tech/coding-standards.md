---
title: "Coding Standards"
type: reference
status: active
audience: all
last-updated: 2026-03-09
---

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [Coding Standards](#coding-standards)
  - [Purpose](#purpose)
  - [Change Discipline](#change-discipline)
  - [Code Style & Consistency](#code-style--consistency)
  - [Structure & Separation of Concerns](#structure--separation-of-concerns)
  - [Explicit Contracts & Schemas](#explicit-contracts--schemas)
  - [State Management & Workflow Safety](#state-management--workflow-safety)
  - [Traceability & Human Control](#traceability--human-control)
  - [Error Handling & Observability](#error-handling--observability)
    - [Error classification](#error-classification)
    - [Observability & metrics](#observability--metrics)
  - [Testing Discipline](#testing-discipline)
  - [Data Handling & Safety](#data-handling--safety)
  - [Configuration & Environment Separation](#configuration--environment-separation)
  - [Versioning & Evolution](#versioning--evolution)
  - [Dependency Management](#dependency-management)
  - [Naming Conventions](#naming-conventions)
    - [API and endpoints](#api-and-endpoints)
    - [Domain concepts and models](#domain-concepts-and-models)
    - [Lifecycle states](#lifecycle-states)
    - [Persistence artifacts](#persistence-artifacts)
  - [Architectural Layering (Review Criteria)](#architectural-layering-review-criteria)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

---

title: "Coding Standards" type: reference status: active audience: all last-updated: 2026-03-09

---

# Coding Standards

> **Canonical source of truth.** This document is the single authoritative reference for all technical coding standards
> in this project.
>
> **Governance:**
>
> - This file is a canonical document maintained by humans.
> - Derived router modules are generated from this canonical source.
> - Flow is **canonical → router only**. Router files MUST NOT be edited directly.
> - Any direct edit to a router file may be overwritten during the next regeneration cycle.

---

## Purpose

These standards define the **mandatory technical rules** for all code in this project. They apply to every approved
implementation and must be followed consistently by all contributors (human and AI). These standards are normative for
implementation and review decisions.

AI assistants must not silently skip or partially comply with these standards. If a standard cannot be satisfied, they
must stop and explain the blocker before proceeding.

---

## Change Discipline

- Implement **one user story at a time** (or a single technical concern for non-story work).
- Do **not** bundle unrelated changes.
- Keep commits logically scoped to a single story (or a single technical concern for non-story work).

---

## Code Style & Consistency

- Follow **PEP 8** conventions consistently across the codebase.
- Prefer **clear, readable naming** over brevity.
- Prefer **explicitness to cleverness**.
- Use **type hints** where they add clarity, especially in:
  - Public APIs
  - Domain services
  - Schemas and data transfer objects

---

## Structure & Separation of Concerns

- Keep **domain logic independent** from frameworks and infrastructure.
- FastAPI routes must act as **thin adapters only**, limited to:
  - Input validation
  - Orchestration
  - Response mapping
- **Business rules must live in domain services**, never in API handlers.
- Access persistence, file storage, and external services **only through explicit interfaces or adapters**.

---

## Explicit Contracts & Schemas

- Define and validate **all API inputs and outputs** using explicit schemas.
- Internal data passed between components must follow **well-defined contracts**.
- Structured domain records must be **schema-validated and versioned**.

---

## State Management & Workflow Safety

- Model **lifecycle states explicitly** and persist them.
- State transitions must be **deterministic and safe to retry**.
- Every state change must be **observable and auditable**.

---

## Traceability & Human Control

- **Never silently overwrite human edits**.
- Persist human corrections as **append-only revisions**, including:
  - Before value
  - After value
  - Timestamp
- Preserve the ability to **distinguish machine-generated data from human-validated data**.

---

## Error Handling & Observability

### Error classification

- Classify errors clearly:
  - User-facing errors
  - Internal/system errors
- **Fail explicitly and early** when inputs or states are invalid.
- Log key operations and state transitions using **correlation identifiers**.

### Observability & metrics

- Key pipeline stages must be **measurable** (e.g., processing time per stage).
- Failures must be **attributable to specific workflow stages**.

---

## Testing Discipline

- Domain logic must be **testable independently** from frameworks and infrastructure.
- Automated tests must cover:
  - Happy paths
  - Meaningful failure scenarios
- Integration tests must validate **critical end-to-end flows**.

---

## Data Handling & Safety

- Treat **external inputs as untrusted by default**.
- Validate file **type and size before processing**.
- Store **raw files outside the database**; persist only references.
- Persist metadata, states, structured outputs, and audit information in the database.

---

## Configuration & Environment Separation

- Configuration must be **environment-driven**.
- No environment-specific values are hardcoded.
- **Secrets are never committed** to the repository.

---

## Versioning & Evolution

- APIs and schemas must be **versioned from the start**.
- Prefer **backward-compatible changes** over breaking ones.
- Schema evolution must be **explicit and intentional**.

---

## Dependency Management

- Keep the dependency footprint **minimal**.
- Do **not introduce new third-party dependencies by default**.
- Prefer **standard library solutions** when reasonable.
- Any new dependency must be **explicitly justified**.

---

## Naming Conventions

> Git naming conventions (branches, commits, Pull Requests) are defined in
> [way-of-working.md §2–§5](../03-ops/way-of-working.md).

### API and endpoints

- Use clear, predictable REST conventions, for example:
  - `POST /documents/upload`
  - `GET /documents/{id}`
  - `GET /documents/{id}/download`
  - `GET /documents/{id}/text`
  - `PUT /documents/{id}/structured-data`

### Domain concepts and models

- Use explicit, domain-oriented names for core concepts, such as:
  - `Document`
  - `ProcessingStatus`
  - `ExtractedText`
  - `StructuredMedicalRecord`
  - `FieldEvidence`
  - `RecordRevision`

### Lifecycle states

- Lifecycle states must be enums using **UPPERCASE_SNAKE_CASE**, for example:
  - `UPLOADED`
  - `TEXT_EXTRACTED`
  - `STRUCTURED`
  - `READY_FOR_REVIEW`

### Persistence artifacts

- Use consistent, descriptive table names, such as:
  - `documents`
  - `document_status_history`
  - `document_text_artifacts`
  - `document_structured_artifacts`
  - `field_evidence`

---

## Architectural Layering (Review Criteria)

When reviewing code, validate correct layering and dependency direction:

1. **Domain layer** (`domain/`): No framework or database imports. Pure business logic, frozen dataclasses, domain
   services.
2. **Application layer** (`application/`): Depends only on `domain/` and `ports/`. Orchestration and use cases.
3. **API layer** (`api/`): Thin HTTP adapter only — mapping and validation. No SQL or business logic.
4. **Infrastructure layer** (`infra/`): Persistence, I/O, and external service adapters only.

Maintainability priorities (in order):

- Clear naming and responsibilities
- Low duplication
- Small, cohesive modules and functions
- Logic located in the correct layer

Testability requirements:

- Core application logic must be testable without FastAPI or SQLite.
- Unit tests for services; integration tests for HTTP + wiring.

Simplicity principle:

- Flag overengineering risks.
- Prefer removing complexity over adding abstraction.
- Prefer small, high-impact fixes over large refactors.
- Do not propose new dependencies or architectural patterns unless explicitly required.
