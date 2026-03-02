# Plan de cobertura E2E — Playwright

## Objetivo

Definir todas las funcionalidades verificables desde la perspectiva del usuario, agruparlas en escenarios de uso coherentes y crear tests Playwright repetibles que se ejecuten en cada PR.

---

## 1. Inventario de funcionalidades (perspectiva del usuario)

### A — Carga de la aplicación

| ID | Funcionalidad | data-testid / selector clave |
|----|---------------|------------------------------|
| A1 | La app carga y muestra el layout principal | `canvas-wrapper`, `main-canvas-layout` |
| A2 | Se muestra el sidebar de documentos | `documents-sidebar` |
| A3 | Se muestra la zona de upload (dropzone) | `upload-dropzone` / UploadDropzone visible |
| A4 | El visor muestra el estado vacío ("Selecciona un documento…") | `viewer-empty-state` |

### B — Sidebar de documentos

| ID | Funcionalidad | data-testid / selector clave |
|----|---------------|------------------------------|
| B1 | Se muestran los documentos existentes agrupados: "Para revisar" / "Revisados" | `left-panel-scroll`, headers de grupo |
| B2 | Seleccionar un documento lo marca como activo (`aria-pressed`) | `doc-row-{id}` |
| B3 | El documento activo muestra indicador visual (barra lateral accent) | `doc-row-{id}[aria-current]` |
| B4 | Fijar/desfijar sidebar | botón "Fijar"/"Fijada" en `sidebar-actions-cluster` |
| B5 | Refrescar lista de documentos | botón "Actualizar" en `sidebar-actions-cluster` |
| B6 | Se muestra el status chip de cada documento (procesando, completo, error) | `DocumentStatusChip` |
| B7 | Hover expande sidebar colapsado | `documents-sidebar[data-expanded]` |
| B8 | Estado vacío: "Aún no hay documentos cargados." | texto visible |
| B9 | Indicador "Tardando más de lo esperado" para procesamiento largo | texto visible |

### C — Upload de documentos

| ID | Funcionalidad | data-testid / selector clave |
|----|---------------|------------------------------|
| C1 | Click en dropzone abre selector de archivos | `#upload-document-input` |
| C2 | Subir PDF vía file input → aparece en sidebar | `doc-row-{new_id}` |
| C3 | Drag & drop en dropzone del sidebar | UploadDropzone + drag events |
| C4 | Drag & drop en el visor PDF | `viewer-dropzone` |
| C5 | Feedback de subida exitosa (toast "Documento subido correctamente") | toast visible |
| C6 | Feedback de error de subida (toast de error) | toast visible |
| C7 | Auto-apertura del documento tras upload (el PDF se carga en el visor) | PDF visible en visor |
| C8 | Indicador de "Subiendo…" durante upload | spinner + texto "Subiendo..." |
| C9 | Rechazo de archivo no-PDF (solo `.pdf`) | toast de error |
| C10 | Rechazo de archivo >20 MB | toast de error |

### D — Visor PDF

| ID | Funcionalidad | data-testid / selector clave |
|----|---------------|------------------------------|
| D1 | El documento se renderiza en el visor (canvas visible) | `pdf-page` (canvas elements) |
| D2 | Indicador de carga "Cargando PDF..." | texto visible |
| D3 | Zoom In (botón +) → zoom incrementa 10% | botón "Acercar", `pdf-zoom-indicator` |
| D4 | Zoom Out (botón −) → zoom decrementa 10% | botón "Alejar", `pdf-zoom-indicator` |
| D5 | Zoom con Ctrl + rueda de ratón | `pdf-scroll-container` wheel event |
| D6 | Ajustar al ancho (botón) → zoom vuelve a 100% | botón "Ajustar al ancho" |
| D7 | Indicador de zoom muestra porcentaje correcto | `pdf-zoom-indicator` |
| D8 | Zoom persiste en localStorage | `pdfViewerZoomLevel` en localStorage |
| D9 | Límites de zoom respetados (50%–200%) | botones disabled en extremos |
| D10 | Navegación a página anterior | botón "Página anterior" |
| D11 | Navegación a página siguiente | botón "Página siguiente" |
| D12 | Indicador de página actual (n/total) | texto en toolbar |
| D13 | Botones de navegación disabled en extremos (primera/última página) | `disabled` state |
| D14 | Scroll continuo entre páginas actualiza indicador de página | `pdf-scroll-container` scroll |

### E — Toolbar del visor (pestañas)

| ID | Funcionalidad | data-testid / selector clave |
|----|---------------|------------------------------|
| E1 | Tab "Documento" muestra el PDF | botón "Documento" `aria-current="page"` |
| E2 | Tab "Texto extraído" muestra el texto raw | botón "Texto extraído" |
| E3 | Tab "Detalles técnicos" muestra el historial | botón "Detalles técnicos" |
| E4 | Botón "Descargar" abre el PDF en nueva pestaña | botón "Descargar" |

### F — Vista de texto extraído (Raw Text)

| ID | Funcionalidad | data-testid / selector clave |
|----|---------------|------------------------------|
| F1 | Se muestra el texto extraído del documento | contenido de texto visible |
| F2 | Buscar en texto extraído → "Coincidencia encontrada" | input de búsqueda + feedback |
| F3 | Buscar sin resultado → "No se encontraron coincidencias" | feedback visible |
| F4 | Copiar texto al portapapeles | botón Copiar |
| F5 | Descargar texto extraído | botón Descargar |
| F6 | Estado de carga del texto | spinner / loading |
| F7 | Error cuando el texto no está disponible | mensaje de error |

### G — Detalles técnicos (historial de procesamiento)

| ID | Funcionalidad | data-testid / selector clave |
|----|---------------|------------------------------|
| G1 | Se muestra el historial de runs del documento | lista de runs |
| G2 | Expandir/colapsar detalles de un step | botón expandir |
| G3 | Reprocesar documento (botón Reintentar) | modal de confirmación |
| G4 | Confirmar reprocesamiento | botón en modal |
| G5 | Indicador de procesamiento activo | status processing |

### H — Panel de datos extraídos (Structured Data)

