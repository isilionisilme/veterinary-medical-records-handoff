import { act, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
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
  waitForStructuredDataReady,
} from "../test/helpers";

vi.mock("./PdfViewer");

describe("App upload and list flow", () => {
  beforeEach(() => {
    resetAppTestEnvironment();
    installDefaultAppFetchMock();
  });

  it("renders the full Global Schema template with explicit missing states", async () => {
    renderApp();
    const panel = await openReadyDocumentAndGetPanel();

    const hiddenCoreKeys = new Set([
      "claim_id",
      "document_date",
      "owner_id",
      "invoice_total",
      "covered_amount",
      "non_covered_amount",
      "line_item",
    ]);
    const uiLabelOverrides: Record<string, string> = {
      clinic_name: "Nombre",
      clinic_address: "Dirección",
      pet_name: "Nombre",
      dob: "Nacimiento",
      owner_name: "Nombre",
      owner_address: "Dirección",
      nhc: "NHC",
      vet_name: "Veterinario",
      breed: "Raza",
      age: "Edad (ultima visita)",
      microchip_id: "Microchip",
      species: "Especie",
      sex: "Sexo",
      weight: "Peso",
    };

    const normalizeLabel = (value: string) =>
      value
        .normalize("NFD")
        .replace(/\p{Diacritic}/gu, "")
        .toLowerCase()
        .trim();

    GLOBAL_SCHEMA.filter((field) => !hiddenCoreKeys.has(field.key)).forEach((field) => {
      const expectedLabel = uiLabelOverrides[field.key] ?? field.label;
      const matchingLabels = within(panel).queryAllByText((content, node) => {
        if (!node || !(node instanceof HTMLElement)) {
          return false;
        }
        return normalizeLabel(content) === normalizeLabel(expectedLabel);
      });
      expect(matchingLabels.length).toBeGreaterThan(0);
    });
    expect(within(panel).queryByText("ID de reclamacion")).toBeNull();
    expect(within(panel).queryByText("Fecha del documento")).toBeNull();
    expect(within(panel).queryByText("Importe total")).toBeNull();
    expect(within(panel).getByText("Plan de tratamiento")).toBeInTheDocument();
    expect(within(panel).getAllByText("—").length).toBeGreaterThan(0);
    expect(within(panel).getByText("Otros campos detectados")).toBeInTheDocument();
    expect(within(panel).getAllByText("Custom tag").length).toBeGreaterThan(0);
    expect(within(panel).getAllByText("Prioridad").length).toBeGreaterThan(0);
  });

  it("hides configured extracted fields from the extra section", async () => {
    renderApp();
    const panel = await openReadyDocumentAndGetPanel();
    const extraSection = within(panel).getByTestId("other-extracted-fields-section");

    expect(within(extraSection).queryByText("Document date")).toBeNull();
    expect(within(extraSection).queryByText("Imagen")).toBeNull();
    expect(within(extraSection).queryByText("Imagine")).toBeNull();
    expect(within(extraSection).queryByText(/Imaging/i)).toBeNull();
  });

  it("uses structured owner/visit rows and long-text wrappers", async () => {
    renderApp();
    const panel = await openReadyDocumentAndGetPanel();

    const ownerSectionTitle = within(panel).getByText("Propietario");
    const ownerSection = ownerSectionTitle.closest("section");
    expect(ownerSection).not.toBeNull();
    const caseSectionTitle = within(panel).getByText("Centro Veterinario");
    const caseSection = caseSectionTitle.closest("section");
    expect(caseSection).not.toBeNull();
    const clinicRow = within(caseSection as HTMLElement).getByTestId("core-row-clinic_name");
    expect(clinicRow).toHaveClass("grid");
    expect(clinicRow).toHaveClass("grid-cols-[var(--field-row-label-col)_minmax(0,1fr)]");
    expect(clinicRow).toHaveClass("gap-x-[var(--field-row-gap-x)]");
    const clinicValue = within(caseSection as HTMLElement).getByTestId("core-value-clinic_name");
    expect(clinicValue).toHaveClass("w-full");
    expect(clinicValue).toHaveClass("bg-surfaceMuted");
    expect(clinicValue).toHaveClass("border");
    expect(clinicValue).toHaveClass("border-borderSubtle");
    const treatmentValueCandidates = within(panel).getAllByTestId("field-value-treatment_plan");
    const treatmentValue =
      treatmentValueCandidates.find((node) => node.textContent?.includes("Reposo relativo")) ??
      treatmentValueCandidates[0];
    expect(treatmentValue.tagName).toBe("DIV");
    expect(treatmentValue).toHaveClass("min-h-[var(--long-text-min-height)]");
    expect(treatmentValue).toHaveClass("max-h-[var(--long-text-max-height)]");
    expect(treatmentValue).toHaveClass("overflow-auto");
    expect(treatmentValue).toHaveClass("px-[var(--value-padding-long-x)]");
    expect(treatmentValue).toHaveClass("whitespace-pre-wrap");
    expect(treatmentValue).toHaveClass("break-words");
    expect(within(panel).queryAllByRole("textbox")).toHaveLength(0);
    const ownerGrid = (ownerSection as HTMLElement).querySelector("div.grid");
    expect(ownerGrid).not.toBeNull();
    expect(ownerGrid).toHaveClass("grid-cols-1");
    expect(ownerGrid).not.toHaveClass("lg:grid-cols-2");

    const ownerNameRow = within(ownerSection as HTMLElement).getByTestId("owner-row-owner_name");
    expect(ownerNameRow).toHaveClass("grid");
    expect(ownerNameRow).toHaveClass("grid-cols-[var(--field-row-label-col)_minmax(0,1fr)]");
    expect(ownerNameRow).toHaveClass("gap-x-[var(--field-row-gap-x)]");

    const ownerNameLabel = within(ownerSection as HTMLElement).getByTestId(
      "owner-label-owner_name",
    );
    expect(ownerNameLabel).toHaveClass("self-start");
    const ownerNameDot = within(ownerSection as HTMLElement).getByTestId("owner-dot-owner_name");
    expect(ownerNameDot).toHaveClass("self-start");
    expect(ownerNameDot).toHaveClass("mt-[var(--dot-offset)]");
    expect(ownerNameDot).toHaveClass("h-4");
    expect(ownerNameDot).toHaveClass("w-4");
    expect(ownerNameDot).toHaveClass("items-center");
    expect(ownerNameDot).toHaveClass("justify-center");

    const ownerNameValue = within(ownerSection as HTMLElement).getByText("BEATRIZ ABARCA");
    expect(ownerNameValue).toHaveAttribute("data-testid", "owner-value-owner_name");
    expect(ownerNameValue).toHaveClass("text-left");
    expect(ownerNameValue).toHaveClass("break-words");
    expect(ownerNameValue).toHaveClass("bg-surfaceMuted");
    expect(ownerNameValue).toHaveClass("rounded-md");
    expect(ownerNameValue).toHaveClass("w-full");
    expect(ownerNameValue).toHaveClass("min-w-0");
    expect(ownerNameValue).toHaveClass("border");
    expect(ownerNameValue).toHaveClass("border-borderSubtle");

    const ownerAddressValue =
      within(ownerSection as HTMLElement).queryByTestId("owner-value-owner_address") ??
      within(ownerSection as HTMLElement).getByTestId("core-value-owner_address");
    expect(ownerAddressValue).toHaveClass("w-full");
    expect(ownerAddressValue).toHaveClass("bg-surfaceMuted");

    const visitSectionTitle = within(panel).getByText("Visitas");
    const visitSection = visitSectionTitle.closest("section");
    expect(visitSection).not.toBeNull();
    const visitGrid = (visitSection as HTMLElement).querySelector("div.grid");
    expect(visitGrid).not.toBeNull();
    expect(visitGrid).toHaveClass("lg:grid-cols-2");

    const visitDateRow = within(visitSection as HTMLElement).getByTestId("visit-row-visit_date");
    const visitReasonRow = within(visitSection as HTMLElement).getByTestId(
      "visit-row-reason_for_visit",
    );
    expect(visitDateRow).toHaveClass("grid");
    expect(visitReasonRow).toHaveClass("grid");
    expect(visitDateRow).toHaveClass("grid-cols-[var(--field-row-label-col)_minmax(0,1fr)]");
    expect(visitDateRow).toHaveClass("gap-x-[var(--field-row-gap-x)]");
    expect(visitReasonRow).toHaveClass("grid-cols-[var(--field-row-label-col)_minmax(0,1fr)]");
    expect(visitReasonRow).toHaveClass("gap-x-[var(--field-row-gap-x)]");

    const visitReasonLabel = within(visitSection as HTMLElement).getByTestId(
      "visit-label-reason_for_visit",
    );
    expect(visitReasonLabel).toHaveClass("self-start");
    const visitReasonDot = within(visitSection as HTMLElement).getByTestId(
      "visit-dot-reason_for_visit",
    );
    expect(visitReasonDot).toHaveClass("self-start");
    expect(visitReasonDot).toHaveClass("mt-[var(--dot-offset)]");

    const visitDateValue = within(visitSection as HTMLElement).getByTestId(
      "visit-value-visit_date",
    );
    const visitReasonValue = within(visitSection as HTMLElement).getByTestId(
      "field-value-reason_for_visit",
    );
    expect(visitDateValue).toHaveClass("w-full");
    expect(visitReasonValue).toHaveClass("w-full");
    expect(visitReasonValue).toHaveClass("min-h-[var(--long-text-min-height)]");
    expect(visitDateValue).toHaveClass("bg-surfaceMuted");
    expect(visitReasonValue).toHaveClass("bg-surfaceMuted");
    expect(visitDateValue).toHaveClass("border");
    expect(visitReasonValue).toHaveClass("border");

    const editButtons = within(panel).getAllByRole("button", { name: /Editar/i });
    expect(editButtons[0]).toHaveClass("border");
    expect(editButtons[0]).toHaveClass("hover:border-borderSubtle");
  });

  it("shows subtle CRÍTICO marker and confidence tooltip for core fields", async () => {
    renderApp();

    fireEvent.click(await screen.findByRole("button", { name: /ready\.pdf/i }));

    await waitForStructuredDataReady();

    const panel = screen.getByTestId("right-panel-scroll");
    const criticalFields = GLOBAL_SCHEMA.filter((field) => field.critical);
    const nonCriticalFields = GLOBAL_SCHEMA.filter((field) => !field.critical);

    criticalFields.forEach((field) => {
      expect(within(panel).queryByTestId(`critical-indicator-${field.key}`)).toBeInTheDocument();
    });

    nonCriticalFields.forEach((field) => {
      expect(within(panel).queryByTestId(`critical-indicator-${field.key}`)).toBeNull();
    });

    const petNameCard = within(panel)
      .getByTestId("confidence-indicator-core:pet_name")
      .closest("article");
    expect(petNameCard).not.toBeNull();
    const petNameCritical = within(petNameCard as HTMLElement).getByTestId(
      "critical-indicator-pet_name",
    );
    expect(petNameCritical).toBeInTheDocument();
    const petNameConfidence = within(petNameCard as HTMLElement).getByTestId(
      "confidence-indicator-core:pet_name",
    );
    expect(petNameConfidence).toHaveAttribute(
      "aria-label",
      expect.stringMatching(/Confianza:\s*\d+%/i),
    );
    expect(petNameConfidence).toHaveAttribute(
      "aria-label",
      expect.not.stringMatching(/\((Alta|Media|Baja)\)/i),
    );
    expect(petNameConfidence).toHaveAttribute(
      "aria-label",
      expect.stringMatching(/Fiabilidad del candidato:\s*65%/i),
    );
    expect(petNameConfidence).toHaveAttribute(
      "aria-label",
      expect.stringMatching(/Ajuste por histórico de revisiones:\s*\+7%/i),
    );

    const clinicalRecordCard = within(panel).getByTestId("core-row-clinic_name").closest("article");
    expect(clinicalRecordCard).not.toBeNull();
    const clinicalRecordConfidence = within(clinicalRecordCard as HTMLElement).getByTestId(
      "confidence-indicator-core:clinic_name",
    );
    expect(clinicalRecordConfidence).toHaveAttribute("aria-label", "Campo vacío");
    expect(within(panel).queryByTestId("critical-indicator-diagnosis")).toBeInTheDocument();
  });

  it("renders canonical sections in US-44 fixed order", async () => {
    installCanonicalUs44FetchMock();
    renderApp();
    const panel = await openReadyDocumentAndGetPanel();
    const panelText = panel.textContent ?? "";

    const orderedSections = [
      "Centro Veterinario",
      "Paciente",
      "Propietario",
      "Visitas",
      "Notas internas",
      "Otros campos detectados",
      "Detalles del informe",
    ];

    let lastIndex = -1;
    orderedSections.forEach((section) => {
      const index = panelText.indexOf(section);
      expect(index).toBeGreaterThan(lastIndex);
      lastIndex = index;
    });
  });

  it("uses canonical field_slots for required placeholders (NHC missing renders —)", async () => {
    installCanonicalUs44FetchMock();
    renderApp();
    const panel = await openReadyDocumentAndGetPanel();

    expect(within(panel).getByTestId("critical-indicator-pet_name")).toBeInTheDocument();
    expect(within(panel).getByText("NHC")).toBeInTheDocument();
    expect(within(panel).getByText("NHC")).toHaveAttribute("title", "Número de historial clínico");
    expect(within(panel).getByTestId("core-value-nhc")).toHaveTextContent("—");
    const nhcIndicator = within(panel).getByTestId("confidence-indicator-core:nhc");
    expect(nhcIndicator).toHaveAttribute("aria-label", "Campo vacío");
    expect(nhcIndicator.className).toContain("border");
    expect(nhcIndicator.className).toContain("border-muted");
    expect(nhcIndicator.className).toContain("bg-surface");
    expect(nhcIndicator.className).not.toContain("bg-missing");
  });

  it("keeps critical badges in canonical Datos extraídos for critical document fields", async () => {
    installCanonicalUs44FetchMock();
    renderApp();
    const panel = await openReadyDocumentAndGetPanel();

    expect(within(panel).queryByTestId("critical-indicator-pet_name")).toBeInTheDocument();
    expect(within(panel).queryByTestId("critical-indicator-clinic_name")).toBeNull();
  });

  it("shows explicit canonical contract error when field_slots are malformed", async () => {
    installCanonicalUs44FetchMock({
      schemaContract: "visit-grouped-canonical",
      fieldSlots: { malformed: true } as unknown as Array<Record<string, unknown>>,
      visits: [],
    });
    renderApp();
    const panel = await openReadyDocumentAndGetPanel();

    expect(within(panel).getByTestId("canonical-contract-error")).toBeInTheDocument();
    expect(within(panel).getByText(/medical_record_view\.field_slots/i)).toBeInTheDocument();
    expect(within(panel).queryByText("Sin visitas detectadas.")).toBeNull();
    expect(within(panel).queryByText(/Identificaci[oó]n del caso/i)).toBeNull();
  });

  it("shows Visitas empty state in canonical contract when visits=[]", async () => {
    installCanonicalUs44FetchMock({ visits: [] });
    renderApp();
    const panel = await openReadyDocumentAndGetPanel();

    expect(within(panel).getByText("Visitas")).toBeInTheDocument();
    expect(within(panel).getByText("Sin visitas detectadas.")).toBeInTheDocument();
  });

  it("renders Visitas grouped by episode with chronological numbering and reverse visual order", async () => {
    installCanonicalUs44FetchMock({
      visits: [
        {
          visit_id: "visit-newest",
          visit_date: "2026-02-20",
          admission_date: null,
          discharge_date: null,
          reason_for_visit: "Revisión final",
          fields: [
            {
              field_id: "f-diagnosis-newest",
              key: "diagnosis",
              value: "Alta",
              value_type: "string",
              scope: "visit",
              section: "visits",
              classification: "medical_record",
              is_critical: false,
              origin: "machine",
            },
          ],
        },
        {
          visit_id: "visit-oldest",
          visit_date: "2026-02-10",
          admission_date: null,
          discharge_date: null,
          reason_for_visit: "Ingreso",
          fields: [],
        },
        {
          visit_id: "visit-middle",
          visit_date: "2026-02-15",
          admission_date: null,
          discharge_date: null,
          reason_for_visit: "Control",
          fields: [],
        },
      ],
    });
    renderApp();
    const panel = await openReadyDocumentAndGetPanel();

    const visitsSection = within(panel).getByText("Visitas").closest("section");
    expect(visitsSection).not.toBeNull();

    const visitHeaders = within(visitsSection as HTMLElement)
      .getAllByText(/^Visita\s\d+$/)
      .map((node) => node.textContent?.trim());
    expect(visitHeaders).toEqual(["Visita 3", "Visita 2", "Visita 1"]);

    const newestEpisode = within(visitsSection as HTMLElement).getByTestId("visit-episode-3");
    const middleEpisode = within(visitsSection as HTMLElement).getByTestId("visit-episode-2");
    const oldestEpisode = within(visitsSection as HTMLElement).getByTestId("visit-episode-1");

    expect(within(newestEpisode).getByTestId("visit-row-visit_date")).toBeInTheDocument();
    expect(within(middleEpisode).getByTestId("visit-row-visit_date")).toBeInTheDocument();
    expect(within(oldestEpisode).getByTestId("visit-row-visit_date")).toBeInTheDocument();

    expect(
      within(newestEpisode).getAllByText(
        new Date("2026-02-20T00:00:00Z").toLocaleDateString("es-ES"),
      ).length,
    ).toBeGreaterThan(0);
    expect(
      within(middleEpisode).getAllByText(
        new Date("2026-02-15T00:00:00Z").toLocaleDateString("es-ES"),
      ).length,
    ).toBeGreaterThan(0);
    expect(
      within(oldestEpisode).getAllByText(
        new Date("2026-02-10T00:00:00Z").toLocaleDateString("es-ES"),
      ).length,
    ).toBeGreaterThan(0);

    expect(within(oldestEpisode).getByText("Diagnóstico")).toBeInTheDocument();
    expect(within(oldestEpisode).getByText("Procedimiento")).toBeInTheDocument();
    expect(within(oldestEpisode).getByText("Medicación")).toBeInTheDocument();
    expect(within(oldestEpisode).getByText("Plan de tratamiento")).toBeInTheDocument();
    expect(within(oldestEpisode).getByText("Resultado de laboratorio")).toBeInTheDocument();
    expect(within(oldestEpisode).getAllByText("Sin elementos").length).toBeGreaterThan(0);
  });

  it("shows unassigned helper text in canonical contract when unassigned visit group is present", async () => {
    installCanonicalUs44FetchMock({
      visits: [
        {
          visit_id: "visit-regular",
          visit_date: "2026-02-20",
          admission_date: null,
          discharge_date: null,
          reason_for_visit: "Control",
          fields: [],
        },
        {
          visit_id: "unassigned",
          visit_date: null,
          admission_date: null,
          discharge_date: null,
          reason_for_visit: null,
          fields: [
            {
              field_id: "f-unassigned-diagnosis",
              key: "diagnosis",
              value: "Sin fecha de visita",
              value_type: "string",
              scope: "visit",
              section: "visits",
              classification: "medical_record",
              is_critical: true,
              origin: "machine",
            },
          ],
        },
      ],
    });
    renderApp();
    const panel = await openReadyDocumentAndGetPanel();

    const hints = within(panel).getAllByTestId("visits-unassigned-hint");
    expect(hints).toHaveLength(1);
    expect(within(panel).getByTestId("visit-unassigned-group")).toBeInTheDocument();
    expect(hints[0]).toHaveTextContent("Elementos detectados sin fecha/visita asociada.");
    expect(
      within(panel).queryAllByText("Elementos detectados sin fecha/visita asociada."),
    ).toHaveLength(1);
    expect(within(panel).queryByText("Sin visitas detectadas.")).toBeNull();
  });

  it("suppresses Visitas empty state when only unassigned visit group exists", async () => {
    installCanonicalUs44FetchMock({
      visits: [
        {
          visit_id: "unassigned",
          visit_date: null,
          admission_date: null,
          discharge_date: null,
          reason_for_visit: null,
          fields: [],
        },
      ],
    });
    renderApp();
    const panel = await openReadyDocumentAndGetPanel();

    expect(within(panel).queryByTestId("visits-unassigned-hint")).toBeNull();
    expect(within(panel).queryByText("Sin visitas detectadas.")).toBeNull();
  });

  it("does not show unassigned helper when all visit groups are assigned", async () => {
    installCanonicalUs44FetchMock({
      visits: [
        {
          visit_id: "visit-1",
          visit_date: "2026-02-20",
          admission_date: null,
          discharge_date: null,
          reason_for_visit: "Control",
          fields: [],
        },
      ],
    });
    renderApp();
    const panel = await openReadyDocumentAndGetPanel();

    expect(within(panel).queryByTestId("visits-unassigned-hint")).toBeNull();
    expect(within(panel).queryByText("Sin visitas detectadas.")).toBeNull();
  });
});
