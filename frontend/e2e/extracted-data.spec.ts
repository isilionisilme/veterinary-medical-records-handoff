import { expect, test, type Page } from "@playwright/test";

import {
  buildMockDocumentPayload,
  buildMockReviewPayload,
  pinSidebar,
  selectDocument,
  uploadAndWaitForProcessing,
} from "./helpers";

async function openWorkspace(page: Page) {
  await pinSidebar(page);
  await page.goto("/");
  await expect(page.getByTestId("documents-sidebar")).toBeVisible();
}

test.describe("extracted data panel", () => {
  test.describe.configure({ mode: "serial" });
  let sharedDocumentId: string | null = null;

  test.beforeEach(async ({ page }) => {
    test.setTimeout(120_000);

    await openWorkspace(page);
    if (!sharedDocumentId) {
      sharedDocumentId = await uploadAndWaitForProcessing(page);
    } else {
      await expect(page.getByTestId(`doc-row-${sharedDocumentId}`)).toBeVisible({ timeout: 90_000 });
    }

    await page.route("**/documents/*/review", async (route) => {
      const url = new URL(route.request().url());
      const match = url.pathname.match(/\/documents\/([^/]+)\/review$/);
      const routeDocumentId = match?.[1];
      if (routeDocumentId) {
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
                },
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
                {
                  field_id: "field-clinic-name",
                  key: "clinic_name",
                  value: null,
                  value_type: "string",
                  field_candidate_confidence: null,
                  field_mapping_confidence: null,
                  is_critical: false,
                  origin: "machine",
                },
              ],
            }),
          ),
        });
        return;
      }
      await route.fallback();
    });

    await page.route("**/documents/*", async (route) => {
      const url = new URL(route.request().url());
      const match = url.pathname.match(/\/documents\/([^/]+)$/);
      const routeDocumentId = match?.[1];
      if (route.request().method() === "GET" && routeDocumentId) {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify(buildMockDocumentPayload(routeDocumentId, { status: "COMPLETED" })),
        });
        return;
      }
      await route.fallback();
    });
    await page.route("**/documents?*", async (route) => {
      if (!sharedDocumentId || route.request().method() !== "GET") {
        await route.fallback();
        return;
      }
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          items: [
            {
              document_id: sharedDocumentId,
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
    await selectDocument(page, sharedDocumentId);
    await expect(page.getByTestId("structured-column-stack")).toBeVisible({ timeout: 60_000 });
  });

  test("shows extracted data panel and at least one extracted field", async ({ page }) => {
    await expect(page.getByText("Datos extraídos")).toBeVisible();
    const extractedFieldTriggers = page.locator('[data-testid^="field-trigger-"]');
    await expect(extractedFieldTriggers.first()).toBeVisible();
    expect(await extractedFieldTriggers.count()).toBeGreaterThan(0);
  });

  test("shows formatted values and placeholder for missing fields", async ({ page }) => {
    const speciesField = page.getByTestId("field-trigger-core:species");
    await expect(speciesField).toBeVisible();
    const speciesText = (await speciesField.textContent())?.trim() ?? "";
    expect(speciesText.length).toBeGreaterThan(1);

    const missingValueFields = page.locator('[data-testid^="field-trigger-"]', { hasText: "—" });
    expect(await missingValueFields.count()).toBeGreaterThan(0);
  });

  test("shows confidence indicators and field-count summary chips", async ({ page }) => {
    const confidenceIndicators = page.locator('[data-testid^="confidence-indicator-"]');
    await expect(confidenceIndicators.first()).toBeVisible();
    expect(await confidenceIndicators.count()).toBeGreaterThan(0);

    await expect(page.locator('[aria-label^="Baja ("]')).toBeVisible();
    await expect(page.locator('[aria-label^="Media ("]')).toBeVisible();
    await expect(page.locator('[aria-label^="Alta ("]')).toBeVisible();
    await expect(page.locator('[aria-label^="Sin confianza ("]')).toBeVisible();
  });
});
