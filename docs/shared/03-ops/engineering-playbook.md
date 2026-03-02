# Engineering Guidelines

**Purpose**  
These guidelines define the **mandatory engineering standards** for this project.  
They apply to **all approved implementations** and must be followed consistently by the AI Coding Assistant.

If any guideline cannot be satisfied, **STOP and explain the blocker before proceeding**.

---
## Change discipline
- Implement **one user story at a time** (or a single technical concern for non-story work).
- Do **not** bundle unrelated changes.
- Keep commits logically scoped to a single story (or a single technical concern for non-story work).

## Code style & consistency
- Follow **PEP 8** conventions consistently across the codebase.
- Prefer **clear, readable naming** over brevity.
- Prefer **explicitness to cleverness**.
- Use **type hints** where they add clarity, especially in:
  - Public APIs
  - Domain services
  - Schemas and data transfer objects

---

## Structure & separation of concerns
- Keep **domain logic independent** from frameworks and infrastructure.
- FastAPI routes must act as **thin adapters only**, limited to:
  - Input validation
  - Orchestration
  - Response mapping
- **Business rules must live in domain services**, never in API handlers.
- Access persistence, file storage, and external services **only through explicit interfaces or adapters**.

---

## Explicit contracts & schemas
- Define and validate **all API inputs and outputs** using explicit schemas.
- Internal data passed between components must follow **well-defined contracts**.
- Structured domain records must be **schema-validated and versioned**.

---

## State management & workflow safety
- Model **lifecycle states explicitly** and persist them.
- State transitions must be **deterministic and safe to retry**.
- Every state change must be **observable and auditable**.

---

## Traceability & human control
- **Never silently overwrite human edits**.
- Persist human corrections as **append-only revisions**, including:
  - Before value
  - After value
  - Timestamp
- Preserve the ability to **distinguish machine-generated data from human-validated data**.

---

## Error handling & observability
- Classify errors clearly:
  - User-facing errors
  - Internal/system errors
- **Fail explicitly and early** when inputs or states are invalid.
- Log key operations and state transitions using **correlation identifiers**.

---

## Observability & metrics
- Key pipeline stages must be **measurable** (e.g. processing time per stage).
- Failures must be **attributable to specific workflow stages**.

---

## Testing discipline
- Domain logic must be **testable independently** from frameworks and infrastructure.
- Automated tests must cover:
  - Happy paths
  - Meaningful failure scenarios
- Integration tests must validate **critical end-to-end flows**.

---

## Data handling & safety
- Treat **external inputs as untrusted by default**.
- Validate file **type and size before processing**.
- Store **raw files outside the database**; persist only references.
- Persist metadata, states, structured outputs, and audit information in the database.

---

## Configuration & environment separation
- Configuration must be **environment-driven**.
- No environment-specific values are hardcoded.
- **Secrets are never committed** to the repository.

---

## Versioning & evolution
- APIs and schemas must be **versioned from the start**.
- Prefer **backward-compatible changes** over breaking ones.
- Schema evolution must be **explicit and intentional**.

---

## Dependency management
- Keep the dependency footprint **minimal**.
- Do **not introduce new third-party dependencies by default**.
- Prefer **standard library solutions** when reasonable.
- Any new dependency must be **explicitly justified**.

---

## Documentation Guidelines

Documentation is a code quality requirement. All AI coding assistants must treat documentation as part of the deliverable and keep it consistent with the implementation.

### Purpose

Documentation must make the system understandable, maintainable, and reviewable by other engineers.
All user-facing written communication must be in English (documentation, pull request titles/descriptions, review comments, ADRs, and release notes).

Document:
- Intent and responsibility
- Contracts and schemas
- Design decisions and tradeoffs

Do not restate obvious code behavior.

Documentation is reviewed together with the code.

### Documentation layers

The project uses three complementary documentation layers. All must stay consistent:

- In-code documentation (docstrings and types)
- API documentation (auto-generated from FastAPI + schemas)
- Repository and architecture documentation (Engineering Playbook; ADR-style notes when explicitly requested)

### In-code documentation rules

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

### Types and contracts

- All public functions and methods must include type hints.
- Treat **type annotations, signatures, and schemas** as part of the documentation contract.
- Ensure all public interfaces include explicit types or schemas when supported.
- Do not duplicate type information in docstrings when already explicit in signatures.

