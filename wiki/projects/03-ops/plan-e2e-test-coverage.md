# E2E Test Coverage Plan

## Purpose
Comprehensive inventory of all user-facing functionalities and the Playwright end-to-end tests that cover them. Section 1 catalogues every testable interaction grouped by feature area; Section 2 specifies concrete test cases in Given/When/Then format, prioritised into smoke (P0), core workflow (P1), and extended coverage (P2) tiers.

> **Audience**: QA, frontend engineers, and evaluators assessing test strategy.

---

## 1. Inventory of functionalities (user perspective)

### A — Loading the application

| ID | Functionality | data-testid / key selector |
| --- | ------------------------------------------------------------- | ------------------------------------------ |
| A1 | The app loads and displays the main layout | `canvas-wrapper`, `main-canvas-layout` |
| A2 | The documents sidebar is displayed | `documents-sidebar` |
| A3 | The upload zone (dropzone) is shown | `upload-dropzone` / UploadDropzone visible |
| A4 | The viewer shows empty status ("Select a document...") | `viewer-empty-state` |

### B — Document Sidebar

| ID | Functionality | data-testid / key selector |
| --- | ----------------------------------------------------------------------------- | --------------------------------------------------- |
| B1 | Existing documents are displayed grouped: "To review" / "Reviewed" | `left-panel-scroll`, group headers |
| B2 | Selecting a document marks it as active (`aria-pressed`) | `doc-row-{id}` |
| B3 | The active document shows visual indicator (accent sidebar) | `doc-row-{id}[aria-current]` |
| B4 | Pin/unpin sidebar | "Pin"/"Pinned" button in `sidebar-actions-cluster` |
| B5 | Refresh list of documents | "Refresh" button in `sidebar-actions-cluster` |
| B6 | The chip status of each document is shown (processing, complete, error) | `DocumentStatusChip` |
| B7 | Hover expands collapsed sidebar | `documents-sidebar[data-expanded]` |
| B8 | Empty status: "No documents uploaded yet."                               | visible text |
| B9 | "Taking longer than expected" indicator for long processing | visible text |

### C — Document upload

| ID | Functionality | data-testid / key selector |
| --- | --------------------------------------------------------------------- | ----------------------------- |
| C1 | Click on dropzone opens file selector | `#upload-document-input` |
| C2 | Upload PDF via file input → appears in sidebar | `doc-row-{new_id}` |
| C3  | Drag & drop in sidebar dropzone                                   | UploadDropzone + drag events  |
| C4 | Drag & drop in PDF viewer | `viewer-dropzone` |
| C5 | Successful upload feedback (toast "Document uploaded successfully") | visible toast |
| C6 | Upload error feedback (error toast) | visible toast |
| C7 | Auto-opening of the document after upload (the PDF is loaded in the viewer) | PDF visible in viewer |
| C8 | "Uploading..." indicator during upload | spinner + text "Uploading..." |
| C9 | Non-PDF file rejection (`.pdf` only) | error toast |
| C10 | File rejection >20 MB | error toast |

### D — PDF Viewer

| ID | Functionality | data-testid / key selector |
| --- | ------------------------------------------------------------------ | ------------------------------------- |
| D1 | The document is rendered in the viewer (canvas visible) | `pdf-page` (canvas elements) |
| D2 | Loading indicator "Loading PDF..." | visible text |
| D3 | Zoom In (+ button) → zoom increases 10% | "Zoom In" button, `pdf-zoom-indicator` |
| D4 | Zoom Out (− button) → zoom decrements 10% | "Zoom out" button, `pdf-zoom-indicator` |
| D5 | Zoom with Ctrl + mouse wheel | `pdf-scroll-container` wheel event |
| D6 | Fit to width (button) → zoom back to 100% | "Fit to Width" button |
| D7 | Zoom indicator shows percentage correct | `pdf-zoom-indicator` |
| D8 | Zoom persist and localStorage | `pdfViewerZoomLevel` and localStorage |
| D9 | Zoom limits respected (50%–200%) | disabled buttons on ends |
| D10 | Navigation to previous page | "Previous Page" button |
| D11 | Navigation to next page | "Next Page" button |
| D12 | Current page indicator (n/total) | text in toolbar |
| D13 | Disabled navigation buttons on ends (first/last page) | `disabled` state |
| D14 | Continuous scrolling between pages updates page indicator | `pdf-scroll-container` scroll |

### E — Viewer toolbar (tabs)

| ID | Functionality | data-testid / key selector |
| --- | ---------------------------------------------- | --------------------------------------- |
| E1 | Tab "Document" shows the PDF | "Document" button `aria-current="page"` |
| E2 | Tab "Extracted text" shows the raw text | "Extracted text" button |
| E3 | Tab "Technical details" shows history | "Technical details" button |
| E4 | "Download" button opens the PDF in a new tab | "Download" button |

### F — Raw Text View

| ID | Functionality | data-testid / key selector |
| --- | -------------------------------------------------------- | ---------------------------- |
| F1 | The text extracted from the document is displayed | visible text content |
| F2 | Search in extracted text → "Match found" | search input + feedback |
| F3 | Search without results → "No matches found" | visible feedback |
| F4 | Copy text to clipboard | Copy button |
| F5 | Download extracted text | Download button |
| F6 | Text loading status | spinner / loading |
| F7 | Error when text is not available | error message |

### G — Technical details (processing history)

| ID | Functionality | data-testid / key selector |
| --- | --------------------------------------------- | ---------------------------- |
| G1 | The run history of the document is displayed | run list |
| G2 | Expand/collapse details of a step | expand button |
| G3 | Reprocess document (Retry button) | confirmation modal |
| G4 | Confirm reprocessing | button in modal |
| G5 | Active processing indicator | status processing |

### H — Extracted Data Panel (Structured Data)

