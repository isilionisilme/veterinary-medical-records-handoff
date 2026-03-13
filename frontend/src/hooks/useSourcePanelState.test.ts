import { act, renderHook } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { useSourcePanelState } from "./useSourcePanelState";

describe("useSourcePanelState", () => {
  it("shows notice and keeps panel closed when evidence has no page", () => {
    const onNotice = vi.fn();
    const { result } = renderHook(() => useSourcePanelState({ isDesktopForPin: true, onNotice }));

    act(() => {
      result.current.openFromEvidence({ page: 0, snippet: "ignored" });
    });

    expect(onNotice).toHaveBeenCalledWith("Sin evidencia disponible para este campo.");
    expect(result.current.isSourceOpen).toBe(false);
  });

  it("opens with normalized evidence and increments focus id", () => {
    const onNotice = vi.fn();
    const { result } = renderHook(() => useSourcePanelState({ isDesktopForPin: true, onNotice }));

    act(() => {
      result.current.openFromEvidence({ page: 3, snippet: "   Snippet relevante   " });
    });

    expect(result.current.isSourceOpen).toBe(true);
    expect(result.current.sourcePage).toBe(3);
    expect(result.current.sourceSnippet).toBe("Snippet relevante");
    expect(result.current.focusRequestId).toBe(1);
    expect(onNotice).toHaveBeenCalledWith("Mostrando fuente en la página 3.");
  });

  it("closes on Escape when open and not pinned", () => {
    const { result } = renderHook(() =>
      useSourcePanelState({ isDesktopForPin: true, onNotice: vi.fn() }),
    );

    act(() => {
      result.current.openSource();
    });

    expect(result.current.isSourceOpen).toBe(true);

    act(() => {
      window.dispatchEvent(new KeyboardEvent("keydown", { key: "Escape" }));
    });

    expect(result.current.isSourceOpen).toBe(false);
  });

  it("enforces pin rules and reset semantics", () => {
    const onNotice = vi.fn();
    const { result, rerender } = renderHook(
      ({ isDesktopForPin }: { isDesktopForPin: boolean }) =>
        useSourcePanelState({ isDesktopForPin, onNotice }),
      { initialProps: { isDesktopForPin: false } },
    );

    act(() => {
      result.current.togglePin();
    });
    expect(onNotice).toHaveBeenCalledWith("Fijar solo está disponible en escritorio.");
    expect(result.current.isSourcePinned).toBe(false);

    rerender({ isDesktopForPin: true });
    act(() => {
      result.current.togglePin();
    });
    expect(result.current.isSourcePinned).toBe(true);

    act(() => {
      result.current.reset();
    });
    expect(result.current.isSourcePinned).toBe(false);
    expect(result.current.sourcePage).toBeNull();
    expect(result.current.sourceSnippet).toBeNull();
    expect(result.current.isSourceOpen).toBe(false);
  });

  it("keeps overlay open when pinned and closes when unpinned", () => {
    const { result } = renderHook(() =>
      useSourcePanelState({ isDesktopForPin: true, onNotice: vi.fn() }),
    );

    act(() => {
      result.current.openSource();
      result.current.togglePin();
    });
    act(() => {
      result.current.closeOverlay();
    });
    expect(result.current.isSourceOpen).toBe(true);

    act(() => {
      result.current.togglePin();
    });
    act(() => {
      result.current.closeOverlay();
    });
    expect(result.current.isSourceOpen).toBe(false);
  });

  it("normalizes empty snippet to null and unpins when desktop mode is disabled", () => {
    const onNotice = vi.fn();
    const { result, rerender } = renderHook(
      ({ isDesktopForPin }: { isDesktopForPin: boolean }) =>
        useSourcePanelState({ isDesktopForPin, onNotice }),
      { initialProps: { isDesktopForPin: true } },
    );

    act(() => {
      result.current.openFromEvidence({ page: 5, snippet: "   " });
      result.current.togglePin();
    });
    expect(result.current.sourceSnippet).toBeNull();
    expect(result.current.isSourcePinned).toBe(true);

    rerender({ isDesktopForPin: false });
    expect(result.current.isSourcePinned).toBe(false);
  });

  it("supports rapid pin toggles and cleans keydown listener on unmount", () => {
    const { result, unmount } = renderHook(() =>
      useSourcePanelState({ isDesktopForPin: true, onNotice: vi.fn() }),
    );

    act(() => {
      result.current.openSource();
      result.current.togglePin();
      result.current.togglePin();
    });
    expect(result.current.isSourcePinned).toBe(false);

    unmount();
    act(() => {
      window.dispatchEvent(new KeyboardEvent("keydown", { key: "Escape" }));
    });
  });
});
