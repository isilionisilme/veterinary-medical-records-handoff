import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import {
  createReviewFieldRenderers,
  type ReviewFieldRenderersContext,
} from "./ReviewFieldRenderers";
import type { ReviewDisplayField, ReviewSelectableField } from "../../types/appWorkspace";

function createSelectableField(overrides?: Partial<ReviewSelectableField>): ReviewSelectableField {
  return {
    id: "field-1",
    key: "diagnosis",
    label: "Diagnóstico",
    section: "Visitas",
    order: 1,
    valueType: "string",
    displayValue: "Gastritis leve",
    isMissing: false,
    hasMappingConfidence: true,
    confidence: 0.92,
    confidenceBand: "high",
    source: "core",
    repeatable: false,
    rawField: {
      field_id: "raw-1",
      key: "diagnosis",
      value: "Gastritis leve",
      value_type: "string",
      is_critical: false,
      origin: "machine",
      field_candidate_confidence: 0.87,
      field_review_history_adjustment: 0.06,
      evidence: { page: 3, snippet: "diagnosis line" },
    },
    evidence: { page: 3, snippet: "diagnosis line" },
    ...overrides,
  };
}

function createDisplayField(
  overrides?: Partial<ReviewDisplayField> & { items?: ReviewSelectableField[] },
): ReviewDisplayField {
  const resolvedItems = overrides?.items ?? [createSelectableField()];
  const { items: _items, ...restOverrides } = overrides ?? {};
  return {
    id: "display-1",
    key: "diagnosis",
    label: "Diagnóstico",
    section: "Visitas",
    order: 1,
    isCritical: false,
    valueType: "string",
    repeatable: false,
    items: resolvedItems,
    isEmptyList: false,
    source: "core",
    ...restOverrides,
  };
}

function createContext(
  overrides?: Partial<ReviewFieldRenderersContext>,
): ReviewFieldRenderersContext {
  return {
    activeConfidencePolicy: {
      policy_version: "v1",
      band_cutoffs: { low_max: 0.4, mid_max: 0.75 },
    },
    isDocumentReviewed: false,
    isInterpretationEditPending: false,
    selectedFieldId: null,
    expandedFieldValues: {},
    hoveredFieldTriggerId: null,
    hoveredCriticalTriggerId: null,
    hasUnassignedVisitGroup: false,
    onOpenFieldEditDialog: vi.fn(),
    onSelectReviewItem: vi.fn(),
    onReviewedEditAttempt: vi.fn(),
    onReviewedKeyboardEditAttempt: vi.fn(),
    onSetExpandedFieldValues: vi.fn(),
    onSetHoveredFieldTriggerId: vi.fn(),
    onSetHoveredCriticalTriggerId: vi.fn(),
    ...overrides,
  };
}

function renderScalarWithContext(
  field: ReviewDisplayField,
  contextOverrides?: Partial<ReviewFieldRenderersContext>,
) {
  const ctx = createContext(contextOverrides);
  const { renderScalarReviewField } = createReviewFieldRenderers(ctx);
  render(<>{renderScalarReviewField(field)}</>);
  return ctx;
}

function renderRepeatableWithContext(
  field: ReviewDisplayField,
  contextOverrides?: Partial<ReviewFieldRenderersContext>,
  options?: { showUnassignedHint?: boolean; hideFieldTitle?: boolean },
) {
  const ctx = createContext(contextOverrides);
  const { renderRepeatableReviewField } = createReviewFieldRenderers(ctx);
  render(<>{renderRepeatableReviewField(field, options)}</>);
  return ctx;
}

