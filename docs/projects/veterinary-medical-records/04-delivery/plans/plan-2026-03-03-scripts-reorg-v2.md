# Plan: Scripts Reorganization v2 — Move-Verify-Commit

> **Operational rules:** See [execution-rules.md](../../03-ops/execution-rules.md) for step integrity, CI-first handoff, and evidence requirements.

**Scope:** Reorganize `scripts/` flat directory into domain folders (34 scripts).
**Out of scope:** New functionality. Only move existing scripts + update references.
**Branch:** `chore/scripts-reorg-v2` (from `main` @ `a0e66aec`)
**Objective:** Every script in a domain folder. Every reference updated. Verified per commit.

## Key Differences vs. v1

- **Scope reduced:** only move existing scripts + update references. No new functionality.
- **No legacy wrappers:** old paths stop existing. Clean cut.
- **One group per commit:** if commit 3 breaks something, it's obvious what to fix.
- **Flat subfolders:** `ci/`, `docs/`, `quality/`, `dev/` — no deeper nesting.
- **Verification after each move** before proceeding.

## Target Structure

```
scripts/
├── README.md
├── ci/
│   ├── preflight-ci-local.ps1 / .bat      (core runner)
│   ├── pre_push_quality_gate.py            (legacy python fallback)
│   ├── install-pre-push-hook.ps1
│   ├── install-pre-commit-hook.ps1
│   ├── test-L1.ps1 / .bat
│   ├── test-L2.ps1 / .bat
│   ├── test-L3.ps1 / .bat
│   ├── preflight-quick.ps1 / .bat          (legacy alias → L1)
│   ├── preflight-push.ps1 / .bat           (legacy alias → L2)
│   └── preflight-full.ps1 / .bat           (legacy alias → L3)
├── docs/
│   ├── check_docs_links.mjs
│   ├── check_doc_test_sync.py
│   ├── check_doc_router_parity.py
│   ├── check_no_canonical_router_refs.py
│   ├── classify_doc_change.py
│   └── sync_docs_to_wiki.py
├── quality/
│   ├── check_brand_compliance.py
│   └── check_design_system.mjs
└── dev/
    ├── start-all.ps1 / .bat
    ├── reset-dev-db.ps1 / .bat
    ├── reload-vscode-window.ps1 / .bat
    ├── clear-documents.bat
    ├── interpretation_debug_snapshot.py
    └── ab_compare_pdf_extractors.py
```

## Complete Reference Map

### Path-resolution fixes (scripts that compute repo-root from `__file__` / `$PSScriptRoot`)

| Script | Current | After move | Fix |
|--------|---------|------------|-----|
| `pre_push_quality_gate.py` | `parents[1]` | `parents[2]` | depth +1 |
| `check_doc_router_parity.py` | `parents[1]` | `parents[2]` | depth +1 |
| `check_no_canonical_router_refs.py` | `parents[1]` | `parents[2]` | depth +1 |
| `interpretation_debug_snapshot.py` | `parents[1]` | `parents[2]` | depth +1 |
| `ab_compare_pdf_extractors.py` | `parents[1]` | `parents[2]` | depth +1 |
| `check_docs_links.mjs` | `__dirname, '..'` | `__dirname, '../..'` | depth +1 |
| `check_design_system.mjs` | `scriptDir, ".."` | `scriptDir, "../.."` | depth +1 |
| `install-pre-push-hook.ps1` | `Join-Path $PSScriptRoot '..'` | `Join-Path $PSScriptRoot '../..'` | depth +1 |
| `install-pre-commit-hook.ps1` | `Join-Path $PSScriptRoot '..'` | `Join-Path $PSScriptRoot '../..'` | depth +1 |
| `preflight-ci-local.ps1` | `Join-Path $PSScriptRoot ".."` | `Join-Path $PSScriptRoot "../.."` | depth +1 |
| `start-all.ps1` | `Split-Path -Parent $PSScriptRoot` | one more `Split-Path` | depth +1 |
| `reset-dev-db.ps1` | `Split-Path -Parent $PSScriptRoot` | one more `Split-Path` | depth +1 |
| `clear-documents.bat` | `%~dp0..` | `%~dp0..\..` | depth +1 |

Scripts that use `$PSScriptRoot` only for sibling resolution (test-L1/L2/L3, preflight-quick/push/full, start-all.bat, reset-dev-db.bat, reload-vscode-window.*): **NO fix needed** — they reference siblings via `Join-Path $PSScriptRoot "sibling"` and will still work since siblings move together.

