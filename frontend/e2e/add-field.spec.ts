import fs from "node:fs";

import { expect, test, type Page } from "@playwright/test";

import { buildMockDocumentPayload, pinSidebar, selectDocument } from "./helpers";

const DOC_ID = "doc-e2e-add-field";
const SAMPLE_PDF_BUFFER = fs.readFileSync("e2e/fixtures/sample.pdf");

async function setupAddFieldScenario(page: Page, reviewStatus: "IN_REVIEW" | "REVIEWED" = "IN_REVIEW") {
  let ownerNameValue: string | null = null;
  let capturedEditPayload: unknown = null;

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
      body: JSON.stringify({
        document_id: DOC_ID,
        latest_completed_run: {
          run_id: "run-e2e-add-field",
          state: "COMPLETED",
          completed_at: "2026-02-27T10:00:00Z",
          failure_type: null,
        },
        active_interpretation: {
          interpretation_id: "interp-e2e-add-field",
          version_number: 1,
          data: {
            document_id: DOC_ID,
            processing_run_id: "run-e2e-add-field",
            created_at: "2026-02-27T10:00:00Z",
            schema_contract: "visit-grouped-canonical",
            medical_record_view: {
              version: "1.0",
              sections: ["patient", "owner"],
              field_slots: [
                {
                  concept_id: "pet_name",
                  section: "patient",
                  scope: "document",
                  canonical_key: "pet_name",
                },
                {
                  concept_id: "owner_name",
                  section: "owner",
                  scope: "document",
                  canonical_key: "owner_name",
                },
              ],
            },
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
              ...(ownerNameValue
                ? [
                    {
                      field_id: "field-owner-name",
                      key: "owner_name",
                      value: ownerNameValue,
                      value_type: "string",
                      field_candidate_confidence: null,
                      field_mapping_confidence: null,
                      is_critical: false,
                      origin: "human",
                    },
                  ]
                : []),
            ],
            confidence_policy: {
              policy_version: "v1",
              band_cutoffs: { low_max: 0.5, mid_max: 0.75 },
            },
          },
        },
        raw_text_artifact: {
          run_id: "run-e2e-add-field",
          available: true,
        },
        review_status: reviewStatus,
        reviewed_at: reviewStatus === "REVIEWED" ? "2026-02-27T10:10:00Z" : null,
        reviewed_by: null,
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
      changes?: Array<{ op?: string; key?: string; value?: string | null }>;
    };
    const addChange = payload.changes?.find((change) => change.op === "ADD" && change.key === "owner_name");
    if (addChange && typeof addChange.value === "string") {
      ownerNameValue = addChange.value;
    }

    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        run_id: "run-e2e-add-field",
        interpretation_id: "interp-e2e-add-field",
        version_number: 2,
        data: {
          document_id: DOC_ID,
          processing_run_id: "run-e2e-add-field",
          created_at: "2026-02-27T10:00:00Z",
          fields: [
            {
              field_id: "field-pet-name",
              key: "pet_name",
              value: "Luna",
              value_type: "string",
            },
            {
              field_id: "field-owner-name",
              key: "owner_name",
              value: ownerNameValue ?? "",
              value_type: "string",
            },
          ],
        },
      }),
    });
  });

  await page.getByRole("button", { name: "Actualizar" }).click();
  await selectDocument(page, DOC_ID);
  await expect(page.getByTestId("structured-column-stack")).toBeVisible({ timeout: 30_000 });

  return {
    getCapturedEditPayload: () => capturedEditPayload,
  };
}

test.describe("add field", () => {
  test("adds new field with key and value", async ({ page }) => {
    test.setTimeout(180_000);
    const scenario = await setupAddFieldScenario(page, "IN_REVIEW");

    await expect(page.getByTestId("field-trigger-core:owner_name")).toContainText("—");
    await page.getByTestId("field-edit-btn-core:owner_name").click();
    await page.getByTestId("field-edit-input").fill("Fernanda Gomez");
    await page.getByTestId("field-edit-save").click();

    await expect(page.getByText("Valor actualizado correctamente.")).toBeVisible();
    await expect(page.getByTestId("field-trigger-core:owner_name")).toContainText("Fernanda Gomez");
    await expect
      .poll(
        () =>
          scenario.getCapturedEditPayload() as {
            changes?: Array<{ op?: string; key?: string; value?: string; value_type?: string }>;
          },
      )
      .toMatchObject({
        changes: [{ op: "ADD", key: "owner_name", value: "Fernanda Gomez", value_type: "string" }],
      });
  });

  test("editing is blocked on reviewed document and shows toast", async ({ page }) => {
    test.setTimeout(180_000);
    await setupAddFieldScenario(page, "REVIEWED");

    await expect(page.getByText(/solo lectura/i)).toBeVisible();
    await page.getByTestId("field-trigger-core:pet_name").click({ force: true });
    await expect(page.getByText("Documento revisado: edición bloqueada.")).toBeVisible();
    await expect(page.getByTestId("field-edit-dialog")).toHaveCount(0);
  });
});