### API documentation rules

For every HTTP endpoint, AI assistants must ensure:

- Route includes summary and description
- Explicit request and response models are defined
- Schema fields include meaningful descriptions

API documentation generated via OpenAPI/Swagger from:

- FastAPI route metadata
- Pydantic model field descriptions
- Type annotations

This auto-generated API documentation is considered part of the deliverable.

### Public interface documentation

For any public interface (API, service, adapter, or module boundary):

- Add a short summary.
- Add a behavior description if not obvious.
- Document input/output contracts.
- Add parameter/field descriptions where they add clarity.
- Prefer metadata compatible with automatic documentation generators when available.

### Architecture and design documentation

Architecture and structural rules must be documented outside the code in the Engineering Playbook.

AI assistants must NOT invent or modify architecture or design documents unless explicitly instructed.

When explicitly requested, record non-obvious technical decisions as short ADR-style notes including:

- Decision
- Rationale
- Tradeoffs

### Commenting rules

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

### Documentation maintenance rule

When a change modifies:

- Public behavior
- Contracts
- Data schemas
- Module responsibilities

AI assistants must update the corresponding documentation in the same change set.

A change is not complete if implementation and documentation diverge.

### How to add a new User Story

When asked to add a new User Story, update [`docs/projects/veterinary-medical-records/04-delivery/IMPLEMENTATION_PLAN.md`](../../projects/veterinary-medical-records/04-delivery/IMPLEMENTATION_PLAN.md) in two places:

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
- For this operation, use this section together with the canonical implementation plan in [`docs/projects/veterinary-medical-records/04-delivery/IMPLEMENTATION_PLAN.md`](../../projects/veterinary-medical-records/04-delivery/IMPLEMENTATION_PLAN.md).

---

## Naming conventions

### Git and delivery workflow

- **Branches**
  - User stories:
    - `feature/<ID>-<short-representative-slug>`
    - The slug must be concise and describe the purpose of the user story.
  - Improvements:
    - `improvement/<short-slug>`
    - User-facing changes that improve a previous implementation. 
  - Technical non-user-facing work (refactors, chores, CI, docs, fixes):
    - `refactor/<short-slug>`
    - `chore/<short-slug>`
    - `ci/<short-slug>`
    - `docs/<short-slug>`
    - `fix/<short-slug>`
  - Branches must be short-lived and focused on a single user story or a single technical concern.

- **Commits**
  - User stories:
    - `Story <ID>: <short imperative description>`
  - Technical work:
    - `<type>: <short imperative description>`
    - Allowed types:
      - `refactor`
      - `chore`
      - `ci`
      - `docs`
      - `test`
      - `build`
      - `fix`
  - Commit messages must be clear, specific, and written in imperative form.
  - Each commit should represent a coherent logical step.

- **Pull Requests**
  - User stories:
    - `Story <ID> — <Full User Story Title>`
  - Technical work:
    - `<type>: <short description>`
  - Each Pull Request must relate to:
    - exactly one user story, or
    - exactly one technical concern.
  - Pull Requests must remain small enough to be reviewed comfortably in isolation.

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

# Way of Working 

You are implementing work for this initiative and must strictly follow the Way of Working described below.

If an implementation conflicts with any of these rules, stop and explain the conflict instead of proceeding.

## Starting New Work (Branch First)

Before making any new changes (code, docs, config, etc.), create a new branch off the appropriate base (default: `main`) using the branch naming conventions defined in this document.

This is the default rule for AI assistants and automation in this repository.

STOP and ask for confirmation only if the repository state is unsafe or ambiguous (examples: uncommitted changes, merge/rebase in progress, conflicts, or it is unclear whether the current branch already corresponds to the intended work item).

### Procedure

1) Confirm repository state is safe:
   - Working tree is clean (no uncommitted changes).
   - No merge/rebase in progress.
   - If not safe, STOP and ask before proceeding.

2) Ensure the correct base branch:
   - Default base is `main` unless the user explicitly specifies another base.
   - Switch to base and update it (for `main`: `git switch main` then `git pull origin main`).

3) Create the branch before editing any files:
   - If already on a correctly named branch for the same work item, proceed.
   - Otherwise, create a new branch from the updated base (for example: `git switch -c <branch-name>`).
   - If it is ambiguous whether the current branch is the correct work branch, STOP and ask.

