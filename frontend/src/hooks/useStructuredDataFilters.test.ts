import { act, renderHook, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { useStructuredDataFilters } from "./useStructuredDataFilters";

describe("useStructuredDataFilters", () => {
  it("returns default filter state on init", () => {
    const { result } = renderHook(() =>
      useStructuredDataFilters({
        activeConfidencePolicy: { version: "v1" },
      }),
    );

    expect(result.current.structuredSearchInput).toBe("");
    expect(result.current.structuredDataFilters).toEqual({
      searchTerm: "",
      selectedConfidence: [],
      onlyCritical: false,
      onlyWithValue: false,
      onlyEmpty: false,
    });
    expect(result.current.hasActiveStructuredFilters).toBe(false);
  });

  it("debounces search input for 200ms before updating searchTerm", () => {
    vi.useFakeTimers();
    const { result } = renderHook(() =>
      useStructuredDataFilters({
        activeConfidencePolicy: { version: "v1" },
      }),
    );

    try {
      act(() => {
        result.current.setStructuredSearchInput("luna");
      });

      expect(result.current.structuredDataFilters.searchTerm).toBe("");
      expect(result.current.hasActiveStructuredFilters).toBe(false);

      act(() => {
        vi.advanceTimersByTime(199);
      });

      expect(result.current.structuredDataFilters.searchTerm).toBe("");

      act(() => {
        vi.advanceTimersByTime(1);
      });

      expect(result.current.structuredDataFilters.searchTerm).toBe("luna");
      expect(result.current.hasActiveStructuredFilters).toBe(true);
    } finally {
      vi.useRealTimers();
    }
  });

  it("resets filters and focuses the search input", () => {
    const { result } = renderHook(() =>
      useStructuredDataFilters({
        activeConfidencePolicy: { version: "v1" },
      }),
    );
    const input = document.createElement("input");
    const focusSpy = vi.spyOn(input, "focus");

    act(() => {
      result.current.setStructuredSearchInput("term");
      result.current.setSelectedConfidenceBuckets(["high"]);
      result.current.setShowOnlyCritical(true);
      result.current.setShowOnlyWithValue(true);
      result.current.setShowOnlyEmpty(true);
      result.current.structuredSearchInputRef.current = input;
      result.current.resetStructuredFilters();
    });

    expect(result.current.structuredSearchInput).toBe("");
    expect(result.current.selectedConfidenceBuckets).toEqual([]);
    expect(result.current.showOnlyCritical).toBe(false);
    expect(result.current.showOnlyWithValue).toBe(false);
    expect(result.current.showOnlyEmpty).toBe(false);
    expect(focusSpy).toHaveBeenCalledTimes(1);
  });

  it("clears selected confidence buckets when no policy is active", async () => {
    const { result } = renderHook(() =>
      useStructuredDataFilters({
        activeConfidencePolicy: null,
      }),
    );

    act(() => {
      result.current.setSelectedConfidenceBuckets(["medium"]);
    });

    await waitFor(() => expect(result.current.selectedConfidenceBuckets).toEqual([]));
  });
});
