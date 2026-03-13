import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { type ReactNode } from "react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { fetchDocuments } from "../api/documentApi";
import { useDocumentListPolling } from "./useDocumentListPolling";

vi.mock("../api/documentApi", () => ({
  fetchDocuments: vi.fn(),
}));

const mockedFetchDocuments = vi.mocked(fetchDocuments);

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
  return { wrapper };
}

describe("useDocumentListPolling", () => {
  afterEach(() => {
    vi.clearAllMocks();
  });

  it("sorts documents by created_at descending", async () => {
    mockedFetchDocuments.mockResolvedValueOnce({
      items: [
        {
          document_id: "doc-old",
          original_filename: "old.pdf",
          created_at: "2026-02-27T10:00:00Z",
          status: "COMPLETED",
          status_label: "Completed",
          failure_type: null,
        },
        {
          document_id: "doc-new",
          original_filename: "new.pdf",
          created_at: "2026-02-28T10:00:00Z",
          status: "COMPLETED",
          status_label: "Completed",
          failure_type: null,
        },
      ],
      limit: 50,
      offset: 0,
      total: 2,
    });

    const { wrapper } = createHarness();
    const { result } = renderHook(
      () => useDocumentListPolling({ setIsDocsSidebarHovered: vi.fn() }),
      { wrapper },
    );

    await waitFor(() => {
      expect(result.current.documentList.status).toBe("success");
    });
    expect(result.current.sortedDocuments.map((item) => item.document_id)).toEqual([
      "doc-new",
      "doc-old",
    ]);
  });

  it("collapses sidebar hover state when list is empty", async () => {
    mockedFetchDocuments.mockResolvedValueOnce({
      items: [],
      limit: 50,
      offset: 0,
      total: 0,
    });

    const setIsDocsSidebarHovered = vi.fn();
    const { wrapper } = createHarness();
    renderHook(() => useDocumentListPolling({ setIsDocsSidebarHovered }), { wrapper });

    await waitFor(() => {
      expect(setIsDocsSidebarHovered).toHaveBeenCalledWith(false);
    });
  });
});