| ID | Funcionalidad | data-testid / selector clave |
|----|---------------|------------------------------|
| H1 | Se muestra el panel "Datos extraídos" con campos organizados por secciones | `structured-column-stack` |
| H2 | Campos organizados en secciones del historial médico | secciones con headers |
| H3 | Cada campo muestra su valor formateado | field value visible |
| H4 | Campos faltantes muestran placeholder "—" | `MISSING_VALUE_PLACEHOLDER` |
| H5 | Indicador de confianza por campo (dot alto/medio/bajo) | `confidence-indicator-{id}` |
| H6 | Badge "Crítico" en campos críticos | CriticalBadge |
| H7 | Resumen de campos detectados (n/total + distribución de confianza) | toolbar summary |
| H8 | Sección "Otros datos extraídos" para campos no canónicos | sección separada |
| H9 | Estado de carga (skeleton) mientras se procesan datos | `review-core-skeleton` |
| H10 | Estado vacío "No hay un run completado" | mensaje visible |
| H11 | Error de interpretación con botón "Reintentar" | botón Reintentar |
| H12 | Aviso de política de confianza degradada | `confidence-policy-degraded` |

### I — Búsqueda y filtros en datos extraídos

| ID | Funcionalidad | data-testid / selector clave |
|----|---------------|------------------------------|
| I1 | Buscar campos por texto (clave, label o valor) | `structured-search-shell` input |
| I2 | Limpiar búsqueda (botón X) | botón "Limpiar búsqueda" |
| I3 | Filtrar por confianza baja | toggle "Baja" |
| I4 | Filtrar por confianza media | toggle "Media" |
| I5 | Filtrar por confianza alta | toggle "Alta" |
| I6 | Filtrar: solo críticos | toggle "Solo críticos" |
| I7 | Filtrar: solo con valor | toggle "Solo con valor" |
| I8 | Filtrar: solo vacíos | toggle "Solo vacíos" |
| I9 | Resetear todos los filtros | botón "Resetear filtros" |
| I10 | Estado vacío cuando filtros no tienen resultados | mensaje "Sin resultados" |

### J — Edición de campos

| ID | Funcionalidad | data-testid / selector clave |
|----|---------------|------------------------------|
| J1 | Click en campo abre diálogo de edición | `FieldEditDialog` open |
| J2 | Editar valor de texto libre | input en dialog |
| J3 | Editar campo Sexo (dropdown con vocabulario controlado) | select con opciones canónicas |
| J4 | Editar campo Especie (dropdown con vocabulario controlado) | select con opciones canónicas |
| J5 | Validación de microchip (formato) | error visible si inválido |
| J6 | Validación de peso (formato) | error visible si inválido |
| J7 | Validación de edad (formato) | error visible si inválido |
| J8 | Validación de fecha (formato) | error visible si inválido |
| J9 | Guardar edición → valor actualizado en panel | botón "Guardar" |
| J10 | Cancelar edición | botón "Cancelar" |
| J11 | Sugerencias de candidatos en edición | sección de candidatos visible |
| J12 | Bloqueo de edición en documento "revisado" (feedback) | toast de aviso |
| J13 | Agregar campo nuevo (AddFieldDialog) | diálogo con clave + valor |
| J14 | Guardar campo nuevo | botón "Guardar" en AddFieldDialog |
| J15 | La confianza se actualiza tras edición manual | cambio de indicador |

### K — Workflow de revisión

| ID | Funcionalidad | data-testid / selector clave |
|----|---------------|------------------------------|
| K1 | Botón "Marcar revisado" marca documento como revisado | botón principal |
| K2 | Botón "Reabrir" reabre documento para revisión | botón outline |
| K3 | Indicador de "Marcando…" / "Reabriendo…" durante mutación | spinner en botón |
| K4 | Documento revisado se mueve al grupo "Revisados" en sidebar | grupo "Revisados" |
| K5 | Documento reabierto vuelve a "Para revisar" | grupo "Para revisar" |

### L — Panel de evidencia (Source Panel)

| ID | Funcionalidad | data-testid / selector clave |
|----|---------------|------------------------------|
| L1 | Seleccionar un campo navega al PDF en la página de evidencia | scroll del visor |
| L2 | Se muestra el panel de fuente con página y snippet | `source-pinned-panel` / `source-drawer` |
| L3 | Fijar/desfijar panel de fuente | botón "Fijar"/"Desfijar" |
| L4 | Cerrar panel de fuente | botón X |
| L5 | Se muestra la evidencia textual del campo | contenido en Source Panel |
| L6 | Highlight visual en la página correcta del PDF | fondo accent en `pdf-page` |

### M — Layout y split panel

| ID | Funcionalidad | data-testid / selector clave |
|----|---------------|------------------------------|
| M1 | Panel dividido entre visor PDF y datos extraídos | `review-split-grid` |
| M2 | Drag handle para redimensionar paneles | `review-split-handle` |
| M3 | Doble-click en handle resetea ratio | `review-split-handle` dblclick |
| M4 | Keyboard resize del split panel | arrow key events |

### N — Toasts y notificaciones

| ID | Funcionalidad | data-testid / selector clave |
|----|---------------|------------------------------|
| N1 | Toast de éxito se auto-cierra tras ~3.5s | auto-dismiss |
| N2 | Toast de error se auto-cierra tras ~5s | auto-dismiss |
| N3 | Toast de conectividad cuando hay error de red | toast connectivity |
| N4 | Cerrar toast manualmente | botón cerrar en toast |
| N5 | Acción "Abrir documento" en toast de upload exitoso | botón acción |

### O — Visitas (contrato canónico)

| ID | Funcionalidad | data-testid / selector clave |
|----|---------------|------------------------------|
| O1 | Episodios de visita agrupados y numerados | `visit-episode-{n}` |
| O2 | Metadata de visita (fecha, ingreso, alta, motivo) | campos dentro de visita |
| O3 | Campos con scope de visita asignados correctamente | fields con `visit_group_id` |
| O4 | Grupo "sin asignar" visible cuando hay campos no agrupados | `visit-unassigned-group` |

---

## 2. Especificación detallada de tests (Given / When / Then)

> Convención: cada test se describe con pasos concretos y resultado esperado.
> Los IDs entre paréntesis (e.g. `[A1]`) referencian el inventario de funcionalidades de la §1.
> **Precondición global:** la app está corriendo en `localhost:80` con Docker Compose.

---

### P0 — Smoke (en cada PR, <30 s cada test)

#### `app-loads.spec.ts`

**Test 1 — "La app carga y muestra el layout principal"** `[A1, A2, A3, A4]`

