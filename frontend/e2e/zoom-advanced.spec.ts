import { expect, test, type Page } from "@playwright/test";

import { pinSidebar, selectDocument, uploadAndWaitForProcessing } from "./helpers";

function parseZoomPercent(value: string | null): number {
  const parsed = Number.parseInt((value ?? "").replace("%", "").trim(), 10);
  return Number.isFinite(parsed) ? parsed : 0;
}

async function openDocumentViewer(page: Page): Promise<string> {
  await pinSidebar(page);
  await page.goto("/");
  await expect(page.getByTestId("documents-sidebar")).toBeVisible();
  const documentId = await uploadAndWaitForProcessing(page);
  await selectDocument(page, documentId);
  await expect(page.getByTestId("pdf-toolbar-shell")).toBeVisible({ timeout: 60_000 });
  return documentId;
}

test.describe("advanced zoom", () => {
  test("Ctrl + scroll wheel zooms in and out", async ({ page }) => {
    test.setTimeout(180_000);
    await openDocumentViewer(page);

    const indicator = page.getByTestId("pdf-zoom-indicator");
    const scrollContainer = page.getByTestId("pdf-scroll-container");
    const initialZoom = parseZoomPercent(await indicator.textContent());
    expect(initialZoom).toBeGreaterThan(0);

    await scrollContainer.hover();
    await page.keyboard.down("Control");
    await page.mouse.wheel(0, -300);
    await page.keyboard.up("Control");

    await expect
      .poll(async () => parseZoomPercent(await indicator.textContent()), { timeout: 5_000 })
      .toBeGreaterThan(initialZoom);
    const afterZoomIn = parseZoomPercent(await indicator.textContent());

    await page.keyboard.down("Control");
    await page.mouse.wheel(0, 300);
    await page.keyboard.up("Control");

    await expect
      .poll(async () => parseZoomPercent(await indicator.textContent()), { timeout: 5_000 })
      .toBeLessThan(afterZoomIn);
  });

  test("zoom level persists via localStorage after reload", async ({ page }) => {
    test.setTimeout(180_000);
    const documentId = await openDocumentViewer(page);

    await page.getByTestId("pdf-zoom-in").click();
    await page.getByTestId("pdf-zoom-in").click();
    await page.getByTestId("pdf-zoom-in").click();
    await expect(page.getByTestId("pdf-zoom-indicator")).toHaveText("130%");

    await page.reload();
    await expect(page.getByTestId("documents-sidebar")).toBeVisible();
    await selectDocument(page, documentId);
    await expect(page.getByTestId("pdf-toolbar-shell")).toBeVisible({ timeout: 60_000 });
    await expect(page.getByTestId("pdf-zoom-indicator")).toHaveText("130%");
  });
});