| ID | Functionality | data-testid / key selector |
| --- | -------------------------------------------------------------------------- | ---------------------------- |
| H1 | The "Extracted Data" panel is displayed with fields organized by sections | `structured-column-stack` |
| H2 | Fields organized into medical history sections | sections with headers |
| H3 | Each field shows its formatted value | field value visible |
| H4 | Missing fields show placeholder "—" | `MISSING_VALUE_PLACEHOLDER` |
| H5 | Confidence indicator by field (high/medium/low dot) | `confidence-indicator-{id}` |
| H6 | "Critical" Badge in critical fields | CriticalBadge |
| H7 | Summary of detected fields (n/total + confidence distribution) | toolbar summary |
| H8 | "Other extracted data" section for non-canonical fields | separate section |
| H9 | Loading state (skeleton) while processing data | `review-core-skeleton` |
| H10 | Empty state "No run completed" | visible message |
| H11 | Interpretation error with "Retry" button | Retry button |
| H12 | Degraded Trust Policy Notice | `confidence-policy-degraded` |

### I — Search and filters on extracted data

| ID | Functionality | data-testid / key selector |
| --- | ------------------------------------------------ | ------------------------------- |
| I1 | Search fields by text (key, label or value) | `structured-search-shell` input |
| I2 | Clear search (X button) | "Clear Search" button |
| I3 | Filter by low confidence | toggle "Low" |
| I4 | Filter by medium confidence | toggle "Medium" |
| I5 | Filter by high confidence | toggle "High" |
| I6 | Filter: critics only | toggle "Critics only" |
| I7 | Filter: only with value | toggle "Only with value" |
| I8 | Filter: empty only | toggle "Empties only" |
| I9 | Reset all filters | "Reset filters" button |
| I10 | Empty state when filters have no results | "No results" message |

### J — Editing fields

| ID | Functionality | data-testid / key selector |
| --- | ---------------------------------------------------------- | --------------------------------- |
| J1 | Click on field opens editing dialog | `FieldEditDialog` open |
| J2 | Edit free text value | input in dialog |
| J3 | Edit Gender field (dropdown with controlled vocabulary) | select with canonical options |
| J4 | Edit Species field (dropdown with controlled vocabulary) | select with canonical options |
| J5 | Microchip validation (format) | error visible if invalid |
| J6 | Weight validation (format) | error visible if invalid |
| J7 | Age validation (format) | error visible if invalid |
| J8 | Date validation (format) | error visible if invalid |
| J9 | Save edit → updated value in panel | "Save" button |
| J10 | Cancel edit | "Cancel" button |
| J11 | Candidate suggestions in editing | candidates section visible |
| J12 | Editing block on "reviewed" document (feedback) | warning toast |
| J13 | Add new field (AddFieldDialog) | dialog with key + value |
| J14 | Save new field | "Save" button in AddFieldDialog |
| J15 | Trust is updated after manual editing | indicator change |

### K — Review Workflow

| ID | Functionality | data-testid / key selector |
| --- | ----------------------------------------------------------- | ---------------------------- |
| K1 | "Mark Reviewed" button marks document as reviewed | main button |
| K2 | "Reopen" button reopens document for review | outline button |
| K3 | "Dialing..." / "Reopening..." indicator during mutation | spinner on button |
| K4 | Reviewed document moved to "Reviewed" group in sidebar | "Revised" group |
| K5 | Reopened document returns to "To review" | "To review" group |

### L — Evidence Panel (Source Panel)

| ID | Functionality | data-testid / key selector |
| --- | ------------------------------------------------------------ | --------------------------------------- |
| L1 | Select a field navigates to the PDF on the evidence page | viewer scroll |
| L2 | The source panel with page and snippet is displayed | `source-pinned-panel` / `source-drawer` |
| L3 | Pin/unpin font panel | "Pin"/"Unpin" button |
| L4 | Close source panel | X button |
| L5 | Textual evidence of the field is shown | content in Source Panel |
| L6 | Visual highlight on the correct page of the PDF | accent background in `pdf-page` |

### M — Layout and split panel

| ID | Functionality | data-testid / key selector |
| --- | ------------------------------------------------ | ------------------------------ |
| M1 | Split panel between PDF viewer and extracted data | `review-split-grid` |
| M2 | Drag handle to resize panels | `review-split-handle` |
| M3  | Doble-click en handle resetea ratio              | `review-split-handle` dblclick |
| M4 | Keyboard resize of the split panel | arrow key events |

### N — Toasts and notifications

| ID | Functionality | data-testid / key selector |
| --- | --------------------------------------------------- | ---------------------------- |
| N1 | Successful Toast auto-closes after ~3.5s | auto-dismiss |
| N2 | Toast error auto-closes after ~5s | auto-dismiss |
| N3 | Connectivity toast when there is a network error | toast connectivity |
| N4 | Close toast manually | close button in toast |
| N5 | "Open document" action on successful upload toast | action button |

### O — Visits (canonical contract)

| ID | Functionality | data-testid / key selector |
| --- | ---------------------------------------------------------- | ---------------------------- |
| O1 | Visit episodes grouped and numbered | `visit-episode-{n}` |
| O2 | Visit metadata (date, admission, discharge, reason) | fields within visit |
| O3 | Fields with visit scope assigned correctly | fields with `visit_group_id` |
| O4 | "Unassigned" group visible when there are ungrouped fields | `visit-unassigned-group` |

---

## 2. Detailed test specification (Given / When / Then)

> Convention: each test is described with specific steps and expected results. The IDs in parentheses (e.g. `[A1]`)
> refer to the inventory of functionalities in §1. **Global precondition:** the app is running on
> `localhost:80` with Docker Compose.

---

### P0 — Smoke (in each PR, <30 s each test)

#### `app-loads.spec.ts`

**Test 1 — "The app loads and displays the main layout"** `[A1, A2, A3, A4]`

