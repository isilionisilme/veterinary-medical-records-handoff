# US-43 — Render “Visitas” agrupadas cuando `canonical contract` (contract-driven, no heuristics)

**Status:** Planned  
**Owner:** Platform / Frontend

## User Story
Como **veterinario revisor**, quiero ver los datos clínicos **agrupados por visita** cuando un documento contiene múltiples visitas, para revisar cada episodio de forma clara y evitar mezclar información de visitas distintas.

## Scope
In scope:
1) For documents with multiple visits, the reviewer sees a separate block per visit in the “Visitas” section.
2) The reviewer sees visit information only inside its visit block, and non-visit document information outside visit blocks.
3) Information is not mixed across visit blocks.
4) Visit order is stable and consistent for the reviewer.
5) Search and filters only affect row visibility within existing containers and do not change visit grouping.
6) Review status (“reviewed/not reviewed”) continues to apply at document level.
7) Clinical-only scope: this story does not include financial or billing concepts.

Out of scope:
- UI heuristics to infer visits or move items.
- “Reviewed per visit”.
- Backend changes beyond the existing contract.

## Acceptance Criteria
1) When multiple visits exist, the reviewer sees one block per visit in the “Visitas” section.
2) Each visit block shows only information for that visit and does not mix information from other visits.
3) Information shown outside visit blocks is not repeated inside any visit block.
4) Visit order is deterministic and remains stable across reloads for the same document.
5) If an “unassigned” block exists, the reviewer sees it as a differentiated block with UX-defined copy.
6) If no visits are detected, the reviewer sees the UX-defined empty state for “Visitas”.
7) Search and filters do not change visit grouping or block order.
8) The review workflow remains document-level.
9) For documents without visit structure, the current experience remains without visible regressions.

## Story-specific technical requirements
- Mantener la autoridad de contrato en `docs/projects/veterinary-medical-records/02-tech/technical-design.md` Appendix D9; no redefinir payloads en esta historia.
- Contract-driven rendering and placement boundaries must follow `docs/projects/veterinary-medical-records/02-tech/technical-design.md` Appendix D9.
- Implementar render sin heurísticas: no crear, fusionar, reasignar ni inferir visitas desde frontend.
- Mantener reglas de separación entre datos de documento y datos de visita según D9.
- Mantener comportamiento de search/filter de US-34 sin reagrupación.
- Añadir cobertura de pruebas para orden estable, bloque sin asignar, estado vacío de visitas y regresión de experiencia vigente.

## Authoritative References
- `docs/projects/veterinary-medical-records/02-tech/technical-design.md` Appendix D9
- `docs/projects/veterinary-medical-records/01-product/ux-design.md`

---
