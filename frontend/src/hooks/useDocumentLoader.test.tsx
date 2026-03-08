import { act, renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { type ReactNode } from "react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { fetchOriginalPdf } from "../api/documentApi";
import { useDocumentLoader } from "./useDocumentLoader";

vi.mock("../api/documentApi", () => ({
  fetchOriginalPdf: vi.fn(),
}));

const mockedFetchOriginalPdf = vi.mocked(fetchOriginalPdf);

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

describe("useDocumentLoader", () => {
  afterEach(() => {
    vi.clearAllMocks();
    vi.useRealTimers();
  });

  it("loads pdf and updates fileUrl/filename", async () => {
    mockedFetchOriginalPdf.mockResolvedValueOnce({
      data: "pdf-data",
      filename: "record.pdf",
    });
    const onUploadFeedback = vi.fn();
    const { result } = renderHook(() => useDocumentLoader({ onUploadFeedback }), {
      wrapper: createWrapper(),
    });

    act(() => {
      result.current.pendingAutoOpenDocumentIdRef.current = "doc-1";
      result.current.requestPdfLoad("doc-1");
    });

    await waitFor(() => {
      expect(result.current.fileUrl).toBe("pdf-data");
      expect(result.current.filename).toBe("record.pdf");
    });
    expect(result.current.pendingAutoOpenDocumentIdRef.current).toBeNull();
    expect(onUploadFeedback).toHaveBeenCalledTimes(1);
  });

  it("retries once for regular document load failures and eventually succeeds", async () => {
    mockedFetchOriginalPdf
      .mockRejectedValueOnce(new Error("temporary failure"))
      .mockResolvedValueOnce({
        data: "pdf-data-retry",
        filename: "record-retry.pdf",
      });

    const onUploadFeedback = vi.fn();
    const { result } = renderHook(() => useDocumentLoader({ onUploadFeedback }), {
      wrapper: createWrapper(),
    });

    act(() => {
      result.current.requestPdfLoad("doc-retry");
    });

    await waitFor(
      () => {
        expect(result.current.fileUrl).toBe("pdf-data-retry");
        expect(result.current.filename).toBe("record-retry.pdf");
        expect(mockedFetchOriginalPdf).toHaveBeenCalledTimes(2);
      },
      { timeout: 4000 },
    );
  });

  it("keeps requestPdfLoad stable across rerenders", () => {
    const onUploadFeedback = vi.fn();
    const { result, rerender } = renderHook(() => useDocumentLoader({ onUploadFeedback }), {
      wrapper: createWrapper(),
    });

    const firstReference = result.current.requestPdfLoad;
    rerender();
    const secondReference = result.current.requestPdfLoad;

    expect(secondReference).toBe(firstReference);
  });
});
