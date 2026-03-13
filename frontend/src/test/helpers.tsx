import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { expect, vi } from "vitest";

import { App } from "../App";
import { registerConsoleSuppression } from "./consoleSuppressions";

export function renderApp() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>,
  );
}

export async function withDesktopHoverMatchMedia(run: () => Promise<void> | void) {
  const originalMatchMedia = window.matchMedia;
  Object.defineProperty(window, "matchMedia", {
    configurable: true,
    writable: true,
    value: vi.fn((query: string) => ({
      matches: query.includes("(min-width: 1024px)") || query.includes("(hover: hover)"),
      media: query,
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    })),
  });

  try {
    await run();
  } finally {
    Object.defineProperty(window, "matchMedia", {
      configurable: true,
      writable: true,
      value: originalMatchMedia,
    });
  }
}

export function createDataTransfer(file: File): DataTransfer {
  return {
    files: [file],
    items: [{ kind: "file", type: file.type }],
    types: ["Files"],
  } as unknown as DataTransfer;
}

export async function waitForStructuredDataReady() {
  await waitFor(() => {
    expect(screen.queryByTestId("review-core-skeleton")).toBeNull();
  });
}

export function clickPetNameField() {
  const indicator = screen.getByTestId("confidence-indicator-core:pet_name");
  const fieldCard = indicator.closest("article");
  expect(fieldCard).not.toBeNull();
  const trigger = (fieldCard as HTMLElement).querySelector('[role="button"]');
  expect(trigger).not.toBeNull();
  fireEvent.click(trigger as HTMLElement);
}

export async function openReadyDocumentAndGetPanel() {
  fireEvent.click(await screen.findByRole("button", { name: /ready\.pdf/i }));
  await screen.findByRole("heading", { name: /Datos extraídos/i });
  await waitForStructuredDataReady();
  return screen.getByTestId("right-panel-scroll");
}

export function parseCountFromAriaLabel(element: HTMLElement): number {
  return Number(element.getAttribute("aria-label")?.match(/\((\d+)\)/)?.[1] ?? "0");
}

export function getConfidenceSummaryCounts() {
  const lowButton = screen.getByRole("button", { name: /^Baja \(\d+\)$/i });
  const mediumButton = screen.getByRole("button", { name: /^Media \(\d+\)$/i });
  const highButton = screen.getByRole("button", { name: /^Alta \(\d+\)$/i });
  const unknownButton = screen.getByRole("button", { name: /^Sin confianza \(\d+\)$/i });

  return {
    low: parseCountFromAriaLabel(lowButton),
    medium: parseCountFromAriaLabel(mediumButton),
    high: parseCountFromAriaLabel(highButton),
    unknown: parseCountFromAriaLabel(unknownButton),
    unknownButton,
  };
}

export type CanonicalUs44FetchMockOptions = {
  schemaContract?: string;
  fieldSlots?: Array<Record<string, unknown>>;
  fields?: Array<Record<string, unknown>>;
  visits?: Array<Record<string, unknown>>;
  otherFields?: Array<Record<string, unknown>>;
  confidencePolicy?: Record<string, unknown>;
};

