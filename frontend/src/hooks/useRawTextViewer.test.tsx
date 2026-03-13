import { act, renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { type ReactNode } from "react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { fetchRawText } from "../api/documentApi";
import { ApiResponseError } from "../types/appWorkspace";
import { useRawTextViewer } from "./useRawTextViewer";

vi.mock("../api/documentApi", () => ({
  fetchRawText: vi.fn(),
  copyTextToClipboard: vi.fn(),
}));

const mockedFetchRawText = vi.mocked(fetchRawText);

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

describe("useRawTextViewer", () => {
  afterEach(() => {
    vi.clearAllMocks();
  });

  it("loads raw text and resolves search notice", async () => {
    mockedFetchRawText.mockResolvedValueOnce({
      run_id: "run-1",
      text: "El paciente presenta mejoria clinica",
      generated_at: "2026-02-28T10:00:00Z",
    });
    const { wrapper } = createHarness();
    const { result } = renderHook(
      () => useRawTextViewer({ rawTextRunId: "run-1", activeViewerTab: "raw_text" }),
      { wrapper },
    );

    await waitFor(() => {
      expect(result.current.rawTextContent).toContain("mejoria");
    });
    act(() => {
      result.current.setRawSearch("clinica");
    });
    act(() => {
      result.current.handleRawSearch();
    });

    expect(result.current.rawSearchNotice).toBe("Coincidencia encontrada.");
    expect(result.current.canSearchRawText).toBe(true);
    expect(result.current.canCopyRawText).toBe(true);
  });

  it("hides raw-text error message for not-available reason", async () => {
    mockedFetchRawText.mockRejectedValueOnce(
      new ApiResponseError("raw text unavailable", "t", "X", "RAW_TEXT_NOT_AVAILABLE"),
    );
    const { wrapper } = createHarness();
    const { result } = renderHook(
      () => useRawTextViewer({ rawTextRunId: "run-2", activeViewerTab: "raw_text" }),
      { wrapper },
    );

    await waitFor(() => {
      expect(result.current.isRawTextLoading).toBe(false);
    });
    expect(result.current.rawTextErrorMessage).toBeNull();
  });
});
