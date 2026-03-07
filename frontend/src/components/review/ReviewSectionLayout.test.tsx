import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import {
  createReviewSectionLayoutRenderer,
  type ReviewSectionLayoutContext,
} from "./ReviewSectionLayout";
import type {
  ReviewDisplayField,
  ReviewField,
  ReviewSelectableField,
  ReviewVisitGroup,
} from "../../types/appWorkspace";

function createReviewField(overrides?: Partial<ReviewField>): ReviewField {
  return {
    field_id: "field-1",
    key: "diagnosis",
    value: "Gastritis",
    value_type: "string",
    visit_group_id: "visit-a",
    scope: "visit",
    section: "visits",
    classification: "medical_record",
    domain: "clinical",
    is_critical: false,
    origin: "machine",
    ...overrides,
  };
}

function createSelectable(base: {
  id: string;
  key: string;
  label: string;
  section: string;
  order: number;
  valueType: string;
  displayValue: string;
  source: "core" | "extracted";
  evidence?: { page: number; snippet: string };
  repeatable: boolean;
}): ReviewSelectableField {
  return {
    ...base,
    isMissing: false,
    hasMappingConfidence: true,
    confidence: 0.8,
    confidenceBand: "high",
    rawField: createReviewField({ key: base.key, value: base.displayValue }),
  };
}

function createDisplayField(overrides?: Partial<ReviewDisplayField>): ReviewDisplayField {
  return {
    id: "display-1",
    key: "diagnosis",
    label: "Diagnóstico",
    section: "Visitas",
    order: 1,
    isCritical: false,
    valueType: "string",
    repeatable: false,
    items: [
      createSelectable({
        id: "item-1",
        key: "diagnosis",
        label: "Diagnóstico",
        section: "Visitas",
        order: 1,
        valueType: "string",
        displayValue: "Gastritis",
        source: "core",
        repeatable: false,
      }),
    ],
    isEmptyList: false,
    source: "core",
    ...overrides,
  };
}

function createContext(
  overrides?: Partial<ReviewSectionLayoutContext>,
): ReviewSectionLayoutContext {
  const renderScalarReviewField = vi.fn((field: ReviewDisplayField) => (
    <div key={`scalar-${field.id}`} data-testid={`scalar-${field.key}`}>
      {field.label}
    </div>
  ));
  const renderRepeatableReviewField = vi.fn(
    (
      field: ReviewDisplayField,
      _options?: { showUnassignedHint?: boolean; hideFieldTitle?: boolean },
    ) => (
      <div key={`repeatable-${field.id}`} data-testid={`repeatable-${field.key}`}>
        {field.label}
      </div>
    ),
  );

  return {
    isCanonicalContract: false,
    hasVisitGroups: true,
    validatedReviewFields: [],
    reviewVisits: [],
    canonicalVisitFieldOrder: ["visit_date", "reason_for_visit", "diagnosis"],
    buildSelectableField: (base, rawField, isMissing) => ({
      ...base,
      isMissing,
      hasMappingConfidence: true,
      confidence: 0.9,
      confidenceBand: "high",
      rawField,
    }),
    renderScalarReviewField,
    renderRepeatableReviewField,
    ...overrides,
  };
}

function renderSection(
  section: { id: string; title: string; fields: ReviewDisplayField[] },
  contextOverrides?: Partial<ReviewSectionLayoutContext>,
) {
  const ctx = createContext(contextOverrides);
  const renderer = createReviewSectionLayoutRenderer(ctx);
  render(<>{renderer(section)}</>);
  return ctx;
}

