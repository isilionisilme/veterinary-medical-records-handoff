# Plan: ARCH-06 Security Architecture Documentation

> **Operational rules:** See [plan-execution-protocol.md](../../../03-ops/plan-execution-protocol.md) for agent execution protocol, SCOPE BOUNDARY template, commit conventions, and handoff messages.

**Branch:** `refactor/arch-06`
**PR:** Pending (PR created on explicit user request)
**Backlog item:** [arch-06-create-security-architecture-documentation.md](../../Backlog/arch-06-create-security-architecture-documentation.md)
**Prerequisite:** None
**Worktree:** `D:\Git\worktrees\cuarto`
**CI Mode:** `2) Pipeline depth-1 gate` (default)
**Agents:** Planning agent (plan authoring) -> Execution agent (implementation)
**Automation Mode:** `Supervisado` (default)
**Iteration:** pending

---

## Agent Instructions

1. En cuanto termines una tarea, marca el checkbox correspondiente en `Execution Status`.
2. No hagas commit ni push sin aprobacion explicita del usuario (`Automation Mode: Supervisado`).
3. Mantener cambios estrictamente en alcance de ARCH-06 (documentacion de arquitectura de seguridad).

---

## Context

ARCH-06 identifica un gap critico: no existe documentacion formal de arquitectura de seguridad para la aplicacion de historiales clinicos veterinarios. La auditoria de arquitectura (2026-03-09) lo marca como prerequisito para trabajos posteriores de autenticacion de produccion (ARCH-13).

---

## Objective

1. Crear `docs/projects/veterinary-medical-records/02-tech/security-architecture.md`.
2. Documentar el estado actual y el objetivo de produccion para controles de seguridad clave.
3. Dejar el documento alineado con ADRs y diseno tecnico existentes.

---

## Scope Boundary

- **In scope:** redaccion y validacion del nuevo documento `02-tech/security-architecture.md`, referencias internas necesarias, consistencia con ADRs/diseno tecnico.
- **Out of scope:** implementacion de controles en codigo, cambios de infraestructura, rollout de autenticacion de produccion.

---

## Design Decisions

### DD-1: Documento unico de arquitectura de seguridad
**Rationale:** Centralizar decisiones y estado objetivo en un artefacto tecnico unico evita dispersion entre backlog, ADRs y notas operativas.

### DD-2: Enfoque dual "actual + target"
**Rationale:** ARCH-06 exige describir estado actual y destino de produccion para habilitar priorizacion y trazabilidad de remediaciones.

### DD-3: Threat model STRIDE acotado al flujo critico
**Rationale:** El backlog define foco en upload de PDF, endpoints API y datos almacenados; este alcance maximiza valor para evaluacion tecnica inmediata.

---

## Execution Status

**Legend**
- 🔄 auto-chain — executable by agent
- 🚧 hard-gate — user review/decision required

### Phase 1 — Discovery and Alignment

- [ ] P1-A 🔄 — Relevar contexto de seguridad existente en `02-tech/architecture.md`, `02-tech/technical-design.md` y ADRs aplicables para extraer restricciones, decisiones y terminologia.
- [ ] P1-B 🔄 — Definir estructura objetivo de `security-architecture.md` con secciones obligatorias ARCH-06 y subapartados de estado actual vs objetivo de produccion.

### Phase 2 — Author Security Architecture Doc

- [ ] P2-A 🔄 — Crear `02-tech/security-architecture.md` cubriendo: (1) authentication strategy, (2) STRIDE threat model, (3) encryption strategy, (4) rate limiting policy, (5) upload validation strategy.
- [ ] P2-B 🔄 — Alinear el contenido con ADRs/diseno tecnico y corregir inconsistencias de terminologia o supuestos.

### Phase 3 — Validation and Handoff

- [ ] P3-A 🔄 — Validar criterios de aceptacion del backlog y revisar enlaces/estructura Markdown del documento.
- [ ] P3-B 🚧 — Hard-gate: presentar el documento final al usuario para aprobacion explicita de alcance, profundidad tecnica y consistencia.

