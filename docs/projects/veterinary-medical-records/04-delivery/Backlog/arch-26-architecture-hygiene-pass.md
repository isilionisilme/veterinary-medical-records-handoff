# ARCH-26 — Architecture Hygiene Pass (Dynamic Re-exports, Local Imports, Public API Naming)

**Status:** Planned

**Type:** Architecture Improvement (code quality)

**Target release:** Release 20 — Architecture hardening

**Origin:** [PR #291 AI Code Review](https://github.com/isilionisilme/veterinary-medical-records/pull/291) — Should-fix: cross-module private APIs, stale shims, ARCH-24 dynamic re-export

**Severity:** MEDIUM  
**Effort:** S (1-2h)

**Problem Statement**
After the ARCH-01 decomposition, three anti-patterns remain that an architecture evaluator would flag:
1. `document_service.py` uses `globals().update()` dynamic re-export — defeats static analysis (ARCH-24).
2. `review_payload_projector.py` has function-local imports (lines 27, 112) — hides dependencies.
3. `documents/__init__.py` exports 3 underscore-prefixed names as public API — contradicts module boundary conventions.

**Action**
1. Rewrite `document_service.py` with explicit named imports (44 symbols).
2. Move function-local imports in `review_payload_projector.py` to module level.
3. Add non-underscore aliases in `__init__.py` for the 3 public exports; deprecate `_`-prefixed names.

**Acceptance Criteria**
- No `globals().update()` or dynamic re-export patterns in `document_service.py`
- No function-local imports in `review_payload_projector.py`
- All 3 underscore-prefixed public exports have non-underscore aliases
- All existing tests pass
- L3 green

**Dependencies**
- ARCH-01 (Done) — decomposition must be merged first.

**Plan**
[PLAN_2026-03-12_ARCH-HYGIENE-PASS.md](../plans/PLAN_2026-03-12_ARCH-HYGIENE-PASS.md)
