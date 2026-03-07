# Scripts

Utility scripts organized by domain. Run from the **repo root**.

## Directory Guide

| Folder | Purpose | Examples |
|--------|---------|----------|
| `ci/` | CI pipeline, pre-commit/pre-push hooks, preflight checks | `test-L1.ps1`, `preflight-ci-local.ps1`, `install-pre-push-hook.ps1` |
| `docs/` | Documentation validation, sync, and local preview | `check_docs_links.mjs`, `check_doc_test_sync.py`, `sync_docs_to_wiki.py`, `docs-local-preview.ps1` |
| `quality/` | Brand and design-system compliance guards | `check_brand_compliance.py`, `check_design_system.mjs` |
| `dev/` | Local development helpers | `start-all.ps1`, `reset-dev-db.ps1`, `clear-documents.bat` |

## Quick Reference

```bash
# Run preflight checks (pre-commit = L1, pre-push = L2, full = L3)
./scripts/ci/test-L1.ps1            # Fast unit tests
./scripts/ci/test-L2.ps1            # Unit + quality gates
./scripts/ci/test-L3.ps1            # Full suite (E2E included)

# Start local development environment
./scripts/dev/start-all.ps1

# Reset development database
./scripts/dev/reset-dev-db.ps1

# Reset test environment (docker dev + DB wipe + health checks)
./scripts/dev/reset-test-env.ps1

# Validate documentation links
node scripts/docs/check_docs_links.mjs
```
