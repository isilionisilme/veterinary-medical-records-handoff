# Manual QA Regression Checklist

Purpose: user-centered manual regression checklist grouped by shared environment to minimize context switching between test cases.

## Environment Blocks

| Block | Objective | Shared environment |
|---|---|---|
| A | Startup and technical smoke | App running (Docker preferred), known DB state |
| B | Ingestion and processing pipeline | 2 valid PDFs + 1 invalid file |
| C | In-context review UI | 1 processed and complete document |
| D | Editing and persistence | Same document from block C |
| E | Visits and determinism | 1 multi-visit fixture document |
| F | Errors and resilience | Backend running + controlled failure test |

## QA Template (recommended execution order)

| ID | US | Test case | Precondition | Steps | Expected result | Severity | Status | Evidence |
|---|---|---|---|---|---|---|---|---|
| A-01 | US-42 | Docker-first startup | Clean/known repo state | Start full stack from scratch | Services start without hidden manual steps | High | Pending |  |
| A-02 | US-42 | Minimum E2E smoke | Stack is up | Upload -> process -> open review | End-to-end flow works | Critical | Pending |  |
| B-01 | US-21, US-01 | Valid upload from UI | App running | Upload valid PDF | Document created with `document_id` | Critical | Pending |  |
| B-02 | US-05, US-02 | Status transitions | Just-uploaded document | Observe status to terminal state | Status moves correctly through pipeline | High | Pending |  |
| B-03 | US-04 | List consistency | 2+ documents available | Open list and refresh | No duplicates, coherent metadata | High | Pending |  |
| B-04 | US-11 | Processing history visibility | Processed document | Open processing history | Steps and failures are visible and understandable | Medium | Pending |  |
| B-05 | US-06 | Extracted text visibility | Processed document | Open extracted text | Non-empty text or valid empty/error state | High | Pending |  |
| B-06 | US-03 | Original preview/download | Existing document | Open preview and download | Correct file opens/downloads | High | Pending |  |
| B-07 | US-21, US-01 | Invalid upload behavior | App running | Upload invalid type/size | Clear error; UI remains stable | High | Pending |  |
| C-01 | US-07, US-32, US-44 | Clinical panel structure | Complete processed document | Open review panel | Sections present in expected order | Critical | Pending |  |
| C-02 | US-44 | Clinical labels and NHC | Same document | Check labels and NHC tooltip | Labels are correct; NHC placeholder `—` when missing | Medium | Pending |  |
| C-03 | US-34 | Search/filter structural safety | Same document | Search, filter, then clear | Only row visibility changes; grouping unchanged | High | Pending |  |
| C-04 | US-35 | Splitter resize behavior | Same document | Drag splitter through extremes | Layout remains stable/usable | Medium | Pending |  |
| C-05 | US-33 | PDF zoom behavior | Same document | Zoom in/out/reset and navigate pages | Rendering and scrolling remain correct | Medium | Pending |  |
| C-06 | US-39, US-40 | Confidence and tooltip coherence | Same document | Inspect confidence badges and tooltip | Values and explanation are coherent | High | Pending |  |
| C-07 | US-36 | Visual consistency and keyboard basics | Same document | Inspect components; tab through key controls | Consistent styling and visible focus | Medium | Pending |  |
| D-01 | US-08 | Edit and save persistence | Review screen open | Edit multiple fields, save, reload | Changes persist after reload | Critical | Pending |  |
| D-02 | US-41 | Top-5 suggestions in edit modal | Editable field available | Open modal, pick suggestion, save | Suggested value is applied correctly | High | Pending |  |
| D-03 | US-09 | Correction signal capture | Field value can be changed | Save a meaningful correction | Correction is captured as expected | High | Pending |  |
| D-04 | US-09 | No-op save behavior | Field with original value known | Save original value unchanged | Not counted as a correction (per contract) | Medium | Pending |  |
| D-05 | US-38 | Reviewed toggle persistence | Edited document | Mark reviewed, refresh, unmark | Toggle state persists and is reversible | High | Pending |  |
| E-01 | US-45 | Multi-visit grouping coverage | Multi-visit fixture document | Process and open Visits section | Real visit groups appear when evidence exists | Critical | Pending |  |
| E-02 | US-45 | Deterministic regrouping | Same fixture | Reprocess identical input | Same visits structure/order is produced | Critical | Pending |  |
| E-03 | US-34, US-45 | Filter behavior with visits | Multi-visit document in review | Apply search/filter in Visits view | Grouping/order do not change | High | Pending |  |
| F-01 | US-02, US-11 | Controlled backend failure recovery | Failure can be simulated | Trigger API failure and retry | Clear error then clean recovery path | High | Pending |  |
| F-02 | US-03 | Missing document behavior | Invalid/non-existing document ID | Open preview/download by invalid ID | Proper error handling; no UI crash | Medium | Pending |  |

## Run Header Template

| Field | Value |
|---|---|
| Run ID |  |
| Date |  |
| Build/Commit |  |
| Environment | Local / Docker / Staging |
| Tester |  |
| Dataset |  |

