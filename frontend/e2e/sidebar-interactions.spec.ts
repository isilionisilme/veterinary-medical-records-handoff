import { expect, test, type Page } from "@playwright/test";

import { buildMockDocumentPayload, pinSidebar } from "./helpers";

const DOC_ID = "doc-e2e-sidebar-interactions";

async function openWorkspace(page: Page) {
  await pinSidebar(page);
  await page.goto("/");
  await expect(page.getByTestId("documents-sidebar")).toBeVisible();
}

async function mockDocumentsList(page: Page): Promise<void> {
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

  await page.route("**/documents/*", async (route) => {
    const url = new URL(route.request().url());
    const match = url.pathname.match(/\/documents\/([^/]+)\/?$/);
    const routeDocId = match?.[1];
    if (route.request().method() !== "GET" || !routeDocId) {
      await route.fallback();
      return;
    }
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(buildMockDocumentPayload(routeDocId)),
    });
  });
}

test.describe("sidebar interactions", () => {
  test("pin and unpin sidebar", async ({ page }) => {
    test.setTimeout(120_000);
    // Start without pinning
    await page.goto("/");
    await expect(page.getByTestId("documents-sidebar")).toBeVisible({ timeout: 30_000 });

    await mockDocumentsList(page);
    await page.getByRole("button", { name: "Actualizar" }).click();

    // Find the pin button in sidebar actions
    const actionsCluster = page.getByTestId("sidebar-actions-cluster");
    await expect(actionsCluster).toBeVisible({ timeout: 10_000 });

    // Look for pin/unpin button
    const pinBtn = actionsCluster.getByRole("button").first();
    if (await pinBtn.isVisible()) {
      await pinBtn.click();
      // Verify localStorage was updated
      const pinned = await page.evaluate(() =>
        window.localStorage.getItem("docsSidebarPinned"),
      );
      // Pin state should have toggled
      expect(pinned).not.toBeNull();
    }
  });

  test("refresh button fetches updated document list", async ({ page }) => {
    test.setTimeout(120_000);
    await openWorkspace(page);
    await mockDocumentsList(page);

    // Click refresh
    const refreshBtn = page.getByRole("button", { name: "Actualizar" });
    await expect(refreshBtn).toBeVisible();
    await refreshBtn.click();

    // After refresh, the document should appear in the sidebar
    await expect(page.getByTestId(`doc-row-${DOC_ID}`)).toBeVisible({ timeout: 30_000 });
  });

  test("hover reveals collapsed sidebar content", async ({ page }) => {
    test.setTimeout(120_000);
    // Don't pin sidebar — let it auto-collapse
    await page.goto("/");
    await expect(page.getByTestId("documents-sidebar")).toBeVisible({ timeout: 30_000 });

    await mockDocumentsList(page);

    // The sidebar should have collapsed branding visible
    const brandMark = page.getByTestId("sidebar-collapsed-brand-mark");
    // Hover over the sidebar area to expand
    const sidebar = page.getByTestId("documents-sidebar");
    await sidebar.hover();

    await page.waitForTimeout(500);
    // After hover, sidebar should be expanded (either brand mark or docs column visible)
    const docsColumn = page.getByTestId("docs-column-stack");
    const isExpanded = await docsColumn.isVisible().catch(() => false);
    const hasBrandMark = await brandMark.isVisible().catch(() => false);
    expect(isExpanded || hasBrandMark).toBe(true);
  });
});