| Step | Action | Expected result |
| ----- | --------------------------------------- | ------------------------------------------------------------------------------- |
| Given | —                                       | —                                                                               |
| When  | Navegar a `/`                           | —                                                                               |
| Then | The main container is visible | `[data-testid="canvas-wrapper"]` visible |
| Then | The document sidebar is visible | `[data-testid="documents-sidebar"]` visible |
| Then | The upload zone (dropzone) is visible | UploadDropzone visible (first `[data-testid="upload-dropzone"]`) |
| Then | Viewer shows empty status | `[data-testid="viewer-empty-state"]` visible, or text "Select a document" |

---

#### `upload-smoke.spec.ts`

**Test 2 — "Uploading a PDF makes it appear in the sidebar"** `[C2, C5, C7, B2]`

| Step | Action | Expected result |
| ----- | -------------------------------------------------------- | --------------------------------------------------------------- |
| Given | Navigate to `/` and wait for visible sidebar | — |
| When | Hover over the sidebar to expand it | Sidebar expanded |
| When | Upload `sample.pdf` via `#upload-document-input` | — |
| Then | The sidebar contains the text "sample.pdf" (timeout 60 s) | `[data-testid="documents-sidebar"]` contains filename text |
| Then | There is a document row with the returned `document_id` | `[data-testid="doc-row-{id}"]` visible |

---

### P1 — Core workflows (in each PR, <60 s per test)

#### `pdf-viewer.spec.ts`

> **Shared precondition:** upload a 2+ page PDF and wait for the viewer to render it.

**Test 3 — "The PDF is rendered in the viewer"** `[D1]`

| Step | Action | Expected result |
| ----- | --------------------------------------- | ------------------------------------------- |
| Given | Document uploaded and selected | — |
| When | Wait for the viewer to load | — |
| Then | At least one page canvas is visible | `[data-testid="pdf-page"]` count ≥ 1 |
| Then | The PDF toolbar is visible | `[data-testid="pdf-toolbar-shell"]` visible |

**Test 4 — "Zoom In increases the zoom by 10%"** `[D3, D7]`

| Step | Action | Expected result |
| ----- | --------------------------- | --------------------------------------------------- |
| Given | PDF uploaded, zoom to 100% | `[data-testid="pdf-zoom-indicator"]` shows "100%" |
| When | Click on the "Zoom In" button | — |
| Then | The indicator shows "110%" | `[data-testid="pdf-zoom-indicator"]` text = "110%" |

**Test 5 — "Zoom Out decreases the zoom by 10%"** `[D4, D7]`

| Step | Action | Expected result |
| ----- | -------------------------- | -------------------------------------------------- |
| Given | PDF uploaded, zoom to 100% | — |
| When | Click on the "Zoom Out" button | — |
| Then | The indicator shows "90%" | `[data-testid="pdf-zoom-indicator"]` text = "90%" |

**Test 6 — "Fit to width resets zoom to 100%"** `[D6, D7]`

| Step | Action | Expected result |
| ----- | ------------------------------------------ | --------------------------------------------------- |
| Given | PDF loaded, zoom in 2 times (→120%) | — |
| When | Click on the "Fit to Width" button | — |
| Then | The indicator shows "100%" | `[data-testid="pdf-zoom-indicator"]` text = "100%" |

**Test 7 — "Zoom buttons are disabled at boundaries"** `[D9]`

| Step | Action | Expected result |
| ----- | ------------------------------------------------- | --------------------------------------- |
| Given | PDF uploaded | — |
| When | Click "Zoom Out" repeatedly up to 50% | — |
| Then | "Zoom out" button is disabled | `[data-testid="pdf-zoom-out"]` disabled |
| When | Click "Zoom In" repeatedly up to 200% | — |
| Then | "Zoom in" button is disabled | `[data-testid="pdf-zoom-in"]` disabled |

**Test 8 — "Navigation between pages"** `[D10, D11, D12, D13]`

| Step | Action | Expected result |
| ----- | ---------------------------------------------------- | -------------------------------------------------- |
| Given | 2+ page PDF loaded, we are on page 1 | Indicator shows "1/N" |
| Then | "Previous page" button is disabled | disabled state |
| When | Click on the "Next page" button | — |
| Then | Indicator shows "2/N" | `[data-testid="pdf-page-indicator"]` text = "2/N" |
| Then | "Previous Page" button is now enabled | — |
| When | On last page, check "Next page" button | disabled state |

---

#### `document-sidebar.spec.ts`

> **Precondition:** at least 1 document already existing in the system.

**Test 9 — "Document list shows 'To Review' and 'Reviewed' groups"** `[B1]`

| Step | Action | Expected result |
| ----- | ------------------------------------------ | ------------------------------------------- |
| Given | Navigate to `/`, expanded sidebar | — |
| When | Observe the sidebar | — |
| Then | At least one group of documents is displayed | Header "To review" or "Reviewed" visible |
| Then | Each document shows name and timestamp | Filename text visible in row |

**Test 10 — "Selecting a document marks it as active"** `[B2, B3]`

| Step | Action | Expected result |
| ----- | -------------------------------------- | ---------------------------------- |
| Given | Sidebar with at least 1 document | — |
| When  | Click en un `doc-row-{id}`             | —                                  |
| Then | The row has `aria-pressed="true"` | Verifiable attribute |
| Then | The row has `aria-current="true"` | Verifiable attribute |
| Then | The viewer loads the PDF (canvas visible) | `[data-testid="pdf-page"]` visible |

**Test 11 — "Each document shows its status chip"** `[B6]`

| Step | Action | Expected result |
| ----- | -------------------------------- | ------------------------------------------------------------------ |
| Given | Expanded sidebar with documents | — |
| When | Observe the rows | — |
| Then | Each row contains a status chip | Element with class `DocumentStatusChip` present within each row |

---

#### `extracted-data.spec.ts`

> **Precondition:** upload `sample.pdf`, wait for processing to finish (status != PROCESSING).

**Test 12 — "The extracted data panel is shown with sections"** `[H1, H2]`

