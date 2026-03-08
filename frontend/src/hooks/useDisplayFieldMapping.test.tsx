import { renderHook } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import type {
  ReviewField,
  ReviewSelectableField,
  StructuredInterpretationData,
} from "../types/appWorkspace";
import { useDisplayFieldMapping } from "./useDisplayFieldMapping";

type BuildSelectableFieldFn = (
  base: Omit<
    ReviewSelectableField,
    "hasMappingConfidence" | "confidence" | "confidenceBand" | "isMissing" | "rawField"
  >,
  rawField: ReviewField | undefined,
  isMissing: boolean,
) => ReviewSelectableField;

const buildSelectableField: BuildSelectableFieldFn = (base, rawField, isMissing) => ({
  ...base,
  isMissing,
  hasMappingConfidence: false,
  confidence: 0,
  confidenceBand: null,
  rawField,
});

function buildInterpretationData(
  overrides: Partial<StructuredInterpretationData> = {},
): StructuredInterpretationData {
  return {
    document_id: "doc-1",
    processing_run_id: "run-1",
    created_at: "2026-02-28T00:00:00Z",
    fields: [],
    ...overrides,
  };
}

describe("useDisplayFieldMapping", () => {
  it("maps non-canonical validated fields into core display fields", () => {
    const validatedReviewFields: ReviewField[] = [
      {
        field_id: "f-pet",
        key: "pet_name",
        value: "Nina",
        value_type: "string",
        is_critical: false,
        origin: "machine",
      },
    ];
    const matchesByKey = new Map<string, ReviewField[]>([["pet_name", validatedReviewFields]]);

    const { result } = renderHook(() =>
      useDisplayFieldMapping({
        isCanonicalContract: false,
        hasMalformedCanonicalFieldSlots: false,
        interpretationData: buildInterpretationData(),
        validatedReviewFields,
        matchesByKey,
        buildSelectableField,
        explicitOtherReviewFields: [],
      }),
    );

    expect(result.current.coreDisplayFields.length).toBeGreaterThan(0);
    expect(result.current.coreDisplayFields.some((field) => field.key === "pet_name")).toBe(true);
  });

  it("returns no core fields when canonical field slots are malformed", () => {
    const { result } = renderHook(() =>
      useDisplayFieldMapping({
        isCanonicalContract: true,
        hasMalformedCanonicalFieldSlots: true,
        interpretationData: buildInterpretationData(),
        validatedReviewFields: [],
        matchesByKey: new Map<string, ReviewField[]>(),
        buildSelectableField,
        explicitOtherReviewFields: [],
      }),
    );

    expect(result.current.coreDisplayFields).toEqual([]);
  });

  it("uses explicitOtherReviewFields for canonical other display mapping", () => {
    const explicitOtherReviewFields: ReviewField[] = [
      {
        field_id: "other-1",
        key: "custom_note",
        value: "observacion",
        value_type: "string",
        classification: "other",
        is_critical: false,
        origin: "machine",
      },
    ];

    const { result } = renderHook(() =>
      useDisplayFieldMapping({
        isCanonicalContract: true,
        hasMalformedCanonicalFieldSlots: false,
        interpretationData: buildInterpretationData(),
        validatedReviewFields: [],
        matchesByKey: new Map<string, ReviewField[]>(),
        buildSelectableField,
        explicitOtherReviewFields,
      }),
    );

    expect(result.current.otherDisplayFields).toHaveLength(1);
    expect(result.current.otherDisplayFields[0]?.key).toBe("custom_note");
  });

  it("prioritizes document-scoped candidate for canonical document slots", () => {
    const visitWeight: ReviewField = {
      field_id: "visit-weight-1",
      key: "weight",
      value: "12.5 kg",
      value_type: "string",
      scope: "visit",
      section: "visits",
      classification: "medical_record",
      origin: "machine",
      field_mapping_confidence: 0.95,
    };
    const derivedDocumentWeight: ReviewField = {
      field_id: "derived-weight-current",
      key: "weight",
      value: "29.6 kg",
      value_type: "string",
      scope: "document",
      section: "patient",
      classification: "medical_record",
      origin: "derived",
      field_mapping_confidence: 0.1,
    };
    const validatedReviewFields: ReviewField[] = [visitWeight, derivedDocumentWeight];
    const matchesByKey = new Map<string, ReviewField[]>([
      ["weight", [visitWeight, derivedDocumentWeight]],
    ]);
    const interpretationData = buildInterpretationData({
      medical_record_view: {
        version: "mvp-1",
        sections: ["patient", "visits"],
        field_slots: [
          {
            canonical_key: "weight",
            scope: "document",
            section: "patient",
            aliases: [],
          },
        ],
      },
    });

    const { result } = renderHook(() =>
      useDisplayFieldMapping({
        isCanonicalContract: true,
        hasMalformedCanonicalFieldSlots: false,
        interpretationData,
        validatedReviewFields,
        matchesByKey,
        buildSelectableField,
        explicitOtherReviewFields: [],
      }),
    );

    const weightField = result.current.coreDisplayFields.find((field) => field.key === "weight");
    expect(weightField).toBeDefined();
    expect(weightField?.items[0]?.displayValue).toBe("29.6 kg");
    expect(weightField?.items[0]?.rawField?.field_id).toBe("derived-weight-current");
  });
});
