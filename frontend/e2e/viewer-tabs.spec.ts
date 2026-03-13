import { expect, test, type Page } from "@playwright/test";

import { pinSidebar, selectDocument, uploadAndWaitForProcessing } from "./helpers";

async function openReviewWithUploadedDocument(page: Page): Promise<string> {
  await pinSidebar(page);
  await page.goto("/");
  await expect(page.getByTestId("documents-sidebar")).toBeVisible();
  const documentId = await uploadAndWaitForProcessing(page);
  await selectDocument(page, documentId);
  await expect(page.getByTestId("pdf-toolbar-shell")).toBeVisible({ timeout: 60_000 });
  return documentId;
}

test.describe("viewer tabs", () => {
  test.beforeEach(async ({ page }) => {
    test.setTimeout(180_000);
    await openReviewWithUploadedDocument(page);
  });

  test("tab Documento is active by default and shows PDF", async ({ page }) => {
    await expect(page.getByTestId("viewer-tab-document")).toHaveAttribute("aria-current", "page");
    await expect(page.getByTestId("pdf-page").first()).toBeVisible();
  });

  test("tab Texto extraido switches to raw text panel", async ({ page }) => {
    await page.getByTestId("viewer-tab-raw-text").click();
    await expect(page.getByTestId("raw-text-search-input")).toBeVisible();
    await expect(page.getByTestId("raw-text-copy")).toBeVisible();
    await expect(page.getByTestId("raw-text-download")).toBeVisible();
  });

  test("tab Detalles tecnicos shows processing history", async ({ page }) => {
    await page.getByTestId("viewer-tab-technical").click();
    await expect(page.getByText("Historial de procesamiento")).toBeVisible();
    await expect(page.getByRole("button", { name: "Reprocesar" })).toBeVisible();
  });

  test("Descargar opens PDF in a new tab", async ({ page }) => {
    const popupPromise = page.waitForEvent("popup");
    const downloadRequestPromise = page.context().waitForEvent(
      "request",
      (request) =>
        request.method() === "GET" &&
        /\/documents\/.+\/download/.test(request.url()),
    );
    await page.getByTestId("viewer-download").click();
    const popup = await popupPromise;
    const downloadRequest = await downloadRequestPromise;
    expect(downloadRequest.url()).toMatch(/\/documents\/.+\/download/);
    await popup.close();
  });
});