Scripts with **NO path fix needed** (use CWD-relative paths): `check_doc_test_sync.py`, `classify_doc_change.py`, `sync_docs_to_wiki.py`, `check_brand_compliance.py`.

### External reference map

| Consumer file | References to update |
|---------------|---------------------|
| `.githooks/pre-push` | `scripts/test-L2.ps1` → `scripts/ci/test-L2.ps1`; `scripts/pre_push_quality_gate.py` → `scripts/ci/pre_push_quality_gate.py` |
| `.githooks/pre-commit` | `scripts/test-L1.ps1` → `scripts/ci/test-L1.ps1` |
| `.github/workflows/ci.yml` | 5 script paths (canonical, classify, sync, parity, brand) |
| `.github/workflows/wiki-sync.yml` | `scripts/sync_docs_to_wiki.py` path trigger + run command |
| `package.json` | `scripts/check_docs_links.mjs` → `scripts/docs/check_docs_links.mjs` |
| `frontend/package.json` | `../scripts/check_design_system.mjs` → `../scripts/quality/check_design_system.mjs` |
| `preflight-ci-local.ps1` (internal) | 4 script path strings calling docs/quality guards |
| `pre_push_quality_gate.py` (internal) | glob patterns for docs scripts |
| `install-pre-push-hook.ps1` (cosmetic) | message about `scripts/test-L2.ps1` |
| `install-pre-commit-hook.ps1` (cosmetic) | message about `scripts/test-L1.ps1` |
| `clear-documents.bat` (cosmetic) | message about `scripts\start-all.bat` |
| `test_impact_map.json` | `scripts/check_doc_test_sync.py`, `scripts/check_doc_router_parity.py`, `scripts/check_brand_compliance.py` |
| `test_brand_compliance_guard.py` | `REPO_ROOT / "scripts" / "check_brand_compliance.py"` |
| `test_doc_test_sync_guard.py` | `REPO_ROOT / "scripts" / "check_doc_test_sync.py"` |
| `test_doc_router_parity_contract.py` | `REPO_ROOT / "scripts" / "check_doc_router_parity.py"` |
| `test_classify_doc_change.py` | `REPO_ROOT / "scripts" / "classify_doc_change.py"` and `"scripts" / "check_doc_test_sync.py"` |
| `test_doc_updates_contract.py` | `REPO_ROOT / "scripts" / "check_doc_test_sync.py"` and `"scripts" / "check_doc_router_parity.py"` |
| `test_interpretation_debug_snapshot.py` | `from scripts.interpretation_debug_snapshot import build_snapshot` → `.dev.` |
| `README.md` | ~10 references to `scripts/test-L*`, `scripts/preflight-*`, `scripts/install-pre-*` |
| `docs/shared/03-ops/engineering-playbook.md` | ~6 references to `scripts/test-L*`, `scripts/preflight-*` |
| `docs/agent_router/03_SHARED/ENGINEERING_PLAYBOOK/210_pull-requests.md` | ~7 references to `scripts/test-L*`, `scripts/preflight-*` |

---

## Estado de ejecución

### S1 — Create folder structure + README (Commit 1) · **Claude Opus 4.6**

- [x] S1-A: Create empty directories: `scripts/ci/`, `scripts/docs/`, `scripts/quality/`, `scripts/dev/`
- [x] S1-B: Create `scripts/README.md` with directory guide
- [x] S1-C: Commit. **Gate:** 4 folders + README, no scripts moved — ✅ `aedbfc50`

### S2 — Move CI scripts (Commit 2) · **Claude Opus 4.6**

Move 15 scripts → `scripts/ci/`: `pre_push_quality_gate.py`, `install-pre-push-hook.ps1`, `install-pre-commit-hook.ps1`, `preflight-ci-local.ps1/.bat`, `test-L1.ps1/.bat`, `test-L2.ps1/.bat`, `test-L3.ps1/.bat`, `preflight-quick.ps1/.bat`, `preflight-push.ps1/.bat`, `preflight-full.ps1/.bat`

- [x] S2-A: `git mv` 17 scripts to `scripts/ci/`
- [x] S2-B: Fix `pre_push_quality_gate.py` — `parents[1]` → `parents[2]` (glob patterns kept flat — updated in S3)
- [x] S2-C: Fix `preflight-ci-local.ps1` — `Join-Path $PSScriptRoot ".."` → `Join-Path $PSScriptRoot ".." ".."` for repo root (4 internal script paths kept flat — updated in S3/S4)
- [x] S2-D: Fix `install-pre-push-hook.ps1` — depth +1 + cosmetic message
- [x] S2-E: Fix `install-pre-commit-hook.ps1` — depth +1 + cosmetic message
- [x] S2-F: Update `.githooks/pre-push` — 4 path refs to `scripts/ci/`
- [x] S2-G: Update `.githooks/pre-commit` — 2 path refs to `scripts/ci/`
- [x] S2-H: Commit + gate — ✅ `cdcd00a5` (pre-commit hook passed)

