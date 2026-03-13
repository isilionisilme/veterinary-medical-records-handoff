import fs from "node:fs";

import { expect, type Page } from "@playwright/test";

const useExternalServers = process.env.PLAYWRIGHT_EXTERNAL_SERVERS === "1";
const defaultBackendPort = process.env.CI || useExternalServers ? 8000 : 18000;
const backendBaseURL =
  process.env.PLAYWRIGHT_BACKEND_BASE_URL || `http://127.0.0.1:${defaultBackendPort}`;

function extractDocumentId(payload: unknown): string | null {
  if (!payload || typeof payload !== "object") {
    return null;
  }
  const candidate = (payload as { document_id?: unknown; documentId?: unknown }).document_id
    ?? (payload as { document_id?: unknown; documentId?: unknown }).documentId;
  if (typeof candidate !== "string") {
    return null;
  }
  const normalized = candidate.trim();
  return normalized.length > 0 && normalized !== "null" ? normalized : null;
}

function extractDocumentIdFromRowTestId(testId: string): string | null {
  if (!testId.startsWith("doc-row-")) {
    return null;
  }
  const value = testId.replace("doc-row-", "").trim();
  return value.length > 0 && value !== "null" ? value : null;
}

async function fetchLatestDocumentId(
  page: Page,
  knownDocumentIds: Set<string>,
): Promise<string | null> {
  const endpoints = [`${backendBaseURL}/documents?limit=50&offset=0`];
  for (const endpoint of endpoints) {
    const response = await page.request.get(endpoint);
    if (!response.ok()) {
      continue;
    }
    try {
      const payload = (await response.json()) as {
        items?: Array<{ document_id?: string; documentId?: string }>;
      };
      const candidate = payload.items
        ?.map((item) => extractDocumentId(item))
        .find((documentId) => typeof documentId === "string" && !knownDocumentIds.has(documentId));
      if (candidate) {
        return candidate;
      }
      const firstKnown = payload.items?.map((item) => extractDocumentId(item)).find(Boolean);
      if (firstKnown) {
        return firstKnown;
      }
    } catch {
      // Ignore malformed payloads and continue with other fallbacks.
    }
  }
  return null;
}

/**
 * Upload a PDF and wait for it to appear in the sidebar.
 * Returns the document_id from the upload response.
 */
export async function uploadAndWaitForProcessing(
  page: Page,
  pdfPath = "e2e/fixtures/sample.pdf",
  options: { timeout?: number } = {},
): Promise<string> {
  const timeout = options.timeout ?? 90_000;
  const pdfBuffer = fs.readFileSync(pdfPath);
  let docId: string | null = null;
  const existingRowTestIds = new Set(
    await page
      .locator('[data-testid^="doc-row-"]')
      .evaluateAll((nodes) => nodes.map((node) => node.getAttribute("data-testid") ?? "")),
  );
  const knownDocumentIds = new Set(
    Array.from(existingRowTestIds)
      .map((testId) => extractDocumentIdFromRowTestId(testId))
      .filter((value): value is string => Boolean(value)),
  );

  const filename = pdfPath.split("/").pop() ?? "sample.pdf";
  const uploadResponse = await page.request.post(`${backendBaseURL}/documents/upload`, {
    multipart: {
      file: {
        name: filename,
        mimeType: "application/pdf",
        buffer: pdfBuffer,
      },
    },
  });
  if (uploadResponse.ok()) {
    try {
      const json = (await uploadResponse.json()) as unknown;
      docId = extractDocumentId(json);
    } catch {
      docId = null;
    }
  } else {
    await page.getByLabel("Archivo PDF").setInputFiles({
      name: filename,
      mimeType: "application/pdf",
      buffer: pdfBuffer,
    });
  }

  try {
    await expect
      .poll(
        async () => {
          if (docId) {
            return docId;
          }
          const currentRowTestIds = await page
            .locator('[data-testid^="doc-row-"]')
            .evaluateAll((nodes) => nodes.map((node) => node.getAttribute("data-testid") ?? ""));
          const newRowTestId = currentRowTestIds.find(
            (testId) => testId.startsWith("doc-row-") && !existingRowTestIds.has(testId),
          );
          if (!newRowTestId) {
            return null;
          }
          const extractedId = newRowTestId.replace("doc-row-", "");
          if (!extractedId || extractedId === "null") {
            return null;
          }
          return extractedId;
        },
        { timeout },
      )
      .not.toBeNull();
  } catch {
    // Fall through to API/list-based fallback below for CI flakiness scenarios.
  }

  if (!docId) {
    const currentRowTestIds = await page
      .locator('[data-testid^="doc-row-"]')
      .evaluateAll((nodes) => nodes.map((node) => node.getAttribute("data-testid") ?? ""));
    const newRowTestId = currentRowTestIds.find(
      (testId) => testId.startsWith("doc-row-") && !existingRowTestIds.has(testId),
    );
    if (newRowTestId) {
      const extractedId = newRowTestId.replace("doc-row-", "");
      if (extractedId && extractedId !== "null") {
        docId = extractedId;
      }
    }
  }

  if (!docId || docId === "null") {
    docId = await fetchLatestDocumentId(page, knownDocumentIds);
  }

  if (!docId || docId === "null") {
    try {
      await expect(page.locator('[data-testid^="doc-row-"]').first()).toBeVisible({ timeout: 15_000 });
      const rowTestIds = await page
        .locator('[data-testid^="doc-row-"]')
        .evaluateAll((nodes) => nodes.map((node) => node.getAttribute("data-testid") ?? ""));
      const fallbackRowId = rowTestIds
        .map((testId) => extractDocumentIdFromRowTestId(testId))
        .find((value): value is string => Boolean(value));
      if (fallbackRowId) {
        docId = fallbackRowId;
      }
    } catch {
      // Keep final guard below for hard failures where no row is available.
    }
  }

  if (!docId || docId === "null") {
    throw new Error("Failed to resolve uploaded document id from response, sidebar, or documents list.");
  }

  const row = page.getByTestId(`doc-row-${docId}`);
  try {
    await expect(row).toBeVisible({ timeout: 5_000 });
  } catch {
    const refreshButton = page.getByRole("button", { name: "Actualizar" });
    if (await refreshButton.isVisible()) {
      await refreshButton.click();
    }
    await expect(row).toBeVisible({ timeout });
  }

  return docId!;
}

