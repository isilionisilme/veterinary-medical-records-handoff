# Documentation Guidelines

Documentation is a code quality requirement. All AI coding assistants must treat documentation as part of the deliverable and keep it consistent with the implementation.

## Purpose

Documentation must make the system understandable, maintainable, and reviewable by other engineers.
All user-facing written communication must be in English (documentation, pull request titles/descriptions, review comments, ADRs, and release notes).

Document:
- Intent and responsibility
- Contracts and schemas
- Design decisions and tradeoffs

Do not restate obvious code behavior.

Documentation is reviewed together with the code.

## Documentation layers

The project uses three complementary documentation layers. All must stay consistent:

- In-code documentation (docstrings and types)
- API documentation (auto-generated from FastAPI + schemas)
- Repository and architecture documentation (Engineering Playbook; ADR-style notes when explicitly requested)

## In-code documentation rules

AI assistants must add docstrings to:

- Public modules
- Domain and application services
- Public functions and methods
- Non-trivial orchestration logic
- Integration and adapter boundaries

Docstrings must include when relevant:

- Purpose and responsibility
- Inputs and outputs
- Requirements and invariants
- Error conditions and exceptions
- Side effects and state changes

Docstring style requirements:

- Use Google-style docstrings
- Follow PEP 257 structure
- First line: short summary sentence
- Then structured sections when applicable (Args, Returns, Raises, Side Effects, Notes)

Do NOT add docstrings for:

- Trivial helpers
- Self-explanatory one-liners
- Simple pass-through logic
- Code already fully clear from names and types

## Types and contracts

- All public functions and methods must include type hints.
- Treat **type annotations, signatures, and schemas** as part of the documentation contract.
- Ensure all public interfaces include explicit types or schemas when supported.
- Do not duplicate type information in docstrings when already explicit in signatures.

## API documentation rules

For every HTTP endpoint, AI assistants must ensure:

- Route includes summary and description
- Explicit request and response models are defined
- Schema fields include meaningful descriptions

API documentation generated via OpenAPI/Swagger from:

- FastAPI route metadata
- Pydantic model field descriptions
- Type annotations

This auto-generated API documentation is considered part of the deliverable.

## Public interface documentation

For any public interface (API, service, adapter, or module boundary):

- Add a short summary.
- Add a behavior description if not obvious.
- Document input/output contracts.
- Add parameter/field descriptions where they add clarity.
- Prefer metadata compatible with automatic documentation generators when available.

## Architecture and design documentation

Architecture and structural rules must be documented outside the code in the Engineering Playbook.

AI assistants must NOT invent or modify architecture or design documents unless explicitly instructed.

When explicitly requested, record non-obvious technical decisions as short ADR-style notes including:

- Decision
- Rationale
- Tradeoffs

## Commenting rules

Comments must explain:

- Why a decision was made
- Why alternatives were rejected
- Domain assumptions
- Non-obvious requirements

Comments must NOT:

- Repeat what the code literally does
- Describe syntax-level behavior
- Drift from the implementation

Outdated comments must be removed or updated in the same change.

## Documentation maintenance rule

When a change modifies:

- Public behavior
- Contracts
- Data schemas
- Module responsibilities

AI assistants must update the corresponding documentation in the same change set.

A change is not complete if implementation and documentation diverge.

## How to add a new User Story

When asked to add a new User Story, update [`docs/projects/veterinary-medical-records/04-delivery/implementation-plan.md`](../../../projects/veterinary-medical-records/04-delivery/implementation-plan.md) in two places:

1) Add the story in the relevant **User Stories (in order)** list for its release.
2) Add or update the full **User Story Details** section for that story.

If the requested story is not yet scheduled in any release, schedule it in the Release Plan:

- Add it to an existing release, or
- create a new release section when needed.

Minimal required fields for each story detail entry:

- ID (e.g., `US-22`)
- Title
- Goal (via `User Story` statement)
- Acceptance Criteria
- Tech Requirements (in `Authoritative References`)
- Dependencies (in `Scope Clarification` and/or ordering references)

Deterministic release assignment rules:

- If the requester names a release explicitly, use that release.
- Otherwise assign to the earliest viable release based on dependencies and existing story order.
- If no existing release is viable, create a new release after the last dependent release.

Completion checklist before finishing:

- Story appears in release-level **User Stories (in order)**.
- Story appears in **User Story Details** with required fields.
- Formatting and section structure remain consistent with existing stories.
- No unrelated documentation edits are bundled.

Workflow reference:
- Follow `docs/agent_router/04_PROJECT/IMPLEMENTATION_PLAN/65_add-user-story-workflow.md`.

---
