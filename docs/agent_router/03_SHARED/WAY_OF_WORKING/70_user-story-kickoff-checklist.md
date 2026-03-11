<!-- AUTO-GENERATED from canonical source: way-of-working.md — DO NOT EDIT -->
<!-- To update, edit the canonical source and run: python scripts/docs/generate-router-files.py -->

## 8. User Story Kickoff Procedure

Before implementing each user story (US-XX):

1. Read the story requirements and relevant authoritative design requirements.
2. Identify **decision points** not explicitly specified (e.g., file size limits, storage roots, timeout values, retry
   counts, error code enums, default configuration values).
3. Resolve **discoverable facts** by inspecting the repository first (code/config/docs). Do not ask the user questions
   that can be answered by reading the repo.
4. Ask the user to confirm or choose for **non-discoverable preferences/tradeoffs**. Present 2–4 meaningful options and
   recommend a default. Do not proceed while any high-impact ambiguity remains; **STOP and ask**.
5. Record the resulting decisions/assumptions explicitly in the Pull Request description (and/or ADR-style note when
   requested).

---
