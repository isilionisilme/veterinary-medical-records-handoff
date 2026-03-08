# Add User Story Workflow

Use this workflow when asked to add a new User Story to the plan.

## Required updates

Update the plan across the release plan and backlog documents:

1) `docs/projects/veterinary-medical-records/04-delivery/implementation-plan.md`
- Add the story to the correct **User Stories (in order)** list under a release.
- If no release is viable, create a new release section.

2) `docs/projects/veterinary-medical-records/04-delivery/Backlog/`
- Create or update the dedicated backlog item file for the story using the canonical backlog format.

3) `docs/projects/veterinary-medical-records/04-delivery/Backlog/README.md`
- Add or update the consolidated index row for the story.

## Minimal required fields for the backlog item file

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
- Story has a dedicated backlog file with required fields.
- Story appears in **Backlog Index** with the correct release assignment.
- Formatting and ordering conventions match existing stories.
- No unrelated document edits are included.
