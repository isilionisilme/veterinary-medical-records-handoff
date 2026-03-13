import { act, renderHook, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import {
  DEFAULT_REVIEW_SPLIT_RATIO,
  REVIEW_SPLIT_RATIO_STORAGE_KEY,
} from "../constants/appWorkspace";
import { useReviewSplitPanel } from "./useReviewSplitPanel";

function buildGrid(width: number) {
  const grid = document.createElement("div");
  Object.defineProperty(grid, "getBoundingClientRect", {
    value: () => ({ width, height: 0, top: 0, left: 0, bottom: 0, right: 0, x: 0, y: 0 }),
  });
  Object.defineProperty(grid, "scrollWidth", { value: width, configurable: true });
  return grid;
}

beforeEach(() => {
  window.localStorage.clear();
  vi.stubGlobal(
    "ResizeObserver",
    class {
      observe() {}
      disconnect() {}
    },
  );
});

describe("useReviewSplitPanel", () => {
  it("uses default split ratio when localStorage value is invalid", () => {
    window.localStorage.setItem(REVIEW_SPLIT_RATIO_STORAGE_KEY, "invalid");

    const { result } = renderHook(() =>
      useReviewSplitPanel({
        isDocsSidebarExpanded: false,
        isDocsSidebarPinned: false,
        shouldAutoCollapseDocsSidebar: false,
      }),
    );

    expect(result.current.reviewSplitRatio).toBe(DEFAULT_REVIEW_SPLIT_RATIO);
  });

  it("updates ratio through keyboard controls and resets with Home", () => {
    const { result } = renderHook(() =>
      useReviewSplitPanel({
        isDocsSidebarExpanded: true,
        isDocsSidebarPinned: false,
        shouldAutoCollapseDocsSidebar: false,
      }),
    );
    const grid = buildGrid(1400);
    const preventDefault = vi.fn();

    act(() => {
      result.current.handleReviewSplitGridRef(grid);
    });
    const initialRatio = result.current.reviewSplitRatio;

    act(() => {
      result.current.handleReviewSplitKeyboard({
        key: "ArrowRight",
        preventDefault,
      } as unknown as Parameters<
        ReturnType<typeof useReviewSplitPanel>["handleReviewSplitKeyboard"]
      >[0]);
    });
    expect(result.current.reviewSplitRatio).toBeGreaterThan(initialRatio);

    act(() => {
      result.current.handleReviewSplitKeyboard({
        key: "Home",
        preventDefault,
      } as unknown as Parameters<
        ReturnType<typeof useReviewSplitPanel>["handleReviewSplitKeyboard"]
      >[0]);
    });
    expect(result.current.reviewSplitRatio).toBe(DEFAULT_REVIEW_SPLIT_RATIO);
  });

  it("updates split ratio while dragging and finalizes on mouse up", async () => {
    const { result } = renderHook(() =>
      useReviewSplitPanel({
        isDocsSidebarExpanded: false,
        isDocsSidebarPinned: false,
        shouldAutoCollapseDocsSidebar: false,
      }),
    );
    const grid = buildGrid(1200);
    const initialRatio = result.current.reviewSplitRatio;

    act(() => {
      result.current.handleReviewSplitGridRef(grid);
      result.current.startReviewSplitDragging({
        clientX: 100,
        preventDefault: vi.fn(),
      } as unknown as Parameters<
        ReturnType<typeof useReviewSplitPanel>["startReviewSplitDragging"]
      >[0]);
    });

    act(() => {
      window.dispatchEvent(new MouseEvent("mousemove", { clientX: 200 }));
      window.dispatchEvent(new MouseEvent("mouseup"));
    });

    await waitFor(() => expect(result.current.reviewSplitRatio).toBeGreaterThan(initialRatio));
    expect(document.body.style.cursor).toBe("");
  });

  it("persists ratio changes to localStorage", async () => {
    const { result } = renderHook(() =>
      useReviewSplitPanel({
        isDocsSidebarExpanded: false,
        isDocsSidebarPinned: false,
        shouldAutoCollapseDocsSidebar: false,
      }),
    );
    const grid = buildGrid(1400);

    act(() => {
      result.current.handleReviewSplitGridRef(grid);
      result.current.handleReviewSplitKeyboard({
        key: "ArrowLeft",
        preventDefault: vi.fn(),
      } as unknown as Parameters<
        ReturnType<typeof useReviewSplitPanel>["handleReviewSplitKeyboard"]
      >[0]);
    });

    await waitFor(() =>
      expect(window.localStorage.getItem(REVIEW_SPLIT_RATIO_STORAGE_KEY)).toBe(
        String(result.current.reviewSplitRatio),
      ),
    );
  });
});
