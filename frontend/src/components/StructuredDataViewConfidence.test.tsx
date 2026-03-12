import { act, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { GLOBAL_SCHEMA } from "../lib/globalSchema";
import {
  CanonicalUs44FetchMockOptions,
  createDataTransfer,
  getConfidenceSummaryCounts,
  installCanonicalUs44FetchMock,
  installDefaultAppFetchMock,
  openReadyDocumentAndGetPanel,
  renderApp,
  resetAppTestEnvironment,
  suppressConsoleWarn,
  waitForStructuredDataReady,
} from "../test/helpers";

vi.mock("./PdfViewer");

describe("App upload and list flow", () => {
  beforeEach(() => {
    resetAppTestEnvironment();
    installDefaultAppFetchMock();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("uses canonical detected summary as X/30 and increments X with visit concepts", async () => {
    const controlledFields = [
      {
        field_id: "f-nhc-alias",
        key: "medical_record_number",
        value: "NHC-001",
        value_type: "string",
        scope: "document",
        section: "clinic",
        classification: "medical_record",
        field_mapping_confidence: 0.6,
        origin: "machine",
      },
      {
        field_id: "f-pet-name",
        key: "pet_name",
        value: "Luna",
        value_type: "string",
        scope: "document",
        section: "patient",
        classification: "medical_record",
        field_mapping_confidence: 0.85,
        origin: "machine",
      },
      {
        field_id: "f-language",
        key: "language",
        value: "es",
        value_type: "string",
        scope: "document",
        section: "report_info",
        classification: "medical_record",
        field_mapping_confidence: 0.2,
        origin: "machine",
      },
      {
        field_id: "f-invoice-total",
        key: "invoice_total",
        value: "123.00",
        value_type: "string",
        scope: "document",
        section: "notes",
        classification: "medical_record",
        field_mapping_confidence: 0.95,
        origin: "machine",
      },
    ];
    const controlledVisits = [
      {
        visit_id: "visit-1",
        visit_date: "2026-02-11",
        admission_date: null,
        discharge_date: null,
        reason_for_visit: "Control",
        fields: [
          {
            field_id: "f-visit-diagnosis",
            key: "diagnosis",
            value: "Estable",
            value_type: "string",
            scope: "visit",
            section: "visits",
            classification: "medical_record",
            field_mapping_confidence: 0.65,
            origin: "machine",
          },
          {
            field_id: "f-visit-procedure",
            key: "procedure",
            value: "Exploración",
            value_type: "string",
            scope: "visit",
            section: "visits",
            classification: "medical_record",
            field_mapping_confidence: 0.3,
            origin: "machine",
          },
        ],
      },
    ];

    const expectedDetected = 3 + 2 + 2;
    installCanonicalUs44FetchMock({ fields: controlledFields, visits: controlledVisits });
    renderApp();
    await openReadyDocumentAndGetPanel();

    const { low, medium, high, unknown, unknownButton } = getConfidenceSummaryCounts();
    expect(unknownButton).toBeInTheDocument();
    expect(low + medium + high + unknown).toBe(expectedDetected);
  });

  it("keeps canonical total at 30 and counts only document concepts when visits=[]", async () => {
    const documentOnlyFields = [
      {
        field_id: "f-pet-name",
        key: "pet_name",
        value: "Luna",
        value_type: "string",
        scope: "document",
        section: "patient",
        classification: "medical_record",
        field_mapping_confidence: 0.8,
        origin: "machine",
      },
      {
        field_id: "f-notes",
        key: "notes",
        value: "Sin incidencias",
        value_type: "string",
        scope: "document",
        section: "notes",
        classification: "medical_record",
        origin: "machine",
      },
    ];

    const expectedDetected = 2;
    installCanonicalUs44FetchMock({ fields: documentOnlyFields, visits: [] });
    renderApp();
    await openReadyDocumentAndGetPanel();

    const { low, medium, high, unknown, unknownButton } = getConfidenceSummaryCounts();
    expect(unknownButton).toBeInTheDocument();
    expect(low + medium + high + unknown).toBe(expectedDetected);
  });

  it("shows Spanish confidence labels in header dots and unknown tooltip", async () => {
    installCanonicalUs44FetchMock();
    renderApp();
    await openReadyDocumentAndGetPanel();

    expect(screen.getByRole("button", { name: /^Baja \(\d+\)$/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /^Media \(\d+\)$/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /^Alta \(\d+\)$/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /^Sin confianza \(\d+\)$/i })).toBeInTheDocument();
  });

  it("renders Otros campos detectados only from other_fields[] in canonical contract", async () => {
    installCanonicalUs44FetchMock();
    renderApp();
    const panel = await openReadyDocumentAndGetPanel();
    const extraSection = within(panel).getByTestId("other-extracted-fields-section");

    expect(within(extraSection).getByText("Contract other")).toBeInTheDocument();
    expect(within(extraSection).getByText("VISIBLE")).toBeInTheDocument();
    expect(within(extraSection).queryByText("Top level other should not render")).toBeNull();
    expect(within(extraSection).queryByText("NO")).toBeNull();
  });

  it("hides billing keys in canonical contract even when contract/data include them", async () => {
    installCanonicalUs44FetchMock();
    renderApp();
    const panel = await openReadyDocumentAndGetPanel();

    expect(within(panel).queryByText("Invoice total")).toBeNull();
    expect(within(panel).queryByText("123.00")).toBeNull();
  });

  it("keeps canonical medical record panel clinical-only even when invoice_total is injected in field_slots and fields", async () => {
    installCanonicalUs44FetchMock({
      fieldSlots: [
        {
          concept_id: "clinic.name",
          section: "clinic",
          scope: "document",
          canonical_key: "clinic_name",
          label_key: "clinic_name",
        },
        {
          concept_id: "contract.invoice_total",
          section: "notes",
          scope: "document",
          canonical_key: "invoice_total",
          label_key: "invoice_total",
        },
      ],
      fields: [
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
      ],
    });
    renderApp();
    const panel = await openReadyDocumentAndGetPanel();

    expect(within(panel).getByText("Centro Veterinario")).toBeInTheDocument();
    expect(within(panel).queryByText(/invoice/i)).toBeNull();
    expect(within(panel).queryByText("123.00")).toBeNull();
  });

  it("shows an empty list state for repeatable fields", async () => {
    renderApp();

    fireEvent.click(await screen.findByRole("button", { name: /ready\.pdf/i }));

    await waitForStructuredDataReady();

    const panel = screen.getByTestId("right-panel-scroll");
    const medicationCard = within(panel)
      .getByText(/Medicaci[oó]n/i)
      .closest("article");
    expect(medicationCard).not.toBeNull();
    expect(within(medicationCard as HTMLElement).getByText("Sin elementos")).toBeInTheDocument();
  });

  it("uses empty indicator for missing fields and keeps low-confidence filter scoped to non-empty values", async () => {
    renderApp();

    fireEvent.click(await screen.findByRole("button", { name: /ready\.pdf/i }));

    await waitForStructuredDataReady();

    const panel = screen.getByTestId("right-panel-scroll");
    const missingIndicator = within(panel).getByTestId("confidence-indicator-core:clinic_name");
    expect(missingIndicator).toHaveAttribute("aria-label", "Campo vacío");
    expect(missingIndicator.className).toContain("border");
    expect(missingIndicator.className).toContain("border-muted");
    expect(missingIndicator.className).toContain("bg-surface");
    expect(missingIndicator.className).not.toContain("bg-missing");

    fireEvent.click(screen.getByRole("button", { name: /^Baja/i }));
    expect(
      within(screen.getByTestId("right-panel-scroll")).queryByTestId(
        "field-trigger-core:clinic_name",
      ),
    ).toBeNull();

    fireEvent.click(screen.getByRole("button", { name: /^Baja/i }));
    fireEvent.click(screen.getByRole("button", { name: "Mostrar solo campos vacíos" }));
    expect(
      within(screen.getByTestId("right-panel-scroll")).getByTestId(
        "field-trigger-core:clinic_name",
      ),
    ).toBeInTheDocument();
  });

  it("shows degraded confidence mode and emits a diagnostic event when policy config is missing", async () => {
    const baseFetch = globalThis.fetch as typeof fetch;
    const restoreWarn = suppressConsoleWarn();

    globalThis.fetch = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = input.toString();
      const method = (init?.method ?? "GET").toUpperCase();
      if (url.includes("/documents/doc-ready/review") && method === "GET") {
        const response = await baseFetch(input, init);
        const payload = await response.json();
        delete payload.active_interpretation?.data?.confidence_policy;
        return new Response(JSON.stringify(payload), { status: 200 });
      }
      return baseFetch(input, init);
    }) as typeof fetch;

    renderApp();

    fireEvent.click(await screen.findByRole("button", { name: /ready\.pdf/i }));
    await screen.findByTestId("confidence-policy-degraded");

    const indicator = screen.getByTestId("confidence-indicator-core:pet_name");
    expect(indicator).not.toHaveAttribute("aria-label", "Campo vacío");
    expect(indicator.className).toContain("bg-missing");
    expect(console.warn).toHaveBeenCalledWith(
      "[confidence-policy]",
      expect.objectContaining({
        event_type: "CONFIDENCE_POLICY_CONFIG_MISSING",
        reason: "missing_policy_version",
      }),
    );
    restoreWarn();
  });

  it("does not show degraded confidence mode when policy config is valid", async () => {
    renderApp();

    fireEvent.click(await screen.findByRole("button", { name: /ready\.pdf/i }));
    await waitForStructuredDataReady();

    expect(screen.queryByTestId("confidence-policy-degraded")).toBeNull();
  });

  it("does not fallback to deprecated confidence when field_mapping_confidence is missing", async () => {
    const baseFetch = globalThis.fetch as typeof fetch;

    globalThis.fetch = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = input.toString();
      const method = (init?.method ?? "GET").toUpperCase();
      if (url.includes("/documents/doc-ready/review") && method === "GET") {
        const response = await baseFetch(input, init);
        const payload = await response.json();
        const fields = payload.active_interpretation?.data?.fields;
        if (Array.isArray(fields)) {
          fields.forEach((field: Record<string, unknown>) => {
            delete field.field_mapping_confidence;
            field.confidence = 0.99;
          });
        }
        return new Response(JSON.stringify(payload), { status: 200 });
      }
      return baseFetch(input, init);
    }) as typeof fetch;

    renderApp();
    fireEvent.click(await screen.findByRole("button", { name: /ready\.pdf/i }));
    await waitForStructuredDataReady();

    expect(screen.queryByTestId("confidence-policy-degraded")).toBeNull();
    const indicator = screen.getByTestId("confidence-indicator-core:pet_name");
    expect(indicator.className).toContain("bg-missing");
    expect(indicator).toHaveAttribute(
      "aria-label",
      expect.stringMatching(/Confianza de mapeo no disponible/i),
    );
  });

  it("treats manually edited values as unknown confidence and keeps unknown filter behavior after refresh", async () => {
    const baseFetch = globalThis.fetch as typeof fetch;
    let reviewEdited = false;

    globalThis.fetch = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = input.toString();
      const method = (init?.method ?? "GET").toUpperCase();

      if (url.includes("/runs/run-doc-ready/interpretations") && method === "POST") {
        reviewEdited = true;
        return new Response(
          JSON.stringify({
            run_id: "run-doc-ready",
            interpretation_id: "interp-doc-ready",
            version_number: 2,
            data: {
              document_id: "doc-ready",
              processing_run_id: "run-doc-ready",
              created_at: "2026-02-10T10:00:00Z",
              fields: [
                {
                  field_id: "field-pet-name-doc-ready",
                  key: "pet_name",
                  value: "Luna editada",
                  value_type: "string",
                  field_candidate_confidence: 0.82,
                  field_mapping_confidence: 0.82,
                  field_review_history_adjustment: 7,
                  is_critical: false,
                  origin: "human",
                  evidence: { page: 1, snippet: "Paciente: Luna" },
                },
              ],
              confidence_policy: {
                policy_version: "v1",
                band_cutoffs: { low_max: 0.5, mid_max: 0.75 },
              },
            },
          }),
          { status: 200 },
        );
      }

      if (url.includes("/documents/doc-ready/review") && method === "GET" && reviewEdited) {
        const response = await baseFetch(input, init);
        const payload = await response.json();
        payload.active_interpretation.version_number = 2;
        const fields = payload.active_interpretation?.data?.fields;
        if (Array.isArray(fields)) {
          const petNameField = fields.find(
            (field: Record<string, unknown>) => field.key === "pet_name",
          );
          if (petNameField) {
            petNameField.value = "Luna editada";
            petNameField.origin = "human";
            petNameField.field_mapping_confidence = 0.82;
            petNameField.field_candidate_confidence = 0.82;
            petNameField.field_review_history_adjustment = 7;
          }
        }
        return new Response(JSON.stringify(payload), { status: 200 });
      }

      return baseFetch(input, init);
    }) as typeof fetch;

    renderApp();
    fireEvent.click(await screen.findByRole("button", { name: /ready\.pdf/i }));
    await waitForStructuredDataReady();

    const indicatorBeforeEdit = screen.getByTestId("confidence-indicator-core:pet_name");
    expect(indicatorBeforeEdit.className).toContain("bg-confidenceHigh");

    const fieldCard = screen.getByTestId("field-trigger-core:pet_name").closest("article");
    expect(fieldCard).not.toBeNull();
    fireEvent.click(within(fieldCard as HTMLElement).getByRole("button", { name: /Editar/i }));

    const editDialog = await screen.findByRole("dialog", { name: /Editar/i });
    fireEvent.change(within(editDialog).getByRole("textbox"), {
      target: { value: "Luna editada" },
    });
    fireEvent.click(within(editDialog).getByRole("button", { name: /^Guardar$/i }));

    await waitFor(() => {
      const editedIndicator = screen.getByTestId("confidence-indicator-core:pet_name");
      expect(editedIndicator.className).toContain("bg-missing");
    });

    const editedIndicator = screen.getByTestId("confidence-indicator-core:pet_name");
    expect(editedIndicator).toHaveAttribute(
      "aria-label",
      expect.stringMatching(
        /La confianza aplica únicamente al valor originalmente detectado por el sistema\. El valor actual ha sido editado y por eso no tiene confianza asociada\./i,
      ),
    );
    expect(editedIndicator).toHaveAttribute(
      "aria-label",
      expect.not.stringMatching(/Fiabilidad del candidato|Ajuste por histórico|Confianza:\s*\d+%/i),
    );

    fireEvent.click(screen.getByRole("button", { name: /^Sin confianza \(\d+\)$/i }));
    expect(screen.getByTestId("field-trigger-core:pet_name")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: /^Sin confianza \(\d+\)$/i }));
    fireEvent.click(screen.getByRole("button", { name: /^Baja \(\d+\)$/i }));
    expect(screen.queryByTestId("field-trigger-core:pet_name")).toBeNull();

    fireEvent.click(screen.getByRole("button", { name: /^Baja \(\d+\)$/i }));
    fireEvent.click(screen.getByRole("button", { name: /Actualizar/i }));
    await waitForStructuredDataReady();

    const indicatorAfterRefresh = screen.getByTestId("confidence-indicator-core:pet_name");
    expect(indicatorAfterRefresh.className).toContain("bg-missing");
    expect(indicatorAfterRefresh).toHaveAttribute(
      "aria-label",
      expect.stringMatching(
        /La confianza aplica únicamente al valor originalmente detectado por el sistema\. El valor actual ha sido editado y por eso no tiene confianza asociada\./i,
      ),
    );
  }, 10000);

  it("shows visit date value when present", async () => {
    renderApp();

    fireEvent.click(await screen.findByRole("button", { name: /ready\.pdf/i }, { timeout: 10000 }));

    await waitForStructuredDataReady();

    const panel = screen.getByTestId("right-panel-scroll");
    const expectedDate = new Date("2026-02-11T00:00:00Z").toLocaleDateString("es-ES");
    const visitDateCard = within(panel).getByText("Fecha de visita").closest("article");
    expect(visitDateCard).not.toBeNull();
    expect(within(visitDateCard as HTMLElement).getByText(expectedDate)).toBeInTheDocument();
  }, 10000);
});
