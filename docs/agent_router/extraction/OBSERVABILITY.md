<!-- AUTO-GENERATED from canonical source: extraction-quality.md — DO NOT EDIT -->
<!-- To update, edit the canonical source and run: python scripts/docs/generate-router-files.py -->

## 3. Observability

### What We Capture

Per-run extraction snapshot with per-field status:
- `missing` / `rejected` / `accepted`

Per-field candidate evidence:
- `topCandidates` (max 3)
- confidence
- reason (for rejected)
- suspicious accepted flags (triage)

### Storage

- Path: `.local/extraction_runs/<documentId>.json`
- Behavior: ring buffer of latest 20 runs per document.

### Backend Endpoints

| Endpoint | Purpose |
|----------|---------|
| `POST /debug/extraction-runs` | Persist one run snapshot |
| `GET /debug/extraction-runs/{documentId}` | Return persisted runs for one document |
| `GET /debug/extraction-runs/{documentId}/summary?limit=...` | Aggregate recent runs (default window: 20) |

Optional `run_id` parameter for run-pinned summary filtering.

### Summary Outputs

- Most missing fields
- Most rejected fields
- For missing/rejected: top1 sample + average confidence
- Suspicious accepted counts
- Missing split: with candidates / without candidates

### Practical Interpretation Rule

- `limit=20` includes historical behavior — useful for **trends**.
- `limit=1` isolates the latest run — correct check to confirm a **new fix**.

### Snapshot Ownership

Snapshots are **backend-canonical**. The backend auto-persists snapshots at completed-run boundary. Frontend does NOT write snapshots.

---
