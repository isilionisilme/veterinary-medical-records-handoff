import { renderHook } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import type {
  ConfidencePolicyConfig,
  DocumentReviewResponse,
  StructuredInterpretationData,
} from "../types/appWorkspace";
import { useReviewDataPipeline } from "./useReviewDataPipeline";

function buildInterpretationData(
  overrides: Partial<StructuredInterpretationData> = {},
): StructuredInterpretationData {
  return {
    document_id: "doc-1",
    processing_run_id: "run-1",
    created_at: "2026-02-28T00:00:00Z",
    fields: [
      {
        field_id: "field-1",
        key: "pet_name",
        value: "Firulais",
        value_type: "string",
        is_critical: false,
        origin: "machine",
      },
    ],
    ...overrides,
  };
}

function buildDocumentReview(data: StructuredInterpretationData): DocumentReviewResponse {
  return {
    document_id: data.document_id,
    latest_completed_run: {
      run_id: data.processing_run_id,
      state: "COMPLETED",
      completed_at: data.created_at,
      failure_type: null,
    },
    active_interpretation: {
      interpretation_id: "interp-1",
      version_number: 1,
      data,
    },
    raw_text_artifact: {
      run_id: data.processing_run_id,
      available: true,
    },
    review_status: "IN_REVIEW",
    reviewed_at: null,
    reviewed_by: null,
  };
}

describe("useReviewDataPipeline", () => {
  it("builds review sections and selectable items from interpretation data", () => {
    const interpretationData = buildInterpretationData();
    const { result } = renderHook(() =>
      useReviewDataPipeline({
        documentReview: { data: buildDocumentReview(interpretationData) },
        interpretationData,
        isCanonicalContract: false,
        hasMalformedCanonicalFieldSlots: false,
        reviewVisits: [],
        activeConfidencePolicy: null,
        structuredDataFilters: {
          searchTerm: "",
          selectedConfidence: [],
          onlyCritical: false,
          onlyWithValue: false,
          onlyEmpty: false,
        },
        hasActiveStructuredFilters: false,
      }),
    );

    expect(result.current.reportSections.length).toBeGreaterThan(0);
    expect(result.current.selectableReviewItems.length).toBeGreaterThan(0);
    expect(result.current.detectedFieldsSummary.total).toBeGreaterThan(0);
  });

  it("applies active structured filters to hide non-matching core groups", () => {
    const interpretationData = buildInterpretationData();
    const activeConfidencePolicy: ConfidencePolicyConfig = {
      policy_version: "v1",
      band_cutoffs: { low_max: 0.4, mid_max: 0.8 },
    };
    const { result } = renderHook(() =>
      useReviewDataPipeline({
        documentReview: { data: buildDocumentReview(interpretationData) },
        interpretationData,
        isCanonicalContract: false,
        hasMalformedCanonicalFieldSlots: false,
        reviewVisits: [],
        activeConfidencePolicy,
        structuredDataFilters: {
          searchTerm: "campo_inexistente",
          selectedConfidence: [],
          onlyCritical: false,
          onlyWithValue: false,
          onlyEmpty: false,
        },
        hasActiveStructuredFilters: true,
      }),
    );

    expect(result.current.visibleCoreGroups).toEqual([]);
    expect(result.current.visibleOtherDisplayFields).toEqual([]);
  });
});
