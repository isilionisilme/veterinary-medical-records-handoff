---
agent: agent
description: Close out a plan before merge.
---

1. Run closeout only before merge and only on the feature branch itself. Do not create a separate closeout branch or PR.
2. Verify the working tree is clean and run `git fetch --prune`.
3. Reconcile the plan: if any steps remain `[ ]`, present each one to the user as `Defer`, `Drop`, or `Mark complete`, then STOP for the user decision.
4. Confirm the iteration lifecycle state: branch already exists, execution steps are done, and PR readiness has been reached. If no PR exists when delivery requires one, STOP and ask whether to create or update it now.
5. Update `IMPLEMENTATION_HISTORY.md` with the timeline row and cumulative progress when the artifact exists for this workflow.
6. Set the backlog item `**Status:**` to `Done`.
7. Move the plan file to `plans/completed/` without changing the filename.
8. Move the backlog artifact to `Backlog/completed/` when it exists; otherwise record `N/A` explicitly.
9. Update every surrounding relative link that still points to the pre-closeout paths so they resolve to the new `completed/` locations.
10. Run DOC_UPDATES normalization for qualifying Markdown files and run local doc-contract or doc-link validation before push.
11. Commit and push on the feature branch with `docs(closeout): archive <plan-slug> and backlog artifacts`. In stacked PR flows, only the last PR performs this move.
12. Wait for CI to turn green on the closeout commit before reporting readiness.
13. If a PR exists, update its body with the closeout checklist:

```markdown
### Closeout
- [ ] Backlog status set to `Done`
- [ ] Plan moved to `completed/` (or N/A)
- [ ] Backlog artifact moved to `completed/` (or N/A)
- [ ] Relative links updated after move
- [ ] Doc-contract tests pass locally
```

14. After the PR is merged into `main`, run post-merge cleanup automatically: ensure the working tree is clean, clean related stashes where safe, switch to `main` and pull latest changes, delete the local branch safely, and attempt remote branch deletion while reporting non-fatal failures.
