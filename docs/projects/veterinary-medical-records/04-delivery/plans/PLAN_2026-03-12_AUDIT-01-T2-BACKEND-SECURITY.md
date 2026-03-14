# Track Plan T2 (AUDIT-01-T2): Backend Security Hardening

> **Operational rules:** See [plan-execution-protocol.md](../../../03-ops/plan-execution-protocol.md) for agent execution protocol, scope boundary, and validation gates.
>
> **Master plan:** [AUDIT-01 Master](PLAN_2026-03-12_AUDIT-01-CODEBASE-QUALITY-MASTER.md)

**Branch:** improvement/audit-01-t2-backend-security
**Worktree:** D:/Git/worktrees/codex-permanent-1
**Execution Mode:** Autonomous
**Model Assignment:** GPT-5.4
**PR:** Pending (PR created on explicit user request)
**Related item ID:** `AUDIT-01-T2`
**Prerequisite:** None (independent track)

**Implementation Report:** [IMPLEMENTATION_REPORT_2026-03-12_AUDIT-01-T2-BACKEND-SECURITY](IMPLEMENTATION_REPORT_2026-03-12_AUDIT-01-T2-BACKEND-SECURITY.md)

---

## TL;DR

Fix two security vulnerabilities found in the audit: (1) Content-Disposition header injection via unsanitized filename at `routes_documents.py:298`, and (2) potential XSS through Starlette's default `HTTPException` handler returning unsanitized error detail as HTML.

---

## Context

### Problem 1: Content-Disposition Header Injection (A4)

**File:** `backend/app/api/routes_documents.py`, line 298–301
**Current code:**
```python
headers = {
    "Content-Disposition": (
        f'{disposition_type}; filename="{location.document.original_filename}"'
    )
}
```

The `original_filename` comes from user upload and is stored unsanitized. A filename containing `"` or newline characters can inject arbitrary headers or break the response. RFC 5987 encoding should be used for non-ASCII and special characters.

### Problem 2: Starlette Default HTTPException Handler (A5)

Starlette's built-in `HTTPException` handler returns `detail` as `text/plain` for non-JSON requests, but some versions may reflect unsanitized input in error responses. Overriding with a JSON-only handler ensures consistent, safe error responses and eliminates XSS risk from error messages.

---

## Scope Boundary

- **In scope:** A4 (Content-Disposition sanitize), A5 (HTTPException override)
- **Out of scope:** Auth mechanism changes (ARCH-13), CORS configuration changes, rate limiting (ARCH-21)

---

## Design Decisions

### DD-1: RFC 5987 filename encoding for Content-Disposition
**Approach:** Use `filename*=UTF-8''<encoded>` with `urllib.parse.quote` for safe encoding. Keep ASCII-only `filename=` fallback for legacy clients.
**Rationale:** Standard approach per RFC 6266 §4.3. Handles non-ASCII filenames (common in Spanish-language veterinary records) and eliminates injection via special characters.

### DD-2: JSON-only HTTPException handler
**Approach:** Register custom exception handler that always returns `application/json` with a sanitized body `{"detail": str(exc.detail)}`.
**Rationale:** Prevents any reflected content from being interpreted as HTML. Consistent with the API's existing JSON-only contract.

---

## PR Partition Gate

| Criterion | Value | Threshold | Result |
|-----------|-------|-----------|--------|
| Estimated diff (LOC) | ~40 | 400 | ✅ |
| Code files changed | 2 | 15 | ✅ |
| Scope classification | code + tests | — | ✅ |
| Semantic risk | LOW (additive security fix) | — | ✅ |

**Decision:** Single PR. No split needed.

---

## DOC-1

`no-doc-needed` — Security hardening of internal response handling. No API contract changes.

---

## Steps

### Phase 1 — A4: Content-Disposition Header Sanitization

#### Step 1: Add filename sanitization utility

**AGENTE: GPT-5.4**

In `routes_documents.py`, add a helper (or import from a new `backend/app/api/response_helpers.py` if preferred):

