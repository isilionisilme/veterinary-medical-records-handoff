# Add User Story Workflow

Use this workflow when asked to add a new User Story to the plan.

## Required updates in `docs/projects/veterinary-medical-records/04-delivery/implementation-plan.md`

Update the plan in exactly two places:

1) Release Plan section:
- Add the story to the correct **User Stories (in order)** list under a release.
- If no release is viable, create a new release section.

2) User Story Details section:
- Add (or update) the full story section using the existing story format.

## Minimal required fields for story details

- ID (e.g., `US-22`)
- Title
- Goal (the `User Story` statement)
- Acceptance Criteria
- Tech Requirements (via `Authoritative References`)
- Dependencies (via `Scope Clarification` and/or ordering references)

## Deterministic release assignment rules

- If the requester specifies a release, use that release.
- Otherwise choose the earliest viable release based on dependencies and existing story order.
- If no existing release is viable, create a new release immediately after the latest dependent release.

## Completion checklist

- Story appears in Release Plan **User Stories (in order)**.
- Story appears in **User Story Details** with required fields.
- Formatting and ordering conventions match existing stories.
- No unrelated document edits are included.
