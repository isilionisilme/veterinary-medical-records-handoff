# Plan: IMP-06 — Localize Core Patient UI Field Labels to Spanish

> **Operational rules:** See [plan-execution-protocol.md](../../03-ops/plan-execution-protocol.md) for agent execution protocol, SCOPE BOUNDARY template, commit conventions, and handoff messages.

**Backlog item:** [imp-06-localize-core-patient-ui-field-labels-to-spanish.md](../Backlog/imp-06-localize-core-patient-ui-field-labels-to-spanish.md)
**Branch:** `codex/veterinary-medical-records/docs/imp-06-ui-labels-es`
**PR:** pendiente
**Prerequisite:** `main` actualizado y tests verdes
**Worktree:** `C:/Users/ferna/.codex/worktrees/c691/veterinary-medical-records`
**CI Mode:** `2) Pipeline depth-1 gate` (default)
**Agents:** pendiente de selección explícita del usuario antes de Step 1
**Automation Mode:** `Supervisado` (default hasta selección explícita del usuario)

---

## Agent Instructions

1. **En cuanto termines una tarea, márcala como completada en el plan** (checkbox `[x]` inmediato, sin esperar lote).
2. **Cuando llegues a una sugerencia de commit, lanza los tests L2** (`scripts/ci/test-L2.ps1`). Si no funcionan, repáralos. Cuando L2 esté verde, espera instrucciones del usuario.
3. **No hagas commit ni push sin aprobación** explícita del usuario.

---

## Context

The `FIELD_LABELS` map in `frontend/src/constants/appWorkspace.ts` is the centralized source for Spanish UI labels. When a key is not in `FIELD_LABELS`, the display falls back through two paths:

1. **Canonical contract path** (non-canonical=false): `GLOBAL_SCHEMA[key].label` from `shared/global_schema_contract.json`.
2. **Dynamic/non-canonical path**: `formatReviewKeyLabel(key)` — converts snake_case to "Title case" in English.

### Current gap analysis

| Field key | In `FIELD_LABELS`? | In `global_schema`? | Current UI render | Required label |
|---|---|---|---|---|
| `vet_name` | ❌ | ✅ "Veterinario" | "Veterinario" via schema | **Veterinario** |
| `breed` | ❌ | ✅ "Raza" | "Raza" via schema | **Raza** |
| `age` | ❌ | ✅ "Edad" | "Edad" via schema | **Edad (ultima visita)** |
| `microchip_id` | ❌ | ✅ "Microchip" | "Microchip" via schema | **Microchip** |
| `reproductive_status` | ❌ | ❌ | "Reproductive status" (EN fallback) | **Estado reproductivo** |
| `repro_status` | ❌ | ❌ | "Repro status" (EN fallback) | **Estado reproductivo** |
| `species` | ❌ | ✅ "Especie" | "Especie" via schema | **Especie** |
| `sex` | ❌ | ✅ "Sexo" | "Sexo" via schema | **Sexo** |
| `weight` | ❌ | ✅ "Peso" | "Peso" via schema | **Peso** |

**Critical gaps**: `reproductive_status` and `repro_status` fall back to English. `age` renders as "Edad" instead of "Edad (ultima visita)".
**Defensive gaps**: 5 keys (`vet_name`, `breed`, `microchip_id`, `species`, `sex`, `weight`) rely on schema label indirectly; adding them to `FIELD_LABELS` makes the display explicit and independent of schema label wording.

### Key files

| File | Role |
|---|---|
| `frontend/src/constants/appWorkspace.ts` | `FIELD_LABELS` map (lines ~137–165), `CANONICAL_DOCUMENT_CONCEPTS` (~101) |
| `frontend/src/hooks/useDisplayFieldMapping.ts` | Label resolution: `FIELD_LABELS[key] ?? definition.label` (~168) |
| `frontend/src/lib/appWorkspaceUtils.ts` | `formatReviewKeyLabel()` fallback (~241) |
| `frontend/src/components/structured/FieldEditDialog.tsx` | Edit dialog title: `Editar "${fieldLabel}"` (~117) |
| `frontend/src/components/review/ReviewFieldRenderers.tsx` | Renders `field.label` in panel |
| `frontend/src/components/review/ReviewSectionLayout.tsx` | `FIELD_LABELS[key] ?? formatReviewKeyLabel(key)` (~223) |
| `frontend/src/components/StructuredDataView.test.tsx` | `uiLabelOverrides` test assertions (~37–46) |
| `frontend/src/hooks/useDisplayFieldMapping.test.tsx` | Hook test for field mapping |
| `shared/global_schema_contract.json` | Schema label definitions (backend contract) |