| Paso | Acción | Resultado esperado |
|------|--------|--------------------|
| Given | — | — |
| When | Navegar a `/` | — |
| Then | El contenedor principal es visible | `[data-testid="canvas-wrapper"]` visible |
| Then | El sidebar de documentos es visible | `[data-testid="documents-sidebar"]` visible |
| Then | La zona de upload (dropzone) es visible | UploadDropzone visible (primer `[data-testid="upload-dropzone"]`) |
| Then | El visor muestra estado vacío | `[data-testid="viewer-empty-state"]` visible, o texto "Selecciona un documento" |

---

#### `upload-smoke.spec.ts`

**Test 2 — "Subir un PDF hace que aparezca en el sidebar"** `[C2, C5, C7, B2]`

| Paso | Acción | Resultado esperado |
|------|--------|--------------------|
| Given | Navegar a `/` y esperar sidebar visible | — |
| When | Hover sobre el sidebar para expandirlo | Sidebar expanded |
| When | Subir `sample.pdf` vía `#upload-document-input` | — |
| Then | El sidebar contiene el texto "sample.pdf" (timeout 60 s) | `[data-testid="documents-sidebar"]` contiene texto del filename |
| Then | Existe un row de documento con el `document_id` devuelto | `[data-testid="doc-row-{id}"]` visible |

---

### P1 — Core workflows (en cada PR, <60 s cada test)

#### `pdf-viewer.spec.ts`

> **Precondición compartida:** subir un PDF de 2+ páginas y esperar a que el visor lo renderice.

**Test 3 — "El PDF se renderiza en el visor"** `[D1]`

| Paso | Acción | Resultado esperado |
|------|--------|--------------------|
| Given | Documento subido y seleccionado | — |
| When | Esperar a que el visor cargue | — |
| Then | Al menos un canvas de página es visible | `[data-testid="pdf-page"]` count ≥ 1 |
| Then | El toolbar del PDF es visible | `[data-testid="pdf-toolbar-shell"]` visible |

**Test 4 — "Zoom In incrementa el zoom 10%"** `[D3, D7]`

| Paso | Acción | Resultado esperado |
|------|--------|--------------------|
| Given | PDF cargado, zoom en 100% | `[data-testid="pdf-zoom-indicator"]` muestra "100%" |
| When | Click en botón "Acercar" | — |
| Then | El indicador muestra "110%" | `[data-testid="pdf-zoom-indicator"]` texto = "110%" |

**Test 5 — "Zoom Out decrementa el zoom 10%"** `[D4, D7]`

| Paso | Acción | Resultado esperado |
|------|--------|--------------------|
| Given | PDF cargado, zoom en 100% | — |
| When | Click en botón "Alejar" | — |
| Then | El indicador muestra "90%" | `[data-testid="pdf-zoom-indicator"]` texto = "90%" |

**Test 6 — "Ajustar al ancho resetea el zoom a 100%"** `[D6, D7]`

| Paso | Acción | Resultado esperado |
|------|--------|--------------------|
| Given | PDF cargado, hacer zoom in 2 veces (→120%) | — |
| When | Click en botón "Ajustar al ancho" | — |
| Then | El indicador muestra "100%" | `[data-testid="pdf-zoom-indicator"]` texto = "100%" |

**Test 7 — "Botones de zoom se deshabilitan en los límites"** `[D9]`

| Paso | Acción | Resultado esperado |
|------|--------|--------------------|
| Given | PDF cargado | — |
| When | Hacer click en "Alejar" repetidamente hasta 50% | — |
| Then | El botón "Alejar" está disabled | `[data-testid="pdf-zoom-out"]` disabled |
| When | Hacer click en "Acercar" repetidamente hasta 200% | — |
| Then | El botón "Acercar" está disabled | `[data-testid="pdf-zoom-in"]` disabled |

**Test 8 — "Navegación entre páginas"** `[D10, D11, D12, D13]`

| Paso | Acción | Resultado esperado |
|------|--------|--------------------|
| Given | PDF de 2+ páginas cargado, estamos en página 1 | Indicador muestra "1/N" |
| Then | Botón "Página anterior" está disabled | disabled state |
| When | Click en botón "Página siguiente" | — |
| Then | Indicador muestra "2/N" | `[data-testid="pdf-page-indicator"]` texto = "2/N" |
| Then | Botón "Página anterior" ahora está enabled | — |
| When | En última página, verificar botón "Página siguiente" | disabled state |

---

#### `document-sidebar.spec.ts`

> **Precondición:** al menos 1 documento ya existente en el sistema.

**Test 9 — "La lista de documentos muestra grupos 'Para revisar' y 'Revisados'"** `[B1]`

| Paso | Acción | Resultado esperado |
|------|--------|--------------------|
| Given | Navegar a `/`, sidebar expandido | — |
| When | Observar el sidebar | — |
| Then | Se muestra al menos un grupo de documentos | Header "Para revisar" o "Revisados" visible |
| Then | Cada documento muestra nombre y timestamp | Texto del filename visible en el row |

**Test 10 — "Seleccionar un documento lo marca como activo"** `[B2, B3]`

| Paso | Acción | Resultado esperado |
|------|--------|--------------------|
| Given | Sidebar con al menos 1 documento | — |
| When | Click en un `doc-row-{id}` | — |
| Then | El row tiene `aria-pressed="true"` | Atributo verificable |
| Then | El row tiene `aria-current="true"` | Atributo verificable |
| Then | El visor carga el PDF (canvas visible) | `[data-testid="pdf-page"]` visible |

**Test 11 — "Cada documento muestra su chip de status"** `[B6]`

| Paso | Acción | Resultado esperado |
|------|--------|--------------------|
| Given | Sidebar expandido con documentos | — |
| When | Observar los rows | — |
| Then | Cada row contiene un status chip | Element con clase `DocumentStatusChip` presente dentro de cada row |

---

#### `extracted-data.spec.ts`

> **Precondición:** subir `sample.pdf`, esperar a que el procesamiento termine (status != PROCESSING).

**Test 12 — "El panel de datos extraídos se muestra con secciones"** `[H1, H2]`

