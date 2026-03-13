import { act, renderHook } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { PDF_ZOOM_STORAGE_KEY } from "../lib/pdfDebug";
import { usePdfZoom } from "./usePdfZoom";

function createScrollRef() {
  const container = document.createElement("div");
  document.body.appendChild(container);
  return { container, scrollRef: { current: container as HTMLDivElement | null } };
}

describe("usePdfZoom", () => {
  afterEach(() => {
    document.body.innerHTML = "";
    window.localStorage.clear();
  });

  it("reads and clamps initial zoom from localStorage", () => {
    window.localStorage.setItem(PDF_ZOOM_STORAGE_KEY, "10");
    const { scrollRef } = createScrollRef();

    const { result } = renderHook(() => usePdfZoom({ scrollRef }));

    expect(result.current.zoomLevel).toBe(2);
    expect(result.current.zoomPercent).toBe(200);
    expect(result.current.canZoomIn).toBe(false);
  });

  it("updates zoom via toolbar handlers and persists value", () => {
    const { scrollRef } = createScrollRef();
    const { result } = renderHook(() => usePdfZoom({ scrollRef }));

    act(() => {
      result.current.handleZoomOut();
    });
    expect(result.current.zoomLevel).toBeCloseTo(0.9);
    expect(window.localStorage.getItem(PDF_ZOOM_STORAGE_KEY)).toBe("0.9");

    act(() => {
      result.current.handleZoomFit();
    });
    expect(result.current.zoomLevel).toBe(1);
    expect(window.localStorage.getItem(PDF_ZOOM_STORAGE_KEY)).toBe("1");
  });

  it("zooms with ctrl+wheel events", () => {
    const { container, scrollRef } = createScrollRef();
    const { result } = renderHook(() => usePdfZoom({ scrollRef }));

    act(() => {
      const event = new WheelEvent("wheel", { deltaY: -100, ctrlKey: true, cancelable: true });
      container.dispatchEvent(event);
    });
    expect(result.current.zoomLevel).toBeCloseTo(1.1);

    act(() => {
      const event = new WheelEvent("wheel", { deltaY: 100, ctrlKey: true, cancelable: true });
      container.dispatchEvent(event);
    });
    expect(result.current.zoomLevel).toBe(1);
  });
});
