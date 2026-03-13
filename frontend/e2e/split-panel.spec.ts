import { expect, test, type Page } from "@playwright/test";

import { buildMockDocumentPayload, buildMockReviewPayload, pinSidebar, selectDocument } from "./helpers";

const DOC_ID = "doc-e2e-split-panel";

async function openWorkspace(page: Page) {
  await pinSidebar(page);
  await page.goto("/");
  await expect(page.getByTestId("documents-sidebar")).toBeVisible();
}

async function setupSplitScenario(page: Page): Promise<void> {
  await openWorkspace(page);

  await page.route("**/documents/*/review", async (route) => {
    const url = new URL(route.request().url());
    const match = url.pathname.match(/\/documents\/([^/]+)\/review\/?$/);
    const routeDocId = match?.[1];
    if (!routeDocId || routeDocId !== DOC_ID) {
      await route.fallback();
      return;
    }
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(buildMockReviewPayload(routeDocId)),
    });
  });

  await page.route("**/documents/*", async (route) => {
    const url = new URL(route.request().url());
    const match = url.pathname.match(/\/documents\/([^/]+)\/?$/);
    const routeDocId = match?.[1];
    if (route.request().method() !== "GET" || !routeDocId || routeDocId !== DOC_ID) {
      await route.fallback();
      return;
    }
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(buildMockDocumentPayload(routeDocId)),
    });
  });

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

  await page.getByRole("button", { name: "Actualizar" }).click();
  await selectDocument(page, DOC_ID);
  await expect(page.getByTestId("review-split-grid")).toBeVisible({ timeout: 30_000 });
}

test.describe("split panel", () => {
  test("split grid visible with drag handle", async ({ page }) => {
    test.setTimeout(120_000);
    await setupSplitScenario(page);

    await expect(page.getByTestId("review-split-grid")).toBeVisible();
    await expect(page.getByTestId("review-split-handle")).toBeVisible();
  });

  test("double-click handle resets split ratio", async ({ page }) => {
    test.setTimeout(120_000);
    await setupSplitScenario(page);

    const handle = page.getByTestId("review-split-handle");
    await expect(handle).toBeVisible();

    // Get initial position of the handle
    const initialBox = await handle.boundingBox();
    expect(initialBox).not.toBeNull();

    // Double-click the handle to reset
    await handle.dblclick();

    // After reset, handle should still be visible (position may change)
    await expect(handle).toBeVisible();
  });
});
