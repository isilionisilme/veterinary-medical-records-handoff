# Plan de ejecución AI — Playwright E2E (Producción)

**PR:** [#159](https://github.com/isilionisilme/veterinary-medical-records/pull/159)

## Objetivo
Integrar y estabilizar Playwright E2E en este repositorio para uso local (VS Code) y CI, dejando una PR lista para merge a `main`.

Focos:
- Setup técnico Playwright en `frontend/`
- Smoke tests E2E confiables
- Señal CI reproducible
- Entrega incremental con evidencia verificable

---

## Estado de ejecución — actualizar al completar cada paso

> **Protocolo `Continúa`:** abre un chat nuevo, selecciona el agente correcto, adjunta este archivo y escribe `Continúa`. El agente leerá el estado, ejecutará el siguiente paso sin completar y se detendrá al terminar.

**Leyenda de automatización:**
- 🔄 **auto-chain** — Codex ejecuta solo; revisión posterior.
- 🚧 **hard-gate** — requiere decisión/validación humana antes de continuar.

### Fase P1 — Integración Playwright E2E
- [x] P1-A 🔄 — Verificación de estado actual y gap analysis (Codex)
- [x] P1-B 🔄 — Setup Playwright en `frontend/` (dependencia, config, scripts, fixture) (Codex)
- [x] P1-C 🔄 — Selectores `data-testid` E2E estables (Codex)
- [x] P1-D 🔄 — Smoke `app-loads` verde y estable (Codex)
- [x] P1-E 🔄 — Smoke `upload` robusto por `document_id` (Codex)
- [x] P1-F 🔄 — Job `CI / e2e` con artifacts en fallo (Codex)
- [x] P1-G 🔄 — Validación técnica: `test:e2e`, `tsc --noEmit`, `eslint .` (Codex)
- [x] P1-H 🚧 — Validación manual en headed + checklist funcional mínimo (Usuario/Claude)
- [x] P1-I 🔄 — Commit, push y PR hacia `main` (Codex)
- [x] P1-J 🚧 — Veredicto final y decisión de merge (Claude/Usuario) ✅ PR #159 merged 2026-02-26

---

## Reglas operativas (obligatorias)

Estas reglas son de cumplimiento estricto para este plan y replican la política operativa del plan maestro.

1. **Identity check (hard rule):**
   - Este flujo está diseñado para `GPT-5.3-Codex` cuando el paso es de Codex.
   - Si el agente activo no corresponde al paso siguiente, detenerse y hacer handoff explícito al agente correcto.

2. **Branch check (hard rule):**
   - Ejecutar `git branch --show-current` antes de empezar cada paso.
   - Rama objetivo de este plan: `improvement/playwright`.
   - Si no coincide, STOP con instrucción concreta para cambiar de rama.

3. **Sync check (hard rule):**
   - Antes de ejecutar un paso, sincronizar rama (`git fetch` + `git pull` cuando aplique).
   - Si no hay upstream configurado, registrarlo como limitación operativa y continuar con evidencia local.

4. **Scope boundary (hard rule):**
   - Cada paso implementa solo su alcance.
   - No encadenar cambios fuera del paso activo.

5. **Paso por paso (hard rule):**
   - Completar y cerrar un paso antes de iniciar el siguiente.
   - Actualizar checkbox del estado al terminar.

6. **Evidencia obligatoria por paso:**
   - Comandos ejecutados.
   - Resultado relevante.
   - Archivos tocados.
   - Criterio de aceptación validado.

7. **Formato de hallazgos/recomendaciones (obligatorio):**
   - Problema
   - Impacto
   - Esfuerzo (S/M/L)
   - Riesgo
   - Criterio de aceptación
   - Evidencia de validación

8. **Commits (convención obligatoria):**
   - Formato: `<tipo>(plan-<id>): <descripción corta>`
   - Ejemplos: `test(plan-p1e): stabilize upload smoke by upload response id`

9. **Cierre obligatorio por paso (hard rule) — SECUENCIA EXACTA:**
   Antes de marcar un paso como completado, ejecutar TODOS estos sub-pasos en orden:
   1. `git add` de los archivos tocados.
   2. `git commit` con mensaje siguiendo regla 8.
   3. Actualizar checkbox `[x]` del paso en este plan.
   4. `git add` del plan actualizado + `git commit -m "docs(plan): mark P?-? complete"`.
   5. `git push origin improvement/playwright`.
   6. Registrar evidencia (regla 6).
   Solo después de los 6 sub-pasos se considera el paso cerrado.
   **Omitir cualquiera de estos sub-pasos es una violación operativa.**

10. **Handoff obligatorio al cerrar paso (hard rule):**
   - Si el siguiente paso es del **mismo agente** y no es 🚧: anunciar cierre y continuar en el mismo chat.
   - Si el siguiente paso es de **otro agente** o es 🚧: STOP. Abrir chat nuevo + agente exacto + adjuntar este archivo + escribir `Continúa`.

11. **Mensajes de handoff (obligatorios):**
   - Caso A (siguiente paso otro agente y prompt listo):
     - "✅ P?-? completado. Siguiente: abre un chat nuevo en Copilot → selecciona **[agente]** → adjunta `PLAN_2026-02-26_INSTALL_PLAYWRIGHT.md` → escribe `Continúa`."
   - Caso B (siguiente paso Codex sin prompt listo):
     - Claude **debe escribir el prompt del siguiente paso directamente en la sección "Prompt activo" del plan** antes de emitir el handoff. Nunca dar el prompt solo como texto de chat.
     - "✅ P?-? completado. Prompt de P?-? escrito en el plan. Siguiente: abre un chat nuevo en Copilot → selecciona **GPT-5.3-Codex** → adjunta `PLAN_2026-02-26_INSTALL_PLAYWRIGHT.md` → escribe `Continúa`."
   - Caso C (siguiente paso Claude/hard-gate):
     - "✅ P?-? completado. Siguiente: abre un chat nuevo en Copilot → selecciona **Claude Opus 4.6** → adjunta `PLAN_2026-02-26_INSTALL_PLAYWRIGHT.md` → escribe `Continúa`."

12. **No-review implícito:**
   - No iniciar code review automáticamente salvo instrucción explícita del usuario.

13. **No implementación fuera de pedido:**
   - Si el objetivo es plan/documentación, no ejecutar implementación técnica en ese turno.

14. **Control de regresión:**
   - No marcar un paso como completo sin validaciones mínimas definidas para ese paso.

15. **Context safety valve:**
   - Si el contexto del chat se agota, cerrar paso actual limpiamente y emitir handoff.

16. **Regla de finalización de iteración:**
   - Ningún cierre sin "siguiente acción" concreta.

17. **Prohibición de saltos:**
   - No saltar hard-gates.

---

## Prompt activo

_Completado: P1-I_

_Vacío._

---

## Cola de prompts

### P1-E — Stabilizar `upload-smoke` (Codex)

**Objetivo:** Hacer el smoke de upload determinístico usando `document_id` de la respuesta API en vez de texto.

**Contexto técnico:**
- `POST /documents/upload` responde HTTP 201 con `{ document_id: string, status: string, created_at: string }`.
- El sidebar ya renderiza `data-testid="doc-row-${item.document_id}"` por cada documento.
- El test actual usa `toContainText("sample.pdf")` que es frágil si hay documentos previos con el mismo nombre.

**Instrucciones operativas:**

1. **Branch check:** `git branch --show-current` → debe ser `improvement/playwright`. Si no, STOP.
2. **Sync check:** `git fetch origin && git pull` (si hay upstream).
3. **Precondición:** Docker stack corriendo en `localhost:80`.
4. Reescribir `e2e/upload-smoke.spec.ts`:
   - Interceptar la respuesta de `POST /documents/upload` con `page.waitForResponse()`.
   - Extraer `document_id` del JSON de respuesta.
   - Asertar visibilidad de `data-testid="doc-row-${document_id}"` en el sidebar.
   - Mantener `test.setTimeout(90_000)` para este test específico (upload + procesamiento backend es lento).
   - No usar assertions basadas en texto del filename.
5. Ejecutar: `cd frontend && npx playwright test e2e/upload-smoke.spec.ts`
6. Ejecutar 3 veces consecutivas para verificar estabilidad.
7. Commit: `test(plan-p1e): stabilize upload smoke by document_id assertion`

**Criterio de aceptación:**
- `npx playwright test e2e/upload-smoke.spec.ts` pasa 3/3 veces.
- La assertion usa `document_id` del response, no texto de filename.
- `cd frontend && npm run test:e2e` (suite completa) en verde.

---

### P1-F — Job `CI / e2e` con artifacts en fallo (Codex)

**Objetivo:** Añadir un job `e2e` al CI que ejecute los tests de Playwright y preserve artifacts (traces, screenshots, video) en caso de fallo.

**Contexto técnico:**
- CI en `.github/workflows/ci.yml`.
- Jobs actuales: `frontend_test_build`, `quality`, `docker_packaging_guard`, más guards de PR.
- El job `docker_packaging_guard` ya hace `docker compose build` y valida contratos — reutilizar patrón.

**Instrucciones operativas:**

1. **Branch check:** `git branch --show-current` → debe ser `improvement/playwright`. Si no, STOP.
2. **Sync check:** `git fetch origin && git pull` (si hay upstream).
3. Añadir job `e2e` en `.github/workflows/ci.yml`:
   - `needs: [docker_packaging_guard]` o equivalente para tener imágenes Docker construidas.
   - Steps:
     1. Checkout.
     2. Setup Node (misma versión que `frontend_test_build`).
     3. `npm ci` en `frontend/`.
     4. `npx playwright install --with-deps chromium`.
     5. Start Docker stack: `docker compose up -d --wait` (o similar; `FRONTEND_PORT=80`).
     6. Run: `cd frontend && npx playwright test`.
     7. Upload artifact on failure: `playwright-report/`, `test-results/` con `actions/upload-artifact@v4`.
   - Trigger: mismos triggers que el job principal (push + PR).
4. **No modificar otros jobs existentes.**
5. Validar: revisar YAML con lint mental; no se requiere ejecución CI real en este paso.
6. Commit: `ci(plan-p1f): add e2e job with playwright artifacts on failure`

**Criterio de aceptación:**
- Job `e2e` presente en `ci.yml`.
- Artifacts configurados para `playwright-report/` y `test-results/` solo en fallo.
- `npx playwright install chromium` en el pipeline.
- Job depende de imágenes Docker construidas.

---

### P1-G — Validación técnica: quality gates (Codex)

**Objetivo:** Ejecutar todos los quality gates locales y consolidar evidencia antes de la validación manual.

**Instrucciones operativas:**

1. **Branch check:** `git branch --show-current` → debe ser `improvement/playwright`. Si no, STOP.
2. **Sync check:** `git fetch origin && git pull` (si hay upstream).
3. **Precondición:** Docker stack corriendo en `localhost:80`.
4. Ejecutar en orden y capturar salida:
   - `cd frontend && npm run test:e2e` → debe pasar (todos los spec verdes).
   - `cd frontend && npx tsc --noEmit` → 0 errores.
   - `cd frontend && npx eslint .` → 0 errores (warnings aceptables si pre-existentes).
5. Si algún check falla:
   - Corregir solo si es un problema introducido por este plan (P1-B a P1-F).
   - Si es pre-existente, documentar como hallazgo y continuar.
6. Consolidar evidencia: lista de comandos + resultados en el handoff.
7. Commit (solo si hay fixes): `fix(plan-p1g): resolve quality gate findings`

**Criterio de aceptación:**
- `npm run test:e2e` verde.
- `tsc --noEmit` limpio.
- `eslint .` limpio (o solo warnings pre-existentes documentados).
- Evidencia de los 3 comandos capturada.

---

### P1-H — Validación manual headed + checklist funcional (Claude/Usuario)

**Objetivo:** Validación humana de los tests E2E en modo visible (headed) y checklist funcional mínimo.

**Instrucciones para el usuario:**

1. **Prerequisito:** Docker stack corriendo en `localhost:80`:
   ```bash
   $env:FRONTEND_PORT='80'; docker compose up -d --build --wait
   ```
2. Ejecutar tests en modo headed:
   ```bash
   cd frontend
   npm run test:e2e:headed
   ```
3. **Checklist funcional (verificar visualmente):**
   - [ ] `app-loads`: el navegador abre y se ven el sidebar y la zona de upload.
   - [ ] `upload-smoke`: se sube un PDF, aparece el toast de progreso, y el documento aparece en el sidebar.
   - [ ] Los tests no tienen delays artificiales visibles (no hay `waitForTimeout(5000)` tipo hacks).
   - [ ] Los tests corren en < 2 minutos totales.
4. **Decisión:**
   - Si todo pasa → marcar P1-H como completado y continuar a P1-I.
   - Si algo falla → describir el problema específico; Claude propondrá fix y se iterará.

**Criterio de aceptación:**
- Checklist 4/4 marcado.
- Sin hallazgos bloqueantes.

---

### P1-I — Commit, push y PR hacia `main` (Codex)

**Objetivo:** Asegurar que todos los cambios están commiteados, pushear la rama y abrir PR hacia `main`.

**Instrucciones operativas:**

1. **Branch check:** `git branch --show-current` → debe ser `improvement/playwright`. Si no, STOP.
2. **Sync check:** `git fetch origin && git pull` (si hay upstream).
3. Verificar estado limpio: `git status` → no debe haber cambios sin commitear.
   - Si los hay, commitear con mensaje descriptivo siguiendo convención del plan.
4. Push: `git push origin improvement/playwright` (o `--set-upstream` si es primera vez).
5. Crear PR con `gh pr create`:
   - Title: `test: integrate Playwright E2E smoke tests`
   - Body debe incluir:
     - **Qué cambia:** setup Playwright, 2 smoke tests, job CI e2e.
     - **How to test:**
       ```bash
       $env:FRONTEND_PORT='80'; docker compose up -d --build --wait
       cd frontend
       npm run test:e2e
       npx tsc --noEmit
       npx eslint .
       ```
     - **Checklist:** links a criterios de aceptación global del plan.
   - Base: `main`.
   - Labels: si disponibles, `test`, `e2e`.
6. Capturar URL de la PR creada.
7. **No hacer merge** — eso es decisión de P1-J.

**Criterio de aceptación:**
- `git status` limpio.
- PR abierta hacia `main` con sección `How to test`.
- URL de PR capturada en evidencia.

---

### P1-J — Veredicto final y decisión de merge (Claude/Usuario)

**Objetivo:** Revisión final de la PR y decisión de merge.

**Instrucciones para Claude:**

1. Leer la PR abierta en P1-I (usar `gh pr view`).
2. Verificar:
   - [ ] CI pasa (job `e2e` verde en la PR).
   - [ ] CI jobs existentes no se rompieron.
   - [ ] Diff es limpio y acotado al scope del plan.
   - [ ] `How to test` está presente y es correcto.
   - [ ] No se introdujeron dependencias innecesarias.
3. **Si todo OK:** recomendar merge al usuario con `gh pr merge --squash`.
4. **Si hay problemas:** listar hallazgos con formato estándar del plan y proponer iteración.

**Criterio de aceptación:**
- PR revisada con veredicto explícito (APPROVE / REQUEST_CHANGES).
- Si APPROVE: merge ejecutado o autorizado por usuario.
- Plan marcado como completado.

---

## Criterios de aceptación global

1. Playwright instalado/configurado en `frontend/`.
2. `app-loads.spec.ts` y `upload-smoke.spec.ts` pasan de forma estable.
3. Job `CI / e2e` funcional y con artifacts en fallo.
4. `npx tsc --noEmit` limpio.
5. `npx eslint .` limpio.
6. PR abierta a `main` con sección `How to test`.

---

## How to test (cuando se ejecute implementación)

```bash
# 1) Levantar stack en puerto 80 para frontend
$env:FRONTEND_PORT='80'; docker compose up -d --build --wait

# 2) Ejecutar E2E
cd frontend
npm run test:e2e

# 3) Ejecutar checks
npx tsc --noEmit
npx eslint .
```

Resultado esperado:
- Todos los tests E2E pasan.
- TypeScript y ESLint sin errores.

---

## Notas de gobierno documental
- Este plan se rige por las políticas de handoff iterativo del plan maestro.
- Cualquier cambio operativo adicional debe registrarse aquí antes de ejecución.
