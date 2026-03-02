# 3. Processing Model

## 3.1 Pipeline

Document processing follows a **linear pipeline**:

1. Upload
2. Text extraction
3. Interpretation into structured data
4. Review & correction
5. Review completion

The pipeline is **observable** and **step-based**.

---

## 3.2 Asynchronous Execution

- Processing is **asynchronous** and runs in the background.
- API requests must **never block** waiting for processing to complete.
- Processing is executed internally (in-process worker or equivalent).
This document describes an in-process execution model; story-specific scope boundaries live in [`docs/projects/veterinary-medical-records/04-delivery/implementation-plan.md`](../IMPLEMENTATION_PLAN/00_entry.md).

---

## 3.3 Processing Runs

- Each processing attempt creates a **new processing run**.
- Processing runs are:
  - immutable
  - append-only
- A document may have many historical runs.

### Active Run Rule
- **Only one processing run may be `RUNNING` per document at any time**.

- States:
  - `QUEUED`
  - `RUNNING`
  - `COMPLETED`
  - `FAILED`
  - `TIMED_OUT`

Multiple `QUEUED` runs may exist per document (append-only history).

If a reprocess is requested while a run is `RUNNING`:

- A new run is created in `QUEUED`
- It starts only after the `RUNNING` run finishes or times out
- `RUNNING` runs are **never cancelled**

---