| Paso | Acción | Resultado esperado |
|------|--------|--------------------|
| Given | Documento procesado y seleccionado | — |
| When | Esperar a que el panel de datos esté ready | `[data-testid="structured-column-stack"]` visible |
| Then | El panel muestra el título "Datos extraídos" | Texto visible |
| Then | Hay al menos una sección con header | Sección con título (e.g., "Datos del paciente") visible |

**Test 13 — "Los campos muestran sus valores formateados"** `[H3, H4]`

| Paso | Acción | Resultado esperado |
|------|--------|--------------------|
| Given | Panel de datos extraídos ready | — |
| When | Buscar campos en el panel | — |
| Then | Al menos un campo muestra un valor no vacío | Texto del valor visible (≠ "—") |
| Then | Los campos sin valor muestran "—" | Placeholder "—" visible |

**Test 14 — "Los campos muestran indicadores de confianza"** `[H5, H6, H7]`

| Paso | Acción | Resultado esperado |
|------|--------|--------------------|
| Given | Panel de datos extraídos ready con campos | — |
| When | Observar los campos | — |
| Then | Al menos un campo tiene indicador de confianza visible | `[data-testid^="confidence-indicator-"]` visible |
| Then | El resumen de campos detectados es visible | Texto con conteo (e.g., "12/20") visible en toolbar |

---

#### `field-editing.spec.ts`

> **Precondición:** documento procesado con al menos un campo editable (e.g., `pet_name`).

**Test 15 — "Click en campo abre diálogo de edición"** `[J1]`

| Paso | Acción | Resultado esperado |
|------|--------|--------------------|
| Given | Panel de datos ready, campo `pet_name` visible | — |
| When | Click en el trigger del campo (`[data-testid^="field-trigger-"]`) | — |
| Then | Se abre el diálogo de edición | Dialog visible con título del campo |
| Then | El input contiene el valor actual del campo | Input pre-populado |

**Test 16 — "Editar valor y guardar actualiza el panel"** `[J2, J9, J15]`

| Paso | Acción | Resultado esperado |
|------|--------|--------------------|
| Given | Diálogo de edición abierto para un campo | — |
| When | Borrar el valor actual e introducir "NuevoValorTest" | — |
| When | Click en "Guardar" | — |
| Then | El diálogo se cierra | Dialog no visible |
| Then | El campo muestra "NuevoValorTest" en el panel | Texto actualizado visible |
| Then | Aparece toast de éxito | Toast visible (auto-desaparece) |

**Test 17 — "Cancelar edición no modifica el campo"** `[J10]`

| Paso | Acción | Resultado esperado |
|------|--------|--------------------|
| Given | Diálogo abierto, valor original = "ValorOriginal" | — |
| When | Cambiar texto a "OtroValor" | — |
| When | Click en "Cancelar" | — |
| Then | Diálogo se cierra | Dialog no visible |
| Then | El campo sigue mostrando "ValorOriginal" | Texto original sin cambios |

---

#### `review-workflow.spec.ts`

> **Precondición:** documento procesado y datos extraídos visibles.

**Test 18 — "Marcar documento como revisado"** `[K1, K3, K4]`

| Paso | Acción | Resultado esperado |
|------|--------|--------------------|
| Given | Documento en estado "Para revisar" | Botón "Marcar revisado" visible |
| When | Click en "Marcar revisado" | — |
| Then | Aparece indicador "Marcando…" brevemente | Spinner visible |
| Then | El botón cambia a "Reabrir" | Texto "Reabrir" visible |
| Then | El documento aparece en grupo "Revisados" del sidebar | Row del doc dentro del grupo "Revisados" |
| Then | Toast de éxito: "Documento marcado como revisado." | Toast visible |

**Test 19 — "Reabrir documento revisado"** `[K2, K5]`

| Paso | Acción | Resultado esperado |
|------|--------|--------------------|
| Given | Documento en estado "Revisado" | Botón "Reabrir" visible |
| When | Click en "Reabrir" | — |
| Then | Aparece indicador "Reabriendo…" brevemente | Spinner visible |
| Then | El botón cambia a "Marcar revisado" | Texto "Marcar revisado" visible |
| Then | El documento vuelve al grupo "Para revisar" del sidebar | Row del doc dentro del grupo "Para revisar" |
| Then | Toast de éxito: "Documento reabierto para revisión." | Toast visible |

---

### P2 — Features secundarias (nightly / pre-release, <90 s cada test)

#### `upload-validation.spec.ts`

**Test 20 — "Rechazo de archivo no-PDF"** `[C9]`

| Paso | Acción | Resultado esperado |
|------|--------|--------------------|
| Given | Navegar a `/`, sidebar expandido | — |
| When | Intentar subir `non-pdf.txt` vía file input | — |
| Then | Aparece toast de error: "Solo se admiten archivos PDF." | Toast error visible |
| Then | El archivo NO aparece en el sidebar | Sidebar sin nuevo row |

**Test 21 — "Drag & drop en el visor"** `[C4]`

| Paso | Acción | Resultado esperado |
|------|--------|--------------------|
| Given | Navegar a `/` | — |
| When | Drag & drop `sample.pdf` sobre el visor | — |
| Then | Overlay de drop visible: "Suelta el PDF para subirlo" | Texto visible |
| When | Soltar el archivo | — |
| Then | El documento se sube y aparece en sidebar | Row de documento visible |

---

#### `viewer-tabs.spec.ts`

> **Precondición:** documento procesado y cargado en visor.

**Test 22 — "Tab 'Documento' muestra el PDF"** `[E1]`

| Paso | Acción | Resultado esperado |
|------|--------|--------------------|
| Given | PDF cargado, tab "Documento" activo por defecto | — |
| Then | Canvas de página visible | `[data-testid="pdf-page"]` visible |
| Then | Botón "Documento" tiene `aria-current="page"` | Atributo verificable |

**Test 23 — "Tab 'Texto extraído' muestra raw text"** `[E2]`

| Paso | Acción | Resultado esperado |
|------|--------|--------------------|
| Given | PDF cargado | — |
| When | Click en tab "Texto extraído" | — |
| Then | El contenido del PDF desaparece (canvas oculto) | Canvas no visible |
| Then | Se muestra contenido de texto | Texto del documento visible |

**Test 24 — "Tab 'Detalles técnicos' muestra historial"** `[E3]`

| Paso | Acción | Resultado esperado |
|------|--------|--------------------|
| Given | PDF cargado | — |
| When | Click en tab "Detalles técnicos" | — |
| Then | Se muestra información del historial de procesamiento | Contenido técnico visible |

