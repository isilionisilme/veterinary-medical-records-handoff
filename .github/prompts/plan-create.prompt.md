---
agent: agent
description: Create a new plan following project conventions.
---

1. Verify the backlog item exists and is `Planned` or `In Progress`; if not, STOP.
2. Use role taxonomy only: Planning agent owns plan authoring, hard-gate decisions, and prompt preparation; Execution agent owns implementation steps from pre-written prompts. If any protocol step cannot be completed as defined, STOP and report the blocker.
3. Create `docs/projects/veterinary-medical-records/04-delivery/plans/PLAN_<YYYY-MM-DD>_<SLUG>.md` as a single flat file with: title, operational rules pointer, metadata, `Context`, `Objective`, `Scope Boundary`, `Execution Status`, `Prompt Queue`, `Active Prompt`, `Acceptance criteria`, and `How to test`.
4. Initialize metadata exactly as follows: `**Branch:** PENDING PLAN-START RESOLUTION`, `**Worktree:** PENDING PLAN-START RESOLUTION`, `**Execution Mode:** PENDING USER SELECTION`, `**Model Assignment:** PENDING USER SELECTION`.
5. Reserve `Phase 0 — Plan-start preflight` before any implementation phase. Do not put implementation work ahead of Phase 0.
6. Apply branch-first rules in the plan text: work must execute from a dedicated branch, never by direct commits to `main`. Default base is `main` unless the user explicitly names another base.
7. When the plan implies a new branch, follow canonical naming: `feature/<ID>-<slug>` for user stories; `improvement/<slug>` for user-facing improvements; `refactor/<slug>`, `chore/<slug>`, `ci/<slug>`, `docs/<slug>`, or `fix/<slug>` for technical work. Slugs use lowercase letters, numbers, and hyphens.
8. Add `DOC-1` in the documentation task section. If no docs update is needed, record `no-doc-needed` with a brief rationale.
9. Run the PR partition gate with explicit evidence: estimate diff size, classify scope as docs/code/config, assess semantic risk axes, and open a user decision gate if code lines exceed `400`, code files exceed `15`, or the plan mixes high-risk axes without split rationale.
10. If thresholds are exceeded, present `Option A`: keep one PR with explicit rationale, and `Option B`: split into additional PRs with proposed boundaries and dependencies. Without explicit user selection, STOP.
11. When the plan spans multiple Pull Requests, add `## Pull Request Roadmap` before `Execution Status` with columns `Pull Request`, `Branch`, `Phases`, `Scope`, and `Depends on`. Each phase belongs to exactly one Pull Request. Each execution step carries a `**[PR-X]**` tag.
12. Write pre-written prompts for every non-dependent execution block that can be prepared upfront. `Prompt Queue` is ordered; `Active Prompt` starts empty unless execution begins immediately.
13. Keep `Execution Status` atomic: one step per objective, clear hard-gate markers, and no mixed-scope steps.
14. Commit with `docs(plan): create <plan-slug>` only after the plan content is complete.
