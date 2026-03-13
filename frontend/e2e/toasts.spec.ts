import fs from "node:fs";

import { expect, test, type Page } from "@playwright/test";

import { buildMockDocumentPayload, buildMockReviewPayload, pinSidebar, selectDocument } from "./helpers";

const DOC_ID = "doc-e2e-toasts";
const SAMPLE_PDF_BUFFER = fs.readFileSync("e2e/fixtures/sample.pdf");

async function setupToastScenario(page: Page, reviewStatus: "IN_REVIEW" | "REVIEWED" = "IN_REVIEW") {
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
            review_status: reviewStatus,
            reviewed_at: reviewStatus === "REVIEWED" ? "2026-02-27T10:10:00Z" : null,
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
        buildMockDocumentPayload(DOC_ID, {
          status: "COMPLETED",
          reviewStatus,
          filename: "sample.pdf",
        }),
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
      body: JSON.stringify(
        buildMockReviewPayload(routeDocumentId, {
          reviewStatus,
          fields: [
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
        }),
      ),
    });
  });

  await page.route("**/documents/*/reviewed", async (route) => {
    const url = new URL(route.request().url());
    const match = url.pathname.match(/\/documents\/([^/]+)\/reviewed\/?$/);
    const routeDocumentId = match?.[1];
    if (!routeDocumentId || routeDocumentId !== DOC_ID) {
      await route.fallback();
      return;
    }
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        document_id: DOC_ID,
        review_status: "REVIEWED",
        reviewed_at: "2026-02-27T10:10:00Z",
        reviewed_by: null,
      }),
    });
  });

  await page.getByRole("button", { name: "Actualizar" }).click();
  await selectDocument(page, DOC_ID);
  await expect(page.getByTestId("structured-column-stack")).toBeVisible({ timeout: 30_000 });
}

test.describe("action toasts", () => {
  test("success toast auto-closes around 3.5s", async ({ page }) => {
    test.setTimeout(180_000);
    await setupToastScenario(page, "IN_REVIEW");

    await page.getByTestId("review-toggle-btn").click();
    await expect(page.getByTestId("toast-success")).toBeVisible();
    await expect(page.getByText("Documento marcado como revisado.")).toBeVisible();
    await page.waitForTimeout(4_200);
    await expect(page.getByTestId("toast-success")).toHaveCount(0);
  });

  test("error toast auto-closes slower (~5s)", async ({ page }) => {
    test.setTimeout(180_000);
    await setupToastScenario(page, "REVIEWED");

    await page.getByTestId("field-trigger-core:species").click({ force: true });
    await expect(page.getByTestId("toast-error")).toBeVisible();
    await expect(page.getByText("Documento revisado: edición bloqueada.")).toBeVisible();
    await page.waitForTimeout(4_000);
    await expect(page.getByTestId("toast-error")).toBeVisible();
    await page.waitForTimeout(1_800);
    await expect(page.getByTestId("toast-error")).toHaveCount(0);
  });

  test("manual close toast using X button", async ({ page }) => {
    test.setTimeout(180_000);
    await setupToastScenario(page, "IN_REVIEW");

    await page.getByTestId("field-edit-btn-core:species").click();
    await page.getByTestId("field-edit-save").click();
    await expect(page.getByTestId("toast-info")).toBeVisible();
    await expect(page.getByText("No se han realizado cambios.")).toBeVisible();

    await page.getByRole("button", { name: "Cerrar notificación de acción" }).click();
    await expect(page.getByTestId("toast-info")).toHaveCount(0);
  });
});
