import { act, renderHook, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { DOCS_SIDEBAR_PIN_STORAGE_KEY } from "../constants/appWorkspace";
import { useDocumentsSidebar } from "./useDocumentsSidebar";

function mockMatchMedia({ docsHover = true, sourcePin = true } = {}) {
  const implementation = (query: string) => {
    const matches = query.includes("1280px") ? sourcePin : docsHover;
    return {
      matches,
      media: query,
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      addListener: vi.fn(),
      removeListener: vi.fn(),
      dispatchEvent: vi.fn(),
      onchange: null,
    } as unknown as MediaQueryList;
  };
  Object.defineProperty(window, "matchMedia", {
    writable: true,
    configurable: true,
    value: vi.fn(implementation),
  });
}

describe("useDocumentsSidebar", () => {
  beforeEach(() => {
    window.localStorage.clear();
  });

  it("loads pinned state from localStorage", () => {
    window.localStorage.setItem(DOCS_SIDEBAR_PIN_STORAGE_KEY, "1");
    mockMatchMedia();
    const sidebarUploadDragDepthRef = { current: 0 };
    const { result } = renderHook(() =>
      useDocumentsSidebar({
        activeId: null,
        isDragOverSidebarUpload: false,
        sidebarUploadDragDepthRef,
      }),
    );

    expect(result.current.isDocsSidebarPinned).toBe(true);
  });

  it("expands on hover and collapses on leave when auto-collapse is enabled", async () => {
    mockMatchMedia({ docsHover: true, sourcePin: true });
    const sidebarUploadDragDepthRef = { current: 0 };
    const { result } = renderHook(() =>
      useDocumentsSidebar({
        activeId: "doc-1",
        isDragOverSidebarUpload: false,
        sidebarUploadDragDepthRef,
      }),
    );

    await waitFor(() => expect(result.current.shouldAutoCollapseDocsSidebar).toBe(true));
    expect(result.current.isDocsSidebarExpanded).toBe(false);

    act(() => {
      result.current.handleDocsSidebarMouseEnter({
        buttons: 0,
      } as Parameters<ReturnType<typeof useDocumentsSidebar>["handleDocsSidebarMouseEnter"]>[0]);
    });
    expect(result.current.isDocsSidebarExpanded).toBe(true);

    act(() => {
      result.current.handleDocsSidebarMouseLeave();
    });
    expect(result.current.isDocsSidebarExpanded).toBe(false);
  });

  it("does not expand on hover while dragging over sidebar upload area", async () => {
    mockMatchMedia({ docsHover: true, sourcePin: true });
    const sidebarUploadDragDepthRef = { current: 1 };
    const { result } = renderHook(() =>
      useDocumentsSidebar({
        activeId: "doc-2",
        isDragOverSidebarUpload: true,
        sidebarUploadDragDepthRef,
      }),
    );

    await waitFor(() => expect(result.current.shouldAutoCollapseDocsSidebar).toBe(true));
    act(() => {
      result.current.handleDocsSidebarMouseEnter({
        buttons: 0,
      } as Parameters<ReturnType<typeof useDocumentsSidebar>["handleDocsSidebarMouseEnter"]>[0]);
    });

    expect(result.current.isDocsSidebarExpanded).toBe(false);
  });

  it("toggles pin and suppresses immediate hover after sidebar upload drop", async () => {
    mockMatchMedia({ docsHover: true, sourcePin: true });
    const sidebarUploadDragDepthRef = { current: 0 };
    const { result } = renderHook(() =>
      useDocumentsSidebar({
        activeId: "doc-3",
        isDragOverSidebarUpload: false,
        sidebarUploadDragDepthRef,
      }),
    );

    await waitFor(() => expect(result.current.isDesktopForPin).toBe(true));
    await waitFor(() => expect(result.current.shouldAutoCollapseDocsSidebar).toBe(true));

    act(() => {
      result.current.handleToggleDocsSidebarPin();
    });
    expect(result.current.isDocsSidebarPinned).toBe(true);
    expect(result.current.isDocsSidebarExpanded).toBe(true);

    act(() => {
      result.current.handleToggleDocsSidebarPin();
      result.current.handleDocsSidebarMouseLeave();
    });
    expect(result.current.isDocsSidebarPinned).toBe(false);
    expect(result.current.isDocsSidebarExpanded).toBe(false);

    act(() => {
      result.current.notifySidebarUploadDrop();
      result.current.handleDocsSidebarMouseEnter({
        buttons: 0,
      } as Parameters<ReturnType<typeof useDocumentsSidebar>["handleDocsSidebarMouseEnter"]>[0]);
    });

    expect(result.current.isDocsSidebarExpanded).toBe(false);
  });
});
