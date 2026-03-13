import { act, renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { type ReactNode } from "react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { triggerReprocess } from "../api/documentApi";
import { useReprocessing } from "./useReprocessing";

vi.mock("../api/documentApi", () => ({
  triggerReprocess: vi.fn(),
}));

const mockedTriggerReprocess = vi.mocked(triggerReprocess);

function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  return ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
}

describe("useReprocessing", () => {
  afterEach(() => {
    vi.clearAllMocks();
  });

  it("closes retry modal and starts reprocess for active document", async () => {
    mockedTriggerReprocess.mockResolvedValueOnce({
      run_id: "run-1",
      state: "QUEUED",
      failure_type: null,
    });
    const onActionFeedback = vi.fn();
    const { result } = renderHook(
      ({ activeId, isActiveDocumentProcessing }) =>
        useReprocessing({ activeId, isActiveDocumentProcessing, onActionFeedback }),
      {
        initialProps: { activeId: "doc-1", isActiveDocumentProcessing: false },
        wrapper: createWrapper(),
      },
    );

    act(() => {
      result.current.setShowRetryModal(true);
      result.current.handleConfirmRetry();
    });

    expect(result.current.showRetryModal).toBe(false);
    await waitFor(() => {
      expect(mockedTriggerReprocess).toHaveBeenCalledWith("doc-1");
    });
    expect(onActionFeedback).toHaveBeenCalledWith({
      kind: "success",
      message: "Reprocesamiento iniciado.",
    });
  });

  it("tracks processing lifecycle and resets when processing ends", async () => {
    mockedTriggerReprocess.mockResolvedValueOnce({
      run_id: "run-2",
      state: "QUEUED",
      failure_type: null,
    });
    const onActionFeedback = vi.fn();
    const { result, rerender } = renderHook(
      ({ activeId, isActiveDocumentProcessing }) =>
        useReprocessing({ activeId, isActiveDocumentProcessing, onActionFeedback }),
      {
        initialProps: { activeId: "doc-2", isActiveDocumentProcessing: true },
        wrapper: createWrapper(),
      },
    );

    act(() => {
      result.current.handleConfirmRetry();
    });

    await waitFor(() => {
      expect(result.current.reprocessingDocumentId).toBe("doc-2");
      expect(result.current.hasObservedProcessingAfterReprocess).toBe(true);
    });

    rerender({ activeId: "doc-2", isActiveDocumentProcessing: false });

    await waitFor(() => {
      expect(result.current.reprocessingDocumentId).toBeNull();
      expect(result.current.hasObservedProcessingAfterReprocess).toBe(false);
    });
  });
});