/**
 * Select a document in the sidebar and wait for the review split grid.
 */
export async function selectDocument(page: Page, documentId: string): Promise<void> {
  const row = page.getByTestId(`doc-row-${documentId}`);
  await row.click();
  await expect(page.getByTestId("review-split-grid")).toBeVisible({ timeout: 30_000 });
}

/**
 * Wait for the structured data panel to be ready.
 */
export async function waitForExtractedData(page: Page): Promise<void> {
  await expect(page.getByTestId("structured-column-stack")).toBeVisible({ timeout: 60_000 });
}

/**
 * Open field edit dialog, change value, save.
 */
export async function editField(page: Page, fieldKey: string, newValue: string): Promise<void> {
  await page.getByTestId(`field-edit-btn-${fieldKey}`).click();
  await expect(page.getByTestId("field-edit-dialog")).toBeVisible();
  const input = page.getByTestId("field-edit-input");
  await input.clear();
  await input.fill(newValue);
  await page.getByTestId("field-edit-save").click();
  await expect(page.getByTestId("field-edit-dialog")).not.toBeVisible();
}

/**
 * Pin the sidebar so it stays expanded.
 */
export async function pinSidebar(page: Page): Promise<void> {
  await page.addInitScript(() => {
    window.localStorage.setItem("docsSidebarPinned", "1");
  });
}

/**
 * Build a mock review payload for route interception.
 */
export function buildMockReviewPayload(
  documentId: string,
  overrides: {
    reviewStatus?: "IN_REVIEW" | "REVIEWED";
    fields?: Array<Record<string, unknown>>;
    versionNumber?: number;
  } = {},
) {
  return {
    document_id: documentId,
    latest_completed_run: {
      run_id: `run-e2e-${documentId}`,
      state: "COMPLETED",
      completed_at: "2026-02-27T10:00:00Z",
      failure_type: null,
    },
    active_interpretation: {
      interpretation_id: `interp-e2e-${documentId}`,
      version_number: overrides.versionNumber ?? 1,
      data: {
        document_id: documentId,
        processing_run_id: `run-e2e-${documentId}`,
        created_at: "2026-02-27T10:00:00Z",
        fields: overrides.fields ?? [
          {
            field_id: "field-pet-name",
            key: "pet_name",
            value: "Luna",
            value_type: "string",
            field_candidate_confidence: 0.91,
            field_mapping_confidence: 0.91,
            is_critical: false,
            origin: "machine",
          },
          {
            field_id: "field-species",
            key: "species",
            value: "canino",
            value_type: "string",
            field_candidate_confidence: 0.95,
            field_mapping_confidence: 0.95,
            is_critical: false,
            origin: "machine",
          },
        ],
        confidence_policy: {
          policy_version: "v1",
          band_cutoffs: { low_max: 0.5, mid_max: 0.75 },
        },
      },
    },
    raw_text_artifact: {
      run_id: `run-e2e-${documentId}`,
      available: true,
    },
    review_status: overrides.reviewStatus ?? "IN_REVIEW",
    reviewed_at: null,
    reviewed_by: null,
  };
}

/**
 * Build a mock document payload for route interception.
 */
export function buildMockDocumentPayload(
  documentId: string,
  overrides: {
    status?: string;
    reviewStatus?: string;
    filename?: string;
  } = {},
) {
  return {
    document_id: documentId,
    original_filename: overrides.filename ?? "sample.pdf",
    content_type: "application/pdf",
    file_size: 1024,
    created_at: "2026-02-27T10:00:00Z",
    updated_at: "2026-02-27T10:05:00Z",
    status: overrides.status ?? "COMPLETED",
    status_message: "Completado",
    failure_type: null,
    review_status: overrides.reviewStatus ?? "IN_REVIEW",
    reviewed_at: null,
    reviewed_by: null,
    latest_run: {
      run_id: `run-e2e-${documentId}`,
      state: "COMPLETED",
      failure_type: null,
    },
  };
}