| Step | Action | Expected result |
| ----- | -------------------------------------------- | ------------------------------------------------------- |
| Given | Document processed and selected | — |
| When | Wait for the data panel to be ready | `[data-testid="structured-column-stack"]` visible |
| Then | The panel displays the title "Extracted Data" | Visible text |
| Then | There is at least one section with header | Section with title (e.g., "Patient data") visible |

**Test 13 — "Fields show their formatted values"** `[H3, H4]`

| Step | Action | Expected result |
| ----- | ------------------------------------------- | ------------------------------- |
| Given | Extracted data panel ready | — |
| When | Find fields in the panel | — |
| Then | At least one field shows a non-empty value | Visible value text (≠ "—") |
| Then | Fields without value show "—" | Placeholder "—" visible |

**Test 14 — "Fields show trust indicators"** `[H5, H6, H7]`

| Step | Action | Expected result |
| ----- | ------------------------------------------------------ | --------------------------------------------------- |
| Given | Ready extracted data panel with fields | — |
| When | Observe the fields | — |
| Then | At least one field has visible trust indicator | `[data-testid^="confidence-indicator-"]` visible |
| Then | The summary of detected fields is visible | Text with count (e.g., "12/20") visible in toolbar |

---

#### `field-editing.spec.ts`

> **Precondition:** processed document with at least one editable field (e.g., `pet_name`).

**Test 15 — "Click on field opens editing dialog"** `[J1]`

| Step | Action | Expected result |
| ----- | ----------------------------------------------------------------- | ----------------------------------- |
| Given | Data panel ready, field `pet_name` visible | — |
| When | Click on the field trigger (`[data-testid^="field-trigger-"]`) | — |
| Then | The editing dialog opens | Visible dialog with field title |
| Then | The input contains the current value of the field | Pre-populated input |

**Test 16 — "Edit value and save updates the panel"** `[J2, J9, J15]`

| Step | Action | Expected result |
| ----- | ---------------------------------------------------- | ------------------------------- |
| Given | Open edit dialog for a field | — |
| When | Delete the current value and enter "NewTestValue" | — |
| When | Click on "Save" | — |
| Then | The dialogue is closed | Dialog not visible |
| Then | The field displays "NewTestValue" in the panel | Updated text visible |
| Then | Successful toast appears | Toast visible (auto-disappears) |

**Test 17 — "Cancel editing does not modify the field"** `[J10]`

| Step | Action | Expected result |
| ----- | ------------------------------------------------- | -------------------------- |
| Given | Open dialog, original value = "OriginalValue" | — |
| When | Change text to "OtroValue" | — |
| When | Click on "Cancel" | — |
| Then | Dialogue closes | Dialog not visible |
| Then | The field still shows "OriginalValue" | Original text without changes |

---

#### `review-workflow.spec.ts`

> **Precondition:** processed document and visible extracted data.

**Test 18 — "Mark document as reviewed"** `[K1, K3, K4]`

| Step | Action | Expected result |
| ----- | ----------------------------------------------------- | ---------------------------------------- |
| Given | Document in status "To review" | "Mark Reviewed" button visible |
| When | Click on "Mark reviewed" | — |
| Then | "Dialing..." indicator appears briefly | Visible spinner |
| Then | The button changes to "Reopen" | "Reopen" text visible |
| Then | The document appears in the "Reviewed" group of the sidebar | Doc row within the "Reviewed" group |
| Then | Success toast: "Document marked as reviewed."    | Toast visible |

**Test 19 — "Reopen revised document"** `[K2, K5]`

| Step | Action | Expected result |
| ----- | ------------------------------------------------------- | ------------------------------------------- |
| Given | Document in "Revised" status | "Reopen" button visible |
| When | Click on "Reopen" | — |
| Then | "Reopening..." indicator appears briefly | Visible spinner |
| Then | The button changes to "Mark Reviewed" | "Mark Reviewed" text visible |
| Then | The document returns to the "To review" group of the sidebar | Doc row within the "To review" group |
| Then | Toast of success: "Document reopened for review."    | Toast visible |

---

### P2 — Secondary features (nightly / pre-release, <90 s each test)

#### `upload-validation.spec.ts`

**Test 20 — "Non-PDF file rejection"** `[C9]`

| Step | Action | Expected result |
| ----- | ------------------------------------------------------- | --------------------- |
| Given | Navigate to `/`, expanded sidebar | — |
| When | Try to upload `non-pdf.txt` via file input | — |
| Then | Error message appears: "Only PDF files are supported." | Toast error visible |
| Then | The file does NOT appear in the sidebar | Sidebar without new row |

**Test 21 — "Drag & drop in the viewer"** `[C4]`

| Step | Action | Expected result |
| ----- | ----------------------------------------------------- | ------------------------ |
| Given | Navegar a `/`                                         | —                        |
| When | Drag & drop `sample.pdf` on the viewer | — |
| Then | Visible drop overlay: "Drop PDF to upload" | Visible text |
| When | Drop file | — |
| Then | The document is uploaded and appears in the sidebar | Visible document row |

---

#### `viewer-tabs.spec.ts`

> **Precondition:** document processed and loaded in viewer.

**Test 22 — "Tab 'Document' shows the PDF"** `[E1]`

| Step | Action | Expected result |
| ----- | ----------------------------------------------- | ---------------------------------- |
| Given | PDF loaded, "Document" tab active by default | — |
| Then | Visible Page Canvas | `[data-testid="pdf-page"]` visible |
| Then | "Document" button has `aria-current="page"` | Verifiable attribute |

**Test 23 — "Tab 'Extracted text' shows raw text"** `[E2]`

| Step | Action | Expected result |
| ----- | ----------------------------------------------- | --------------------------- |
| Given | PDF uploaded | — |
| When | Click on the "Extracted text" tab | — |
| Then | PDF content disappears (canvas hidden) | Canvas not visible |
| Then | Text content displayed | Document text visible |

