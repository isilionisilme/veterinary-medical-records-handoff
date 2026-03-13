import fs from "node:fs";

import { expect, test, type Page } from "@playwright/test";

import { buildMockDocumentPayload, buildMockReviewPayload, pinSidebar, selectDocument } from "./helpers";

const DOC_ID = "doc-e2e-structured-filters";
const SAMPLE_PDF_BUFFER = fs.readFileSync("e2e/fixtures/sample.pdf");

async function setupStructuredFiltersScenario(page: Page): Promise<void> {
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
              field_candidate_confidence: 0.95,
              field_mapping_confidence: 0.95,
              is_critical: true,
              origin: "machine",
            },
            {
              field_id: "field-species",
              key: "species",
              value: "canino",
              value_type: "string",
              field_candidate_confidence: 0.3,
              field_mapping_confidence: 0.3,
              is_critical: false,
              origin: "machine",
            },
            {
              field_id: "field-owner-name",
              key: "owner_name",
              value: "Fernanda",
              value_type: "string",
              field_candidate_confidence: 0.7,
              field_mapping_confidence: 0.7,
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
  });

  await page.getByRole("button", { name: "Actualizar" }).click();
  await selectDocument(page, DOC_ID);
  await expect(page.getByTestId("structured-column-stack")).toBeVisible({ timeout: 30_000 });
}

test.describe("structured data filters", () => {
  test.beforeEach(async ({ page }) => {
    test.setTimeout(180_000);
    await setupStructuredFiltersScenario(page);
  });

  test("search by text filters results", async ({ page }) => {
    await page.getByLabel("Buscar en datos extraídos").fill("Luna");
    await expect(page.getByTestId("field-trigger-core:pet_name")).toBeVisible();
    await expect(page.getByTestId("field-trigger-core:species")).toHaveCount(0);
  });

  test("clear search restores all fields", async ({ page }) => {
    await page.getByLabel("Buscar en datos extraídos").fill("Luna");
    await page.getByRole("button", { name: "Limpiar búsqueda" }).click();
    await expect(page.getByTestId("field-trigger-core:pet_name")).toBeVisible();
    await expect(page.getByTestId("field-trigger-core:species")).toBeVisible();
    await expect(page.getByTestId("field-trigger-core:microchip_id")).toBeVisible();
  });

  test("filter by low confidence", async ({ page }) => {
    await page.getByLabel(/^Baja \(/).click();
    await expect(page.getByTestId("field-trigger-core:species")).toBeVisible();
    await expect(page.getByTestId("field-trigger-core:pet_name")).toHaveCount(0);
  });

  test("filter critical only", async ({ page }) => {
    await page.getByLabel("Mostrar solo campos críticos").click();
    await expect(page.getByTestId("field-trigger-core:pet_name")).toBeVisible();
    await expect(page.getByTestId("field-trigger-core:clinic_name")).toHaveCount(0);
  });

  test("filter with value and empty only", async ({ page }) => {
    await page.getByLabel("Mostrar solo campos no vacíos").click();
    await expect(page.getByTestId("field-trigger-core:pet_name")).toBeVisible();
    await expect(page.getByTestId("field-trigger-core:clinic_name")).toHaveCount(0);

    await page.getByRole("button", { name: "Limpiar filtros" }).click();
    await page.getByLabel("Mostrar solo campos vacíos").click();
    await expect(page.getByTestId("field-trigger-core:clinic_name")).toBeVisible();
    await expect(page.getByTestId("field-trigger-core:pet_name")).toHaveCount(0);
  });

  test("reset filters restores full view", async ({ page }) => {
    await page.getByLabel("Buscar en datos extraídos").fill("Luna");
    await page.getByLabel("Mostrar solo campos críticos").click();
    await page.getByRole("button", { name: "Limpiar filtros" }).click();
    await expect(page.getByTestId("field-trigger-core:pet_name")).toBeVisible();
    await expect(page.getByTestId("field-trigger-core:species")).toBeVisible();
    await expect(page.getByTestId("field-trigger-core:owner_name")).toBeVisible();
    await expect(page.getByTestId("field-trigger-core:clinic_name")).toBeVisible();
  });
});
