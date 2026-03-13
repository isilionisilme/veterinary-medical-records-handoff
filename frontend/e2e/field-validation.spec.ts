import fs from "node:fs";

import { expect, test, type Page } from "@playwright/test";

import { buildMockDocumentPayload, buildMockReviewPayload, pinSidebar, selectDocument } from "./helpers";

const DOC_ID = "doc-e2e-field-validation";
const SAMPLE_PDF_BUFFER = fs.readFileSync("e2e/fixtures/sample.pdf");

async function setupFieldValidationScenario(page: Page): Promise<void> {
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
              field_id: "field-microchip",
              key: "microchip_id",
              value: "123456789",
              value_type: "string",
              field_candidate_confidence: 0.8,
              field_mapping_confidence: 0.8,
              is_critical: true,
              origin: "machine",
            },
            {
              field_id: "field-sex",
              key: "sex",
              value: "macho",
              value_type: "string",
              field_candidate_confidence: 0.9,
              field_mapping_confidence: 0.9,
              is_critical: false,
              origin: "machine",
            },
            {
              field_id: "field-species",
              key: "species",
              value: "canino",
              value_type: "string",
              field_candidate_confidence: 0.9,
              field_mapping_confidence: 0.9,
              is_critical: false,
              origin: "machine",
            },
            {
              field_id: "field-weight",
              key: "weight",
              value: "12.5",
              value_type: "number",
              field_candidate_confidence: 0.7,
              field_mapping_confidence: 0.7,
              is_critical: false,
              origin: "machine",
            },
            {
              field_id: "field-dob",
              key: "dob",
              value: "2026-02-27",
              value_type: "date",
              field_candidate_confidence: 0.7,
              field_mapping_confidence: 0.7,
              is_critical: false,
              origin: "machine",
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

test.describe("field validation", () => {
  test.beforeEach(async ({ page }) => {
    test.setTimeout(180_000);
    await setupFieldValidationScenario(page);
  });

  test("microchip invalid format shows validation error", async ({ page }) => {
    await page.getByTestId("field-edit-btn-core:microchip_id").click();
    await page.getByTestId("field-edit-input").fill("abc");
    await expect(page.getByText("Introduce entre 9 y 15 dígitos.")).toBeVisible();
    await expect(page.getByTestId("field-edit-save")).toBeDisabled();
  });

  test("sex dropdown uses canonical options", async ({ page }) => {
    await page.getByTestId("field-edit-btn-core:sex").click();
    const input = page.getByTestId("field-edit-input");
    await expect(input).toBeVisible();
    const optionTexts = await input.locator("option").allTextContents();
    expect(optionTexts).toContain("Macho");
    expect(optionTexts).toContain("Hembra");
  });

  test("species dropdown uses canonical options", async ({ page }) => {
    await page.getByTestId("field-edit-btn-core:species").click();
    const input = page.getByTestId("field-edit-input");
    await expect(input).toBeVisible();
    const optionTexts = await input.locator("option").allTextContents();
    expect(optionTexts).toContain("Canino");
    expect(optionTexts).toContain("Felino");
  });

  test("weight rejects non-numeric value", async ({ page }) => {
    await page.getByTestId("field-edit-btn-core:weight").click();
    await page.getByTestId("field-edit-input").fill("abc");
    await expect(page.getByText("Introduce un peso entre 0,5 y 120 kg.")).toBeVisible();
    await expect(page.getByTestId("field-edit-save")).toBeDisabled();
  });

  test("date rejects invalid format", async ({ page }) => {
    await page.getByTestId("field-edit-btn-core:dob").click();
    await page.getByTestId("field-edit-input").fill("99/99/9999");
    await expect(page.getByText("Formato no válido. Usa dd/mm/aaaa o aaaa-mm-dd.")).toBeVisible();
    await expect(page.getByTestId("field-edit-save")).toBeDisabled();
  });
});