**Test 24 — "'Technical details' tab shows history"** `[E3]`

| Step | Action | Expected result |
| ----- | ----------------------------------------------------- | ------------------------- |
| Given | PDF uploaded | — |
| When | Click on the "Technical details" tab | — |
| Then | Processing history information displayed | Visible technical content |

**Test 25 — "'Download' button opens the PDF"** `[E4]`

| Step | Action | Expected result |
| ----- | ------------------------------------------------ | -------------------------------------- |
| Given | PDF uploaded | — |
| When | Click on the "Download" button | — |
| Then | A new tab opens with the download URL | `window.open` called with correct URL |

---

#### `raw-text.spec.ts`

> **Precondition:** processed document, "Extracted text" tab active.

**Test 26 — "The extracted text is displayed"** `[F1]`

| Step | Action | Expected result |
| ----- | ------------------------------ | --------------------------------- |
| Given | Tab "Extracted text" active | — |
| When | Wait for loading | — |
| Then | Document text is visible | Text content with length > 0 |

**Test 27 — "Search for existing text shows match"** `[F2]`

| Step | Action | Expected result |
| ----- | ------------------------------------------------------------------- | ------------------ |
| Given | Extracted text visible | — |
| When | Type a word that exists in the text in the search field | — |
| When | Run search | — |
| Then | "Match found." message appears.                          | Visible text |

**Test 28 — "Search for nonexistent text shows 'not found'"** `[F3]`

| Step | Action | Expected result |
| ----- | -------------------------------------------------- | ------------------ |
| Given | Extracted text visible | — |
| When | Type "xyznonexistent999" in search field | — |
| When | Run search | — |
| Then | "No matches found." message appears. | Visible text |

**Test 29 — "Copy text to clipboard"** `[F4]`

| Step | Action | Expected result |
| ----- | ----------------------------- | ------------------------------------------------------------------- |
| Given | Extracted text visible | — |
| When | Click on the "Copy" button | — |
| Then | Text copied to clipboard | Verify via `page.evaluate(() => navigator.clipboard.readText())` |

**Test 30 — "Download extracted text"** `[F5]`

| Step | Action | Expected result |
| ----- | ------------------------------- | --------------------------- |
| Given | Extracted text visible | — |
| When | Click on the "Download" button | — |
| Then | A text file is downloaded | Download event intercepted |

---

#### `structured-filters.spec.ts`

> **Precondition:** processed document with extracted fields visible.

**Test 31 — "Search field by text filters results"** `[I1]`

| Step | Action | Expected result |
| ----- | ---------------------------------------------------------------- | ------------------------- |
| Given | Ready data panel with multiple fields | — |
| When | Write "name" in the search input | — |
| Then | Only fields whose key/label/value contains "name" are shown | Filtered visible fields |

**Test 32 — "Clear search restores all fields"** `[I2]`

| Step | Action | Expected result |
| ----- | --------------------------------------- | --------------------------- |
| Given | Active search filtering results | — |
| When | Click on the X button to clear search | — |
| Then | All fields are visible again | Field count restored |

**Test 33 — "Filter by low trust"** `[I3]`

| Step | Action | Expected result |
| ----- | ---------------------------------------------- | ------------------ |
| Given | Panel with fields of different trusts | — |
| When | Click on the "Low" toggle of the trust filter | — |
| Then | Only fields with low confidence are shown | Filtered fields |

**Test 34 — "Filter: critical fields only"** `[I6]`

| Step | Action | Expected result |
| ----- | ---------------------------------------------- | --------------------------------- |
| Given | Panel with critical and non-critical fields | — |
| When | Activate toggle "Critics only" | — |
| Then | Only fields marked as critical are displayed | Fields with CriticalBadge visible |

**Test 35 — "Filter: only with value / only empty"** `[I7, I8]`

| Step | Action | Expected result |
| ----- | -------------------------------------- | ------------------------------------ |
| Given | Panel with fields with value and without value | — |
| When | Activate toggle "Only with value" | Only fields with value ≠ "—" visible |
| When | Disable and activate "Empties only" | Only fields with value = "—" visible |

**Test 36 — "Reset filters restores full view"** `[I9, I10]`

| Step | Action | Expected result |
| ----- | --------------------------------------------------- | ------------------------- |
| Given | Active filters, few visible fields | — |
| When | Click on "Reset filters" | — |
| Then | All fields and sections are visible again | Full view restored |

---

#### `field-validation.spec.ts`

> **Precondition:** processed document with fields of each type available.

**Test 37 — "Microchip validation rejects invalid format"** `[J5]`

| Step | Action | Expected result |
| ----- | ---------------------------------------------------- | --------------------------- |
| Given | Open edit dialog for field `microchip_id` | — |
| When | Write "abc" (invalid format) | — |
| Then | Validation error message displayed | Error visible under input |
| Then | "Save" button is disabled | disabled state |

**Test 38 — "Edit Gender field with dropdown"** `[J3]`

| Step | Action | Expected result |
| ----- | --------------------------------------------------------------------- | --------------------------- |
| Given | Open dialog for field `sex` | — |
| Then | A `<select>` is displayed with canonical options (Male, Female, etc.) | Select visible with options |
| When | Select "Female" | — |
| When  | Click "Guardar"                                                       | —                           |
| Then | Field shows "Female" in panel | Updated value |

**Test 39 — "Edit Species field with dropdown"** `[J4]`

| Step | Action | Expected result |
| ----- | ----------------------------------------------- | ------------------ |
| Given | Open dialog for field `species` | — |
| Then | Shown is a `<select>` with canonical options | Select visible |
| When | Select a species and save | — |
| Then | Updated field in panel | Visible value |

**Test 40 — "Weight validation rejects non-numeric text"** `[J6]`

