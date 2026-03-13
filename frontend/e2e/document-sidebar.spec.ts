import { expect, test, type Page } from "@playwright/test";

import { pinSidebar, selectDocument, uploadAndWaitForProcessing } from "./helpers";

async function openSidebar(page: Page) {
  await pinSidebar(page);
  await page.goto("/");
  await expect(page.getByTestId("documents-sidebar")).toBeVisible();
}

test("document list shows 'Para revisar' and 'Revisados' groups", async ({ page }) => {
  test.setTimeout(180_000);

  await openSidebar(page);

  const reviewedDocumentId = await uploadAndWaitForProcessing(page);
  await selectDocument(page, reviewedDocumentId);
  await page.getByTestId("review-toggle-btn").click();
  await expect(page.getByTestId("review-toggle-btn")).toContainText("Reabrir");

  await uploadAndWaitForProcessing(page);

  await expect(page.getByText("Para revisar")).toBeVisible();
  await expect(page.getByText("Revisados")).toBeVisible();
});

test("selecting a document marks row active and loads the PDF viewer", async ({ page }) => {
  test.setTimeout(120_000);

  await openSidebar(page);

  const documentId = await uploadAndWaitForProcessing(page);
  const row = page.getByTestId(`doc-row-${documentId}`);
  await row.click();

  await expect(row).toHaveAttribute("aria-pressed", "true");
  await expect(row).toHaveAttribute("aria-current", "true");
  await expect(page.getByTestId("review-split-grid")).toBeVisible({ timeout: 30_000 });
  await expect(page.getByTestId("pdf-page").first()).toBeVisible({ timeout: 30_000 });
});

test("each document row exposes a status label in aria metadata", async ({ page }) => {
  test.setTimeout(180_000);

  await openSidebar(page);

  const documentIdA = await uploadAndWaitForProcessing(page);
  const documentIdB = await uploadAndWaitForProcessing(page);

  const rows = [page.getByTestId(`doc-row-${documentIdA}`), page.getByTestId(`doc-row-${documentIdB}`)];
  for (const row of rows) {
    await expect(row).toBeVisible();
    const ariaLabel = await row.getAttribute("aria-label");
    expect(ariaLabel).toBeTruthy();
    expect(ariaLabel).toMatch(/\(.+\)$/);
  }
});