export function installCanonicalUs44FetchMock(options?: CanonicalUs44FetchMockOptions) {
  globalThis.fetch = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
    const url = input.toString();
    const method = (init?.method ?? "GET").toUpperCase();

    if (url.includes("/documents?") && method === "GET") {
      return new Response(
        JSON.stringify({
          items: [
            {
              document_id: "doc-canonical",
              original_filename: "ready.pdf",
              created_at: "2026-02-10T10:00:00Z",
              status: "COMPLETED",
              status_label: "Listo",
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
        { status: 200 },
      );
    }

    if (url.match(/\/documents\/doc-canonical$/) && method === "GET") {
      return new Response(
        JSON.stringify({
          document_id: "doc-canonical",
          original_filename: "ready.pdf",
          content_type: "application/pdf",
          file_size: 10,
          created_at: "2026-02-10T10:00:00Z",
          updated_at: "2026-02-10T10:00:00Z",
          status: "COMPLETED",
          status_message: "Completed",
          failure_type: null,
          review_status: "IN_REVIEW",
          reviewed_at: null,
          reviewed_by: null,
          latest_run: { run_id: "run-doc-canonical", state: "COMPLETED", failure_type: null },
        }),
        { status: 200 },
      );
    }

    if (url.match(/\/documents\/doc-canonical\/review$/) && method === "GET") {
      return new Response(
        JSON.stringify({
          document_id: "doc-canonical",
          latest_completed_run: {
            run_id: "run-doc-canonical",
            state: "COMPLETED",
            completed_at: "2026-02-10T10:00:00Z",
            failure_type: null,
          },
          active_interpretation: {
            interpretation_id: "interp-doc-canonical",
            version_number: 1,
            data: {
              document_id: "doc-canonical",
              processing_run_id: "run-doc-canonical",
              created_at: "2026-02-10T10:00:00Z",
              schema_contract: options?.schemaContract ?? "visit-grouped-canonical",
              medical_record_view: {
                version: "mvp-1",
                sections: ["clinic", "patient", "owner", "visits", "notes", "other", "report_info"],
                field_slots: options?.fieldSlots ?? [
                  {
                    concept_id: "clinic.name",
                    section: "clinic",
                    scope: "document",
                    canonical_key: "clinic_name",
                    label_key: "clinic_name",
                  },
                  {
                    concept_id: "clinic.nhc",
                    section: "clinic",
                    scope: "document",
                    canonical_key: "nhc",
                    aliases: ["medical_record_number"],
                    label_key: "nhc",
                  },
                  {
                    concept_id: "patient.pet_name",
                    section: "patient",
                    scope: "document",
                    canonical_key: "pet_name",
                    label_key: "pet_name",
                  },
                  {
                    concept_id: "owner.name",
                    section: "owner",
                    scope: "document",
                    canonical_key: "owner_name",
                    label_key: "owner_name",
                  },
                  {
                    concept_id: "owner.address",
                    section: "owner",
                    scope: "document",
                    canonical_key: "owner_address",
                    label_key: "owner_address",
                  },
                  {
                    concept_id: "notes.main",
                    section: "notes",
                    scope: "document",
                    canonical_key: "notes",
                    label_key: "notes",
                  },
                  {
                    concept_id: "report.language",
                    section: "report_info",
                    scope: "document",
                    canonical_key: "language",
                    label_key: "language",
                  },
                  {
                    concept_id: "contract.allow.invoice_total",
                    section: "notes",
                    scope: "document",
                    canonical_key: "invoice_total",
                    label_key: "invoice_total",
                  },
                ],
              },
              fields: options?.fields ?? [
                {
                  field_id: "field-clinic-name-doc-canonical",
                  key: "clinic_name",
                  value: "Centro Norte",
                  value_type: "string",
                  scope: "document",
                  section: "clinic",
                  classification: "medical_record",
                  is_critical: false,
                  origin: "machine",
                },
                {
                  field_id: "field-pet-name-doc-canonical",
                  key: "pet_name",
                  value: "Luna",
                  value_type: "string",
                  scope: "document",
                  section: "patient",
                  classification: "medical_record",
                  is_critical: false,
                  origin: "machine",
                },
                {
                  field_id: "field-owner-name-doc-canonical",
                  key: "owner_name",
                  value: "Ana",
                  value_type: "string",
                  scope: "document",
                  section: "owner",
                  classification: "medical_record",
                  is_critical: false,
                  origin: "machine",
                },
                {
                  field_id: "field-owner-address-doc-canonical",
                  key: "owner_address",
                  value: "Calle Sur 8",
                  value_type: "string",
                  scope: "document",
                  section: "owner",
                  classification: "medical_record",
                  is_critical: false,
                  origin: "machine",
                },
                {
                  field_id: "field-notes-doc-canonical",
                  key: "notes",
                  value: "Revisar evolución",
                  value_type: "string",
                  scope: "document",
                  section: "notes",
                  classification: "medical_record",
                  is_critical: false,
                  origin: "machine",
                },
                {
                  field_id: "field-language-doc-canonical",
                  key: "language",
                  value: "es",
                  value_type: "string",
                  scope: "document",
                  section: "report_info",
                  classification: "medical_record",
                  is_critical: false,
                  origin: "machine",
                },
                {
                  field_id: "field-invoice-total-doc-canonical",
                  key: "invoice_total",
                  value: "123.00",
                  value_type: "string",
                  scope: "document",
                  section: "notes",
                  classification: "medical_record",
                  is_critical: false,
                  origin: "machine",
                },
                {
                  field_id: "field-top-level-other-doc-canonical",
                  key: "top_level_other_should_not_render",
                  value: "NO",
                  value_type: "string",
                  scope: "document",
                  section: "other",
                  classification: "other",
                  is_critical: false,
                  origin: "machine",
                },
              ],
              visits: options?.visits ?? [
                {
                  visit_id: "visit-1",
                  visit_date: "2026-02-11",
                  admission_date: null,
                  discharge_date: null,
                  reason_for_visit: "Control",
                  fields: [
                    {
                      field_id: "field-visit-diagnosis-doc-canonical",
                      key: "diagnosis",
                      value: "Estable",
                      value_type: "string",
                      scope: "visit",
                      section: "visits",
                      classification: "medical_record",
                      is_critical: false,
                      origin: "machine",
                    },
                  ],
                },
              ],
              other_fields: options?.otherFields ?? [
                {
                  field_id: "field-other-contract-doc-canonical",
                  key: "contract_other",
                  value: "VISIBLE",
                  value_type: "string",
                  scope: "document",
                  section: "other",
                  classification: "other",
                  is_critical: false,
                  origin: "machine",
                },
              ],
              confidence_policy: options?.confidencePolicy ?? {
                policy_version: "test-v1",
                band_cutoffs: {
                  low_max: 0.4,
                  mid_max: 0.7,
                },
              },
            },
          },
          raw_text_artifact: {
            run_id: "run-doc-canonical",
            available: true,
          },
          review_status: "IN_REVIEW",
          reviewed_at: null,
          reviewed_by: null,
        }),
        { status: 200 },
      );
    }

    if (url.includes("/processing-history") && method === "GET") {
      return new Response(JSON.stringify({ document_id: "doc-canonical", runs: [] }), {
        status: 200,
      });
    }

    if (url.includes("/download") && method === "GET") {
      return new Response(new Blob(["pdf"], { type: "application/pdf" }), { status: 200 });
    }

    if (url.includes("/raw-text") && method === "GET") {
      return new Response(
        JSON.stringify({
          run_id: "run-doc-canonical",
          artifact_type: "RAW_TEXT",
          content_type: "text/plain",
          text: "texto",
        }),
        { status: 200 },
      );
    }

    return new Response(JSON.stringify({ error_code: "NOT_FOUND" }), { status: 404 });
  }) as typeof fetch;

  globalThis.URL.createObjectURL = vi.fn(() => "blob://mock");
  globalThis.URL.revokeObjectURL = vi.fn();
}

export function installReviewedModeFetchMock() {
  const docs: Array<{
    document_id: string;
    original_filename: string;
    created_at: string;
    status: string;
    status_label: string;
    failure_type: string | null;
    review_status: "IN_REVIEW" | "REVIEWED";
    reviewed_at: string | null;
    reviewed_by: string | null;
  }> = [
    {
      document_id: "doc-ready",
      original_filename: "ready.pdf",
      created_at: "2026-02-09T10:00:00Z",
      status: "COMPLETED",
      status_label: "Completed",
      failure_type: null,
      review_status: "IN_REVIEW",
      reviewed_at: null,
      reviewed_by: null,
    },
  ];

  globalThis.fetch = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
    const url = input.toString();
    const method = (init?.method ?? "GET").toUpperCase();
    const activeDoc = docs[0];

    if (url.includes("/documents?") && method === "GET") {
      return new Response(
        JSON.stringify({ items: docs, limit: 50, offset: 0, total: docs.length }),
        { status: 200 },
      );
    }

    if (url.includes("/download") && method === "GET") {
      return new Response(new Blob(["pdf"], { type: "application/pdf" }), { status: 200 });
    }

    if (url.includes("/documents/doc-ready/reviewed") && method === "POST") {
      if (activeDoc.review_status !== "REVIEWED") {
        activeDoc.review_status = "REVIEWED";
        activeDoc.reviewed_at = "2026-02-10T10:30:00Z";
        activeDoc.reviewed_by = null;
      }
      return new Response(
        JSON.stringify({
          document_id: activeDoc.document_id,
          review_status: activeDoc.review_status,
          reviewed_at: activeDoc.reviewed_at,
          reviewed_by: activeDoc.reviewed_by,
        }),
        { status: 200 },
      );
    }

    if (url.includes("/documents/doc-ready/reviewed") && method === "DELETE") {
      activeDoc.review_status = "IN_REVIEW";
      activeDoc.reviewed_at = null;
      activeDoc.reviewed_by = null;
      return new Response(
        JSON.stringify({
          document_id: activeDoc.document_id,
          review_status: activeDoc.review_status,
          reviewed_at: activeDoc.reviewed_at,
          reviewed_by: activeDoc.reviewed_by,
        }),
        { status: 200 },
      );
    }

    if (url.match(/\/documents\/doc-ready$/) && method === "GET") {
      return new Response(
        JSON.stringify({
          document_id: activeDoc.document_id,
          original_filename: activeDoc.original_filename,
          content_type: "application/pdf",
          file_size: 10,
          created_at: activeDoc.created_at,
          updated_at: "2026-02-10T10:00:00Z",
          status: activeDoc.status,
          status_message: "Completed",
          failure_type: activeDoc.failure_type,
          review_status: activeDoc.review_status,
          reviewed_at: activeDoc.reviewed_at,
          reviewed_by: activeDoc.reviewed_by,
          latest_run: { run_id: "run-doc-ready", state: "COMPLETED", failure_type: null },
        }),
        { status: 200 },
      );
    }

    if (url.match(/\/documents\/doc-ready\/review$/) && method === "GET") {
      return new Response(
        JSON.stringify({
          document_id: activeDoc.document_id,
          latest_completed_run: {
            run_id: "run-doc-ready",
            state: "COMPLETED",
            completed_at: "2026-02-10T10:00:00Z",
            failure_type: null,
          },
          active_interpretation: {
            interpretation_id: "interp-doc-ready",
            version_number: 1,
            data: {
              document_id: activeDoc.document_id,
              processing_run_id: "run-doc-ready",
              created_at: "2026-02-10T10:00:00Z",
              fields: [
                {
                  field_id: "field-pet-name-doc-ready",
                  key: "pet_name",
                  value: "Luna",
                  value_type: "string",
                  field_candidate_confidence: 0.82,
                  field_mapping_confidence: 0.82,
                  is_critical: false,
                  origin: "machine",
                  evidence: { page: 1, snippet: "Paciente: Luna" },
                },
                {
                  field_id: "field-species-doc-ready",
                  key: "species",
                  value: "Canina",
                  value_type: "string",
                  field_candidate_confidence: 0.9,
                  field_mapping_confidence: 0.9,
                  is_critical: false,
                  origin: "machine",
                },
              ],
              confidence_policy: {
                policy_version: "v1",
                band_cutoffs: { low_max: 0.5, mid_max: 0.75 },
              },
            },
          },
          raw_text_artifact: {
            run_id: "run-doc-ready",
            available: true,
          },
          review_status: activeDoc.review_status,
          reviewed_at: activeDoc.reviewed_at,
          reviewed_by: activeDoc.reviewed_by,
        }),
        { status: 200 },
      );
    }

    if (url.includes("/processing-history") && method === "GET") {
      return new Response(JSON.stringify({ document_id: "doc-ready", runs: [] }), { status: 200 });
    }

    return new Response(JSON.stringify({ error_code: "NOT_FOUND" }), { status: 404 });
  }) as typeof fetch;
}

