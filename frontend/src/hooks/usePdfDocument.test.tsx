import { act, renderHook, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { usePdfDocument } from "./usePdfDocument";

const getDocumentMock = vi.fn();

vi.mock("pdfjs-dist", () => ({
  getDocument: (...args: unknown[]) => getDocumentMock(...args),
}));

function createScrollRef() {
  const container = document.createElement("div");
  container.scrollTo = vi.fn();
  document.body.appendChild(container);
  return { scrollRef: { current: container as HTMLDivElement | null }, container };
}

describe("usePdfDocument", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    vi.clearAllMocks();
    document.body.innerHTML = "";
  });

  it("returns empty state when fileUrl is null", () => {
    const { scrollRef } = createScrollRef();
    const { result } = renderHook(() =>
      usePdfDocument({
        fileUrl: null,
        scrollRef,
        cancelAllRenderTasks: vi.fn(),
      }),
    );

    expect(result.current.pdfDoc).toBeNull();
    expect(result.current.totalPages).toBe(0);
    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it("loads PDF, reports total pages, and cleans up on unmount", async () => {
    const { scrollRef, container } = createScrollRef();
    const cancelAllRenderTasks = vi.fn();
    const destroyDoc = vi.fn();
    const destroyLoadingTask = vi.fn();
    const mockDoc = { numPages: 3, destroy: destroyDoc };

    (fetch as unknown as ReturnType<typeof vi.fn>).mockResolvedValue({
      ok: true,
      arrayBuffer: async () => new ArrayBuffer(8),
    });
    getDocumentMock.mockReturnValue({
      promise: Promise.resolve(mockDoc),
      destroy: destroyLoadingTask,
    });

    const { result, unmount } = renderHook(() =>
      usePdfDocument({
        fileUrl: "https://example.test/file.pdf",
        scrollRef,
        cancelAllRenderTasks,
      }),
    );

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
      expect(result.current.totalPages).toBe(3);
      expect(result.current.pdfDoc).toBe(mockDoc);
    });

    expect(container.scrollTo).toHaveBeenCalledWith({ top: 0, behavior: "auto" });

    act(() => {
      unmount();
    });

    expect(cancelAllRenderTasks).toHaveBeenCalled();
    expect(destroyDoc).toHaveBeenCalled();
    expect(destroyLoadingTask).toHaveBeenCalled();
  });

  it("retries PDF loading task after a transient failure", async () => {
    const { scrollRef } = createScrollRef();
    const cancelAllRenderTasks = vi.fn();
    const mockDoc = { numPages: 2, destroy: vi.fn() };

    (fetch as unknown as ReturnType<typeof vi.fn>).mockResolvedValue({
      ok: true,
      arrayBuffer: async () => new ArrayBuffer(8),
    });

    getDocumentMock
      .mockReturnValueOnce({
        promise: Promise.reject(new Error("transient parse error")),
        destroy: vi.fn(),
      })
      .mockReturnValueOnce({
        promise: Promise.resolve(mockDoc),
        destroy: vi.fn(),
      });

    const { result } = renderHook(() =>
      usePdfDocument({
        fileUrl: "https://example.test/file.pdf",
        scrollRef,
        cancelAllRenderTasks,
      }),
    );

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
      expect(result.current.error).toBeNull();
      expect(result.current.totalPages).toBe(2);
    });
    expect(getDocumentMock).toHaveBeenCalledTimes(2);
  });
});
