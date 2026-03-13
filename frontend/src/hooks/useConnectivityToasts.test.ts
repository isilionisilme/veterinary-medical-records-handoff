import { act, renderHook } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { useConnectivityToasts } from "./useConnectivityToasts";

describe("useConnectivityToasts", () => {
  it("shows and auto-dismisses connectivity toast after 5 seconds", () => {
    vi.useFakeTimers();
    const { result } = renderHook(() => useConnectivityToasts());

    act(() => {
      result.current.showConnectivityToast();
    });
    expect(result.current.connectivityToast).toEqual({});

    act(() => {
      vi.advanceTimersByTime(4999);
    });
    expect(result.current.connectivityToast).toEqual({});

    act(() => {
      vi.advanceTimersByTime(1);
    });
    expect(result.current.connectivityToast).toBeNull();
    vi.useRealTimers();
  });

  it("throttles repeated toast opens within 5 seconds", () => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date("2026-02-28T00:00:00.000Z"));
    const { result } = renderHook(() => useConnectivityToasts());

    act(() => {
      result.current.showConnectivityToast();
      result.current.setConnectivityToast(null);
    });
    expect(result.current.connectivityToast).toBeNull();

    act(() => {
      vi.advanceTimersByTime(4999);
      vi.setSystemTime(new Date("2026-02-28T00:00:04.999Z"));
      result.current.showConnectivityToast();
    });
    expect(result.current.connectivityToast).toBeNull();

    act(() => {
      vi.advanceTimersByTime(1);
      vi.setSystemTime(new Date("2026-02-28T00:00:05.000Z"));
      result.current.showConnectivityToast();
    });
    expect(result.current.connectivityToast).toEqual({});

    vi.useRealTimers();
  });

  it("exposes list-error toast state setters", () => {
    const { result } = renderHook(() => useConnectivityToasts());
    expect(result.current.hasShownListErrorToast).toBe(false);

    act(() => {
      result.current.setHasShownListErrorToast(true);
    });
    expect(result.current.hasShownListErrorToast).toBe(true);
  });
});
