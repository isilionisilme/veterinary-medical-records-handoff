# IMP-06 — Preflight Wrapper Integrity and L3 Entrypoint Hardening

**Status:** Planned

**Type:** Technical Improvement (non-user-facing)

**Target release:** Release 17 — Engineering quality and project governance

**PR strategy:** Single dedicated PR (wrapper resolution hardening + guard checks + CI wiring)

**Technical Outcome**
Make L1/L2/L3 wrapper scripts deterministic and self-validating so preflight entrypoints cannot silently drift to non-existent script targets.

**Problem Statement**
The `test-L3.ps1` wrapper can break when it references a stale preflight filename (for example `preflight-ci-local-utf8.ps1`), causing local validation to fail even when core preflight logic is correct.

**Scope**
- Harden wrapper target resolution so wrappers point to existing preflight scripts only.
- Add explicit fail-fast messaging when a wrapper target cannot be resolved.
- Add a lightweight wrapper-integrity check that validates wrapper target paths.
- Run wrapper-integrity checks in local preflight and CI to prevent regressions.
- Update CI/script documentation to match final wrapper behavior.

**Out of Scope**
- No changes to business/domain behavior.
- No new frontend/backend product functionality.
- No changes to release workflow semantics beyond wrapper integrity.

**Acceptance Criteria**
- `test-L1.ps1`, `test-L2.ps1`, and `test-L3.ps1` resolve valid preflight script paths.
- Running `pwsh -File scripts/ci/test-L3.ps1` does not fail due to missing wrapper target files.
- A wrapper-integrity guard fails with actionable output if wrapper targets are invalid.
- CI enforces wrapper integrity for PRs touching CI scripts.
- Documentation under `scripts/ci/README.md` reflects the implemented wrapper behavior.

**Validation Checklist**
- Execute `pwsh -File scripts/ci/test-L1.ps1` and confirm pass/fail is based on checks, not missing wrapper files.
- Execute `pwsh -File scripts/ci/test-L2.ps1` and confirm pass/fail is based on checks, not missing wrapper files.
- Execute `pwsh -File scripts/ci/test-L3.ps1` and confirm pass/fail is based on checks, not missing wrapper files.
- Trigger wrapper-integrity guard against a deliberately invalid target and verify deterministic failure message.
- Confirm CI runs wrapper-integrity validation on pull requests.

**Risks and Mitigations**
- Risk: Overly strict wrapper checks may block valid developer workflows.
  - Mitigation: keep checks scoped to wrapper target existence and documented invariants only.
- Risk: Divergence between local and CI wrapper behavior.
  - Mitigation: enforce the same wrapper-integrity check in both local preflight and CI.

**Dependencies**
- Depends on existing L1/L2/L3 preflight pipeline conventions.
- Should remain aligned with IMP-03 (Plan Execution Guard Enforcement) and subsequent CI hardening improvements.
