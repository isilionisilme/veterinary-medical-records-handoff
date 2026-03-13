import { act, renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { type ReactNode } from "react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { fetchDocuments, uploadDocument } from "../api/documentApi";
import { useDocumentUpload } from "./useDocumentUpload";

vi.mock("../api/documentApi", () => ({
  fetchDocuments: vi.fn(),
  uploadDocument: vi.fn(),
}));

const mockedFetchDocuments = vi.mocked(fetchDocuments);
const mockedUploadDocument = vi.mocked(uploadDocument);

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

describe("useDocumentUpload", () => {
  afterEach(() => {
    vi.clearAllMocks();
  });

  it("uploads a document and triggers open flow callbacks", async () => {
    mockedUploadDocument.mockResolvedValueOnce({
      document_id: "doc-2",
      status: "PROCESSING",
      created_at: "2026-02-28T12:00:00Z",
    });
    mockedFetchDocuments.mockResolvedValueOnce({
      items: [],
      limit: 50,
      offset: 0,
      total: 0,
    });

    const { queryClient, wrapper } = createHarness();
    queryClient.setQueryData(["documents", "list"], {
      items: [
        {
          document_id: "doc-1",
          original_filename: "existing.pdf",
          created_at: "2026-02-28T11:00:00Z",
          status: "COMPLETED",
          status_label: "Completed",
          failure_type: null,
        },
      ],
      limit: 50,
      offset: 0,
      total: 1,
    });
    const requestPdfLoad = vi.fn();
    const onUploadFeedback = vi.fn();
    const onSetActiveId = vi.fn();
    const onSetActiveViewerTab = vi.fn();
    const pendingAutoOpenDocumentIdRef = { current: null as string | null };

    const { result } = renderHook(
      () =>
        useDocumentUpload({
          requestPdfLoad,
          pendingAutoOpenDocumentIdRef,
          onUploadFeedback,
          onSetActiveId,
          onSetActiveViewerTab,
        }),
      { wrapper },
    );

    const file = new File(["file-content"], "new.pdf", { type: "application/pdf" });
    act(() => {
      result.current.uploadMutation.mutate(file);
    });

    await waitFor(() => {
      expect(mockedUploadDocument).toHaveBeenCalledWith(file);
    });
    await waitFor(() => {
      expect(requestPdfLoad).toHaveBeenCalledWith("doc-2");
    });
    expect(onSetActiveViewerTab).toHaveBeenCalledWith("document");
    expect(onSetActiveId).toHaveBeenCalledWith("doc-2");
    expect(onUploadFeedback).toHaveBeenCalledWith({
      kind: "success",
      message: "Documento subido correctamente.",
      documentId: "doc-2",
      showOpenAction: false,
    });
    expect(pendingAutoOpenDocumentIdRef.current).toBe("doc-2");
  });

  it("surfaces upload error feedback", async () => {
    mockedUploadDocument.mockRejectedValueOnce(new Error("boom"));

    const { wrapper } = createHarness();
    const onUploadFeedback = vi.fn();

    const { result } = renderHook(
      () =>
        useDocumentUpload({
          requestPdfLoad: vi.fn(),
          pendingAutoOpenDocumentIdRef: { current: null },
          onUploadFeedback,
          onSetActiveId: vi.fn(),
          onSetActiveViewerTab: vi.fn(),
        }),
      { wrapper },
    );

    act(() => {
      result.current.uploadMutation.mutate(new File(["file-content"], "broken.pdf"));
    });

    await waitFor(() => {
      expect(onUploadFeedback).toHaveBeenCalledWith(
        expect.objectContaining({
          kind: "error",
        }),
      );
    });
  });
});