## Delivery Model (Releases)
- Work is delivered using vertical slices, referred to as releases.
- A release represents a complete increment of user-facing value.
- A release may span multiple user stories across different epics.
- Each release must be coherent, end-to-end, and meaningful from a user perspective.
- Releases must not be isolated technical components.

Each release must result in:
- A runnable and testable system state
- Clear, observable user-facing behavior
- Explicitly persisted data and state transitions
- Automated test coverage for the delivered functionality

## Branching Strategy
- The default branching strategy is Feature Branching.
- Work is developed in short-lived branches on top of a stable `main` branch.
- `main` always reflects a runnable, test-passing state.
- Each change is implemented in a dedicated branch:
  - User stories use the story branch naming convention.
  - Technical non user-facing work (refactors, chores, CI, docs, fixes) uses the technical branch naming convention.
- Branches are merged once the change is complete and reviewed.
- Teams are encouraged to adopt a different strategy if they believe it better suits their context.

## Commit Discipline
- Commits are small and scoped to a single logical change.
- A commit must never span multiple user stories.
- A change may be implemented through multiple commits.
- Commit history must remain readable to support reasoning and review.

## Pull Requests
- A pull request is opened for each user story or each technical non user-facing change (refactors, chores, CI, docs, fixes).
- Pull requests are opened once the change is fully implemented and all automated tests are passing.
- Each pull request must be small enough to be reviewed comfortably in isolation and should focus on a single user story or a single technical concern.

### Plan-level PR Roadmap

When a plan (`PLAN_*.md`) spans work large enough to require more than one Pull Request, the plan must include a **PR Roadmap** section that maps execution phases to PRs.

Rules:

- Add a `## PR Roadmap` section after the Scope Boundary and before the Estado de ejecución.
- The roadmap is a table with columns: **PR** (identifier or link), **Rama** (branch name), **Fases** (which plan phases it covers), **Alcance** (short description), **Depende de** (prerequisite PR).
- Each phase belongs to exactly one PR. A phase must **not** be split across PRs.
- Each execution step in the Estado de ejecución must carry a `**[PR-X]**` tag indicating which PR it belongs to.
- A PR is merged only when all its assigned phases pass CI and user review.
- The roadmap is written when the plan is created or when scope grows beyond a single PR. It may be updated as phases are completed.

This ensures reviewable, isolated PRs while maintaining a clear dependency chain across the full plan.

### Pull Request Automation (AI Assistants)

When an AI coding assistant or automation tool is used to create or update a Pull Request in this repository, it must follow this procedure automatically. This operational rule complements the existing Pull Request and Code Review policies and does not replace them.

### Pull Request Procedure

1) Confirm repository state before creating the PR:
   - Current branch name
   - Base branch (main)
   - Working tree status (report if not clean)

2) Create or update the Pull Request to `main` using the standard branching and naming conventions already defined in this document.
   - PR title, body, and review comments must be written in English.
   - When setting the PR description/body from CLI, use real multiline content (heredoc or file input), not escaped `\n` sequences.
   - Do not submit PR bodies that contain literal `\n`.
   - Preferred patterns:
     - `gh pr create --body-file <path-to-markdown-file>`
     - PowerShell here-string (`@' ... '@`) assigned to a variable and passed to `--body`

3) Check CI status (if configured):
   - Report whether CI is pending, passing, or failing.
   - Include end-user validation steps in the PR description when applicable; if not applicable, state why and provide alternative verification steps.

4) Classify the PR by file types (use changed file paths; do not require reading full diff content):
   - **Docs-only PR**: the diff contains **only**:
     - `docs/**`
     - `*.md`, `*.txt`, `*.rst`, `*.adoc`
   - **Code PR**: the diff contains **any** code file, such as:
     - `*.py`
     - `*.ts`, `*.tsx`
     - `*.js`, `*.jsx`
     - `*.css`, `*.scss`
     - `*.html`
     - `*.sql`
   - **Non-code, non-doc PR**: the diff contains files that are neither docs nor code (examples: `*.json`, `*.yaml`, `*.yml`, `*.toml`, `*.ini`, `*.env`).

