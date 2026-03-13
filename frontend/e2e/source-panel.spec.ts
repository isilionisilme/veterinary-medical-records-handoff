import fs from "node:fs";

import { expect, test } from "@playwright/test";

import { buildMockDocumentPayload, buildMockReviewPayload, pinSidebar, selectDocument } from "./helpers";

const DOC_ID = "doc-e2e-source-panel";
const SAMPLE_PDF_BUFFER = fs.readFileSync("e2e/fixtures/sample.pdf");

async function setupSourceEvidenceScenario(page: import("@playwright/test").Page): Promise<void> {
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
      body: JSON.stringify(buildMockDocumentPayload(DOC_ID, { status: "COMPLETED" })),
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
          fields: [
            {
              field_id: "field-pet-name",
              key: "pet_name",
              value: "Luna",
              value_type: "string",
              field_candidate_confidence: 0.91,
              field_mapping_confidence: 0.91,
              is_critical: false,
              origin: "machine",
              evidence: { page: 2, snippet: "Paciente: Luna" },
            },
          ],
        }),
      ),
    });
  });

  await page.getByRole("button", { name: "Actualizar" }).click();
  await selectDocument(page, DOC_ID);
  await expect(page.getByTestId("structured-column-stack")).toBeVisible({ timeout: 30_000 });
}

test.describe("source panel baseline interactions", () => {
  test("field trigger with evidence is visible and selectable", async ({ page }) => {
    test.setTimeout(180_000);
    await setupSourceEvidenceScenario(page);
    const trigger = page.getByTestId("field-trigger-core:pet_name");
    await expect(trigger).toBeVisible();
    await trigger.click();
    await expect(trigger).toHaveAttribute("aria-disabled", "false");
  });

  test("field edit affordance is available on source-backed field", async ({ page }) => {
    test.setTimeout(180_000);
    await setupSourceEvidenceScenario(page);
    await expect(page.getByTestId("field-edit-btn-core:pet_name")).toBeVisible();
  });

  test("review layout remains stable after selecting source-backed field", async ({ page }) => {
    test.setTimeout(180_000);
    await setupSourceEvidenceScenario(page);
    await page.getByTestId("field-trigger-core:pet_name").click();
    await expect(page.getByTestId("review-split-grid")).toBeVisible();
    await expect(page.getByTestId("review-split-handle")).toBeVisible();
    await expect(page.getByTestId("pdf-toolbar-shell")).toBeVisible();
  });
});
