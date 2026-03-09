import fs from "node:fs";

import { expect, test } from "@playwright/test";

// E2E: full upload flow — upload PDF -> verify sidebar -> verify document is selectable
test("uploading a PDF adds it to documents sidebar", async ({ page }) => {
  test.setTimeout(90_000);
  const samplePdfBuffer = fs.readFileSync("e2e/fixtures/sample.pdf");

  await page.addInitScript(() => {
    window.localStorage.setItem("docsSidebarPinned", "1");
  });

  await page.goto("/");
  await expect(page.getByTestId("documents-sidebar")).toBeVisible();
  const uploadResponsePromise = page.waitForResponse((response) => {
    return response.request().method() === "POST"
      && response.url().includes("/documents/upload");
  }, { timeout: 90_000 });

  await page.locator("#upload-document-input").setInputFiles({
    name: "sample.pdf",
    mimeType: "application/pdf",
    buffer: samplePdfBuffer,
  });

  const uploadResponse = await uploadResponsePromise;
  expect(uploadResponse.status()).toBe(201);
  const uploadPayload = (await uploadResponse.json()) as { document_id?: string };
  expect(uploadPayload.document_id).toBeTruthy();
  const uploadedDocumentId = uploadPayload.document_id!;

  const documentRow = page.getByTestId(`doc-row-${uploadedDocumentId}`);
  await expect(documentRow).toBeVisible({ timeout: 90_000 });

  await documentRow.click();
  await expect(page.getByTestId("review-split-grid")).toBeVisible({ timeout: 30_000 });

  // The sidebar may show processing-related statuses (e.g., "Procesando" / "Completado")
  // depending on environment timing, so we avoid asserting a specific final status here.
});