---

## Prompt Queue

### Prompt 1 — P1-A + P1-B: Discovery + structure

**Steps:** P1-A, P1-B  
**Files:** `docs/projects/veterinary-medical-records/02-tech/architecture.md`, `docs/projects/veterinary-medical-records/02-tech/technical-design.md`, `docs/projects/veterinary-medical-records/02-tech/adr/*.md`

**Instructions:**

1. Leer fuentes tecnicas actuales para extraer decisiones o constraints relacionados con autenticacion, cifrado, validacion de subida y limites de uso.
2. Consolidar vocabulario canonico (terminos y componentes) para evitar contradicciones.
3. Proponer estructura final de `security-architecture.md` con 5 secciones obligatorias y subbloques "Current state" y "Production target" cuando aplique.

---

### Prompt 2 — P2-A + P2-B: Author + consistency

**Steps:** P2-A, P2-B  
**Files:** `docs/projects/veterinary-medical-records/02-tech/security-architecture.md`

**Instructions:**

1. Crear el documento con secciones minimas:
   - Authentication strategy (current state + production target).
   - Threat model (STRIDE) para upload PDF, endpoints API y datos almacenados.
   - Encryption strategy (TLS termination + data-at-rest para PII en SQLite).
   - Rate limiting policy (current + planned).
   - Upload validation strategy.
2. Incluir riesgos conocidos, mitigaciones actuales y mejoras planificadas donde corresponda.
3. Verificar que el texto no contradiga ADRs ni arquitectura/diseno tecnico existente.

---

### Prompt 3 — P3-A + P3-B: Validate + user hard-gate

**Steps:** P3-A, P3-B  
**Files:** `docs/projects/veterinary-medical-records/02-tech/security-architecture.md`

**Instructions:**

1. Comprobar acceptance criteria de ARCH-06 uno por uno y documentar PASS/FAIL.
2. Revisar calidad documental (encabezados, enlaces, consistencia terminologica).
3. Presentar al usuario checklist final para aprobacion:
   - [ ] Existe `02-tech/security-architecture.md`.
   - [ ] Cubre los 5 temas obligatorios.
   - [ ] Es consistente con ADRs y diseno tecnico.
4. Esperar aprobacion explicita antes de marcar P3-B como completado.

---

## Active Prompt

Pending plan approval.

---

## Acceptance Criteria

From [ARCH-06 backlog item](../../Backlog/arch-06-create-security-architecture-documentation.md):

1. Document exists at `02-tech/security-architecture.md`.
2. Covers all 5 required topics:
   - Authentication strategy (current state + production target)
   - STRIDE threat model (PDF upload, API endpoints, stored data)
   - Encryption strategy (TLS termination, data-at-rest for PII in SQLite)
   - Rate limiting policy (current + planned)
   - Upload validation strategy
3. Content is consistent with existing ADRs and technical design.

---

## Validation Checklist

- [ ] Documento creado en la ruta esperada.
- [ ] Las cinco secciones obligatorias existen y tienen contenido tecnico concreto.
- [ ] El threat model STRIDE cubre explicitamente upload PDF, API y datos almacenados.
- [ ] Se documenta diferencia entre estado actual y objetivo de produccion donde aplica.
- [ ] No se detectan contradicciones con ADRs/diseno tecnico.

---

## How to Test

1. Abrir `docs/projects/veterinary-medical-records/02-tech/security-architecture.md` y verificar que existe.
2. Confirmar que contiene las 5 secciones obligatorias de ARCH-06.
3. Revisar que STRIDE menciona explicitamente: upload de PDF, endpoints API y datos almacenados.
4. Revisar que autenticacion y rate limiting incluyen estado actual y target/plan.
5. Comparar con ADRs y `technical-design.md` para validar consistencia terminologica y de decisiones.