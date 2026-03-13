import { act, renderHook } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import type { DocumentReviewResponse, StructuredInterpretationData } from "../types/appWorkspace";
import { useReviewPanelStatus } from "./useReviewPanelStatus";

function buildInterpretationData(): StructuredInterpretationData {
  return {
    document_id: "doc-1",
    processing_run_id: "run-1",
    created_at: "2026-02-28T00:00:00Z",
    fields: [],
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

describe("useReviewPanelStatus", () => {
  afterEach(() => {
    vi.useRealTimers();
    vi.clearAllMocks();
  });

  it("returns idle when there is no active document", () => {
    const { result } = renderHook(() =>
      useReviewPanelStatus({
        activeId: null,
        documentReview: {
          data: undefined,
          isFetching: false,
          isError: false,
          error: null,
          refetch: vi.fn().mockResolvedValue(undefined),
        },
        isActiveDocumentProcessing: false,
        hasActiveStructuredFilters: false,
        visibleCoreGroupsLength: 0,
      }),
    );

    expect(result.current.reviewPanelState).toBe("idle");
    expect(result.current.shouldShowReviewEmptyState).toBe(true);
  });

  it("keeps retry indicator visible for minimum time on manual retry", async () => {
    vi.useFakeTimers();
    const refetch = vi.fn().mockResolvedValue(undefined);
    const interpretationData = buildInterpretationData();

    const { result } = renderHook(() =>
      useReviewPanelStatus({
        activeId: "doc-1",
        documentReview: {
          data: buildDocumentReview(interpretationData),
          isFetching: false,
          isError: false,
          error: null,
          refetch,
        },
        isActiveDocumentProcessing: false,
        hasActiveStructuredFilters: false,
        visibleCoreGroupsLength: 1,
      }),
    );

    await act(async () => {
      const promise = result.current.handleRetryInterpretation();
      await Promise.resolve();
      await promise;
    });

    expect(refetch).toHaveBeenCalledTimes(1);
    expect(result.current.isRetryingInterpretation).toBe(true);

    await act(async () => {
      vi.advanceTimersByTime(300);
    });

    expect(result.current.isRetryingInterpretation).toBe(false);
  });
});