**Test 25 — "Botón 'Descargar' abre el PDF"** `[E4]`

| Paso | Acción | Resultado esperado |
|------|--------|--------------------|
| Given | PDF cargado | — |
| When | Click en botón "Descargar" | — |
| Then | Se abre una nueva pestaña con la URL de descarga | `window.open` llamado con URL correcta |

---

#### `raw-text.spec.ts`

> **Precondición:** documento procesado, tab "Texto extraído" activo.

**Test 26 — "Se muestra el texto extraído"** `[F1]`

| Paso | Acción | Resultado esperado |
|------|--------|--------------------|
| Given | Tab "Texto extraído" activo | — |
| When | Esperar carga | — |
| Then | Texto del documento es visible | Contenido de texto con length > 0 |

**Test 27 — "Buscar texto existente muestra coincidencia"** `[F2]`

| Paso | Acción | Resultado esperado |
|------|--------|--------------------|
| Given | Texto extraído visible | — |
| When | Escribir una palabra que existe en el texto en el campo de búsqueda | — |
| When | Ejecutar búsqueda | — |
| Then | Aparece mensaje "Coincidencia encontrada." | Texto visible |

**Test 28 — "Buscar texto inexistente muestra 'no encontrado'"** `[F3]`

| Paso | Acción | Resultado esperado |
|------|--------|--------------------|
| Given | Texto extraído visible | — |
| When | Escribir "xyznonexistent999" en campo de búsqueda | — |
| When | Ejecutar búsqueda | — |
| Then | Aparece mensaje "No se encontraron coincidencias." | Texto visible |

**Test 29 — "Copiar texto al portapapeles"** `[F4]`

| Paso | Acción | Resultado esperado |
|------|--------|--------------------|
| Given | Texto extraído visible | — |
| When | Click en botón "Copiar" | — |
| Then | Texto copiado al portapapeles | Verificar via `page.evaluate(() => navigator.clipboard.readText())` |

**Test 30 — "Descargar texto extraído"** `[F5]`

| Paso | Acción | Resultado esperado |
|------|--------|--------------------|
| Given | Texto extraído visible | — |
| When | Click en botón "Descargar" | — |
| Then | Se descarga un archivo de texto | Download event interceptado |

---

#### `structured-filters.spec.ts`

> **Precondición:** documento procesado con campos extraídos visibles.

**Test 31 — "Buscar campo por texto filtra resultados"** `[I1]`

| Paso | Acción | Resultado esperado |
|------|--------|--------------------|
| Given | Panel de datos ready con múltiples campos | — |
| When | Escribir "nombre" en el input de búsqueda | — |
| Then | Solo se muestran campos cuya clave/label/valor contiene "nombre" | Campos visibles filtrados |

**Test 32 — "Limpiar búsqueda restaura todos los campos"** `[I2]`

| Paso | Acción | Resultado esperado |
|------|--------|--------------------|
| Given | Búsqueda activa filtrando resultados | — |
| When | Click en botón X de limpiar búsqueda | — |
| Then | Todos los campos vuelven a ser visibles | Conteo de campos restaurado |

**Test 33 — "Filtrar por confianza baja"** `[I3]`

| Paso | Acción | Resultado esperado |
|------|--------|--------------------|
| Given | Panel con campos de distintas confianzas | — |
| When | Click en toggle "Baja" del filtro de confianza | — |
| Then | Solo se muestran campos con confianza baja | Campos filtrados |

**Test 34 — "Filtrar: solo campos críticos"** `[I6]`

| Paso | Acción | Resultado esperado |
|------|--------|--------------------|
| Given | Panel con campos críticos y no críticos | — |
| When | Activar toggle "Solo críticos" | — |
| Then | Solo se muestran campos marcados como críticos | Campos con CriticalBadge visibles |

**Test 35 — "Filtrar: solo con valor / solo vacíos"** `[I7, I8]`

| Paso | Acción | Resultado esperado |
|------|--------|--------------------|
| Given | Panel con campos con valor y sin valor | — |
| When | Activar toggle "Solo con valor" | Solo campos con valor ≠ "—" visibles |
| When | Desactivar y activar "Solo vacíos" | Solo campos con valor = "—" visibles |

**Test 36 — "Resetear filtros restaura vista completa"** `[I9, I10]`

| Paso | Acción | Resultado esperado |
|------|--------|--------------------|
| Given | Filtros activos, pocos campos visibles | — |
| When | Click en "Resetear filtros" | — |
| Then | Todos los campos y secciones vuelven a ser visibles | Vista completa restaurada |

---

#### `field-validation.spec.ts`

> **Precondición:** documento procesado con campos de cada tipo disponibles.

**Test 37 — "Validación de microchip rechaza formato inválido"** `[J5]`

| Paso | Acción | Resultado esperado |
|------|--------|--------------------|
| Given | Diálogo de edición abierto para campo `microchip_id` | — |
| When | Escribir "abc" (formato inválido) | — |
| Then | Se muestra mensaje de error de validación | Error visible bajo el input |
| Then | Botón "Guardar" está disabled | disabled state |

**Test 38 — "Editar campo Sexo con dropdown"** `[J3]`

| Paso | Acción | Resultado esperado |
|------|--------|--------------------|
| Given | Diálogo abierto para campo `sex` | — |
| Then | Se muestra un `<select>` con opciones canónicas (Macho, Hembra, etc.) | Select visible con opciones |
| When | Seleccionar "Hembra" | — |
| When | Click "Guardar" | — |
| Then | Campo muestra "Hembra" en el panel | Valor actualizado |

**Test 39 — "Editar campo Especie con dropdown"** `[J4]`

| Paso | Acción | Resultado esperado |
|------|--------|--------------------|
| Given | Diálogo abierto para campo `species` | — |
| Then | Se muestra un `<select>` con opciones canónicas | Select visible |
| When | Seleccionar una especie y guardar | — |
| Then | Campo actualizado en el panel | Valor visible |

**Test 40 — "Validación de peso rechaza texto no numérico"** `[J6]`

| Paso | Acción | Resultado esperado |
|------|--------|--------------------|
| Given | Diálogo abierto para campo `weight` | — |
| When | Escribir "no-es-un-peso" | — |
| Then | Error de validación visible | Error visible |

