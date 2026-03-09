# Release 15 — Extraction field expansion (golden loops)

## Goal
Expand extraction coverage to all critical patient and clinic fields via the golden loop pattern, ensuring each field has dedicated fixtures, benchmark tests, labeled patterns, and normalization.

## Scope
- Pet name extraction hardening
- Clinic name extraction hardening
- Clinic address extraction hardening
- Bidirectional clinic enrichment (name <-> address)
- Date of birth (DOB) extraction hardening
- Microchip ID extraction hardening
- Owner address extraction (active)

## User Stories (in order)
- US-69 — Extract pet name accurately
- US-70 — Extract clinic name accurately
- US-71 — Extract clinic address accurately
- US-72 — Complete clinic address from name (and vice versa) on demand
- US-61 — Extract patient date of birth accurately
- US-62 — Extract patient microchip number accurately
- US-63 — Extract owner address without confusing it with clinic address

---