describe("ReviewFieldRenderers", () => {
  it("renders scalar fields and selects item on click", () => {
    const field = createDisplayField();
    const ctx = renderScalarWithContext(field);

    const trigger = screen.getByTestId("field-trigger-field-1");
    fireEvent.click(trigger);

    expect(screen.getByText("Diagnóstico")).toBeInTheDocument();
    expect(screen.getByText("Gastritis leve")).toBeInTheDocument();
    expect(ctx.onSelectReviewItem).toHaveBeenCalledTimes(1);
    expect(ctx.onSelectReviewItem).toHaveBeenCalledWith(field.items[0]);
  });

  it("blocks selection and hides edit controls when document is reviewed", () => {
    const field = createDisplayField();
    const ctx = renderScalarWithContext(field, { isDocumentReviewed: true });

    fireEvent.click(screen.getByTestId("field-trigger-field-1"));

    expect(ctx.onSelectReviewItem).not.toHaveBeenCalled();
    expect(screen.queryByRole("button", { name: "Editar" })).not.toBeInTheDocument();
  });

  it("supports keyboard selection and confidence tooltip rendering", () => {
    const field = createDisplayField();
    const ctx = renderScalarWithContext(field, { hoveredFieldTriggerId: "field-1" });

    const trigger = screen.getByTestId("field-trigger-field-1");
    fireEvent.keyDown(trigger, { key: "Enter" });

    expect(ctx.onReviewedKeyboardEditAttempt).toHaveBeenCalledTimes(1);
    expect(ctx.onSelectReviewItem).toHaveBeenCalledTimes(1);
    expect(screen.getByRole("tooltip")).toHaveTextContent("Confianza:");
  });

  it("renders missing-value confidence indicator and supports expand/collapse", () => {
    const longText = "A".repeat(180);
    const item = createSelectableField({
      id: "field-long",
      displayValue: longText,
      key: "weight",
      isMissing: true,
      rawField: {
        field_id: "raw-long",
        key: "weight",
        value: null,
        value_type: "string",
        is_critical: false,
        origin: "machine",
      },
    });
    const field = createDisplayField({
      key: "weight",
      label: "Peso",
      items: [item],
    });
    const ctx = renderScalarWithContext(field);

    expect(screen.getByTestId("confidence-indicator-field-long")).toHaveAttribute(
      "aria-label",
      "Campo vacío",
    );

    fireEvent.click(screen.getByRole("button", { name: "Ver más" }));
    expect(ctx.onSetExpandedFieldValues).toHaveBeenCalledTimes(1);
  });

  it("renders repeatable fields with unassigned hint and forwards repeatable selection", () => {
    const items = [
      createSelectableField({
        id: "repeat-1",
        repeatable: true,
        visitGroupId: "unassigned",
      }),
      createSelectableField({
        id: "repeat-2",
        repeatable: true,
        visitGroupId: "unassigned",
      }),
    ];
    const field = createDisplayField({
      id: "repeat-display",
      key: "medication",
      label: "Medicación",
      repeatable: true,
      items,
      isEmptyList: false,
    });
    const ctx = renderRepeatableWithContext(field, { hasUnassignedVisitGroup: true });

    expect(screen.getByText("2 elementos")).toBeInTheDocument();
    expect(screen.getAllByTestId("visits-unassigned-hint")).toHaveLength(1);

    fireEvent.click(screen.getByTestId("field-trigger-repeat-1"));
    expect(ctx.onSelectReviewItem).toHaveBeenCalledWith(items[0]);
  });

  it("renders empty repeatable list placeholder", () => {
    const field = createDisplayField({
      id: "empty-repeat",
      key: "allergies",
      label: "Alergias",
      repeatable: true,
      items: [],
      isEmptyList: true,
    });

    renderRepeatableWithContext(field);

    expect(screen.getByText("Sin elementos")).toBeInTheDocument();
  });

  it("hides repeatable field title row when requested", () => {
    const field = createDisplayField({
      id: "summary-observations",
      key: "observations",
      label: "Observaciones",
      repeatable: true,
      items: [createSelectableField({ id: "summary-item", repeatable: true })],
      isEmptyList: false,
    });

    renderRepeatableWithContext(field, undefined, { hideFieldTitle: true });

    expect(screen.queryByText("1 elemento")).not.toBeInTheDocument();
    expect(screen.getByTestId("field-trigger-summary-item")).toBeInTheDocument();
  });

  it("shows fallback tooltip when confidence config is missing", () => {
    const noPolicyItem = createSelectableField({ id: "no-policy-item" });
    const noPolicyField = createDisplayField({
      id: "display-no-policy",
      items: [noPolicyItem],
    });

    renderScalarWithContext(noPolicyField, {
      activeConfidencePolicy: null,
      hoveredFieldTriggerId: "no-policy-item",
    });

    expect(screen.getByRole("tooltip")).toHaveTextContent(
      "Configuración de confianza no disponible.",
    );
  });

  it("shows fallback tooltip when mapping confidence is missing", () => {
    const missingMappingItem = createSelectableField({
      id: "no-mapping-item",
      hasMappingConfidence: false,
    });
    const missingMappingField = createDisplayField({
      id: "display-no-mapping",
      items: [missingMappingItem],
    });
    renderScalarWithContext(missingMappingField, {
      hoveredFieldTriggerId: "no-mapping-item",
    });

    expect(screen.getByRole("tooltip")).toHaveTextContent("Confianza de mapeo no disponible.");
  });

  it("shows manual override tooltip for human-origin fields", () => {
    const humanItem = createSelectableField({
      id: "human-item",
      rawField: {
        field_id: "raw-human",
        key: "diagnosis",
        value: "Manual",
        value_type: "string",
        is_critical: false,
        origin: "human",
      },
    });
    const field = createDisplayField({ id: "display-human", items: [humanItem] });

    renderScalarWithContext(field, { hoveredFieldTriggerId: "human-item" });

    expect(screen.getByRole("tooltip")).toHaveTextContent(
      "La confianza aplica únicamente al valor originalmente detectado por el sistema.",
    );
  });

  it("renders derived-origin fields with the derived highlight style", () => {
    const derivedItem = createSelectableField({
      id: "derived-item",
      rawField: {
        field_id: "raw-derived",
        key: "age",
        value: "7",
        value_type: "string",
        is_critical: true,
        origin: "derived",
      },
    });
    const field = createDisplayField({
      id: "display-derived",
      key: "age",
      label: "Edad",
      items: [derivedItem],
    });

    renderScalarWithContext(field);

    expect(screen.getByText("Gastritis leve").closest("div")).toHaveClass("!bg-blue-50");
  });

  it("wires hover, blur and reviewed edit handlers on repeatable trigger", () => {
    const repeatableItem = createSelectableField({ id: "repeat-events", repeatable: true });
    const field = createDisplayField({
      id: "repeat-events-field",
      repeatable: true,
      items: [repeatableItem],
    });
    const ctx = renderRepeatableWithContext(field);

    const trigger = screen.getByTestId("field-trigger-repeat-events");
    fireEvent.mouseEnter(trigger);
    fireEvent.mouseLeave(trigger);
    fireEvent.mouseUp(trigger);
    fireEvent.focus(trigger);
    fireEvent.blur(trigger, { relatedTarget: null });

    expect(ctx.onSetHoveredFieldTriggerId).toHaveBeenCalled();
    expect(ctx.onSetHoveredCriticalTriggerId).toHaveBeenCalled();
    expect(ctx.onReviewedEditAttempt).toHaveBeenCalledTimes(1);
  });

  it("does not select items with keyboard when reviewed", () => {
    const field = createDisplayField();
    const ctx = renderScalarWithContext(field, { isDocumentReviewed: true });

    fireEvent.keyDown(screen.getByTestId("field-trigger-field-1"), { key: " " });

    expect(ctx.onReviewedKeyboardEditAttempt).toHaveBeenCalledTimes(1);
    expect(ctx.onSelectReviewItem).not.toHaveBeenCalled();
  });
});