5) For PRs that change `frontend/**` or user-visible behavior/copy:
  - Review canonical UX/brand sources before implementation/review: [`docs/shared/UX_GUIDELINES.md`](UX_GUIDELINES.md), [`docs/projects/veterinary-medical-records/01-product/UX_DESIGN.md`](../../projects/veterinary-medical-records/01-product/UX_DESIGN.md), and [`docs/shared/BRAND_GUIDELINES.md`](BRAND_GUIDELINES.md).
   - Add a `UX/Brand compliance` section to the PR description with concrete evidence.

6) Ask the user whether they want a code review:
   - Ask explicitly for every PR classification (docs-only, code, non-code/non-doc).
   - For docs-only PRs, recommend skipping the review by policy unless the user explicitly asks for one.
   - Run the review only after explicit user confirmation.

7) Perform a maintainability-focused code review of the PR diff (when user-approved):
   - Use `git diff main...HEAD` as the review input.
   - Apply all rules from:
     "Code Review Guidelines (Maintainability-Focused, Take-Home Pragmatic)"

### Pull Request review visibility

After producing a PR code review, the AI assistant must publish the review output as a comment in the Pull Request (or update an existing “AI Code Review” comment), using the mandatory review output format.

For `frontend/**` or user-visible changes, that PR review comment must include a dedicated `UX/Brand Compliance` section.

If one or more review findings are addressed in subsequent commits, the AI assistant must add a brief follow-up comment summarizing which findings were addressed.

If the PR changes after review (new commits that materially affect the diff), the AI assistant must add a follow-up comment summarizing what changed and whether the previous findings are still applicable.

If the AI assistant cannot post a comment to the Pull Request (for example due to missing PR reference, missing GitHub CLI access, or authentication), STOP and ask the user before proceeding. Do not treat chat-only output as satisfying the “publish to PR” requirement.

For docs-only PRs, no review comment is required (review is skipped by policy).

### Post-merge Cleanup (AI Assistants)

After the user confirms that a Pull Request has been **merged into `main`**, the AI assistant must run the following **post-merge cleanup** procedure automatically.

Only STOP and ask for confirmation if the repository state is unsafe or ambiguous (examples: uncommitted changes, rebase/merge in progress, conflicts, or unclear stash purpose/ownership).

#### Post-merge cleanup checklist

1) Ensure the working tree is clean:
   - If there are uncommitted changes, STOP and ask before proceeding.
   - If a merge/rebase is in progress, STOP and ask before proceeding.

2) Check for existing stashes:
   - List stashes (`git stash list`).
   - If a stash is clearly related to the merged branch and no longer needed, delete it (`git stash drop ...`).
   - If there is any ambiguity about a stash (purpose unclear, potentially still needed), STOP and ask before deleting it.

3) Switch to `main`.

4) Pull the latest changes from `origin/main` into local `main`.

5) Delete the **local** branch that was used for the merged PR:
   - If the branch is currently checked out, switch to `main` first.
   - Try safe deletion first: `git branch -d <branch>`.
   - If deletion fails due to “not fully merged” (common with squash merges):
     - Verify the branch has **no unique commits** relative to `main` (for example: `git log <branch> --not main`).
     - If there are no unique commits, it is safe to force delete: `git branch -D <branch>`.
     - If unique commits exist, STOP and ask what to do.

By default, this procedure deletes only local state (local branches and stashes). Do not delete remote branches unless explicitly requested.


## Code Reviews

Apply the following rules by default to every future code review in this repo unless explicitly overridden.

- Reviews focus on:
  - Correctness and alignment with the intended behavior
  - Clarity, readability, and maintainability
  - Adherence to the Engineering Guidelines and architectural intent
  - Explicit handling of edge cases, errors, and state transitions
  - Test coverage and test quality

### Code Review stance

- Reviews must be constructive and pragmatic.
- Prioritize shared understanding and long-term code health over stylistic preferences.
- Optimize for clarity, testability, and low coupling.
- Prefer small, high-impact fixes over large refactors.
- Avoid overengineering suggestions.
- Do not propose new dependencies or new architectural patterns unless explicitly required.

### Code Review Guidelines

When performing code reviews in this repository, use a **maintainability-focused** review style.

