import { renderHook } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import * as workspaceUtils from "../lib/appWorkspaceUtils";
import type { StructuredInterpretationData } from "../types/appWorkspace";
import { useConfidenceDiagnostics } from "./useConfidenceDiagnostics";

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

describe("useConfidenceDiagnostics", () => {
  it("returns active confidence policy when interpretation policy is valid", () => {
    const { result } = renderHook(() =>
      useConfidenceDiagnostics({
        interpretationData: buildInterpretationData({
          confidence_policy: {
            policy_version: "v1",
            band_cutoffs: { low_max: 0.4, mid_max: 0.8 },
          },
        }),
        reviewVisits: [],
        isCanonicalContract: false,
      }),
    );

    expect(result.current.activeConfidencePolicy).toEqual({
      policy_version: "v1",
      band_cutoffs: { low_max: 0.4, mid_max: 0.8 },
    });
    expect(result.current.confidencePolicyDegradedReason).toBeNull();
  });

  it("emits degraded diagnostic once per document+reason", () => {
    const emitSpy = vi
      .spyOn(workspaceUtils, "emitConfidencePolicyDiagnosticEvent")
      .mockImplementation(() => {});

    const interpretationData = buildInterpretationData({
      confidence_policy: {
        policy_version: "",
        band_cutoffs: { low_max: 0.4, mid_max: 0.8 },
      },
    });

    const { rerender } = renderHook(() =>
      useConfidenceDiagnostics({
        interpretationData,
        reviewVisits: [],
        isCanonicalContract: false,
      }),
    );

    rerender();

    expect(emitSpy).toHaveBeenCalledTimes(1);
    expect(emitSpy).toHaveBeenCalledWith({
      event_type: "CONFIDENCE_POLICY_CONFIG_MISSING",
      document_id: "doc-1",
      reason: "missing_policy_version",
    });

    emitSpy.mockRestore();
  });
});