describe("ReviewSectionLayout", () => {
  it("renders empty-state messages for extra section and empty visits", () => {
    renderSection({ id: "extra:section", title: "Otros campos detectados", fields: [] });
    expect(screen.getByText("Sin otros campos detectados.")).toBeInTheDocument();

    renderSection(
      { id: "visits", title: "Visitas", fields: [] },
      { hasVisitGroups: false, isCanonicalContract: false },
    );
    expect(screen.getByText("Sin visitas detectadas.")).toBeInTheDocument();
  });

  it("uses scalar and repeatable renderers for non-canonical sections", () => {
    const scalar = createDisplayField({ key: "owner_name", label: "Nombre" });
    const repeatable = createDisplayField({
      key: "allergies",
      label: "Alergias",
      repeatable: true,
    });
    const ctx = renderSection({
      id: "owner",
      title: "Propietario",
      fields: [scalar, repeatable],
    });

    expect(ctx.renderScalarReviewField).toHaveBeenCalled();
    expect(ctx.renderRepeatableReviewField).toHaveBeenCalled();
    expect(ctx.renderScalarReviewField.mock.calls[0]?.[0]).toEqual(scalar);
    expect(ctx.renderRepeatableReviewField.mock.calls[0]?.[0]).toEqual(repeatable);
    expect(screen.getByTestId("scalar-owner_name")).toBeInTheDocument();
    expect(screen.getByTestId("repeatable-allergies")).toBeInTheDocument();
  });

  it("renders canonical visits by episode and unassigned group", () => {
    const validatedReviewFields: ReviewField[] = [
      createReviewField({
        field_id: "visit-field-obs-1",
        key: "observations",
        value: "Prurito auricular",
        visit_group_id: "visit-1",
      }),
      createReviewField({
        field_id: "visit-field-actions-1",
        key: "actions",
        value: "Tratamiento con gotas",
        visit_group_id: "visit-1",
      }),
      createReviewField({
        field_id: "visit-field-1",
        key: "diagnosis",
        value: "Otitis",
        visit_group_id: "visit-1",
      }),
      createReviewField({
        field_id: "visit-field-unassigned",
        key: "symptoms",
        value: "Fiebre",
        visit_group_id: "unassigned",
      }),
    ];
    const reviewVisits: ReviewVisitGroup[] = [
      {
        visit_id: "visit-1",
        visit_date: "2025-01-10",
        admission_date: null,
        discharge_date: null,
        reason_for_visit: "Control",
        fields: [],
      },
    ];

    const ctx = renderSection(
      { id: "visits", title: "Visitas", fields: [createDisplayField()] },
      {
        isCanonicalContract: true,
        validatedReviewFields,
        reviewVisits,
        canonicalVisitFieldOrder: [
          "visit_date",
          "reason_for_visit",
          "observations",
          "actions",
          "diagnosis",
          "symptoms",
        ],
      },
    );

    expect(screen.getByText("Visita 1")).toBeInTheDocument();
    expect(screen.getByTestId("visit-episode-1")).toBeInTheDocument();
    expect(screen.getByTestId("visit-date-section-1")).toBeInTheDocument();
    expect(screen.getByTestId("visit-summary-section-1")).toBeInTheDocument();
    expect(screen.getByText("Resumen")).toBeInTheDocument();
    expect(screen.getByTestId("repeatable-observations")).toBeInTheDocument();
    expect(screen.getByTestId("repeatable-actions")).toBeInTheDocument();
    expect(screen.getByTestId("visit-unassigned-group")).toBeInTheDocument();
    expect(screen.getByText("No asociadas a visita")).toBeInTheDocument();
    const observationsCall = ctx.renderRepeatableReviewField.mock.calls.find(
      (call) => call[0]?.key === "observations",
    );
    const actionsCall = ctx.renderRepeatableReviewField.mock.calls.find(
      (call) => call[0]?.key === "actions",
    );
    expect(observationsCall?.[1]).toEqual({ hideFieldTitle: true });
    expect(actionsCall?.[1]).toEqual({ hideFieldTitle: true });
    expect(ctx.renderScalarReviewField).toHaveBeenCalled();
    expect(ctx.renderRepeatableReviewField).toHaveBeenCalled();
  });

  it("does not render canonical episodes for non-visit sections even if canonical contract is enabled", () => {
    renderSection(
      {
        id: "patient",
        title: "Paciente",
        fields: [createDisplayField({ key: "pet_name", label: "Nombre" })],
      },
      {
        isCanonicalContract: true,
      },
    );

    expect(screen.queryByText("Visita 1")).not.toBeInTheDocument();
    expect(screen.getByTestId("scalar-pet_name")).toBeInTheDocument();
  });

  it("renders canonical visit badges for missing date/reason and avoids unassigned block when not needed", () => {
    const validatedReviewFields: ReviewField[] = [
      createReviewField({
        field_id: "visit-only",
        key: "diagnosis",
        value: "Gingivitis",
        visit_group_id: "visit-2",
      }),
    ];
    const reviewVisits: ReviewVisitGroup[] = [
      {
        visit_id: "visit-2",
        visit_date: null,
        admission_date: null,
        discharge_date: null,
        reason_for_visit: null,
        fields: [],
      },
    ];

    renderSection(
      { id: "visits", title: "Visitas", fields: [createDisplayField()] },
      {
        isCanonicalContract: true,
        validatedReviewFields,
        reviewVisits,
        canonicalVisitFieldOrder: ["visit_date", "reason_for_visit", "diagnosis"],
      },
    );

    expect(screen.getAllByText("Sin fecha").length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("Sin motivo")).toBeInTheDocument();
    expect(screen.queryByTestId("visit-unassigned-group")).not.toBeInTheDocument();
  });

  it("keeps canonical visit detail blocks collapsed by default and renders details toggle", () => {
    const validatedReviewFields: ReviewField[] = [
      createReviewField({
        field_id: "visit-detail",
        key: "diagnosis",
        value: "Artritis",
        visit_group_id: "visit-3",
      }),
    ];
    const reviewVisits: ReviewVisitGroup[] = [
      {
        visit_id: "visit-3",
        visit_date: "2025-01-12",
        admission_date: null,
        discharge_date: null,
        reason_for_visit: "Chequeo",
        fields: [],
      },
    ];

    renderSection(
      { id: "visits", title: "Visitas", fields: [createDisplayField()] },
      {
        isCanonicalContract: true,
        validatedReviewFields,
        reviewVisits,
      },
    );

    expect(screen.getByText("Detalles")).toBeInTheDocument();
    expect(screen.getByText("Con fecha")).toBeInTheDocument();
    expect(screen.getByText("Con motivo")).toBeInTheDocument();
  });

  it("handles stable chronological fallback and includes visit-scoped fields without visit_group_id as unassigned", () => {
    const validatedReviewFields: ReviewField[] = [
      createReviewField({
        field_id: "visit-a-diagnosis",
        key: "diagnosis",
        value: "Otitis",
        visit_group_id: "visit-a",
      }),
      createReviewField({
        field_id: "visit-b-diagnosis",
        key: "diagnosis",
        value: "Dermatitis",
        visit_group_id: "visit-b",
      }),
      createReviewField({
        field_id: "missing-visit-group",
        key: "symptoms",
        value: "Letargia",
        visit_group_id: undefined,
      }),
    ];
    const reviewVisits: ReviewVisitGroup[] = [
      {
        visit_id: "visit-a",
        visit_date: null,
        admission_date: null,
        discharge_date: null,
        reason_for_visit: "Control",
        fields: [],
      },
      {
        visit_id: "visit-b",
        visit_date: null,
        admission_date: null,
        discharge_date: null,
        reason_for_visit: "Seguimiento",
        fields: [],
      },
    ];

    renderSection(
      { id: "visits", title: "Visitas", fields: [createDisplayField()] },
      {
        isCanonicalContract: true,
        validatedReviewFields,
        reviewVisits,
        canonicalVisitFieldOrder: ["visit_date", "reason_for_visit", "diagnosis", "symptoms"],
      },
    );

    expect(screen.getByTestId("visit-episode-1")).toBeInTheDocument();
    expect(screen.getByTestId("visit-episode-2")).toBeInTheDocument();
    expect(screen.getByTestId("visit-unassigned-group")).toBeInTheDocument();
  });
});