```python
from urllib.parse import quote

def _safe_content_disposition(disposition_type: str, filename: str) -> str:
    """Build a Content-Disposition header with RFC 5987 encoding."""
    ascii_filename = filename.encode("ascii", "replace").decode("ascii").replace('"', "'")
    encoded_filename = quote(filename, safe="")
    return (
        f'{disposition_type}; '
        f'filename="{ascii_filename}"; '
        f"filename*=UTF-8''{encoded_filename}"
    )
```

#### Step 2: Replace current header construction

**AGENTE: GPT-5.4**

At `routes_documents.py:298`, replace:
```python
headers = {
    "Content-Disposition": (
        f'{disposition_type}; filename="{location.document.original_filename}"'
    )
}
```
With:
```python
headers = {
    "Content-Disposition": _safe_content_disposition(
        disposition_type, location.document.original_filename
    )
}
```

#### Step 3: Add unit test

**AGENTE: GPT-5.4**

Add a test to `backend/tests/unit/` that verifies:
- Normal filename produces valid header
- Filename with `"` characters is escaped
- Filename with non-ASCII characters (e.g., `"histórico_clínico.pdf"`) produces valid UTF-8 encoding
- Filename with newline characters is sanitized

### Phase 2 — A5: HTTPException Handler Override

#### Step 4: Add custom exception handler in `main.py`

**AGENTE: GPT-5.4**

In `create_app()` function, after app creation and before middleware registration:

```python
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

@app.exception_handler(StarletteHTTPException)
async def _http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": str(exc.detail)},
    )
```

#### Step 5: Add test for exception handler

**AGENTE: GPT-5.4**

Add a test that verifies:
- A 404 response returns `Content-Type: application/json`
- Error detail is returned as JSON, not HTML
- No HTML tags appear in error responses

### Phase 3 — Validation

#### Step 6: Full test suite

**AGENTE: GPT-5.4**

- `python -m pytest backend/tests/ -x --tb=short -q` — all 709+ pass
- `ruff check backend/` — 0 errors
- `ruff format --check backend/` — 0 diffs

---

## Execution Status

### Phase 0 — Preflight

- [x] P0-A 🔄 — Create branch `improvement/audit-01-t2-backend-security` from latest `main`. Verify clean worktree. **AGENTE: GPT-5.4**

### Phase 1 — A4: Content-Disposition

- [x] P1-A 🔄 — Add `_safe_content_disposition` helper function. **AGENTE: GPT-5.4**
- [x] P1-B 🔄 — Replace header construction in `routes_documents.py`. **AGENTE: GPT-5.4**
- [x] P1-C 🔄 — Add unit tests for filename sanitization. **AGENTE: GPT-5.4**
- [x] P1-D 🚧 — Checkpoint: present diff for user review. **AGENTE: GPT-5.4**

### Phase 2 — A5: HTTPException Handler

- [x] P2-A 🔄 — Add custom exception handler in `main.py`. **AGENTE: GPT-5.4**
- [x] P2-B 🔄 — Add test for JSON-only error responses. **AGENTE: GPT-5.4**
- [x] P2-C 🚧 — Checkpoint: present diff for user review. **AGENTE: GPT-5.4**

### Phase 3 — Final

- [x] P3-A 🔄 — Full validation (tests + lint). **AGENTE: GPT-5.4**
- [x] P3-B 🚧 — Present commit proposal to user. **AGENTE: GPT-5.4**

---

## Relevant Files

| File | Action |
|------|--------|
| `backend/app/api/routes_documents.py` | MODIFY (A4 — sanitize Content-Disposition) |
| `backend/app/main.py` | MODIFY (A5 — add exception handler) |
| `backend/tests/unit/test_content_disposition.py` | CREATE (A4 tests) |
| `backend/tests/unit/test_exception_handler.py` | CREATE (A5 tests) |

---

## Acceptance Criteria

- [x] Content-Disposition header uses RFC 5987 encoding for all filenames
- [x] Filenames with `"`, `\n`, `\r`, non-ASCII characters are all safely encoded
- [x] All HTTP error responses return `Content-Type: application/json`
- [x] 709+ tests pass, ≥91% coverage
- [x] `ruff check` + `ruff format` clean
