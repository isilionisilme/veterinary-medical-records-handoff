# Persistence model (SQLite)

## Minimum entities (authoritative)
Authority: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../TECHNICAL_DESIGN/00_entry.md) Appendix B2 (Minimal Persistent Data Model).

Implementation responsibility: provide repositories/adapters for:
- Document
- ProcessingRun
- Artifacts
- InterpretationVersion
- FieldChangeLog

## Document status derivation (authoritative)
Authority: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../TECHNICAL_DESIGN/00_entry.md) Appendix A (Contracts, States & Invariants).

Implementation guidance:
- Implement status derivation as a pure domain rule (e.g., a function that maps “latest run summary” to a status).
- Do not store or mutate `Document.status`; it is derived.

## Run invariants (authoritative)
Authority: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../TECHNICAL_DESIGN/00_entry.md) Appendix A2 + Appendix B1.2.

Implementation reminder: enforce invariants transactionally at the persistence layer; never via in-memory locks.

## SQLite guard pattern (authoritative)
Authority: [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../TECHNICAL_DESIGN/00_entry.md) Appendix B1.2.1 (Persistence-Level Guard Pattern).

Implementation guidance:
- Encapsulate `BEGIN IMMEDIATE` + “check for RUNNING” + “transition to RUNNING” into a single repository method.
- Never perform the check and the transition in separate transactions (no partial transitions).
