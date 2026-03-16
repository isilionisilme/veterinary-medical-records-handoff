# User Guide — What the App Does and How to Try It

This page explains what the application does from the user's perspective and walks you through the main workflows so you can evaluate them hands-on.

> **Prerequisites:** the app must be running. See [Deployment](deployment) for Docker commands and URLs.

---

## What it does

The system assists veterinarians in reviewing medical records. When a document is uploaded, the backend extracts structured data — dates, diagnoses, treatments, amounts — and assigns a confidence score to each field. The veterinarian then reviews, corrects, and confirms the interpretation.

Every correction is preserved as a structured signal. The system uses accumulated review data to refine confidence scores for future extractions — fields that are frequently corrected receive lower initial confidence, while consistently accepted fields gain trust.

---

## Workflows to try

Open the frontend at **http://localhost:5173** and follow the flows below.

### 1. Upload a document

1. Click **Upload** and select a PDF file, or drag & drop a PDF file on the doc viewer area. 
2. The document appears in the list with a **Processing** status.
3. After a few seconds, status changes to **Ready for review** — the backend has extracted structured data and computed confidence scores.

### 2. Review the interpretation

1. Open a processed document from the list on the left.
2. The **review workspace** shows the source PDF alongside the extracted data.
3. Each field displays a confidence indicator (coloured dot before the name of the field) — higher confidence means the extraction is more certain. Hover your mouse over one field to see more details. 
4. Preview or download the original PDF to compare against the extracted values.

### 3. Edit structured fields

1. In the review workspace, click any extracted field to edit it.
2. Correct values that the extraction got wrong (e.g., a misread date or diagnosis).
3. Each correction is recorded as an explicit signal — the system tracks what was changed and why confidence was insufficient.

### 4. Mark as reviewed

1. Once satisfied with all fields, toggle **Mark as reviewed**.
2. The document status updates, confirming the veterinarian has validated the interpretation.
3. This completes the review cycle for that document.
4. After 3+ reviewed documents, confidence scores for new extractions adjust based on past corrections.

---

## What to look for

- **Confidence scoring** — fields the system is unsure about are visually distinct from high-confidence extractions.
- **Human-in-the-loop design** — the system assists but never decides; the veterinarian always has final authority.
- **Traceability** — every correction and status change is preserved, never silently overwritten.

---

## Suggested next reads

- [Product Design](product-design) — vision, strategy, and the human-in-the-loop philosophy behind the system
- [Architecture](architecture) — modular monolith, module boundaries, data flow
- [Event Architecture](event-architecture) — async processing pipeline and state machine
- [Extraction Quality](extraction-quality) — confidence calibration, quality metrics, error taxonomy
- [Implementation History](implementation-history) — chronological build log with decisions at each iteration
