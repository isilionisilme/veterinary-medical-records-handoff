import { expect, test, type Page } from "@playwright/test";

import {
  buildMockDocumentPayload,
  buildMockReviewPayload,
  pinSidebar,
  selectDocument,
} from "./helpers";

type EditScenario = {
  getCapturedEditPayload: () => unknown;
};

async function openWorkspace(page: Page) {
  await pinSidebar(page);
  await page.goto("/");
  await expect(page.getByTestId("documents-sidebar")).toBeVisible();
}

async function setupFieldEditingScenario(page: Page): Promise<EditScenario> {
  const documentId = "doc-e2e-field-editing";
  let speciesValue = "canino";
  let versionNumber = 1;
  let capturedEditPayload: unknown = null;

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
          versionNumber,
          fields: [
            {
              field_id: "field-species-e2e",
              key: "species",
              value: speciesValue,
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
      body: JSON.stringify(buildMockDocumentPayload(routeDocumentId, { status: "COMPLETED" })),
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

  await page.route("**/runs/*/interpretations", async (route) => {
    if (route.request().method() !== "POST") {
      await route.fallback();
      return;
    }

    capturedEditPayload = route.request().postDataJSON();
    const payload = capturedEditPayload as {
      changes?: Array<{ value?: string | null }>;
    };
    const nextValue = payload.changes?.[0]?.value;
    if (typeof nextValue === "string") {
      speciesValue = nextValue;
    }
    versionNumber += 1;

    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        run_id: `run-e2e-${documentId}`,
        interpretation_id: `interp-e2e-${documentId}`,
        version_number: versionNumber,
        data: buildMockReviewPayload(documentId, {
          versionNumber,
          fields: [
            {
              field_id: "field-species-e2e",
              key: "species",
              value: speciesValue,
              value_type: "string",
              field_candidate_confidence: 0.95,
              field_mapping_confidence: 0.95,
              is_critical: false,
              origin: "machine",
            },
          ],
        }).active_interpretation.data,
      }),
    });
  });

  await page.getByRole("button", { name: "Actualizar" }).click();
  await selectDocument(page, documentId);
  await expect(page.getByTestId("structured-column-stack")).toBeVisible({ timeout: 30_000 });
  await expect(page.getByTestId("field-trigger-core:species")).toContainText(/canino/i);

  return {
    getCapturedEditPayload: () => capturedEditPayload,
  };
}

test.describe("field editing workflow", () => {
  test("opens edit dialog with pre-populated field value", async ({ page }) => {
    test.setTimeout(120_000);
    await setupFieldEditingScenario(page);

    await page.getByTestId("field-edit-btn-core:species").click();
    await expect(page.getByTestId("field-edit-dialog")).toBeVisible();
    await expect(page.getByRole("heading", { name: /Editar/i })).toBeVisible();
    await expect(page.getByTestId("field-edit-input")).toHaveValue("canino");
  });

  test("saves edited value, closes dialog, updates field and shows toast", async ({ page }) => {
    test.setTimeout(120_000);
    const scenario = await setupFieldEditingScenario(page);

    await page.getByTestId("field-edit-btn-core:species").click();
    await expect(page.getByTestId("field-edit-dialog")).toBeVisible();

    await page.getByTestId("field-edit-input").selectOption("felino");
    await page.getByTestId("field-edit-save").click();

    await expect(page.getByTestId("field-edit-dialog")).not.toBeVisible();
    await expect(page.getByTestId("field-trigger-core:species")).toContainText(/felino/i);
    await expect(page.getByText("Valor actualizado correctamente.")).toBeVisible();

    await expect.poll(() => scenario.getCapturedEditPayload()).not.toBeNull();
    await expect
      .poll(() => scenario.getCapturedEditPayload() as { base_version_number?: number })
      .toMatchObject({ base_version_number: 1 });
    await expect
      .poll(
        () =>
          scenario.getCapturedEditPayload() as {
            changes?: Array<{ op?: string; field_id?: string; value?: string; value_type?: string }>;
          },
      )
      .toMatchObject({
        changes: [
          {
            op: "UPDATE",
            field_id: "field-species-e2e",
            value: "felino",
            value_type: "string",
          },
        ],
      });
  });

  test("cancels edit and keeps original value unchanged", async ({ page }) => {
    test.setTimeout(120_000);
    const scenario = await setupFieldEditingScenario(page);

    await page.getByTestId("field-edit-btn-core:species").click();
    await expect(page.getByTestId("field-edit-dialog")).toBeVisible();

    await page.getByTestId("field-edit-input").selectOption("felino");
    await page.getByTestId("field-edit-cancel").click();

    await expect(page.getByTestId("field-edit-dialog")).not.toBeVisible();
    await expect(page.getByTestId("field-trigger-core:species")).toContainText(/canino/i);
    await expect(scenario.getCapturedEditPayload()).toBeNull();
  });
});