export async function openReviewedDocument() {
  fireEvent.click(await screen.findByRole("button", { name: /ready\.pdf/i }));
  await screen.findByTestId("confidence-indicator-core:pet_name");
}

export function getPetNameFieldButton() {
  const indicator = screen.getByTestId("confidence-indicator-core:pet_name");
  const fieldCard = indicator.closest("article");
  expect(fieldCard).not.toBeNull();
  const trigger = (fieldCard as HTMLElement).querySelector('[role="button"]');
  expect(trigger).not.toBeNull();
  return trigger as HTMLElement;
}

export function installDefaultAppFetchMock() {
  const docs = [
    {
      document_id: "doc-processing",
      original_filename: "processing.pdf",
      created_at: "2026-02-09T10:00:00Z",
      status: "PROCESSING",
      status_label: "Processing",
      failure_type: null,
    },
    {
      document_id: "doc-ready",
      original_filename: "ready.pdf",
      created_at: "2026-02-09T10:00:00Z",
      status: "COMPLETED",
      status_label: "Completed",
      failure_type: null,
    },
    {
      document_id: "doc-failed",
      original_filename: "failed.pdf",
      created_at: "2026-02-09T10:00:00Z",
      status: "FAILED",
      status_label: "Failed",
      failure_type: "EXTRACTION_FAILED",
    },
  ];

  globalThis.fetch = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
    const url = input.toString();
    const method = (init?.method ?? "GET").toUpperCase();

    if (url.includes("/documents?") && method === "GET") {
      return new Response(
        JSON.stringify({ items: docs, limit: 50, offset: 0, total: docs.length }),
        { status: 200 },
      );
    }

    if (url.endsWith("/documents/upload") && method === "POST") {
      docs.unshift({
        document_id: "doc-new",
        original_filename: "nuevo.pdf",
        created_at: "2026-02-10T10:00:00Z",
        status: "COMPLETED",
        status_label: "Completed",
        failure_type: null,
      });
      return new Response(
        JSON.stringify({
          document_id: "doc-new",
          status: "COMPLETED",
          created_at: "2026-02-10T10:00:00Z",
        }),
        { status: 201 },
      );
    }

    if (url.includes("/download") && method === "GET") {
      return new Response(new Blob(["pdf"], { type: "application/pdf" }), {
        status: 200,
        headers: { "content-disposition": 'inline; filename="record.pdf"' },
      });
    }

    const detailMatch = url.match(/\/documents\/([^/]+)$/);
    if (detailMatch && method === "GET") {
      const docId = detailMatch[1];
      const found = docs.find((doc) => doc.document_id === docId);
      return new Response(
        JSON.stringify({
          document_id: docId,
          original_filename: found?.original_filename ?? "record.pdf",
          content_type: "application/pdf",
          file_size: 10,
          created_at: found?.created_at ?? "2026-02-09T10:00:00Z",
          updated_at: "2026-02-10T10:00:00Z",
          status: found?.status ?? "PROCESSING",
          status_message: "Processing is in progress.",
          failure_type: found?.failure_type ?? null,
          latest_run: {
            run_id: `run-${docId}`,
            state: found?.status ?? "PROCESSING",
            failure_type: null,
          },
        }),
        { status: 200 },
      );
    }

    const reviewMatch = url.match(/\/documents\/([^/]+)\/review$/);
    if (reviewMatch && method === "GET") {
      const docId = reviewMatch[1];
      return new Response(
        JSON.stringify({
          document_id: docId,
          latest_completed_run: {
            run_id: `run-${docId}`,
            state: "COMPLETED",
            completed_at: "2026-02-10T10:00:00Z",
            failure_type: null,
          },
          active_interpretation: {
            interpretation_id: `interp-${docId}`,
            version_number: 1,
            data: {
              document_id: docId,
              processing_run_id: `run-${docId}`,
              created_at: "2026-02-10T10:00:00Z",
              fields: [
                {
                  field_id: `field-document-date-${docId}`,
                  key: "document_date",
                  value: null,
                  value_type: "date",
                  field_mapping_confidence: 0.32,
                  is_critical: false,
                  origin: "machine",
                },
                {
                  field_id: `field-visit-date-${docId}`,
                  key: "visit_date",
                  value: "2026-02-11T00:00:00Z",
                  value_type: "date",
                  field_mapping_confidence: 0.74,
                  is_critical: true,
                  origin: "machine",
                },
                {
                  field_id: `field-pet-name-${docId}`,
                  key: "pet_name",
                  value: "Luna",
                  value_type: "string",
                  field_mapping_confidence: 0.82,
                  field_candidate_confidence: 0.65,
                  field_review_history_adjustment: 7,
                  is_critical: false,
                  origin: "machine",
                  evidence: { page: 1, snippet: "Paciente: Luna" },
                },
                {
                  field_id: `field-diagnosis-${docId}`,
                  key: "diagnosis",
                  value: "Gastroenteritis",
                  value_type: "string",
                  field_mapping_confidence: 0.62,
                  field_candidate_confidence: 0.71,
                  field_review_history_adjustment: -4,
                  is_critical: false,
                  origin: "machine",
                  evidence: { page: 2, snippet: "Diagnostico: Gastroenteritis" },
                },
                {
                  field_id: `field-treatment-${docId}`,
                  key: "treatment_plan",
                  value:
                    "Reposo relativo durante 7 días.\nDieta blanda en 3 tomas al día y control de hidratación.",
                  value_type: "string",
                  field_mapping_confidence: 0.72,
                  is_critical: false,
                  origin: "machine",
                },
                {
                  field_id: `field-extra-${docId}`,
                  key: "custom_tag",
                  value: "Prioridad",
                  value_type: "string",
                  field_mapping_confidence: 0.88,
                  is_critical: false,
                  origin: "machine",
                  evidence: { page: 1, snippet: "Prioridad: Alta" },
                },
                {
                  field_id: `field-imagen-${docId}`,
                  key: "imagen",
                  value: "Rx abdomen",
                  value_type: "string",
                  field_mapping_confidence: 0.61,
                  is_critical: false,
                  origin: "machine",
                },
                {
                  field_id: `field-imagine-${docId}`,
                  key: "imagine",
                  value: "Eco",
                  value_type: "string",
                  field_mapping_confidence: 0.58,
                  is_critical: false,
                  origin: "machine",
                },
                {
                  field_id: `field-owner-name-${docId}`,
                  key: "owner_name",
                  value: "BEATRIZ ABARCA",
                  value_type: "string",
                  field_mapping_confidence: 0.84,
                  field_candidate_confidence: null,
                  field_review_history_adjustment: 0,
                  is_critical: false,
                  origin: "machine",
                },
                {
                  field_id: `field-owner-address-${docId}`,
                  key: "owner_address",
                  value: "Calle Mayor 10, Madrid",
                  value_type: "string",
                  field_mapping_confidence: 0.77,
                  field_candidate_confidence: 0.77,
                  field_review_history_adjustment: -4,
                  is_critical: false,
                  origin: "machine",
                },
                {
                  field_id: `field-imaging-${docId}`,
                  key: "IMAGING:",
                  value: "Radiografia lateral",
                  value_type: "string",
                  field_mapping_confidence: 0.57,
                  is_critical: false,
                  origin: "machine",
                },
              ],
              confidence_policy: {
                policy_version: "v1",
                band_cutoffs: { low_max: 0.5, mid_max: 0.75 },
              },
            },
          },
          raw_text_artifact: {
            run_id: `run-${docId}`,
            available: true,
          },
        }),
        { status: 200 },
      );
    }

    if (url.includes("/processing-history") && method === "GET") {
      return new Response(JSON.stringify({ document_id: "doc-any", runs: [] }), {
        status: 200,
      });
    }

    if (url.includes("/reprocess") && method === "POST") {
      return new Response(
        JSON.stringify({ run_id: "run-new", state: "QUEUED", created_at: "2026-02-10T10:00:00Z" }),
        { status: 201 },
      );
    }

    return new Response(JSON.stringify({ error_code: "NOT_FOUND" }), { status: 404 });
  }) as typeof fetch;

  globalThis.URL.createObjectURL = vi.fn(() => "blob://mock");
  globalThis.URL.revokeObjectURL = vi.fn();
}

export function resetAppTestEnvironment() {
  window.localStorage.clear();
  window.history.replaceState({}, "", "/");
}

function createConsoleSuppressor(method: "error" | "warn", pattern?: string | RegExp): () => void {
  return registerConsoleSuppression(method, pattern);
}

export function suppressConsoleError(pattern?: string | RegExp) {
  return createConsoleSuppressor("error", pattern);
}

export function suppressConsoleWarn(pattern?: string | RegExp) {
  return createConsoleSuppressor("warn", pattern);
}

export function suppressExpectedWindowError(message: string) {
  const handler = (event: ErrorEvent) => {
    if (event.error instanceof Error && event.error.message === message) {
      event.preventDefault();
    }
  };

  window.addEventListener("error", handler);
  return () => window.removeEventListener("error", handler);
}
