# US-44 — Medical Record MVP: Update Extracted Data panel structure, labels, and scope

**Status:** Implemented (2026-02-20)  
**Owner:** Platform / Frontend (UX-led)  
**Type:** UX/UI behavior + mapping (contract-driven)

## User Story
As a **veterinarian reviewer**,  
I want the “Extracted Data / Informe” panel to present a **clinical medical record** with clear sections and field labels,  
so that I can review and edit clinical information quickly in a clinical-only panel.

## Scope

**In scope**
1) **Panel purpose and scope (MVP)**
   - The Extracted Data panel represents a **clinical Medical Record**.
   - The panel is clinical-only.

2) **Section structure (MVP)**
   - The panel renders sections in this exact order:
     1) **Centro Veterinario**
     2) **Paciente**
     3) **Propietario**
     4) **Visitas**
     5) **Notas internas**
     6) **Otros campos detectados**
     7) **Detalles del informe** (bottom)

3) **Field label changes (display-only)**
   - Display labels are updated for clarity in the review panel.
   - “NHC” is shown as **NHC** with tooltip “Número de historial clínico”.

**Out of scope**
- Introducing new clinical extraction logic beyond what the contract already provides.
- Normalizing clinical terms (e.g., SNOMED coding) in MVP UI.
- Any non-clinical claim UI (this story explicitly excludes it).

## Acceptance Criteria

1) The reviewer sees the Extracted Data panel as a **clinical-only** view, without financial/claim concepts.
2) The reviewer sees the seven sections in this exact order: Centro Veterinario, Paciente, Propietario, Visitas, Notas internas, Otros campos detectados, Detalles del informe.
3) The reviewer sees updated labels in the panel:
   - “Identificación del caso” is shown as “Centro Veterinario”.
   - Clinic and owner names are shown as “Nombre”.
   - Address fields are shown as “Dirección”.
   - Date of birth is shown as “Nacimiento”.
4) The reviewer sees “NHC” with tooltip “Número de historial clínico”.
5) If NHC is expected but no value is available, the reviewer still sees the NHC row with placeholder “—”.
6) In “Propietario”, “Dirección” shows an address value; identifier-like values are not presented as addresses.
7) The reviewer sees “Otros campos detectados” as a separate section for additional detected data.
8) The reviewer sees “Visitas” grouped by visit, without mixed data between different visits.

## Story-specific technical requirements
- Keep contract authority in `docs/projects/veterinary-medical-records/02-tech/technical-design.md` (Appendix D9 or equivalent authoritative section); do not redefine contract structure in this plan.
- Keep copy/labels/empty states aligned with `docs/projects/veterinary-medical-records/01-product/ux-design.md`.
- Use contract-driven rendering for visit grouping and “Otros campos detectados”; no UI-side heuristics or reclassification.
- If required contract capabilities are missing (e.g., explicit “other” bucket or owner address concept), this story is blocked until TECHNICAL_DESIGN is updated and backend output is aligned.
- Add/adjust UI tests for section order, clinical-only scope, NHC behavior, and owner address labeling.

## Dependencies / Placement
- Depends on UX copy/spec being updated in `docs/projects/veterinary-medical-records/01-product/ux-design.md`.
- **Placement:** implement **US-44 before US-43** (US-44 remains separate).

---