# US-42 — Provide evaluator-friendly installation & execution (Docker-first)

**Status**: Implemented (2026-02-19)

**User Story**
As an evaluator,
I want to install and run the full application locally with minimal setup (Docker-first),
so that I can validate MVP behavior quickly and reliably.

**Scope Clarification**
- Delivery and operability only (packaging + instructions).
- Must not change product behavior, API semantics, confidence model semantics, or UX behavior beyond what is required to run the system.

**Acceptance Criteria**
1. One-command run (preferred target)
- Running `docker compose up --build` (or equivalent documented command) starts the system in a usable local configuration:
  - backend API
  - frontend web app
  - required local persistence/storage with deterministic defaults
- After startup, the app is usable from a browser at documented URLs/ports.
2. Clear evaluator run instructions
- README (or a doc linked from README) includes:
  - prerequisites (Docker / Docker Compose)
  - exact commands to run the app
  - URLs/ports for frontend and backend
  - how to run automated tests (backend + frontend)
  - minimal manual smoke test steps (e.g., upload -> preview -> structured view -> edit; and any other MVP flows implemented, such as mark reviewed if available)
  - known limitations / assumptions and expected behavior
3. Config hygiene
- Provide `.env.example` (or documented defaults) requiring no secrets.
- The app runs without external services.
4. Optional QoL (non-blocking)
- Convenience wrappers (e.g., `make run`, `make test`) if feasible.

**Out of Scope**
- No new product capabilities.
- No changes to confidence computation/propagation semantics or UX beyond what is required to run.

**Fallback (only if needed)**
- If full FE+BE Dockerization is not feasible, allow:
  - backend via Docker + documented local run for frontend,
  - but the primary target remains full Docker Compose.

**Authoritative References**
- Exercise deliverables requirement at a high level for evaluator installation and execution readiness.
- Engineering playbook expectations for documented runbook quality, when applicable.

**Test Expectations**
- Evaluator can run the documented commands and access the frontend/backend at documented URLs/ports.
- Automated test commands (backend + frontend) and minimal smoke test steps are executable from provided instructions.

**Definition of Done (DoD)**
- Acceptance criteria satisfied.
- Delivery/run instructions are complete enough for evaluator execution without hidden setup steps.

---
