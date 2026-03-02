# Continuous Scroll Preview

The document preview renders PDF pages in a single vertical scroll so users can read continuously
without manual page switching.

Implementation uses `pdfjs-dist` for PDF rendering. Rendering must be incremental (lazy) to avoid blocking the UI
on large PDFs.

## PDF.js wiring (Vite)
PDF.js must be configured with an explicit worker (required for production builds).
In Vite, use a worker URL import and assign it to `GlobalWorkerOptions.workerSrc`.

## Paging and navigation rules
- Evidence `page` values are **1-based** (as defined in [`docs/projects/veterinary-medical-records/02-tech/technical-design.md`](../TECHNICAL_DESIGN/00_entry.md)). Keep viewer navigation 1-based.
- "Next" / "Previous" scroll within the viewer's scroll container only (no global page scroll hijacking).
- Track active page based on scroll position (IntersectionObserver), keeping the page index in sync with what is visible.
- Show placeholders while a page is loading/rendering; empty/blank content must be treated as a normal transient state.

Navigation buttons remain available:
- **Next** scrolls to the top of the next page in the continuous stack.
- **Previous** scrolls to the top of the previous page.

Tests should validate the scroll + navigation behavior at the component level, without relying on pixel-perfect rendering.

---