---

## Objective

1. Add explicit Spanish entries in `FIELD_LABELS` for all 8 targeted field keys (+ `repro_status` alias).
2. Ensure review panel and edit dialog both use the explicit labels.
3. Update/add frontend tests to assert the new labels render correctly and prevent regression.

## Scope Boundary

- **In scope:** `FIELD_LABELS` entries in `appWorkspace.ts`, `uiLabelOverrides` in `StructuredDataView.test.tsx`, new or updated unit test assertions in `useDisplayFieldMapping.test.tsx`, manual validation guidance.
- **Out of scope:** No rename of internal field keys (`vet_name`, `breed`, etc.), no backend API / schema / extraction changes, no i18n framework, no UI layout/style changes, no `global_schema_contract.json` edits.

---

## Commit recommendations (inline, non-blocking)

| After steps | Recommended message |
|---|---|
| P1-A .. P1-B | `feat(labels): add explicit Spanish FIELD_LABELS for targeted patient fields` |
| P2-A .. P2-C | `test(labels): update and add tests for Spanish label mapping` |
| P3-A | `docs(labels): add validation evidence to plan` |

En modo Supervisado, cada commit requiere confirmación explícita del usuario.
Push permanece manual en todos los modos.

---

## Execution Status

**Leyenda**
- 🔄 auto-chain — ejecutable por agente
- 🚧 hard-gate — revisión/decisión de usuario

### Phase 0 — Validación de prerequisitos

- [x] P0-A 🔄 — Verificar que la rama base (`main`) está actualizada y los tests L1 pasan. Si no, STOP. — `no-commit`
- [x] P0-B 🚧 — Hard-gate: usuario confirma agente y modo de automatización. — `no-commit`

### Phase 1 — Añadir labels al mapa `FIELD_LABELS`

- [x] P1-A 🔄 — Añadir las siguientes entradas al objeto `FIELD_LABELS` en `frontend/src/constants/appWorkspace.ts` (tras las entradas existentes, agrupadas al final de las claves de paciente):

  ```typescript
  vet_name: "Veterinario",
  breed: "Raza",
  age: "Edad (ultima visita)",
  microchip_id: "Microchip",
  reproductive_status: "Estado reproductivo",
  repro_status: "Estado reproductivo",
  species: "Especie",
  sex: "Sexo",
  weight: "Peso",
  ```

  No modificar ni eliminar entradas existentes. — `no-commit (pending commit point)`

- [x] P1-B 🔄 — Verificar que `ReviewSectionLayout.tsx` (~L223) consume `FIELD_LABELS` igual que `useDisplayFieldMapping.ts`; si usa un path distinto confirmar que los nuevos labels también se resuelven. Si no, añadir import o ajustar. — `no-commit (pending commit point)`

> **Commit point →** `feat(labels): add explicit Spanish FIELD_LABELS for targeted patient fields`
> Lanzar L2. Si falla, reparar. Cuando L2 verde → esperar instrucciones del usuario.

### Phase 2 — Tests

- [x] P2-A 🔄 — Actualizar `uiLabelOverrides` en `StructuredDataView.test.tsx` (~L37) para incluir las claves que ahora tienen label explícito en `FIELD_LABELS` y que previamente caían al schema label (para que el test siga siendo correcto cuando el label map tenga prioridad). Claves a añadir: `vet_name`, `breed`, `age`, `microchip_id`, `species`, `sex`, `weight`. Valor esperado = el nuevo label de `FIELD_LABELS`. — `no-commit (pending commit point)`

- [x] P2-B 🔄 — Añadir test case en `useDisplayFieldMapping.test.tsx` que verifique: dado un field con `key: "reproductive_status"` (no presente en `GLOBAL_SCHEMA`), el `label` del `ReviewDisplayField` resultante es `"Estado reproductivo"` y no el fallback en inglés `"Reproductive status"`. — `no-commit (pending commit point)`

