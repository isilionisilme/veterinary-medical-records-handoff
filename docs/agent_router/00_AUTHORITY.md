# Authority Router (Operational, Token-Optimized)

Use this file to route by **intent**. Load only the module(s) listed below.

## Intent → Module

- Start new work → `docs/agent_router/01_WORKFLOW/START_WORK/00_entry.md`
- Branching or naming → `docs/agent_router/01_WORKFLOW/BRANCHING/00_entry.md`
- Pull request workflow → `docs/agent_router/01_WORKFLOW/PULL_REQUESTS/00_entry.md`
- Code review → `docs/agent_router/01_WORKFLOW/CODE_REVIEW/00_entry.md`
- Testing → `docs/agent_router/01_WORKFLOW/TESTING/00_entry.md`
- Documentation updates → `docs/agent_router/01_WORKFLOW/DOC_UPDATES/00_entry.md`
- User-visible change → `docs/agent_router/02_PRODUCT/USER_VISIBLE/00_entry.md`
- Plan audit / compliance check (historical) → `docs/projects/veterinary-medical-records/03-ops/plan-execution-protocol.md`
- Engineering standards (shared) → `docs/agent_router/03_SHARED/00_entry.md`
- Project design / requirements / contracts → `docs/agent_router/04_PROJECT/00_entry.md`
- Assistant benchmarks → `metrics/llm_benchmarks/README.md`
- Fallback / unclear intent → `docs/agent_router/00_FALLBACK.md`

## Rule
Load **only one** module unless it explicitly triggers another.

## Documentation governance
- Canonical docs (human SoT): `docs/projects/veterinary-medical-records/*`, `docs/shared/*`, and `docs/README.md`.
- Router docs are derived assistant modules under `docs/agent_router/*`.
- Prefer router modules for discovery/token-optimized reads; do not load canonical docs by default.
- Consult canonical docs only when explicitly requested, when router guidance is missing/ambiguous, or when resolving a source-of-truth conflict.
- Directionality is canonical → derived.
- Canonical docs MUST NOT reference `docs/agent_router/*`.

## Auto-generated files
- Files with `<!-- AUTO-GENERATED -->` header are managed by `docs/agent_router/MANIFEST.yaml`.
- Regenerate: `python scripts/docs/generate-router-files.py`.
- CI checks for drift: `python scripts/docs/generate-router-files.py --check`.
