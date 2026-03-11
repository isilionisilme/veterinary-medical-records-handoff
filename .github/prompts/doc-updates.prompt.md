---
agent: agent
description: Normalize and propagate documentation changes using DOC_UPDATES rules.
---

1. Trigger this workflow when the user says docs changed, updated a specific doc, asks to sync or normalize docs, or asks to update a legacy or reference doc.
2. Support these three trigger scenarios: A) user specifies document paths, B) user does not specify docs so you must discover changed docs, C) user asks to update a legacy or reference doc.
3. Always inspect evidence in this order and merge results: local working tree (`git status --porcelain`, `git diff --name-status`, `git diff --cached --name-status`), unpushed commits (`git log --oneline @{upstream}..HEAD`, `git diff --name-status @{upstream}..HEAD`), and branch-vs-base diff (`git diff --name-status <base_ref>...HEAD`). If git evidence is unavailable, ask for file paths plus snippet or diff with section context.
4. If the user did not specify files, discover changed docs from the union of those three evidence sources and list them before processing. If the user specified files, validate each path and inspect per-file hunks across the same three evidence sources.
5. For legacy or reference docs, update the reference doc first, then extract any operational rule changes into the correct owner module, keep the reference doc concise, and avoid duplicating operational rules there.
6. Classify each changed doc as `R` = rule change, `C` = clarification, or `N` = navigation/structure/links. Mixed classification in one file is allowed.
7. For every `R` change, determine the single owner module where the rule must live, update or create that owner module before summary output, and update `docs/agent_router/00_RULES_INDEX.md` only if a rule id or owner path changed.
8. Enforce doc/test sync using `docs/agent_router/01_WORKFLOW/DOC_UPDATES/test_impact_map.json`: every changed doc must match a rule, mapped docs must update at least one related test or guard, `owner_any` rules require at least one mapped owner file update, and any exception must be recorded as a propagation gap with rationale.
9. Enforce source-to-router parity using `docs/agent_router/01_WORKFLOW/DOC_UPDATES/router_parity_map.json`: every changed mapped source doc must preserve required terms in all mapped router modules; missing required terms are blocking failures.
10. Run the verification checklist once at task end: links intact, balanced fences, no duplicated rules, discovery includes untracked or renamed docs, all changed docs have mapping coverage, owner propagation is source-specific, parity passes for mapped docs, and no unresolved propagation gaps remain unless explicitly approved as blockers.
11. Anti-loop rule: run normalization once at task end; do not re-run normalization for changes produced by normalization itself.
12. Finish with this required output exactly:

```text
DOC_UPDATES Summary

| Source doc (inspected) | Diff inspected | Evidence source | Classification | Owner module(s) updated | Related tests/guards updated | Source→Router parity | Files modified |
|---|---:|---|---|---|---|---|---|
| docs/... | Yes/No | local / unpushed / branch-vs-base / mixed / snippet | Rule change / Clarification / Navigation | docs/... | path/to/test_or_guard.py | Pass/Fail/Not mapped | docs/... |
```

13. Print `**Propagation gaps:** None` when there are no gaps; otherwise number each gap with `Source`, `Reason`, and `Suggested action`. If gaps exist, tell the user: `If you want, say: show me the unpropagated changes`.