| Step | Action | Expected result |
| ----- | ----------------------------------- | ------------------ |
| Given | Open dialog for field `weight` | — |
| When | Write "it's-not-a-peso" | — |
| Then | Validation error visible | Visible error |

**Test 41 — "Date validation rejects invalid format"** `[J8]`

| Step | Action | Expected result |
| ----- | -------------------------------------------------------------------- | ------------------ |
| Given | Open dialog for date field (`visit_date` or `document_date`) | — |
| When | Write "this-is-not-date" | — |
| Then | Validation error visible | Visible error |

---

#### `source-panel.spec.ts`

> **Precondition:** processed document with fields that have evidence (`evidence.page`).

**Test 42 — "Select field navigates to PDF on evidence page"** `[L1, L6]`

| Step | Action | Expected result |
| ----- | -------------------------------------------------------------- | ------------------------------- |
| Given | Ready data panel with field that has evidence on page 2 | — |
| When | Click on the field | — |
| Then | The viewer scrolls to page 2 | Page 2 visible in viewport |
| Then | The page has visual highlight (accent background) | Applied highlight CSS class |

**Test 43 — "Source panel with snippet displayed"** `[L2, L5]`

| Step | Action | Expected result |
| ----- | ---------------------------------- | ------------------------------------------------------------------------------- |
| Given | Field with evidence selected | — |
| Then | Font panel visible | `[data-testid="source-drawer"]` or `[data-testid="source-pinned-panel"]` visible |
| Then | "Page N" is displayed | Text with page number |
| Then | Evidence snippet displayed | Text in "Evidence" section |

**Test 44 — "Pin and close source panel"** `[L3, L4]`

| Step | Action | Expected result |
| ----- | ----------------------------------------- | --------------------------------------------- |
| Given | Open source panel | — |
| When | Click on "Set" | — |
| Then | Panel remains visible as pinned panel | `[data-testid="source-pinned-panel"]` visible |
| When | Click on the X button to close | — |
| Then | Panel closes | Panel not visible |

---

#### `sidebar-interactions.spec.ts`

**Test 45 — "Fijar/desfijar sidebar"** `[B4]`

| Step | Action | Expected result |
| ----- | ---------------------------------------------------- | -------------------------------------------------------- |
| Given | Expanded Sidebar | — |
| When | Click on "Set" button | — |
| Then | Sidebar is fixed (remains expanded without hover) | `[data-testid="documents-sidebar"]` expanded persistent |
| When | Click on the "Pinned" button (unpin) | — |
| Then | Sidebar returns to hover mode | Collapses when mouse exits |

**Test 46 — "Refresh document list"** `[B5]`

| Step | Action | Expected result |
| ----- | ----------------------------------------------- | ---------------------------------- |
| Given | Sidebar with documents | — |
| When | Click on the "Update" button | — |
| Then | Refresh animation shown (spinner) | Classy Icon `animate-spin` |
| Then | The list is updated | Document list re-rendered |

**Test 47 — "Hover expands collapsed sidebar"** `[B7]`

| Step | Action | Expected result |
| ----- | -------------------------------------------- | ------------------------- |
| Given | Sidebar in hover mode (not pinned), collapsed | `[data-expanded="false"]` |
| When | Move mouse over the sidebar | — |
| Then | The sidebar expands | `[data-expanded="true"]` |
| When | Move mouse out of sidebar | — |
| Then | The sidebar collapses | `[data-expanded="false"]` |

---

#### `split-panel.spec.ts`

**Test 48 — "The layout shows split grid between viewer and data"** `[M1]`

| Step | Action | Expected result |
| ----- | ----------------------------------- | --------------------------------------------- |
| Given | Selected document | — |
| Then | The split grid is visible | `[data-testid="review-split-grid"]` visible |
| Then | The resize handle is visible | `[data-testid="review-split-handle"]` visible |

**Test 49 — "Double-click on handle resets the ratio"** `[M3]`

| Step | Action | Expected result |
| ----- | ---------------------------------------------------- | ---------------------------- |
| Given | Split grid with modified ratio | — |
| When  | Doble-click en `[data-testid="review-split-handle"]` | —                            |
| Then | The ratio returns to the default value | Restored visual proportion |

---

#### `zoom-advanced.spec.ts`

> **Precondition:** document with PDF loaded.

**Test 50 — "Ctrl + mouse wheel zooms"** `[D5]`

| Step | Action | Expected result |
| ----- | -------------------------------------------- | ----------------------------------------- |
| Given | PDF a zoom 100% | — |
| When | Ctrl + scroll up on the PDF container | — |
| Then | Zoom increases | Indicator shows >100% |
| When  | Ctrl + scroll down                           | —                                         |
| Then | Zoom decreases | Indicator shows <100% (or returns to 100%) |

**Test 51 — "Zoom persists in localStorage"** `[D8]`

| Step | Action | Expected result |
| ----- | ---------------------------------------------------- | ------------------------------------- |
| Given | PDF uploaded | — |
| When | Zoom to 130% | — |
| Then | `localStorage.getItem("pdfViewerZoomLevel")` = "1.3" | Verifiable value via `page.evaluate` |
| When | Reload the page and reload the PDF | — |
| Then | Zoom starts at 130% | Indicator shows "130%" |

---

#### `reprocess.spec.ts`

> **Precondition:** processed document (status COMPLETED or FAILED).

**Test 52 — "Reprocess confirmation modal sample document"** `[G3]`

| Step | Action | Expected result |
| ----- | ------------------------------------------------------ | ------------------------------------------------- |
| Given | Selected document, "Technical details" tab active | — |
| When | Click on the "Retry" button | — |
| Then | Visible confirmation modal | `[data-testid="reprocess-confirm-modal"]` visible |

**Test 53 — "Confirm reprocessing starts new processing"** `[G4, G5]`

| Step | Action | Expected result |
| ----- | ------------------------------------------- | ----------------------- |
| Given | Visible confirmation modal | — |
| When | Click on confirm button | — |
| Then | Modal closes | Modal not visible |
| Then | Toast: "Reprocessing started."          | Toast visible |
| Then | The status of the document changes to PROCESSING | Updated chip status |