- [x] P2-C 🔄 — Añadir test case que verifique: dado un field con `key: "age"`, el label resultante es `"Edad (ultima visita)"` y no `"Edad"` (el valor del schema). — `no-commit (pending commit point)`

> **Commit point →** `test(labels): update and add tests for Spanish label mapping`
> Lanzar L2. Si falla, reparar. Cuando L2 verde → esperar instrucciones del usuario.

### Phase 3 — Validación y cierre

- [ ] P3-A 🔄 — Ejecutar validation checklist completa del backlog item. Documentar evidencia en este plan:
  1. Revisar que todas las 8 claves + alias `repro_status` están en `FIELD_LABELS`.
  2. Buscar cualquier campo que aún caiga al fallback inglés: `grep` por `formatReviewKeyLabel` y confirmar que no se invoca para las claves objetivo.
  3. Confirmar que `FieldEditDialog` recibe el `fieldLabel` correcto (flujo: `ReviewDisplayField.label` → `onOpenFieldEditDialog` → dialog).
  — `no-commit (evidence documented)`

- [ ] P3-B 🚧 — Hard-gate: usuario valida resultados y aprueba para PR. — `no-commit`

---

## Manual Validation Guidance

Una vez implementado, el evaluador puede verificar:

1. **Panel de revisión:** abrir un documento procesado y confirmar que los campos `Veterinario`, `Raza`, `Edad (ultima visita)`, `Microchip`, `Estado reproductivo`, `Especie`, `Sexo`, `Peso` se muestran en español.
2. **Diálogo de edición:** hacer clic en "Editar" en cada uno de esos campos y verificar que el título dice `Editar "Veterinario"`, `Editar "Raza"`, etc.
3. **Sin regresiones:** los campos que ya tenían label explícito (`clinic_name`, `pet_name`, `dob`, etc.) siguen mostrándose correctamente.

---

## Prompt Queue

### P0-A — Verificar prerequisitos

```
Verificar que main está actualizado (git log --oneline -1 main vs origin/main).
Ejecutar tests L1 (scripts/ci/test-L1.ps1).
Si alguno falla, STOP y reportar.
```

### P1-A — Añadir entradas a FIELD_LABELS

```
Abrir frontend/src/constants/appWorkspace.ts.
En el objeto FIELD_LABELS (aprox línea 137), añadir las 9 entradas nuevas
(vet_name, breed, age, microchip_id, reproductive_status, repro_status, species, sex, weight)
con los labels en español definidos en el gap analysis.
No modificar entradas existentes. No cambiar ningún otro archivo aún.
```

### P1-B — Verificar path de resolución en ReviewSectionLayout

```
Abrir frontend/src/components/review/ReviewSectionLayout.tsx.
Buscar la línea donde se resuelve el label (aprox ~223).
Confirmar que usa FIELD_LABELS[key] con el mismo import.
Si el import falta o usa un path distinto, ajustar.
```

### P2-A — Actualizar uiLabelOverrides en test

```
Abrir frontend/src/components/StructuredDataView.test.tsx.
En el objeto uiLabelOverrides (~L37), añadir las entradas para las claves
que ahora tienen label explícito en FIELD_LABELS y sobrescriben el schema label.
Solo necesitas añadir las que difieren del schema label: age: "Edad (ultima visita)".
Las demás (vet_name, breed, etc.) coinciden con el schema label, así que el test sigue pasando.
Pero añade igualmente las que ahora están en FIELD_LABELS para documentar la intención.
```

### P2-B — Test para reproductive_status

```
Abrir frontend/src/hooks/useDisplayFieldMapping.test.tsx.
Añadir un test case:
- Input: un ReviewField con key "reproductive_status", value "Castrado", sin canonical contract.
- Assert: el ReviewDisplayField resultante tiene label "Estado reproductivo".
- Assert negativo: label !== "Reproductive status".
```

### P2-C — Test para age override

```
En el mismo archivo, añadir un test case:
- Input: un ReviewField con key "age", value "5 años", con canonical contract (usa GLOBAL_SCHEMA).
- Assert: el ReviewDisplayField resultante tiene label "Edad (ultima visita)" (FIELD_LABELS override gana sobre schema "Edad").
```
