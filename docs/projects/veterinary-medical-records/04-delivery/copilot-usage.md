---
title: "Copilot Usage Metrics — veterinary-medical-records"
type: reference
status: active
audience: all
last-updated: 2026-03-02
---

# Copilot Usage Metrics — veterinary-medical-records


**Breadcrumbs:** [Docs](../../../README.md) / [Projects](../../README.md) / veterinary-medical-records / 04-delivery

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->


- [Overview](#overview)
- [Account summary](#account-summary)
  - [Why multiple accounts?](#why-multiple-accounts)
- [Daily usage table](#daily-usage-table)
- [Key observations](#key-observations)
- [Data quality](#data-quality)
- [Regeneration](#regeneration)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Overview

This document summarizes the **real GitHub Copilot usage** for this project during
the February 2026 development period, consolidated from 11 personal accounts.

For a general explanation of the benchmarks system, see
[docs/shared/02-tech/llm-benchmarks.md](../../../../shared/02-tech/llm-benchmarks.md).

---

## Account summary

| Metric | Value |
|---|---:|
| Billing period | 2026-02-01 → 2026-02-28 |
| Accounts used | 11 |
| Total Copilot spend (USD) | $130.28 |
| Estimated Premium Requests | 3 257 |
| Included USD per account | $12.00 |
| Included USD all accounts | $132.00 |
| Utilization vs included cap | 98.7 % |
| Actions spend (USD) | $26.78 |

Data source: `metrics/llm_benchmarks/account_usage_quality.json`

### Why multiple accounts?

Each GitHub account includes 300 Premium Requests ($12.00) per month.
When the cap is reached on one account, a new account is used to continue working.
11 accounts × $12 = $132 included; actual spend was $130.28 (near-full utilization).

---

## Daily usage table

Source: `metrics/llm_benchmarks/account_usage_merged_daily.csv`

Interpretation: `Copilot` values from account CSV exports represent **USD**;
Premium Requests are estimated as `USD / $0.04`.

| Date | Copilot USD daily | Copilot USD cumulative | Premium Requests daily (est) | Premium Requests cumulative (est) |
|---|---:|---:|---:|---:|
| 2026-02-01 | 0.00 | 0.00 | 0 | 0 |
| 2026-02-02 | 0.00 | 0.00 | 0 | 0 |
| 2026-02-03 | 0.00 | 0.00 | 0 | 0 |
| 2026-02-04 | 0.00 | 0.00 | 0 | 0 |
| 2026-02-05 | 0.00 | 0.00 | 0 | 0 |
| 2026-02-06 | 0.00 | 0.00 | 0 | 0 |
| 2026-02-07 | 0.00 | 0.00 | 0 | 0 |
| 2026-02-08 | 0.00 | 0.00 | 0 | 0 |
| 2026-02-09 | 0.00 | 0.00 | 0 | 0 |
| 2026-02-10 | 0.00 | 0.00 | 0 | 0 |
| 2026-02-11 | 0.00 | 0.00 | 0 | 0 |
| 2026-02-12 | 1.56 | 1.56 | 39 | 39 |
| 2026-02-13 | 6.92 | 8.48 | 173 | 212 |
| 2026-02-14 | 6.44 | 14.92 | 161 | 373 |
| 2026-02-15 | 4.12 | 19.04 | 103 | 476 |
| 2026-02-16 | 1.80 | 20.84 | 45 | 521 |
| 2026-02-17 | 3.40 | 24.24 | 85 | 606 |
| 2026-02-18 | 0.00 | 24.24 | 0 | 606 |
| 2026-02-19 | 0.12 | 24.36 | 3 | 609 |
| 2026-02-20 | 4.28 | 28.64 | 107 | 716 |
| 2026-02-21 | 6.44 | 35.08 | 161 | 877 |
| 2026-02-22 | 14.40 | 49.48 | 360 | 1 237 |
| 2026-02-23 | 9.40 | 58.88 | 235 | 1 472 |
| 2026-02-24 | 9.40 | 68.28 | 235 | 1 707 |
| 2026-02-25 | 17.60 | 85.88 | 440 | 2 147 |
| 2026-02-26 | 23.32 | 109.20 | 583 | 2 730 |
| 2026-02-27 | 14.88 | 124.08 | 372 | 3 102 |
| 2026-02-28 | 6.20 | 130.28 | 155 | 3 257 |

---

## Key observations

1. **First 11 days (Feb 1–11):** no Copilot premium usage recorded — initial project
   setup, manual work, and environment configuration.

2. **Ramp-up (Feb 12–17):** first week of active AI-assisted development. Average
   ~$4/day (~100 requests/day).

3. **Peak (Feb 22–26):** heaviest development sprint. Peak day was Feb 26 at $23.32
   (583 estimated requests) — this corresponds to major multi-file refactors and
   agent-driven iteration work.

4. **Tail-off (Feb 27–28):** reduced activity as the iteration closed out.

5. **Zero day (Feb 18):** no premium usage — likely a rest day or work limited to
   inline autocompletion (which does not count as premium).

---

## Data quality

| Check | Result |
|---|---|
| Exact duplicate CSV files | None detected |
| Duplicate Copilot series | None detected |
| Days covered | 28 (full month) |

Full diagnostics: `metrics/llm_benchmarks/account_usage_quality.json`

---

## Regeneration

To regenerate these metrics from raw account exports:

```bash
# 1. Merge account CSVs
python metrics/llm_benchmarks/scripts/merge_multi_account_usage.py --input-dir tmp/usage

# 2. Regenerate summary table
python metrics/llm_benchmarks/scripts/summarize.py --write metrics/llm_benchmarks/summary.md
```
