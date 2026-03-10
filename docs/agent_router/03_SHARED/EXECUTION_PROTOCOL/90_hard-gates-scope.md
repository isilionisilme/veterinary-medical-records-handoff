<!-- AUTO-GENERATED from canonical source: plan-execution-protocol.md — DO NOT EDIT -->
<!-- To update, edit the canonical source and run: python scripts/docs/generate-router-files.py -->

## 12. Hard-Gates: Structured Decision Protocol

> **Presentation rule:** All options in hard-gates MUST be presented following the Agent-user interaction rule (AGENTS.md → Global rules).

In 🚧 steps, the planning agent presents options:
```
Backlog items:
1. ✅ Centralize config — Impact: High, Effort: S
2. ✅ Add health check — Impact: Medium, Effort: S
3. ❌ Migrate to PostgreSQL — Impact: High, Effort: L (OUT OF SCOPE)
```
The user responds with numbers: `1, 2, 4` or `all` or `none`.
The planning agent records the decision, commits, prepares the prompt, and directs to the execution agent.

---
