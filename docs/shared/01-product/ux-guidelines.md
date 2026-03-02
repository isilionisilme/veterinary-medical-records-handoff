# UX Guidelines — Shared Principles

This document defines the **global UX principles and interaction guidelines**
that apply to **all products and initiatives** developed at Barkibu.

It is **project-agnostic** and must not contain product- or initiative-specific
flows, behaviors, roles, or domain assumptions.

If any UX decision depends on product context, it must be defined in the
corresponding **project-level UX document** (e.g. [`docs/projects/veterinary-medical-records/01-product/ux-design.md`](../../projects/veterinary-medical-records/01-product/ux-design.md)).

---

## Scope and Authority

This document defines:

- Shared UX principles
- Global interaction heuristics
- Accessibility and usability expectations
- Cross-product consistency rules

This document does **not** define:

- Concrete user flows
- Role-specific behaviors
- Domain-specific UX rules
- Confidence semantics or thresholds
- Review, governance, or approval workflows
- Product strategy or prioritization

Those belong in **project-level UX design documents**.

---

## Core UX Principles

All Barkibu products must follow these principles:

- **Clarity over cleverness**  
  Interfaces must be understandable at a glance.

- **Reduce cognitive load**  
  Prefer simple, progressive interactions over dense or overloaded screens.

- **Progressive disclosure**  
  Reveal complexity only when it is relevant to the user’s current task.

- **Avoid unnecessary friction**  
  Do not introduce steps, confirmations, or controls without clear user value.

- **Make system state explicit**  
  Users must always understand what the system is doing and why.

---

## Human-in-the-Loop (Shared Principle)

All Barkibu products follow a **human-in-the-loop philosophy**:

- Automated outputs are **assistive by default**.
- High-stakes decisions require **explicit human confirmation**.
- Systems must remain **explainable and auditable**.

How this philosophy is realized in concrete workflows (review, editing,
confirmation, escalation) is **project-specific** and must not be defined here.

---

## Confidence & Uncertainty (Shared Principle)

When confidence, uncertainty, or quality signals are exposed in a UI:

- They **guide attention**, not decisions.
- They **must not block** user actions.
- They **must not imply correctness or authority**.

The exact semantics, thresholds, visual encoding, or prioritization rules for
confidence are **project-specific**.

---

## Accessibility & Usability

All products must:

- Follow basic accessibility standards (contrast, legibility, focus states).
- Support keyboard navigation where applicable.
- Avoid relying on color alone to convey meaning.
- Use consistent interaction patterns across similar contexts.

Accessibility requirements beyond these shared expectations are defined
per project.

---

## Role-Specific Workflows

Role definitions (e.g. veterinarian, reviewer, admin), responsibilities,
and workflows:

- Must **not** be defined in shared UX guidelines.
- Must live in **project-level UX design documents**.

This prevents accidental coupling between unrelated initiatives.

---

## Governance & Review (Shared Boundary)

If a product includes governance, review, or approval mechanisms:

- The UX must clearly separate operational users from governance roles.
- Governance must not block normal user workflows by default.

Concrete governance UX models are **not defined by this document**.

---

## Delegation Rule (Mandatory)

For any UX decision that depends on:

- Domain semantics
- User roles or permissions
- Product strategy or goals
- Confidence interpretation
- Review, learning, or governance workflows

This document **must defer** to the corresponding project-level UX document
(e.g. [`docs/projects/veterinary-medical-records/01-product/ux-design.md`](../../projects/veterinary-medical-records/01-product/ux-design.md)).

If no such document exists, **STOP and ask** before inventing UX behavior.

---

## Final Rule

This document defines **principles and boundaries**, not product behavior.

If a concrete UX decision cannot be resolved using only the rules above,
it does **not** belong here.
