import { act, renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { type ReactNode } from "react";
import { afterEach, describe, expect, it, vi } from "vitest";

import {
  fetchDocumentDetails,
  fetchDocumentReview,
  fetchProcessingHistory,
  fetchVisitScopingMetrics,
} from "../api/documentApi";
import { useActiveDocumentQueries } from "./useActiveDocumentQueries";

vi.mock("../api/documentApi", () => ({
  fetchDocumentDetails: vi.fn(),
  fetchDocumentReview: vi.fn(),
  fetchProcessingHistory: vi.fn(),
  fetchVisitScopingMetrics: vi.fn(),
}));

const mockedFetchDocumentDetails = vi.mocked(fetchDocumentDetails);
const mockedFetchDocumentReview = vi.mocked(fetchDocumentReview);
const mockedFetchProcessingHistory = vi.mocked(fetchProcessingHistory);
const mockedFetchVisitScopingMetrics = vi.mocked(fetchVisitScopingMetrics);

function createHarness() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });
  const wrapper = ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
  return { wrapper, queryClient };
}

describe("useActiveDocumentQueries", () => {
  afterEach(() => {
    vi.clearAllMocks();
  });

  it("derives run metadata and processing state from active document queries", async () => {
    mockedFetchDocumentDetails.mockResolvedValueOnce({
      document_id: "doc-1",
      original_filename: "a.pdf",
      content_type: "application/pdf",
      file_size: 1,
      created_at: "2026-02-28T00:00:00Z",
      updated_at: "2026-02-28T00:00:00Z",
      status: "PROCESSING",
      status_message: "processing",
      failure_type: null,
      review_status: "IN_REVIEW",
      reviewed_at: null,
      reviewed_by: null,
      latest_run: { run_id: "run-1", state: "RUNNING", failure_type: null },
    });
    mockedFetchProcessingHistory.mockResolvedValueOnce({ document_id: "doc-1", runs: [] });
    mockedFetchDocumentReview.mockResolvedValueOnce({
      document_id: "doc-1",
      latest_completed_run: {
        run_id: "run-0",
        state: "COMPLETED",
        completed_at: null,
        failure_type: null,
      },
      active_interpretation: {
        interpretation_id: "interp-1",
        version_number: 1,
        data: {
          document_id: "doc-1",
          processing_run_id: "run-1",
          created_at: "2026-02-28T00:00:00Z",
          fields: [],
        },
      },
      raw_text_artifact: { run_id: "run-1", available: true },
      review_status: "IN_REVIEW",
      reviewed_at: null,
      reviewed_by: null,
    });
    mockedFetchVisitScopingMetrics.mockResolvedValueOnce({
      document_id: "doc-1",
      run_id: "run-1",
      summary: {
        total_visits: 1,
        assigned_visits: 1,
        anchored_visits: 1,
        unassigned_field_count: 0,
        raw_text_available: true,
      },
      visits: [],
    });

    const { wrapper, queryClient } = createHarness();
    const { result } = renderHook(
      () =>
        useActiveDocumentQueries({
          activeId: "doc-1",
          shouldFetchVisitScopingMetrics: true,
          documentList: {
            refetch: vi.fn(),
            isFetching: false,
            isLoading: false,
            data: { items: [], limit: 50, offset: 0, total: 0 },
          },
          showRefreshFeedback: false,
          setShowRefreshFeedback: vi.fn(),
          refreshFeedbackTimerRef: { current: null },
          queryClient,
        }),
      { wrapper },
    );

    await waitFor(() => {
      expect(result.current.latestRunId).toBe("run-1");
    });

    expect(result.current.rawTextRunId).toBe("run-1");
    expect(result.current.latestState).toBe("RUNNING");
    expect(result.current.isProcessing).toBe(true);
  });

  it("handleRefresh toggles refresh feedback and refetches list", () => {
    vi.useFakeTimers();
    const listRefetch = vi.fn();
    const setFeedback = vi.fn();
    const { wrapper, queryClient } = createHarness();
    const refreshFeedbackTimerRef = { current: null as number | null };

    const { result } = renderHook(
      () =>
        useActiveDocumentQueries({
          activeId: null,
          shouldFetchVisitScopingMetrics: false,
          documentList: {
            refetch: listRefetch,
            isFetching: false,
            isLoading: false,
            data: { items: [], limit: 50, offset: 0, total: 0 },
          },
          showRefreshFeedback: false,
          setShowRefreshFeedback: setFeedback,
          refreshFeedbackTimerRef,
          queryClient,
        }),
      { wrapper },
    );

    act(() => {
      result.current.handleRefresh();
    });
    expect(setFeedback).toHaveBeenCalledWith(true);
    expect(listRefetch).toHaveBeenCalledTimes(1);

    act(() => {
      vi.advanceTimersByTime(350);
    });
    expect(setFeedback).toHaveBeenCalledWith(false);
    vi.useRealTimers();
  });
});