### S3 — Move docs scripts (Commit 3) · **Claude Opus 4.6**

Move 6 scripts → `scripts/docs/`: `check_docs_links.mjs`, `check_doc_test_sync.py`, `check_doc_router_parity.py`, `check_no_canonical_router_refs.py`, `classify_doc_change.py`, `sync_docs_to_wiki.py`

- [x] S3-A: `git mv` 6 scripts to `scripts/docs/`
- [x] S3-B: Fix `check_docs_links.mjs` — `path.resolve(__dirname, '..')` → `path.resolve(__dirname, '../..')`
- [x] S3-C: Fix `check_doc_router_parity.py` — `parents[1]` → `parents[2]`
- [x] S3-D: Fix `check_no_canonical_router_refs.py` — `parents[1]` → `parents[2]`
- [x] S3-E: Update `.github/workflows/ci.yml` — 4 script paths:
  - `scripts/check_no_canonical_router_refs.py` → `scripts/docs/check_no_canonical_router_refs.py`
  - `scripts/classify_doc_change.py` → `scripts/docs/classify_doc_change.py`
  - `scripts/check_doc_test_sync.py` → `scripts/docs/check_doc_test_sync.py`
  - `scripts/check_doc_router_parity.py` → `scripts/docs/check_doc_router_parity.py`
- [x] S3-F: Update `.github/workflows/wiki-sync.yml` — path trigger + run command:
  - `scripts/sync_docs_to_wiki.py` → `scripts/docs/sync_docs_to_wiki.py`
- [x] S3-G: Update `package.json` — `scripts/check_docs_links.mjs` → `scripts/docs/check_docs_links.mjs`
- [x] S3-H: Update `test_impact_map.json` — all `scripts/check_doc_test_sync.py` → `scripts/docs/check_doc_test_sync.py` and `scripts/check_doc_router_parity.py` → `scripts/docs/check_doc_router_parity.py`
- [x] S3-I: Update test files:
  - `test_doc_test_sync_guard.py`: SCRIPT_PATH → `"scripts" / "docs" / "check_doc_test_sync.py"`
  - `test_doc_router_parity_contract.py`: PARITY_SCRIPT → `"scripts" / "docs" / "check_doc_router_parity.py"`
  - `test_classify_doc_change.py`: CLASSIFIER_PATH → `"scripts" / "docs" / "classify_doc_change.py"`, DOC_SYNC_GUARD_PATH → `"scripts" / "docs" / "check_doc_test_sync.py"`
  - `test_doc_updates_contract.py`: DOC_TEST_SYNC_GUARD → `"scripts" / "docs" / "check_doc_test_sync.py"`, DOC_ROUTER_PARITY_GUARD → `"scripts" / "docs" / "check_doc_router_parity.py"`
- [x] S3-J: Commit. **Gate:** Run `pytest backend/tests/unit/test_doc_test_sync_guard.py backend/tests/unit/test_doc_router_parity_contract.py backend/tests/unit/test_classify_doc_change.py -x -q -o addopts=`. Verify no stale flat refs via grep.

### S4 — Move quality scripts (Commit 4) · **Claude Opus 4.6**

Move 2 scripts → `scripts/quality/`: `check_brand_compliance.py`, `check_design_system.mjs`

- [x] S4-A: `git mv` 2 scripts to `scripts/quality/`
- [x] S4-B: Fix `check_design_system.mjs` — `path.resolve(scriptDir, "..")` → `path.resolve(scriptDir, "../..")`
- [x] S4-C: Update `frontend/package.json` — `../scripts/check_design_system.mjs` → `../scripts/quality/check_design_system.mjs`
- [x] S4-D: Update `.github/workflows/ci.yml` — `scripts/check_brand_compliance.py` → `scripts/quality/check_brand_compliance.py`
- [x] S4-E: Update `test_impact_map.json` — `scripts/check_brand_compliance.py` → `scripts/quality/check_brand_compliance.py`
- [x] S4-F: Update `test_brand_compliance_guard.py` — SCRIPT_PATH → `"scripts" / "quality" / "check_brand_compliance.py"`
- [x] S4-G: Commit. **Gate:** Run `pytest backend/tests/unit/test_brand_compliance_guard.py -x -q -o addopts=`. Verify no stale flat refs via grep.

