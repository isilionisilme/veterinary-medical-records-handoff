# Completed: Iteration 8 — Bugs + CI governance + AppWorkspace round 3 + coverage

**Date:** 2026-02-26
**PRs:** #156 (PR A — CI governance), #157 (PR B — refactor + coverage)
**Branches:** `improvement/iteration-8-ci`, `improvement/iteration-8-refactor` → `main`

## Context

Two-PR strategy: PR A addressed bugs + CI doc governance (PdfViewer hotfix, 3 independent CI doc guard jobs, doc change classifier, Navigation exemption + Clarification relaxed mode). PR B covered AppWorkspace round 3 refactor + coverage push (render section extraction, hook tests, branch coverage improvements, candidate_mining split).

## Steps — PR A (CI governance)

| ID | Description | Agent | Status |
|---|---|---|---|
| F14-A | Hotfix PdfViewer: accept ArrayBuffer, remove fetch indirection | Codex | ✅ |
| F14-B | Separate doc_test_sync_guard into 3 independent CI jobs | Codex | ✅ |
| F14-C | Doc change classifier: script + CI integration | Codex | ✅ |
| F14-D | Navigation exemption + relaxed Clarification mode in check_doc_test_sync.py | Codex | ✅ |
| F14-E | Unit tests for classifier + calibration | Codex | ✅ |
| F14-L | Smoke test PR A + merge → main | Claude | ✅ |

## Steps — PR B (refactor + coverage)

| ID | Description | Agent | Status |
|---|---|---|---|
| F14-F | Extract render sections: UploadPanel, StructuredDataPanel, PdfViewerPanel | Codex | ✅ |
| F14-G | Tests for hooks extracted in Iter 7 | Codex | ✅ |
| F14-H | PdfViewer branch coverage 47%→65%+ | Codex | ✅ |
| F14-I | documentApi branch coverage 67%→80%+ | Codex | ✅ |
| F14-J | config.py coverage 83%→90%+ | Codex | ✅ |
| F14-K | Split candidate_mining.py (789 LOC → 2 modules < 400 LOC) | Codex | ✅ |
| F14-M | FUTURE_IMPROVEMENTS refresh + smoke test PR B + merge → main | Claude | ✅ |

## Key outcomes
- 372 backend tests (90% coverage)
- 263 frontend tests (85% coverage)
- 3 independent doc guard CI jobs (parity, sync, brand)
- Doc change classifier: Rule/Clarification/Navigation
- AppWorkspace.tsx: 2,221 LOC (−62% from original 5,770)
- candidate_mining.py split into 2 modules < 400 LOC
- 0 lint issues, 8 CI jobs green