Review emphasis:
- Keep changes within the requested scope.
- Keep the dependency footprint minimal; add dependencies only when needed.
- Keep architecture consistent with the agreed design; introduce new patterns only when a story/design requires it.
- Keep solutions lightweight and easy to explain to evaluators.

Primary review focus (in order):
1) Layering and dependency direction:
   - `domain` has no framework/db imports
   - `application` depends only on `domain` + `ports`
   - `api` is thin (HTTP + mapping only; no SQL/business logic)
   - `infra` contains persistence/IO only
2) Maintainability:
   - clear naming and responsibilities
   - low duplication
   - small, cohesive modules/functions
   - logic located in the correct layer
3) Testability:
   - core application logic testable without FastAPI or sqlite
   - presence and quality of unit tests for services
   - integration tests cover HTTP + wiring
4) Simplicity over purity:
   - flag overengineering risks
   - prefer removing complexity over adding abstraction
5) CI and tooling sanity:
   - workflows valid
   - tests and lint runnable and reproducible

### Code Review Output Format

Produce the review using this mandatory output format:
   - Must-fix (blocking maintainability or correctness issues)
   - Should-fix (strong recommendations)
   - Nice-to-have (optional improvements)
   - Questions / assumptions

For PRs that include `frontend/**` or user-visible behavior/copy changes, include:
   - UX/Brand Compliance (mandatory section)
   - Any UX/Brand non-compliance must be reported under Must-fix.

Each finding must include:
- File reference(s)
- Short rationale
- Minimal suggested change

### Code Review Safety rule

After producing a PR code review, STOP and wait for explicit user instruction before making any code changes.

Do not modify code as part of the review step unless explicitly asked to do so.

## User Story kickoff checklist

Before implementing each user story (US-XX), the AI assistant must:

1) Read the story requirements and the relevant authoritative design requirements.
2) Identify **decision points** required to implement the story that are not explicitly specified.
   - Examples: file size limits, storage roots, timeout values, retry counts, error code enums, default configuration values.
3) Resolve **discoverable facts** by inspecting the repository first (code/config/docs).
   - Do not ask the user questions that can be answered by reading the repo.
4) Ask the user to confirm or choose for **non-discoverable preferences/tradeoffs**.
   - Present 2–4 meaningful options and recommend a default.
   - Do not proceed while any high-impact ambiguity remains; **STOP and ask**.
5) Record the resulting decisions/assumptions explicitly in the PR description (and/or ADR-style note when requested).

## Definition of Done
A change is considered done when it satisfies the criteria that apply to its type (user story or technical change).

For user stories:
- It delivers a complete vertical slice of user-facing value.
- It is documented (README and/or ADR if a design decision was made).
- If user-visible behavior is affected, UX guidance is applied from `docs/shared/UX_GUIDELINES.md` and `docs/projects/veterinary-medical-records/01-product/UX_DESIGN.md`.
- If visual identity or user-facing copy is affected, brand guidance is applied from `docs/shared/BRAND_GUIDELINES.md`.
- When the user story is completed, `docs/projects/veterinary-medical-records/04-delivery/IMPLEMENTATION_PLAN.md` is updated in the same change and the story includes `**Status**: Implemented (YYYY-MM-DD)`.
- Backfilling status/date for previously implemented stories is allowed when explicitly requested.

For technical non user-facing changes (refactors, chores, CI, docs, fixes):
- The change intent and scope are explicitly documented in the Pull Request.
- Behavior is preserved, or any intended behavior change is clearly explained and justified.

For all changes:
- The resulting code remains easy to understand, extend, and evolve without refactoring core logic.
- Automated tests pass, and test coverage is updated where applicable.
- For any implemented change that is testable from an end-user perspective (feature, fix, technical improvement, or small in-flight adjustment), the assistant final response must include clear step-by-step validation instructions from the end-user point of view.
- When end-user testing is not possible, the completion report must explicitly state that and provide the best alternative verification method (for example: API checks, logs, automated tests, or controlled manual simulation).
- The change is merged into main via Pull Request.
- Continuous Integration (CI) has run and passed successfully.
- `main` remains in a green (passing) state after the merge.

## Execution Rule
- Always prefer completing a smaller, well-defined user story over partially implementing a larger one.
- Validate every implementation explicitly against the Definition of Done.
- Do not bypass reviews, tests, or workflow rules to accelerate delivery.
