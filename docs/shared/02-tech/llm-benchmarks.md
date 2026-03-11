---
title: "LLM Benchmarks System"
type: explanation
status: active
audience: all
last-updated: 2026-03-02
---

# LLM Benchmarks System

**Breadcrumbs:** [Docs](../../README.md) / Shared / 02-tech

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Purpose](#purpose)
- [Key concepts](#key-concepts)
  - [Premium Request](#premium-request)
  - [tok_est (repository-side proxy)](#tok_est-repository-side-proxy)
- [Architecture](#architecture)
  - [Data flow](#data-flow)
- [Billing model](#billing-model)
  - [Why "estimated" requests](#why-estimated-requests)
- [Scenarios](#scenarios)
- [When to use this system](#when-to-use-this-system)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Purpose

The LLM Benchmarks system measures **AI-assistant resource consumption** in projects that use GitHub Copilot (or similar
LLM-based assistants) as the primary development tool.

It answers two questions:

1. **How much documentation does the assistant need to read** to perform a given task?
2. **How much real spend (USD / Premium Requests) has been consumed** across accounts?

These metrics are meant for **self-assessment and optimization**, not product telemetry.

---

## Key concepts

### Premium Request

A **Premium Request** is GitHub Copilot's billing unit for advanced model invocations (chat, multi-file edits, agents,
refactors, repo analysis).

| Property                   | Detail                                                              |
| -------------------------- | ------------------------------------------------------------------- |
| Price                      | $0.04 per request                                                   |
| Included per account/month | 300 requests ($12.00)                                               |
| Token equivalence          | **None** — 1 request = 1 model invocation regardless of token count |

A single premium request may consume anywhere from a few thousand to over a million tokens depending on task complexity.
GitHub normalizes this to a flat billing unit.

> **Important:** a single agent action can trigger multiple premium requests when it chains steps, retries prompts, or
> analyzes multiple contexts.

What **counts** as premium: chat with advanced models, multi-file edits, agents, refactors, repo analysis.

What **does not** count: inline autocompletion, simple code suggestions.

### tok_est (repository-side proxy)

`tok_est` is an **internal proxy** computed as `round(chars_read / 4)` from the docs the assistant opened during a
benchmark run. It is useful for comparing documentation overhead across commits but **does not represent billing data**
and should not be compared with Premium Requests.

---

## Architecture

```text
metrics/llm_benchmarks/
├── runs.jsonl                          # append-only log (one JSON object per run)
├── runs.schema.json                    # documentation-only schema
├── SCENARIOS.md                        # reproducible benchmark prompts
├── account_usage_merged_daily.csv      # merged real usage from account exports
├── account_usage_quality.json          # duplicate checks + totals
├── summary.md                          # generated human-readable summary
└── scripts/
    ├── add_run.py                      # append a new benchmark run
    ├── validate_runs.py                # validate runs against commit snapshots
    ├── summarize.py                    # generate summary.md
    ├── backfill_daily.py               # create retroactive daily runs from git history
    └── merge_multi_account_usage.py    # merge multi-account CSV exports
```

### Data flow

```text
Account CSV exports (tmp/usage/*.csv)
        │
        ▼
merge_multi_account_usage.py
        │
        ├──► account_usage_merged_daily.csv
        └──► account_usage_quality.json
                │
                ▼
          summarize.py ──► summary.md
```

---

## Billing model

GitHub Copilot reports usage as **cumulative USD** per account per billing period. When multiple accounts are used (to
stay within the included $12 cap per account), each account's CSV export contains a `Copilot` column with cumulative
dollar values.

The merge pipeline:

1. Reads all CSV files from an input directory.
2. Computes daily deltas from cumulative values.
3. Sums deltas across accounts for each day.
4. Derives estimated Premium Requests as `USD / 0.04`.
5. Performs duplicate detection (exact file hash + Copilot series hash).

### Why "estimated" requests

The CSV exports contain USD, not request counts. Dividing by $0.04 gives the estimated number of requests **assuming no
overage pricing changes**. This is the best approximation available from the exported data.

---

## Scenarios

Benchmark scenarios are reproducible prompts that measure how many docs the assistant reads for a specific task type.
See `metrics/llm_benchmarks/SCENARIOS.md` for the full catalog and prompt templates.

Each scenario produces a `METRICS` line that is parsed and appended to `runs.jsonl`.

---

## When to use this system

- **Optimization:** compare doc consumption before and after architectural changes (e.g., introducing a docs router,
  splitting plans).
- **Cost tracking:** monitor real spend across accounts during a billing period.
- **Auditing:** provide evaluators with transparent, in-repo methodology for AI-assistant resource usage.
