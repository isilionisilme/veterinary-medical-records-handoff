import { renderHook } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { useReviewRenderers } from "./useReviewRenderers";

describe("useReviewRenderers", () => {
  it("returns renderer functions for scalar, repeatable and section layout", () => {
    const { result } = renderHook(() =>
      useReviewRenderers({
        activeConfidencePolicy: null,
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
        isCanonicalContract: false,
        hasVisitGroups: false,
        validatedReviewFields: [],
        reviewVisits: [],
        canonicalVisitFieldOrder: [],
        buildSelectableField: (base, rawField, isMissing) => ({
          ...base,
          isMissing,
          hasMappingConfidence: false,
          confidence: 0,
          confidenceBand: null,
          rawField,
        }),
      }),
    );

    expect(typeof result.current.renderScalarReviewField).toBe("function");
    expect(typeof result.current.renderRepeatableReviewField).toBe("function");
    expect(typeof result.current.renderSectionLayout).toBe("function");
  });
});
