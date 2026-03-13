import { expect, test } from "@playwright/test";

import { pinSidebar, selectDocument, uploadAndWaitForProcessing } from "./helpers";

test.describe("pdf viewer interactions", () => {
  test.describe.configure({ mode: "serial" });
  let sharedDocumentId: string | null = null;

  test.beforeEach(async ({ page }) => {
    test.setTimeout(120_000);

    await pinSidebar(page);
    await page.goto("/");
    await expect(page.getByTestId("documents-sidebar")).toBeVisible();

    if (!sharedDocumentId) {
      sharedDocumentId = await uploadAndWaitForProcessing(page);
    } else {
      await expect(page.getByTestId(`doc-row-${sharedDocumentId}`)).toBeVisible({ timeout: 90_000 });
    }
    await selectDocument(page, sharedDocumentId);

    await expect(page.getByTestId("pdf-toolbar-shell")).toBeVisible({ timeout: 60_000 });
    await expect(page.getByTestId("pdf-page").first()).toBeVisible({ timeout: 60_000 });
  });

  test("renders PDF pages and toolbar", async ({ page }) => {
    const pages = page.getByTestId("pdf-page");
    await expect(pages.first()).toBeVisible();
    await expect(page.getByTestId("pdf-toolbar-shell")).toBeVisible();
  });

  test("zoom in sets indicator to 110%", async ({ page }) => {
    await page.getByTestId("pdf-zoom-in").click();
    await expect(page.getByTestId("pdf-zoom-indicator")).toHaveText("110%");
  });

  test("zoom out sets indicator to 90%", async ({ page }) => {
    await page.getByTestId("pdf-zoom-out").click();
    await expect(page.getByTestId("pdf-zoom-indicator")).toHaveText("90%");
  });

  test("fit to width resets zoom to 100%", async ({ page }) => {
    await page.getByTestId("pdf-zoom-in").click();
    await page.getByTestId("pdf-zoom-in").click();
    await expect(page.getByTestId("pdf-zoom-indicator")).toHaveText("120%");

    await page.getByTestId("pdf-zoom-fit").click();
    await expect(page.getByTestId("pdf-zoom-indicator")).toHaveText("100%");
  });

  test("zoom buttons are disabled at 50% and 200% limits", async ({ page }) => {
    const zoomOut = page.getByTestId("pdf-zoom-out");
    const zoomIn = page.getByTestId("pdf-zoom-in");
    const indicator = page.getByTestId("pdf-zoom-indicator");

    for (let i = 0; i < 20 && !(await zoomOut.isDisabled()); i += 1) {
      await zoomOut.click();
    }
    await expect(indicator).toHaveText("50%");
    await expect(zoomOut).toBeDisabled();

    for (let i = 0; i < 20 && !(await zoomIn.isDisabled()); i += 1) {
      await zoomIn.click();
    }
    await expect(indicator).toHaveText("200%");
    await expect(zoomIn).toBeDisabled();
  });

  test("page navigation updates indicator and button states", async ({ page }) => {
    const pageIndicator = page.getByTestId("pdf-page-indicator");
    const previousButton = page.getByTestId("pdf-page-prev");
    const nextButton = page.getByTestId("pdf-page-next");

    const initialIndicator = (await pageIndicator.textContent())?.trim() ?? "";
    const [, totalPagesText = "1"] = initialIndicator.split("/");
    const totalPages = Number.parseInt(totalPagesText, 10);

    test.skip(totalPages < 2, "sample.pdf has a single page; navigation assertions require 2+ pages");

    await expect(pageIndicator).toHaveText(`1/${totalPages}`);
    await expect(previousButton).toBeDisabled();
    await expect(nextButton).toBeEnabled();

    await nextButton.click();
    await expect(pageIndicator).toHaveText(`2/${totalPages}`);
    await expect(previousButton).toBeEnabled();

    await previousButton.click();
    await expect(pageIndicator).toHaveText(`1/${totalPages}`);
    await expect(previousButton).toBeDisabled();
  });
});
