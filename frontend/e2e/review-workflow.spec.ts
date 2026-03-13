import { expect, test, type Page } from "@playwright/test";

import { buildMockDocumentPayload, buildMockReviewPayload, pinSidebar, selectDocument } from "./helpers";

type ReviewStatus = "IN_REVIEW" | "REVIEWED";

async function openWorkspace(page: Page) {
  await pinSidebar(page);
  await page.goto("/");
  await expect(page.getByTestId("documents-sidebar")).toBeVisible();
}

async function setupReviewWorkflowScenario(
  page: Page,
  initialReviewStatus: ReviewStatus = "IN_REVIEW",
): Promise<void> {
  const documentId = "doc-e2e-review-workflow";
  let reviewStatus: ReviewStatus = initialReviewStatus;
  let reviewedAt: string | null = reviewStatus === "REVIEWED" ? "2026-02-27T10:06:00Z" : null;

  await openWorkspace(page);

  await page.route("**/documents/*/review", async (route) => {
    const url = new URL(route.request().url());
    const match = url.pathname.match(/\/documents\/([^/]+)\/review\/?$/);
    const routeDocumentId = match?.[1];
    if (!routeDocumentId || routeDocumentId !== documentId) {
      await route.fallback();
      return;
    }

    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(
        buildMockReviewPayload(routeDocumentId, {
          reviewStatus,
        }),
      ),
    });
  });

  await page.route("**/documents/*", async (route) => {
    const url = new URL(route.request().url());
    const match = url.pathname.match(/\/documents\/([^/]+)\/?$/);
    const routeDocumentId = match?.[1];
    if (route.request().method() !== "GET" || !routeDocumentId || routeDocumentId !== documentId) {
      await route.fallback();
      return;
    }

    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(
        buildMockDocumentPayload(routeDocumentId, {
          status: "COMPLETED",
          reviewStatus,
          filename: "sample.pdf",
        }),
      ),
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
            document_id: documentId,
            original_filename: "sample.pdf",
            created_at: "2026-02-27T10:00:00Z",
            status: "COMPLETED",
            status_label: "Completado",
            failure_type: null,
            review_status: reviewStatus,
            reviewed_at: reviewedAt,
            reviewed_by: null,
          },
        ],
        limit: 50,
        offset: 0,
        total: 1,
      }),
    });
  });

  await page.route("**/documents/*/reviewed", async (route) => {
    const url = new URL(route.request().url());
    const match = url.pathname.match(/\/documents\/([^/]+)\/reviewed\/?$/);
    const routeDocumentId = match?.[1];
    if (!routeDocumentId || routeDocumentId !== documentId) {
      await route.fallback();
      return;
    }

    const method = route.request().method();
    if (method === "POST") {
      reviewStatus = "REVIEWED";
      reviewedAt = "2026-02-27T10:06:00Z";
    } else if (method === "DELETE") {
      reviewStatus = "IN_REVIEW";
      reviewedAt = null;
    } else {
      await route.fallback();
      return;
    }

    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        document_id: documentId,
        review_status: reviewStatus,
        reviewed_at: reviewedAt,
        reviewed_by: null,
      }),
    });
  });

  await page.getByRole("button", { name: "Actualizar" }).click();
  await selectDocument(page, documentId);
  await expect(page.getByTestId("structured-column-stack")).toBeVisible({ timeout: 30_000 });
}

test.describe("review workflow", () => {
  test("mark as reviewed updates CTA and switches to read-only state", async ({ page }) => {
    test.setTimeout(120_000);
    await setupReviewWorkflowScenario(page, "IN_REVIEW");

    const reviewToggleButton = page.getByTestId("review-toggle-btn");
    await expect(reviewToggleButton).toContainText("Marcar revisado");
    await reviewToggleButton.click();

    await expect(reviewToggleButton).toContainText("Reabrir");
    await expect(page.getByText(/solo lectura/i)).toBeVisible();
    await expect(page.getByText("Revisados")).toBeVisible();
  });

  test("reopen switches CTA back and keeps document editable", async ({ page }) => {
    test.setTimeout(120_000);
    await setupReviewWorkflowScenario(page, "REVIEWED");

    const reviewToggleButton = page.getByTestId("review-toggle-btn");
    await expect(reviewToggleButton).toContainText("Reabrir");
    await reviewToggleButton.click();

    await expect(reviewToggleButton).toContainText("Marcar revisado");
    await expect(page.getByText(/solo lectura/i)).not.toBeVisible();
    await expect(page.getByText("Para revisar")).toBeVisible();
  });
});
