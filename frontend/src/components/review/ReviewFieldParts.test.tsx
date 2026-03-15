import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { renderConfidenceIndicator, renderEditableFieldValue } from "./ReviewFieldParts";
import type { ReviewSelectableField } from "../../types";

function createSelectableField(overrides?: Partial<ReviewSelectableField>): ReviewSelectableField {
  return {
    id: "field-1",
    key: "pet_name",
    label: "Nombre",
    section: "patient",
    order: 1,
    valueType: "string",
    displayValue: "Luna",
    isMissing: false,
    hasMappingConfidence: true,
    confidence: 0.88,
    confidenceBand: "high",
    source: "core",
    repeatable: false,
    ...overrides,
  };
}

describe("ReviewFieldParts", () => {
  it("renders empty confidence indicator for missing values", () => {
    const item = createSelectableField({
      id: "missing-1",
      isMissing: true,
      displayValue: "—",
    });

    render(<>{renderConfidenceIndicator(item, "Confianza alta")}</>);

    expect(screen.getByTestId("confidence-indicator-missing-1")).toHaveAttribute(
      "aria-label",
      "Campo vacío",
    );
  });

  it("hides edit action when document is reviewed", () => {
    const item = createSelectableField();

    render(
      <>
        {renderEditableFieldValue(
          {
            isDocumentReviewed: true,
            isInterpretationEditPending: false,
            onOpenFieldEditDialog: vi.fn(),
          },
          {
            item,
            value: item.displayValue,
            isLongText: false,
            shortTextTestId: "short-value",
          },
        )}
      </>,
    );

    expect(screen.getByTestId("short-value")).toBeInTheDocument();
    expect(screen.queryByTestId("field-edit-btn-field-1")).not.toBeInTheDocument();
  });

  it("invokes edit callback with field payload when edit button is clicked", () => {
    const onOpenFieldEditDialog = vi.fn();
    const item = createSelectableField();

    render(
      <>
        {renderEditableFieldValue(
          {
            isDocumentReviewed: false,
            isInterpretationEditPending: false,
            onOpenFieldEditDialog,
          },
          {
            item,
            value: item.displayValue,
            isLongText: false,
            shortTextTestId: "short-value",
          },
        )}
      </>,
    );

    fireEvent.click(screen.getByTestId("field-edit-btn-field-1"));
    expect(onOpenFieldEditDialog).toHaveBeenCalledWith(item);
  });
});
