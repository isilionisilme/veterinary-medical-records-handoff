<!-- AUTO-GENERATED from canonical source: plan-execution-protocol.md — DO NOT EDIT -->
<!-- To update, edit the canonical source and run: python scripts/docs/generate-router-files.py -->

## 15. Plan Todo Projection (Chat) (Hard Rule)

During plan execution, the agent MUST project plan progress into chat todos.

### Required behavior

1. On continuation-intent requests, read `Execution Status` and create one chat todo per pending plan step (`- [ ]`).
2. Mark exactly one todo as `in_progress`: the current active step.
3. Mark a todo as `completed` only when the corresponding plan step is `[x]`.
4. If a plan step is `🚫 BLOCKED`, keep its todo as `in_progress` and include blocker context in the chat progress update.
5. Keep a rolling window of at least the next 3 pending steps visible in chat todos.
6. Todo titles MUST preserve plan step identifiers (for example: `F2-C — Update wiki section indexes`).

### Synchronization rules

- `PLAN_*.md` checkboxes are the source of truth.
- Chat todos are an execution-time projection and MUST stay synchronized with the plan.
- If plan and chat todos diverge, reconcile immediately from the plan before continuing.

---

## 16. Token-Efficiency Policy

To avoid context explosion:
1. **iterative-retrieval** before each step: load only current state, step objective, target files, guardrails, validation outputs.
2. **strategic-compact** at step close: summarize only the delta, validation, risks, and next move.
3. Do not carry full chat history if not necessary.
4. For chat-switch decisions, apply the **Single-Chat Execution Rule**.

> **Mandatory compact template:**
> - Step: F?-?
> - Delta: <concrete changes>
> - Validation: <tests/guards + result>
> - Risks/Open: <if applicable>

---

## 17. Commit Conventions

All commits in this flow follow the format:
```
<type>(plan-<id>): <short description>
```
Examples:
- `audit(plan-f1a): 12-factor compliance report + backlog`
- `refactor(plan-f2c): split App.tsx into page and API modules`
- `test(plan-f4c): add frontend coverage gaps for upload flow`
- `docs(plan-f5c): add ADR-ARCH-001 through ADR-ARCH-004`

---

## 18. How to Add a New User Story

When asked to add a new User Story, update [`IMPLEMENTATION_PLAN.md`](../04-delivery/IMPLEMENTATION_PLAN.md) in two places:

1. Add the story in the relevant **User Stories (in order)** list for its release.
2. Add or update the full **User Story Details** section for that story.

If the requested story is not yet scheduled in any release, schedule it in the Release Plan:
- Add it to an existing release, or
- Create a new release section when needed.

### Minimal required fields

- **ID** (e.g., `US-22`)
- **Title**
- **Goal** (via `User Story` statement)
- **Acceptance Criteria**
- **Tech Requirements** (in `Authoritative References`)
- **Dependencies** (in `Scope Clarification` and/or ordering references)

### Release assignment rules

- If the requester names a release explicitly, use that release.
- Otherwise, assign to the earliest viable release based on dependencies and existing story order.
- If no existing release is viable, create a new release after the last dependent release.

### Completion checklist

- Story appears in release-level **User Stories (in order)**.
- Story appears in **User Story Details** with required fields.
- Formatting and section structure remain consistent with existing stories.
- No unrelated documentation edits are bundled.
