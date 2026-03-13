import fs from "node:fs";

import { expect, test, type Page } from "@playwright/test";

import { buildMockDocumentPayload, pinSidebar, selectDocument } from "./helpers";

const DOC_ID = "doc-e2e-visit-grouping";
const SAMPLE_PDF_BUFFER = fs.readFileSync("e2e/fixtures/sample.pdf");

async function setupVisitGroupingScenario(page: Page): Promise<void> {
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
      body: JSON.stringify(
        buildMockDocumentPayload(DOC_ID, {
          status: "COMPLETED",
          reviewStatus: "IN_REVIEW",
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
          run_id: "run-e2e-visit-grouping",
          state: "COMPLETED",
          completed_at: "2026-02-27T10:00:00Z",
          failure_type: null,
        },
        active_interpretation: {
          interpretation_id: "interp-e2e-visit-grouping",
          version_number: 1,
          data: {
            document_id: DOC_ID,
            processing_run_id: "run-e2e-visit-grouping",
            created_at: "2026-02-27T10:00:00Z",
            schema_contract: "visit-grouped-canonical",
            medical_record_view: {
              version: "1.0",
              sections: ["visits", "patient", "owner"],
              field_slots: [
                {
                  concept_id: "visit_date",
                  section: "visits",
                  scope: "visit",
                  canonical_key: "visit_date",
                },
                {
                  concept_id: "reason_for_visit",
                  section: "visits",
                  scope: "visit",
                  canonical_key: "reason_for_visit",
                },
                {
                  concept_id: "diagnosis",
                  section: "visits",
                  scope: "visit",
                  canonical_key: "diagnosis",
                },
              ],
            },
            fields: [
              {
                field_id: "visit-1-diagnosis",
                key: "diagnosis",
                value: "Gastritis",
                value_type: "string",
                visit_group_id: "visit-1",
                scope: "visit",
                section: "visits",
                field_candidate_confidence: 0.86,
                field_mapping_confidence: 0.86,
                is_critical: false,
                origin: "machine",
              },
              {
                field_id: "visit-2-diagnosis",
                key: "diagnosis",
                value: "Control general",
                value_type: "string",
                visit_group_id: "visit-2",
                scope: "visit",
                section: "visits",
                field_candidate_confidence: 0.93,
                field_mapping_confidence: 0.93,
                is_critical: false,
                origin: "machine",
              },
              {
                field_id: "visit-unassigned-symptoms",
                key: "symptoms",
                value: "No asociadas",
                value_type: "string",
                scope: "visit",
                section: "visits",
                field_candidate_confidence: 0.6,
                field_mapping_confidence: 0.6,
                is_critical: false,
                origin: "machine",
              },
            ],
            visits: [
              {
                visit_id: "visit-1",
                visit_date: "2026-02-10",
                admission_date: null,
                discharge_date: null,
                reason_for_visit: "Ingreso",
                fields: [
                  {
                    field_id: "visit-1-diagnosis",
                    key: "diagnosis",
                    value: "Gastritis",
                    value_type: "string",
                    scope: "visit",
                    section: "visits",
                  },
                ],
              },
              {
                visit_id: "visit-2",
                visit_date: "2026-02-20",
                admission_date: null,
                discharge_date: null,
                reason_for_visit: "Control",
                fields: [
                  {
                    field_id: "visit-2-diagnosis",
                    key: "diagnosis",
                    value: "Control general",
                    value_type: "string",
                    scope: "visit",
                    section: "visits",
                  },
                ],
              },
            ],
            confidence_policy: {
              policy_version: "v1",
              band_cutoffs: { low_max: 0.5, mid_max: 0.75 },
            },
          },
        },
        raw_text_artifact: {
          run_id: "run-e2e-visit-grouping",
          available: true,
        },
        review_status: "IN_REVIEW",
        reviewed_at: null,
        reviewed_by: null,
      }),
    });
  });

  await page.getByRole("button", { name: "Actualizar" }).click();
  await selectDocument(page, DOC_ID);
  await expect(page.getByTestId("structured-column-stack")).toBeVisible({ timeout: 30_000 });
}

test.describe("visit grouping", () => {
  test.beforeEach(async ({ page }) => {
    test.setTimeout(180_000);
    await setupVisitGroupingScenario(page);
  });

  test("visit episodes are grouped and numbered", async ({ page }) => {
    await expect(page.getByTestId("visit-episode-2")).toBeVisible();
    await expect(page.getByTestId("visit-episode-1")).toBeVisible();
    await expect(page.getByText("Visita 2")).toBeVisible();
    await expect(page.getByText("Visita 1")).toBeVisible();
  });

  test("each visit shows metadata labels for date and reason", async ({ page }) => {
    await expect(page.getByTestId("visit-episode-2").getByText("Con fecha")).toBeVisible();
    await expect(page.getByTestId("visit-episode-2").getByText("Con motivo")).toBeVisible();
    await expect(page.getByTestId("visit-episode-2").getByText("20/2/2026").first()).toBeVisible();
    await expect(page.getByTestId("visit-episode-1").getByText("10/2/2026").first()).toBeVisible();
  });

  test("unassigned group is visible for orphan visit-scoped fields", async ({ page }) => {
    await expect(page.getByTestId("visit-unassigned-group")).toBeVisible();
    await expect(page.getByText("No asociadas a visita")).toBeVisible();
    await expect(page.getByTestId("visits-unassigned-hint")).toBeVisible();
  });
});