---

#### `visit-grouping.spec.ts`

> **Precondition:** document processed with canonical contract `visit-grouped-canonical` and 2+ visits.

**Test 54 — "Visit episodes are displayed grouped"** `[O1]`

| Step | Action | Expected result |
| ----- | -------------------------------------- | ----------------------------------------- |
| Given | Ready data panel with visits | — |
| Then | At least one visit episode visible | `[data-testid^="visit-episode-"]` visible |
| Then | The episodes are numbered | Text "Visit 1", "Visit 2", etc.        |

**Test 55 — "Each visit shows its metadata"** `[O2]`

| Step | Action | Expected result |
| ----- | ----------------------------------------- | ------------------------------------ |
| Given | Visible visit episode | — |
| Then | Visit date shown | `visit_date` field with visible value |
| Then | Reason for inquiry is shown (if any) | `reason_for_visit` field visible |

**Test 56 — "'Unallocated' group visible for orphan fields"** `[O4]`

| Step | Action | Expected result |
| ----- | ------------------------------------------ | ------------------------------------------------ |
| Given | Document with ungrouped fields in visit | — |
| Then | "Unassigned" group shown | `[data-testid="visit-unassigned-group"]` visible |

---

#### `toasts.spec.ts`

**Test 57 — "Success Toast closes itself"** `[N1]`

| Step | Action | Expected result |
| ----- | -------------------------------------------------------- | ----------------------------- |
| Given | Action that generates success toast (e.g., check checked) | — |
| Then  | Toast visible                                            | —                             |
| Then | At ~3.5s the toast disappears | Toast not visible (timeout 5s) |

**Test 58 — "Toast error auto-closes slower"** `[N2]`

| Step | Action | Expected result |
| ----- | --------------------------------------------- | ----------------------------- |
| Given | Action that generates error (force network error) | — |
| Then | Visible error toast | — |
| Then | At ~5s the toast disappears | Toast not visible (timeout 7s) |

**Test 59 — "Close toast manually"** `[N4]`

| Step | Action | Expected result |
| ----- | ------------------------------- | ------------------ |
| Given | Toast visible                   | —                  |
| When | Click on the X button of the toast | — |
| Then | Toast disappears immediately | Toast not visible |

---

#### `add-field.spec.ts`

> **Precondition:** processed document, not reviewed.

**Test 60 — "Add new field with key and value"** `[J13, J14]`

| Step | Action | Expected result |
| ----- | --------------------------------------------------------------------- | ----------------------------- |
| Given | Data panel ready | — |
| When | Open "Add field" dialog | — |
| Then | Visible dialog with inputs for key and value | Title "Add field" visible |
| When | Enter key "test_field" and value "test_value" | — |
| When  | Click "Guardar"                                                       | —                             |
| Then | Dialogue closes | Dialog not visible |
| Then | The "test_field" field appears in the "Other extracted data" section | Visible field with value |

**Test 61 — "Editing lock on revised document"** `[J12]`

| Step | Action | Expected result |
| ----- | -------------------------------------------------- | ------------------------ |
| Given | Document marked as revised | — |
| When | Try clicking on field trigger to edit | — |
| Then | Notice is displayed that the document is reviewed | Toast or visible feedback |
| Then | The editing dialog does NOT open | Dialog not visible |

---

## 3. Execution strategy

### In each PR (CI `e2e` job)

> **Trigger condition:** E2E tests run only when the PR includes changes to relevant paths:
> `frontend/src/**`, `frontend/e2e/**`, `frontend/playwright.config.ts`, `docker-compose*.yml`,
> `backend/src/**`, or any workflow file that affects the `e2e` job.
> PRs that only touch documentation, CI configs unrelated to E2E, or non-app files skip this job.

```text
P0 (smoke) + P1 (core workflows)
```

- Maximum target time: ~3 minutes
- Workers: 1 (to avoid race conditions with shared backend)
- Retry: 1 attempt in CI

### Nightly / pre-release

```text
P0 + P1 + P2 (todos)
```

- Maximum target time: ~10 minutes
- Workers: 1
- Retry: 2 intentos

### Technical configuration

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
      testMatch:
        /pdf-viewer|extracted-data|field-editing|review-workflow|document-sidebar/,
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

### Proposed npm scripts

```json
{
  "test:e2e": "playwright test --project=smoke --project=core",
  "test:e2e:smoke": "playwright test --project=smoke",
  "test:e2e:all": "playwright test --project=extended",
  "test:e2e:ui": "playwright test --ui"
}
```

---

## 4. Necessary fixtures and helpers

| Fixture/Helper | Purpose |
| ------------------------------------------- | -------------------------------------------------------------- |
| `sample.pdf` | 2+ page PDF for navigation tests |
| `sample-multifield.pdf` | Real veterinary PDF for extraction tests |
| `oversized.pdf` | PDF >20 MB for rejection test (generated in setup) |
| `non-pdf.txt` | Non-PDF file for MIME type test |
| `uploadAndWaitForProcessing(page, pdfPath)` | Helper: upload PDF, wait for processing, return `document_id` |
| `selectDocument(page, documentId)` | Helper: select an existing document in sidebar |
| `waitForExtractedData(page)` | Helper: wait for the extracted data panel to be ready |
| `editField(page, fieldKey, newValue)` | Helper: open dialog, change value, save |

---

## 5. Additional `data-testid` required

Some tests require stable selectors that do not exist today. List of `data-testid` to add:

| Component | proposed data-testid | Needed by |
| ----------------------------------- | ------------------------------- | -------------- |
| UploadDropzone (sidebar expanded)   | `upload-dropzone`               | C1, C3         |
| Toast container                     | `toast-host`                    | N1–N5          |
| Individual toast | `toast-{kind}` | N1–N5 |
| "Mark Reviewed" / "Reopen" Button | `review-toggle-button` | K1, K2 |
| "Zoom in" button | `pdf-zoom-in` | D3 |
| "Zoom out" button | `pdf-zoom-out` | D4 |
| "Fit to width" button | `pdf-zoom-fit` | D6 |
| "Previous page" button | `pdf-page-prev` | D10 |
| "Next page" button | `pdf-page-next` | D11 |
| Page number indicator | `pdf-page-indicator` | D12 |
| Tab "Document" | `viewer-tab-document` | E1 |
| Tab "Extracted text" | `viewer-tab-raw-text` | E2 |
| Tab "Technical details" | `viewer-tab-technical` | E3 |
| "Download" button | `viewer-download` | E4 |
| Input search raw text | `raw-text-search-input` | F2, F3 |
| Copy raw text button | `raw-text-copy` | F4 |
| Download raw text button | `raw-text-download` | F5 |
| Modal reprocess | `reprocess-confirm-modal` | G3, G4 |
| Confirm reprocess button | `reprocess-confirm-btn` | G4 |
| Editable field (trigger) | Already exists: `field-trigger-{id}` | J1 |
| Visit section | Already exists: `visit-episode-{n}` | O1 |

---

## 6. Coverage per layer

```text
┌─────────────────────────────────────────────────────┐
│  P0 Smoke (2 tests, 2 spec files)                   │
│  → App loads, Basic upload                          │
├─────────────────────────────────────────────────────┤
│  P1 Core (5 specs, 13 tests)                        │
│  → PDF viewer (6), Extracted data (3),              │
│    Field editing (3), Review workflow (2), Sidebar docs (3) │
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

**Total: 61 tests in 20 spec files.** **Functionalities covered: 87 of 87 (100%).**

### Test-Functionality traceability matrix

| Test # | Spec file                      | IDs cubiertos                              |
| ------ | ------------------------------ | ------------------------------------------ |
| 1 | `app-loads.spec.ts` | A1, A2, A3, A4 |
| 2      | `upload-smoke.spec.ts`         | C2, C5, C7, B2                             |
| 3–8 | `pdf-viewer.spec.ts` | D1, D3, D4, D6, D7, D9, D10, D11, D12, D13 |
| 9–11   | `document-sidebar.spec.ts`     | B1, B2, B3, B6                             |
| 12–14  | `extracted-data.spec.ts`       | H1, H2, H3, H4, H5, H6, H7                 |
| 15–17  | `field-editing.spec.ts`        | J1, J2, J9, J10, J15                       |
| 18–19 | `review-workflow.spec.ts` | K1, K2, K3, K4, K5 |
| 20–21  | `upload-validation.spec.ts`    | C4, C9                                     |
| 22–25  | `viewer-tabs.spec.ts`          | E1, E2, E3, E4                             |
| 26–30  | `raw-text.spec.ts`             | F1, F2, F3, F4, F5                         |
| 31–36 | `structured-filters.spec.ts` | I1, I2, I3, I6, I7, I8, I9, I10 |
| 37–41  | `field-validation.spec.ts`     | J3, J4, J5, J6, J8                         |
| 42–44 | `source-panel.spec.ts` | L1, L2, L3, L4, L5, L6 |
| 45–47 | `sidebar-interactions.spec.ts` | B4, B5, B7 |
| 48–49  | `split-panel.spec.ts`          | M1, M3                                     |
| 50–51  | `zoom-advanced.spec.ts`        | D5, D8                                     |
| 52–53 | `reprocess.spec.ts` | G3, G4, G5 |
| 54–56  | `visit-grouping.spec.ts`       | O1, O2, O4                                 |
| 57–59  | `toasts.spec.ts`               | N1, N2, N4                                 |
| 60–61  | `add-field.spec.ts`            | J12, J13, J14                              |

---

## 7. Recommended implementation order

> **Final state (Iteration 12):** 22 spec files, 65 tests. Phases 1–3 completed.

1. **Phase 1 — Infrastructure** ✅
   - [x] Playwright installed and configured
   - [x] `app-loads.spec.ts` (P0)
   - [x] `upload-smoke.spec.ts` (P0)
   - [x] Add missing `data-testid` (table §5) — 17+ testids added in Iter 11, expanded in Iter 12
   - [x] Crear helpers reutilizables (`uploadAndWaitForProcessing`, etc.) — `e2e/helpers.ts` + `e2e/fixtures.ts`

2. **Phase 2 — Core P1** ✅ (Iteration 11)
   - [x] `pdf-viewer.spec.ts` (6 tests)
   - [x] `extracted-data.spec.ts` (3 tests)
   - [x] `field-editing.spec.ts` (3 tests)
   - [x] `review-workflow.spec.ts` (2 tests)
   - [x] `document-sidebar.spec.ts` (3 tests)

3. **Phase 3 — Extended P2** ✅ (Iteration 12, F19-A → F19-E)
   - [x] Bloque Viewer: `viewer-tabs` (4), `raw-text` (5), `zoom-advanced` (2) — F19-A
   - [x] Bloque Data: `structured-filters` (6), `field-validation` (5), `add-field` (2) — F19-B
   - [x] Bloque Workflow: `reprocess` (2), `toasts` (3) — F19-C
   - [x] Bloque Layout: `source-panel` (3), `split-panel` (2), `sidebar-interactions` (3) — F19-D
   - [x] Advanced Block: `visit-grouping` (3), `upload-validation` (2) — F19-E

4. **Phase 4 — Accessibility** ✅ (Iteration 12, F19-I + F19-J)
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

## Notes

- The backend has polling (~1.5s) for documents in processing. The tests must wait with
  `expect().toBeVisible({ timeout })` reasonable, not with `waitForTimeout`.
- Edit operations are mutations to the backend (POST to `/runs/{id}/interpretations`), so each test must be idempotent or clear its state.