**Test 41 — "Validación de fecha rechaza formato inválido"** `[J8]`

| Paso | Acción | Resultado esperado |
|------|--------|--------------------|
| Given | Diálogo abierto para campo de fecha (`visit_date` o `document_date`) | — |
| When | Escribir "esto-no-es-fecha" | — |
| Then | Error de validación visible | Error visible |

---

#### `source-panel.spec.ts`

> **Precondición:** documento procesado con campos que tienen evidencia (`evidence.page`).

**Test 42 — "Seleccionar campo navega al PDF en la página de evidencia"** `[L1, L6]`

| Paso | Acción | Resultado esperado |
|------|--------|--------------------|
| Given | Panel de datos ready con campo que tiene evidencia en página 2 | — |
| When | Click en el campo | — |
| Then | El visor hace scroll a la página 2 | Página 2 visible en el viewport |
| Then | La página tiene highlight visual (fondo accent) | Clase CSS de highlight aplicada |

**Test 43 — "Se muestra el panel de fuente con snippet"** `[L2, L5]`

| Paso | Acción | Resultado esperado |
|------|--------|--------------------|
| Given | Campo con evidencia seleccionado | — |
| Then | Panel de fuente visible | `[data-testid="source-drawer"]` o `[data-testid="source-pinned-panel"]` visible |
| Then | Se muestra "Página N" | Texto con número de página |
| Then | Se muestra el snippet de evidencia | Texto en sección "Evidencia" |

**Test 44 — "Fijar y cerrar panel de fuente"** `[L3, L4]`

| Paso | Acción | Resultado esperado |
|------|--------|--------------------|
| Given | Panel de fuente abierto | — |
| When | Click en "Fijar" | — |
| Then | Panel permanece visible como panel fijado | `[data-testid="source-pinned-panel"]` visible |
| When | Click en botón X de cerrar | — |
| Then | Panel se cierra | Panel no visible |

---

#### `sidebar-interactions.spec.ts`

**Test 45 — "Fijar/desfijar sidebar"** `[B4]`

| Paso | Acción | Resultado esperado |
|------|--------|--------------------|
| Given | Sidebar expandido | — |
| When | Click en botón "Fijar" | — |
| Then | Sidebar queda fijado (permanece expandido sin hover) | `[data-testid="documents-sidebar"]` expanded persistente |
| When | Click en botón "Fijada" (desfijar) | — |
| Then | Sidebar vuelve a modo hover | Se colapsa al salir el ratón |

**Test 46 — "Refrescar lista de documentos"** `[B5]`

| Paso | Acción | Resultado esperado |
|------|--------|--------------------|
| Given | Sidebar con documentos | — |
| When | Click en botón "Actualizar" | — |
| Then | Se muestra animación de actualización (spinner) | Icono con clase `animate-spin` |
| Then | La lista se actualiza | Lista de documentos re-renderizada |

**Test 47 — "Hover expande sidebar colapsado"** `[B7]`

| Paso | Acción | Resultado esperado |
|------|--------|--------------------|
| Given | Sidebar en modo hover (no fijado), colapsado | `[data-expanded="false"]` |
| When | Mover ratón sobre el sidebar | — |
| Then | El sidebar se expande | `[data-expanded="true"]` |
| When | Mover ratón fuera del sidebar | — |
| Then | El sidebar se colapsa | `[data-expanded="false"]` |

---

#### `split-panel.spec.ts`

**Test 48 — "El layout muestra split grid entre visor y datos"** `[M1]`

| Paso | Acción | Resultado esperado |
|------|--------|--------------------|
| Given | Documento seleccionado | — |
| Then | El split grid es visible | `[data-testid="review-split-grid"]` visible |
| Then | El handle de redimensión es visible | `[data-testid="review-split-handle"]` visible |

**Test 49 — "Doble-click en handle resetea el ratio"** `[M3]`

| Paso | Acción | Resultado esperado |
|------|--------|--------------------|
| Given | Split grid con ratio modificado | — |
| When | Doble-click en `[data-testid="review-split-handle"]` | — |
| Then | El ratio vuelve al valor por defecto | Proporción visual restaurada |

---

#### `zoom-advanced.spec.ts`

> **Precondición:** documento con PDF cargado.

**Test 50 — "Ctrl + rueda de ratón hace zoom"** `[D5]`

| Paso | Acción | Resultado esperado |
|------|--------|--------------------|
| Given | PDF en zoom 100% | — |
| When | Ctrl + scroll up sobre el contenedor del PDF | — |
| Then | Zoom incrementa | Indicador muestra >100% |
| When | Ctrl + scroll down | — |
| Then | Zoom decrementa | Indicador muestra <100% (o vuelve a 100%) |

**Test 51 — "El zoom persiste en localStorage"** `[D8]`

| Paso | Acción | Resultado esperado |
|------|--------|--------------------|
| Given | PDF cargado | — |
| When | Hacer zoom a 130% | — |
| Then | `localStorage.getItem("pdfViewerZoomLevel")` = "1.3" | Valor verificable vía `page.evaluate` |
| When | Recargar la página y volver a cargar el PDF | — |
| Then | El zoom empieza en 130% | Indicador muestra "130%" |

---

#### `reprocess.spec.ts`

> **Precondición:** documento procesado (status COMPLETED o FAILED).

**Test 52 — "Reprocesar documento muestra modal de confirmación"** `[G3]`

| Paso | Acción | Resultado esperado |
|------|--------|--------------------|
| Given | Documento seleccionado, tab "Detalles técnicos" activo | — |
| When | Click en botón "Reintentar" | — |
| Then | Modal de confirmación visible | `[data-testid="reprocess-confirm-modal"]` visible |

**Test 53 — "Confirmar reprocesamiento inicia nuevo procesamiento"** `[G4, G5]`

| Paso | Acción | Resultado esperado |
|------|--------|--------------------|
| Given | Modal de confirmación visible | — |
| When | Click en botón de confirmar | — |
| Then | Modal se cierra | Modal no visible |
| Then | Toast: "Reprocesamiento iniciado." | Toast visible |
| Then | El status del documento cambia a PROCESSING | Status chip actualizado |

---

#### `visit-grouping.spec.ts`

> **Precondición:** documento procesado con contrato canónico `visit-grouped-canonical` y 2+ visitas.

**Test 54 — "Los episodios de visita se muestran agrupados"** `[O1]`

