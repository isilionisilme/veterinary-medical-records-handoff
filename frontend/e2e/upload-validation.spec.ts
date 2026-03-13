import fs from "node:fs";

import { expect, test, type Page } from "@playwright/test";

import { buildMockDocumentPayload, buildMockReviewPayload, pinSidebar, selectDocument } from "./helpers";

const DOC_ID = "doc-e2e-upload-validation";
const SAMPLE_PDF_BUFFER = fs.readFileSync("e2e/fixtures/sample.pdf");

async function setupViewerScenario(page: Page): Promise<void> {
  await pinSidebar(page);
  await page.goto("/");
  await expect(page.getByTestId("documents-sidebar")).toBeVisible();

  await page.route("**/documents?*", async (route) => {
    if (route.request().method() !== "GET") {
      await route.fallback();
      return;
    }
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        items: [
          {
            document_id: DOC_ID,
            original_filename: "sample.pdf",
            created_at: "2026-02-27T10:00:00Z",
            status: "COMPLETED",
            status_label: "Completado",
            failure_type: null,
            review_status: "IN_REVIEW",
            reviewed_at: null,
            reviewed_by: null,
          },
        ],
        limit: 50,
        offset: 0,
        total: 1,
      }),
    });
  });

  await page.route("**/documents/*/download**", async (route) => {
    const url = new URL(route.request().url());
    const match = url.pathname.match(/\/documents\/([^/]+)\/download\/?$/);
    const routeDocumentId = match?.[1];
    if (!routeDocumentId || routeDocumentId !== DOC_ID) {
      await route.fallback();
      return;
    }
    await route.fulfill({
      status: 200,
      contentType: "application/pdf",
      body: SAMPLE_PDF_BUFFER,
    });
  });

  await page.route("**/documents/*", async (route) => {
    const url = new URL(route.request().url());
    const match = url.pathname.match(/\/documents\/([^/]+)\/?$/);
    const routeDocumentId = match?.[1];
    if (route.request().method() !== "GET" || !routeDocumentId || routeDocumentId !== DOC_ID) {
      await route.fallback();
      return;
    }
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(
        buildMockDocumentPayload(DOC_ID, { status: "COMPLETED", reviewStatus: "IN_REVIEW" }),
      ),
    });
  });

  await page.route("**/documents/*/review", async (route) => {
    const url = new URL(route.request().url());
    const match = url.pathname.match(/\/documents\/([^/]+)\/review\/?$/);
    const routeDocumentId = match?.[1];
    if (!routeDocumentId || routeDocumentId !== DOC_ID) {
      await route.fallback();
      return;
    }
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(buildMockReviewPayload(DOC_ID)),
    });
  });

  await page.getByRole("button", { name: "Actualizar" }).click();
  await selectDocument(page, DOC_ID);
  await expect(page.getByTestId("pdf-page").first()).toBeVisible({ timeout: 30_000 });
}

test.describe("upload validation", () => {
  test("non-PDF file is rejected with error toast", async ({ page }) => {
    test.setTimeout(120_000);
    await pinSidebar(page);
    await page.goto("/");
    await expect(page.getByTestId("documents-sidebar")).toBeVisible();

    await page.getByLabel("Archivo PDF").setInputFiles({
      name: "not-pdf.txt",
      mimeType: "text/plain",
      buffer: Buffer.from("not-a-pdf"),
    });

    await expect(page.getByTestId("toast-error")).toBeVisible();
    await expect(page.getByText("Solo se admiten archivos PDF.")).toBeVisible();
  });

  test("drag and drop over viewer displays upload overlay", async ({ page }) => {
    test.setTimeout(180_000);
    await setupViewerScenario(page);

    const dataTransfer = await page.evaluateHandle(() => {
      const transfer = new DataTransfer();
      transfer.items.add(new File(["dummy"], "dragged.pdf", { type: "application/pdf" }));
      return transfer;
    });

    const viewerDropzone = page.getByTestId("viewer-dropzone");
    await viewerDropzone.dispatchEvent("dragenter", { dataTransfer });
    await expect(viewerDropzone.getByText("Suelta el PDF para subirlo")).toBeVisible();

    await viewerDropzone.dispatchEvent("dragleave", { dataTransfer });
    await expect(viewerDropzone.getByText("Suelta el PDF para subirlo")).toHaveCount(0);
  });
});
