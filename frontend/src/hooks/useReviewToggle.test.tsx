import { act, renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { type ReactNode } from "react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { markDocumentReviewed, reopenDocumentReview } from "../api/documentApi";
import { useReviewToggle } from "./useReviewToggle";

vi.mock("../api/documentApi", () => ({
  markDocumentReviewed: vi.fn(),
  reopenDocumentReview: vi.fn(),
}));

const mockedMarkDocumentReviewed = vi.mocked(markDocumentReviewed);
const mockedReopenDocumentReview = vi.mocked(reopenDocumentReview);

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
  return { queryClient, wrapper };
}

describe("useReviewToggle", () => {
  afterEach(() => {
    vi.clearAllMocks();
  });

  it("updates cached review status and emits success feedback", async () => {
    mockedMarkDocumentReviewed.mockResolvedValueOnce({
      document_id: "doc-1",
      review_status: "REVIEWED",
      reviewed_at: "2026-02-28T12:00:00Z",
      reviewed_by: "qa-user",
    });

    const { queryClient, wrapper } = createHarness();
    queryClient.setQueryData(["documents", "list"], {
      items: [
        {
          document_id: "doc-1",
          original_filename: "a.pdf",
          created_at: "2026-02-28T11:00:00Z",
          status: "COMPLETED",
          status_label: "Completed",
          failure_type: null,
          review_status: "IN_REVIEW",
          reviewed_at: null,
          reviewed_by: null,
        },
      ],
      limit: 50,
      offset: 0,
      total: 1,
    });
    queryClient.setQueryData(["documents", "detail", "doc-1"], {
      document_id: "doc-1",
      original_filename: "a.pdf",
      content_type: "application/pdf",
      file_size: 1,
      created_at: "2026-02-28T11:00:00Z",
      updated_at: "2026-02-28T11:00:00Z",
      status: "COMPLETED",
      status_message: "",
      failure_type: null,
      review_status: "IN_REVIEW",
      reviewed_at: null,
      reviewed_by: null,
      latest_run: null,
    });
    queryClient.setQueryData(["documents", "review", "doc-1"], {
      document_id: "doc-1",
      latest_completed_run: null,
      active_interpretation: null,
      raw_text_artifact: null,
      review_status: "IN_REVIEW",
      reviewed_at: null,
      reviewed_by: null,
    });

    const onActionFeedback = vi.fn();
    const { result } = renderHook(() => useReviewToggle({ onActionFeedback }), { wrapper });

    act(() => {
      result.current.reviewToggleMutation.mutate({ docId: "doc-1", target: "reviewed" });
    });

    await waitFor(() => {
      expect(mockedMarkDocumentReviewed).toHaveBeenCalledWith("doc-1");
    });
    await waitFor(() => {
      expect(onActionFeedback).toHaveBeenCalledWith({
        kind: "success",
        message: "Documento marcado como revisado.",
      });
    });
  });

  it("calls reopen endpoint for in_review target", async () => {
    mockedReopenDocumentReview.mockResolvedValueOnce({
      document_id: "doc-2",
      review_status: "IN_REVIEW",
      reviewed_at: null,
      reviewed_by: null,
    });

    const { wrapper } = createHarness();
    const { result } = renderHook(() => useReviewToggle({ onActionFeedback: vi.fn() }), {
      wrapper,
    });

    act(() => {
      result.current.reviewToggleMutation.mutate({ docId: "doc-2", target: "in_review" });
    });

    await waitFor(() => {
      expect(mockedReopenDocumentReview).toHaveBeenCalledWith("doc-2");
    });
  });
});