### S5 — Move dev scripts (Commit 5) · **Claude Opus 4.6**

Move 9 scripts → `scripts/dev/`: `start-all.ps1/.bat`, `reset-dev-db.ps1/.bat`, `reload-vscode-window.ps1/.bat`, `clear-documents.bat`, `interpretation_debug_snapshot.py`, `ab_compare_pdf_extractors.py`

- [x] S5-A: `git mv` 9 scripts to `scripts/dev/`
- [x] S5-B: Fix `start-all.ps1` — repo root resolution (one more `Split-Path` level)
- [x] S5-C: Fix `reset-dev-db.ps1` — repo root resolution (one more `Split-Path` level)
- [x] S5-D: Fix `clear-documents.bat` — `%~dp0..` → `%~dp0..\..`; update cosmetic message `scripts\start-all.bat` → `scripts\dev\start-all.bat`
- [x] S5-E: Fix `interpretation_debug_snapshot.py` — `parents[1]` → `parents[2]`
- [x] S5-F: Fix `ab_compare_pdf_extractors.py` — `parents[1]` → `parents[2]`
- [x] S5-G: Update `test_interpretation_debug_snapshot.py` — `from scripts.interpretation_debug_snapshot import build_snapshot` → `from scripts.dev.interpretation_debug_snapshot import build_snapshot`
- [x] S5-H: Commit. **Gate:** `Get-ChildItem scripts/ -File` returns only `README.md` (no scripts left at root). Run `pytest backend/tests/unit/test_interpretation_debug_snapshot.py -x -q -o addopts=`.

### S6 — Update docs references (Commit 6) · **Claude Opus 4.6**

- [x] S6-A: Update `README.md` — all `scripts/test-L*` → `scripts/ci/test-L*`, `scripts/preflight-*` → `scripts/ci/preflight-*`, `scripts/install-pre-*` → `scripts/ci/install-pre-*`
- [x] S6-B: Update `docs/shared/03-ops/engineering-playbook.md` — same pattern
- [x] S6-C: Update `docs/agent_router/03_SHARED/ENGINEERING_PLAYBOOK/210_pull-requests.md` — same pattern
- [x] S6-D: Commit. **Gate:** `git grep -n 'scripts/test-L\|scripts/preflight-\|scripts/install-pre' -- '*.md'` shows only `scripts/ci/` paths (and this plan).

### S7 — Final verification + cleanup (Commit 7) · **Claude Opus 4.6**

- [x] S7-A: Run full grep: `git grep -n 'scripts/[a-z_]' -- '*.py' '*.yml' '*.json' '*.mjs' '*.ps1' '*.bat' '*.sh'` — verify all references use subfolder paths
- [x] S7-B: Remove `scripts/__pycache__/` if present — not present, no action needed
- [x] S7-C: Run full test suite: `pytest backend/tests/unit -x -q -o addopts=` — ✅ 346 passed
- [x] S7-D: Commit if cleanup needed. **Gate:** All tests pass, no stale refs. — No cleanup needed.

---

## Verification Matrix

| Check | Commands | Steps affected |
|-------|----------|---------------|
| Pre-push hook path | `cat .githooks/pre-push` | S2 |
| Pre-commit hook path | `cat .githooks/pre-commit` | S2 |
| CI workflow syntax | `python -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml'))"` | S3, S4 |
| Wiki-sync syntax | `python -c "import yaml; yaml.safe_load(open('.github/workflows/wiki-sync.yml'))"` | S3 |
| Unit tests (docs) | `pytest backend/tests/unit/test_doc_test_sync_guard.py test_doc_router_parity_contract.py test_classify_doc_change.py -x` | S3 |
| Unit tests (brand) | `pytest backend/tests/unit/test_brand_compliance_guard.py -x` | S4 |
| Unit tests (snapshot) | `pytest backend/tests/unit/test_interpretation_debug_snapshot.py -x` | S5 |
| Full unit suite | `pytest backend/tests/unit -x -o addopts=` | S7 |
| No flat scripts left | `Get-ChildItem scripts/ -File` → only `README.md` | S5 |
| Docs refs clean | `git grep -n 'scripts/[a-z_]' -- '*.md'` → only `scripts/ci/` or `scripts/docs/` etc. | S6 |

## Rollback Policy

- Each step is one atomic commit. `git revert <sha>` undoes exactly one group.
- Do not proceed to next step without passing its gate.
