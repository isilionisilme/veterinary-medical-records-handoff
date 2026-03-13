import fs from "node:fs";

import { expect, test, type Page } from "@playwright/test";

import {
  buildMockDocumentPayload,
  buildMockReviewPayload,
  pinSidebar,
  selectDocument,
} from "./helpers";

const MOCK_RAW_TEXT = "Paciente: Luna\nEspecie: Canino\nDiagnostico: Gastroenteritis";
const MOCK_DOCUMENT_ID = "doc-e2e-raw-text";
const MOCK_RUN_ID = "run-e2e-raw-text";
const SAMPLE_PDF_BUFFER = fs.readFileSync("e2e/fixtures/sample.pdf");

async function openRawTextTabWithMock(page: Page): Promise<void> {
  await pinSidebar(page);
  await page.addInitScript(() => {
    Object.defineProperty(window.navigator, "clipboard", {
      configurable: true,
      value: {
        writeText: async () => Promise.resolve(),
      },
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
            document_id: MOCK_DOCUMENT_ID,
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

  await page.route("**/documents/*/review", async (route) => {
    const url = new URL(route.request().url());
    const match = url.pathname.match(/\/documents\/([^/]+)\/review\/?$/);
    const routeDocumentId = match?.[1];
    if (!routeDocumentId || routeDocumentId !== MOCK_DOCUMENT_ID) {
      await route.fallback();
      return;
    }
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(buildMockReviewPayload(MOCK_DOCUMENT_ID)),
    });
  });

  await page.route("**/documents/*/download**", async (route) => {
    const url = new URL(route.request().url());
    const match = url.pathname.match(/\/documents\/([^/]+)\/download\/?$/);
    const routeDocumentId = match?.[1];
    if (!routeDocumentId || routeDocumentId !== MOCK_DOCUMENT_ID) {
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
    if (route.request().method() !== "GET" || !routeDocumentId || routeDocumentId !== MOCK_DOCUMENT_ID) {
      await route.fallback();
      return;
    }
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(
        buildMockDocumentPayload(MOCK_DOCUMENT_ID, {
          status: "COMPLETED",
          reviewStatus: "IN_REVIEW",
          filename: "sample.pdf",
        }),
      ),
    });
  });

  await page.route("**/runs/*/artifacts/raw-text", async (route) => {
    if (route.request().method() !== "GET") {
      await route.fallback();
      return;
    }
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        run_id: MOCK_RUN_ID,
        artifact_type: "raw_text",
        content_type: "text/plain; charset=utf-8",
        text: MOCK_RAW_TEXT,
      }),
    });
  });

  await page.goto("/");
  await expect(page.getByTestId("documents-sidebar")).toBeVisible();
  await page.getByRole("button", { name: "Actualizar" }).click();
  await selectDocument(page, MOCK_DOCUMENT_ID);

  await page.getByTestId("viewer-tab-raw-text").click();
  await expect(page.getByTestId("raw-text-search-input")).toBeEnabled({ timeout: 30_000 });
}

test.describe("raw text tab", () => {
  test.beforeEach(async ({ page }) => {
    test.setTimeout(180_000);
    await openRawTextTabWithMock(page);
  });

  test("shows extracted text", async ({ page }) => {
    await expect(page.getByText("Paciente: Luna")).toBeVisible();
  });

  test("search existing text shows Coincidencia encontrada", async ({ page }) => {
    await page.getByTestId("raw-text-search-input").fill("Luna");
    await page.getByRole("button", { name: "Buscar" }).click();
    await expect(page.getByText("Coincidencia encontrada.")).toBeVisible();
  });

  test("search nonexistent text shows no matches", async ({ page }) => {
    await page.getByTestId("raw-text-search-input").fill("texto-inexistente");
    await page.getByRole("button", { name: "Buscar" }).click();
    await expect(page.getByText("No se encontraron coincidencias.")).toBeVisible();
  });

  test("copy all text shows copied feedback", async ({ page }) => {
    await page.getByTestId("raw-text-copy").click();
    await expect(page.getByText("Texto copiado.")).toBeVisible();
    await expect(page.getByTestId("raw-text-copy")).toHaveText("Copiado");
  });

  test("download text file triggers .txt download", async ({ page }) => {
    const downloadPromise = page.waitForEvent("download");
    await page.getByTestId("raw-text-download").click();
    const download = await downloadPromise;
    expect(download.suggestedFilename()).toBe("texto-extraido.txt");
  });
});