| Paso | Acción | Resultado esperado |
|------|--------|--------------------|
| Given | Panel de datos ready con visitas | — |
| Then | Al menos un episodio de visita visible | `[data-testid^="visit-episode-"]` visible |
| Then | Los episodios están numerados | Texto "Visita 1", "Visita 2", etc. |

**Test 55 — "Cada visita muestra su metadata"** `[O2]`

| Paso | Acción | Resultado esperado |
|------|--------|--------------------|
| Given | Episodio de visita visible | — |
| Then | Se muestra fecha de visita | Campo `visit_date` con valor visible |
| Then | Se muestra motivo de consulta (si existe) | Campo `reason_for_visit` visible |

**Test 56 — "Grupo 'sin asignar' visible para campos huérfanos"** `[O4]`

| Paso | Acción | Resultado esperado |
|------|--------|--------------------|
| Given | Documento con campos sin agrupar en visita | — |
| Then | Se muestra grupo "sin asignar" | `[data-testid="visit-unassigned-group"]` visible |

---

#### `toasts.spec.ts`

**Test 57 — "Toast de éxito se auto-cierra"** `[N1]`

| Paso | Acción | Resultado esperado |
|------|--------|--------------------|
| Given | Acción que genera toast de éxito (e.g., marcar revisado) | — |
| Then | Toast visible | — |
| Then | A los ~3.5s el toast desaparece | Toast no visible (timeout 5s) |

**Test 58 — "Toast de error se auto-cierra más lento"** `[N2]`

| Paso | Acción | Resultado esperado |
|------|--------|--------------------|
| Given | Acción que genera error (forzar error de red) | — |
| Then | Toast de error visible | — |
| Then | A los ~5s el toast desaparece | Toast no visible (timeout 7s) |

**Test 59 — "Cerrar toast manualmente"** `[N4]`

| Paso | Acción | Resultado esperado |
|------|--------|--------------------|
| Given | Toast visible | — |
| When | Click en botón X del toast | — |
| Then | Toast desaparece inmediatamente | Toast no visible |

---

#### `add-field.spec.ts`

> **Precondición:** documento procesado, no revisado.

**Test 60 — "Añadir campo nuevo con clave y valor"** `[J13, J14]`

| Paso | Acción | Resultado esperado |
|------|--------|--------------------|
| Given | Panel de datos ready | — |
| When | Abrir diálogo "Añadir campo" | — |
| Then | Diálogo visible con inputs para clave y valor | Título "Añadir campo" visible |
| When | Introducir clave "campo_prueba" y valor "valor_prueba" | — |
| When | Click "Guardar" | — |
| Then | Diálogo se cierra | Dialog no visible |
| Then | El campo "campo_prueba" aparece en la sección "Otros datos extraídos" | Campo visible con valor |

**Test 61 — "Bloqueo de edición en documento revisado"** `[J12]`

| Paso | Acción | Resultado esperado |
|------|--------|--------------------|
| Given | Documento marcado como revisado | — |
| When | Intentar click en trigger de campo para editar | — |
| Then | Se muestra aviso de que el documento está revisado | Toast o feedback visible |
| Then | NO se abre el diálogo de edición | Dialog no visible |

---

## 3. Estrategia de ejecución

### En cada PR (CI `e2e` job)
```
P0 (smoke) + P1 (core workflows)
```
- Tiempo máximo target: ~3 minutos
- Workers: 1 (para evitar race conditions con backend compartido)
- Retry: 1 intento en CI

### Nightly / pre-release
```
P0 + P1 + P2 (todos)
```
- Tiempo máximo target: ~10 minutos
- Workers: 1
- Retry: 2 intentos

### Configuración técnica

```typescript
// playwright.config.ts — estructura propuesta
const config = {
  projects: [
    {
      name: "smoke",
      testMatch: /app-loads|upload-smoke/,
      timeout: 30_000,
    },
    {
      name: "core",
      testMatch: /pdf-viewer|extracted-data|field-editing|review-workflow|document-sidebar/,
      timeout: 60_000,
    },
    {
      name: "extended",
      testMatch: /.*/,
      timeout: 90_000,
    },
  ],
};
```

### Scripts npm propuestos

```json
{
  "test:e2e": "playwright test --project=smoke --project=core",
  "test:e2e:smoke": "playwright test --project=smoke",
  "test:e2e:all": "playwright test --project=extended",
  "test:e2e:ui": "playwright test --ui"
}
```

---

## 4. Fixtures y helpers necesarios

| Fixture/Helper | Propósito |
|----------------|-----------|
| `sample.pdf` | PDF de 2+ páginas para tests de navegación |
| `sample-multifield.pdf` | PDF de veterinaria real para tests de extracción |
| `oversized.pdf` | PDF >20 MB para test de rechazo (generado en setup) |
| `non-pdf.txt` | Archivo no-PDF para test de tipo MIME |
| `uploadAndWaitForProcessing(page, pdfPath)` | Helper: sube PDF, espera procesamiento, devuelve `document_id` |
| `selectDocument(page, documentId)` | Helper: selecciona un documento existente en sidebar |
| `waitForExtractedData(page)` | Helper: espera a que el panel de datos extraídos esté ready |
| `editField(page, fieldKey, newValue)` | Helper: abre diálogo, cambia valor, guarda |

---

## 5. `data-testid` adicionales necesarios

Algunos tests requieren selectores estables que hoy no existen. Listado de `data-testid` a añadir:

| Componente | data-testid propuesto | Necesitado por |
|------------|----------------------|----------------|
| UploadDropzone (sidebar expanded) | `upload-dropzone` | C1, C3 |
| Toast container | `toast-host` | N1–N5 |
| Toast individua | `toast-{kind}` | N1–N5 |
| Botón "Marcar revisado" / "Reabrir" | `review-toggle-button` | K1, K2 |
| Botón "Acercar" (zoom in) | `pdf-zoom-in` | D3 |
| Botón "Alejar" (zoom out) | `pdf-zoom-out` | D4 |
| Botón "Ajustar al ancho" | `pdf-zoom-fit` | D6 |
| Botón "Página anterior" | `pdf-page-prev` | D10 |
| Botón "Página siguiente" | `pdf-page-next` | D11 |
| Indicador nº página | `pdf-page-indicator` | D12 |
| Tab "Documento" | `viewer-tab-document` | E1 |
| Tab "Texto extraído" | `viewer-tab-raw-text` | E2 |
| Tab "Detalles técnicos" | `viewer-tab-technical` | E3 |
| Botón "Descargar" | `viewer-download` | E4 |
| Input búsqueda raw text | `raw-text-search-input` | F2, F3 |
| Botón copiar raw text | `raw-text-copy` | F4 |
| Botón descargar raw text | `raw-text-download` | F5 |
| Modal reprocesar | `reprocess-confirm-modal` | G3, G4 |
| Botón confirmar reproceso | `reprocess-confirm-btn` | G4 |
| Campo editable (trigger) | Ya existe: `field-trigger-{id}` | J1 |
| Sección de visita | Ya existe: `visit-episode-{n}` | O1 |

