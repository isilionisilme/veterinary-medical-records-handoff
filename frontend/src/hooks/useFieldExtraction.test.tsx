import { renderHook } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import type {
  DocumentReviewResponse,
  ReviewField,
  StructuredInterpretationData,
} from "../types/appWorkspace";
import { useFieldExtraction } from "./useFieldExtraction";

function buildInterpretationData(fields: ReviewField[]): StructuredInterpretationData {
  return {
    document_id: "doc-1",
    processing_run_id: "run-1",
    created_at: "2026-02-28T00:00:00Z",
    fields,
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

describe("useFieldExtraction", () => {
  it("returns validated review fields for non-canonical payload", () => {
    const interpretationData = buildInterpretationData([
      {
        field_id: "f-1",
        key: "pet_name",
        value: "Firulais",
        value_type: "string",
        is_critical: false,
        origin: "machine",
      },
    ]);

    const { result } = renderHook(() =>
      useFieldExtraction({
        documentReview: { data: buildDocumentReview(interpretationData) },
        interpretationData,
        isCanonicalContract: false,
        reviewVisits: [],
        activeConfidencePolicy: null,
      }),
    );

    expect(result.current.validatedReviewFields).toHaveLength(1);
    expect(result.current.matchesByKey.get("pet_name")).toHaveLength(1);
  });

  it("filters billing fields under canonical contract", () => {
    const interpretationData = buildInterpretationData([
      {
        field_id: "f-claim",
        key: "claim_id",
        value: "123",
        value_type: "string",
        is_critical: false,
        origin: "machine",
      },
      {
        field_id: "f-pet",
        key: "pet_name",
        value: "Mora",
        value_type: "string",
        is_critical: false,
        origin: "machine",
      },
    ]);

    const { result } = renderHook(() =>
      useFieldExtraction({
        documentReview: { data: buildDocumentReview(interpretationData) },
        interpretationData,
        isCanonicalContract: true,
        reviewVisits: [],
        activeConfidencePolicy: null,
      }),
    );

    expect(result.current.validatedReviewFields.some((field) => field.key === "claim_id")).toBe(
      false,
    );
    expect(result.current.validatedReviewFields.some((field) => field.key === "pet_name")).toBe(
      true,
    );
  });

  it("buildSelectableField annotates confidence when policy is present", () => {
    const interpretationData = buildInterpretationData([
      {
        field_id: "f-1",
        key: "pet_name",
        value: "Luna",
        value_type: "string",
        field_mapping_confidence: 0.9,
        is_critical: false,
        origin: "machine",
      },
    ]);

    const { result } = renderHook(() =>
      useFieldExtraction({
        documentReview: { data: buildDocumentReview(interpretationData) },
        interpretationData,
        isCanonicalContract: false,
        reviewVisits: [],
        activeConfidencePolicy: {
          policy_version: "v1",
          band_cutoffs: { low_max: 0.4, mid_max: 0.8 },
        },
      }),
    );

    const rawField = result.current.validatedReviewFields[0];
    const selectable = result.current.buildSelectableField(
      {
        id: "x",
        key: rawField.key,
        label: "Nombre",
        section: "Paciente",
        order: 1,
        valueType: rawField.value_type,
        displayValue: "Luna",
        source: "core",
        repeatable: false,
      },
      rawField,
      false,
    );

    expect(selectable.hasMappingConfidence).toBe(true);
    expect(selectable.confidenceBand).toBe("high");
  });
});
