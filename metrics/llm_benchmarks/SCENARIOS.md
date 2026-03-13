# LLM Benchmarks — Scenarios

These scenarios are meant to be **reproducible** and **comparable** across commits.

Guidelines:
- Use the exact prompt text (or copy it verbatim) to avoid drift.
- Run benchmark prompts with `#metrics`.
- The assistant must print a final single-line block:

```text
METRICS scenario=<scenario_id> docs=<path1>|<path2>|... fallback=<int> clarifying=<int> violations=<comma-separated>
```

Notes:
- `docs=` must contain repo-relative paths separated by `|` (no spaces).
- If there are no violations, use `violations=` (empty).

---

## start_new_work

```text
#metrics
You are starting new work on this repo. Do the minimum doc reading needed to decide:
1) whether a new branch is required
2) the correct branch naming convention

Follow the repo rules. At the end, print the METRICS line with docs consulted.
```

## docs_only_pr

```text
#metrics
Assume the change only touches Markdown files under docs/. Do the minimum doc reading needed to decide:
1) how to classify the PR (docs-only vs code)
2) whether an automated code review is required

Follow the repo rules. At the end, print the METRICS line with docs consulted.
```

## code_pr

```text
#metrics
Assume the change touches files under backend/ and frontend/. Do the minimum doc reading needed to decide:
1) how to classify the PR
2) whether a code review is required and what procedure applies

Follow the repo rules. At the end, print the METRICS line with docs consulted.
```

## code_review

```text
#metrics
You are asked to perform a code review for a Code PR in this repo. Do the minimum doc reading needed to decide:
1) whether a review is mandatory
2) the required review style/output and any "publish to PR" requirements

Follow the repo rules. At the end, print the METRICS line with docs consulted.
```

## run_tests

```text
#metrics
You are asked to run tests/lint for this repo locally. Do the minimum doc reading needed to decide:
1) what commands to run
2) any rules about when tests are required

Follow the repo rules. At the end, print the METRICS line with docs consulted.
```

## ui_copy_change

```text
#metrics
Assume you are about to change user-facing UI copy in the frontend. Do the minimum doc reading needed to decide:
1) what UX rules apply
2) what Brand rules apply

Follow the repo rules. At the end, print the METRICS line with docs consulted.
```

## backend_contract_change

```text
#metrics
Assume you are about to change an API schema in backend/app/api/schemas.py. Do the minimum doc reading needed to decide:
1) what contract/architecture docs are authoritative
2) what versioning or compatibility rules apply

Follow the repo rules. At the end, print the METRICS line with docs consulted.
```

## doc_updates_trigger_a

```text
#metrics
I updated docs/shared/03-ops/way-of-working.md. Run the documentation-update workflow exactly as defined by the canonical docs.
Do the minimum doc reading needed to:
1) classify the update
2) run normalization for the specified file
3) report the normalization output summary

At the end, print the METRICS line with docs consulted.
```

## doc_updates_trigger_b

```text
#metrics
Docs changed; please sync and normalize. No file paths are specified.
Do the minimum doc reading needed to:
1) discover changed docs from git status/diff
2) apply normalization in stable order
3) report detected files and normalization summary

At the end, print the METRICS line with docs consulted.
```

## doc_updates_trigger_c

```text
#metrics
Update the documentation section I mention below, then apply the required post-change normalization workflow.
Do the minimum doc reading needed to:
1) edit the requested reference document
2) run one normalization pass at task end (no loop)
3) report classifications and owner-module updates

At the end, print the METRICS line with docs consulted.
```

## doc_updates_trigger_d_no_git

```text
#metrics
Repository access is unavailable. I updated docs, please normalize.
Do the minimum doc reading needed to:
1) request required fallback inputs (file paths + snippet/diff)
2) classify using snippet evidence only
3) report that diff source is snippet

At the end, print the METRICS line with docs consulted.
```

## doc_updates_trigger_e_rule_id

```text
#metrics
Change rule R-DOC-UPDATES-NORMALIZE to tighten propagation behavior.
Do the minimum doc reading needed to:
1) resolve rule id in the rules index
2) update owner module only
3) update references only if needed

At the end, print the METRICS line with docs consulted.
```

## doc_updates_mixed_classification

```text
#metrics
A single doc change includes both a rule update and wording cleanup.
Do the minimum doc reading needed to:
1) classify mixed changes (Rule change + Clarification)
2) propagate only rule portions to owner modules
3) report mixed classification in summary output

At the end, print the METRICS line with docs consulted.
```

## doc_updates_rename_untracked

```text
#metrics
Docs include one renamed file and one new untracked markdown file.
Do the minimum doc reading needed to:
1) discover files with git status plus name-status diff
2) normalize both renamed and untracked docs
3) report deterministic processing order

At the end, print the METRICS line with docs consulted.
```

## doc_updates_ambiguous_owner

```text
#metrics
A rule change could map to UX or Brand ownership.
Do the minimum doc reading needed to:
1) evaluate known mapping hints
2) avoid silent auto-pick when ambiguous
3) ask for clarification or record a propagation gap with candidates

At the end, print the METRICS line with docs consulted.
```

## retro_daily_snapshot

```text
#metrics
Generate a retroactive daily benchmark snapshot for this repository.
Use a deterministic docs set and produce one run per day from repo creation to today.
Mark runs as retrospective estimates (not live captured sessions).

At the end, print the METRICS line with docs consulted.
```

## retro_daily_operational_path

```text
#metrics
Generate a retroactive daily benchmark focused on the operational decision path.
Use a deterministic minimal docs set that changes with repo architecture milestones:
- before docs router: AGENTS + engineering playbook + docs index
- after docs router: AGENTS + router authority + start-work workflow entry
- include the active planning source (monolithic AI_ITERATIVE_EXECUTION_PLAN or split PLAN_*).

Produce one run per day from repo creation to today.
Mark runs as retrospective estimates (not live captured sessions).

At the end, print the METRICS line with docs consulted.
```

## retro_daily_docs_footprint

```text
#metrics
Generate a retroactive daily benchmark using documentation footprint from git history.
For each UTC day, collect markdown docs touched in commits that day under docs/.
Filter to files that still exist at the selected commit for that day.
If no docs were touched that day, fallback to the operational-path minimal set.

Produce one run per day from repo creation to today.
Mark runs as retrospective estimates (not live captured sessions).

At the end, print the METRICS line with docs consulted.
```

## retro_daily_realistic_estimate

```text
#metrics
Generate a retroactive daily benchmark using a realistic-reading model.
Build from the operational path baseline, then add only high-signal touched docs for that day:
- keep canonical docs in docs/project and docs/shared,
- keep docs/README.md and docs/shared/03-ops/way-of-working.md,
- for router changes keep only authority and 00_entry files,
- ignore archival noise (completed plans/refactor archives),
- cap extra touched docs to avoid counting full migration churn as if everything was read.

Produce one run per day from repo creation to today.
Mark runs as retrospective estimates (not live captured sessions).

At the end, print the METRICS line with docs consulted.
```