---

## 6. Cobertura por capa

```
┌─────────────────────────────────────────────────────┐
│  P0 Smoke (2 tests, 2 spec files)                   │
│  → App loads, Upload básico                         │
├─────────────────────────────────────────────────────┤
│  P1 Core (5 specs, 13 tests)                        │
│  → PDF viewer (6), Datos extraídos (3),             │
│    Edición (3), Revisión (2), Sidebar docs (3)      │
├─────────────────────────────────────────────────────┤
│  P2 Extended (13 specs, 46 tests)                   │
│  → Upload validation (2), Viewer tabs (4),          │
│    Raw text (4), Structured filters (6),            │
│    Field validation (5), Source panel (3),           │
│    Sidebar interactions (3), Split panel (2),       │
│    Zoom advanced (2), Reprocess (2),                │
│    Visit grouping (3), Toasts (3), Add field (2)    │
└─────────────────────────────────────────────────────┘
```

**Total: 61 tests en 20 spec files.**
**Funcionalidades cubiertas: 87 de 87 (100%).**

### Matriz de trazabilidad Test → Funcionalidad

| Test # | Spec file | IDs cubiertos |
|--------|-----------|---------------|
| 1 | `app-loads.spec.ts` | A1, A2, A3, A4 |
| 2 | `upload-smoke.spec.ts` | C2, C5, C7, B2 |
| 3–8 | `pdf-viewer.spec.ts` | D1, D3, D4, D6, D7, D9, D10, D11, D12, D13 |
| 9–11 | `document-sidebar.spec.ts` | B1, B2, B3, B6 |
| 12–14 | `extracted-data.spec.ts` | H1, H2, H3, H4, H5, H6, H7 |
| 15–17 | `field-editing.spec.ts` | J1, J2, J9, J10, J15 |
| 18–19 | `review-workflow.spec.ts` | K1, K2, K3, K4, K5 |
| 20–21 | `upload-validation.spec.ts` | C4, C9 |
| 22–25 | `viewer-tabs.spec.ts` | E1, E2, E3, E4 |
| 26–30 | `raw-text.spec.ts` | F1, F2, F3, F4, F5 |
| 31–36 | `structured-filters.spec.ts` | I1, I2, I3, I6, I7, I8, I9, I10 |
| 37–41 | `field-validation.spec.ts` | J3, J4, J5, J6, J8 |
| 42–44 | `source-panel.spec.ts` | L1, L2, L3, L4, L5, L6 |
| 45–47 | `sidebar-interactions.spec.ts` | B4, B5, B7 |
| 48–49 | `split-panel.spec.ts` | M1, M3 |
| 50–51 | `zoom-advanced.spec.ts` | D5, D8 |
| 52–53 | `reprocess.spec.ts` | G3, G4, G5 |
| 54–56 | `visit-grouping.spec.ts` | O1, O2, O4 |
| 57–59 | `toasts.spec.ts` | N1, N2, N4 |
| 60–61 | `add-field.spec.ts` | J12, J13, J14 |

---

## 7. Orden de implementación recomendado

> **Estado final (Iteración 12):** 22 spec files, 65 tests. Fases 1–3 completadas.

1. **Fase 1 — Infraestructura** ✅
   - [x] Playwright instalado y configurado
   - [x] `app-loads.spec.ts` (P0)
   - [x] `upload-smoke.spec.ts` (P0)
   - [x] Añadir `data-testid` faltantes (tabla §5) — 17+ testids añadidos en Iter 11, ampliados en Iter 12
   - [x] Crear helpers reutilizables (`uploadAndWaitForProcessing`, etc.) — `e2e/helpers.ts` + `e2e/fixtures.ts`

2. **Fase 2 — Core P1** ✅ (Iteración 11)
   - [x] `pdf-viewer.spec.ts` (6 tests)
   - [x] `extracted-data.spec.ts` (3 tests)
   - [x] `field-editing.spec.ts` (3 tests)
   - [x] `review-workflow.spec.ts` (2 tests)
   - [x] `document-sidebar.spec.ts` (3 tests)

3. **Fase 3 — Extended P2** ✅ (Iteración 12, F19-A → F19-E)
   - [x] Bloque Viewer: `viewer-tabs` (4), `raw-text` (5), `zoom-advanced` (2) — F19-A
   - [x] Bloque Data: `structured-filters` (6), `field-validation` (5), `add-field` (2) — F19-B
   - [x] Bloque Workflow: `reprocess` (2), `toasts` (3) — F19-C
   - [x] Bloque Layout: `source-panel` (3), `split-panel` (2), `sidebar-interactions` (3) — F19-D
   - [x] Bloque Avanzado: `visit-grouping` (3), `upload-validation` (2) — F19-E

4. **Fase 4 — Accessibility** ✅ (Iteración 12, F19-I + F19-J)
   - [x] `accessibility.spec.ts` (3 tests) — axe-core WCAG 2.1 AA audit
   - [x] aria-labels, focus management, color contrast fixes

---

## How to test

```bash
# Verificar que los tests P0 existentes siguen verdes:
$env:FRONTEND_PORT='80'; docker compose up -d --build --wait
cd frontend
npm run test:e2e
```

---

## Notas

- Todos los labels de la UI están en español (los selectores deben usar `data-testid` no texto).
- El backend tiene polling (~1.5s) para documentos en procesamiento. Los tests deben esperar con `expect().toBeVisible({ timeout })` razonables, no con `waitForTimeout`.
- Operaciones de edición son mutaciones al backend (POST a `/runs/{id}/interpretations`), por lo que cada test debe ser idempotente o limpiar su estado.
