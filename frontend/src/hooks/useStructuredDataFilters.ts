import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { type ConfidenceBucket } from "../lib/structuredDataFilters";

type UseStructuredDataFiltersParams = {
  activeConfidencePolicy: unknown;
};

export function useStructuredDataFilters({
  activeConfidencePolicy,
}: UseStructuredDataFiltersParams) {
  const [structuredSearchInput, setStructuredSearchInput] = useState("");
  const [selectedConfidenceBuckets, setSelectedConfidenceBuckets] = useState<ConfidenceBucket[]>(
    [],
  );
  const [showOnlyCritical, setShowOnlyCritical] = useState(false);
  const [showOnlyWithValue, setShowOnlyWithValue] = useState(false);
  const [showOnlyEmpty, setShowOnlyEmpty] = useState(false);
  const structuredSearchInputRef = useRef<HTMLInputElement | null>(null);
  const [structuredSearchTerm, setStructuredSearchTerm] = useState(structuredSearchInput);

  useEffect(() => {
    const debounceTimer = window.setTimeout(() => {
      setStructuredSearchTerm(structuredSearchInput);
    }, 200);

    return () => {
      window.clearTimeout(debounceTimer);
    };
  }, [structuredSearchInput]);

  useEffect(() => {
    if (activeConfidencePolicy || selectedConfidenceBuckets.length === 0) {
      return;
    }
    setSelectedConfidenceBuckets([]);
  }, [activeConfidencePolicy, selectedConfidenceBuckets]);

  const structuredDataFilters = useMemo(
    () => ({
      searchTerm: structuredSearchTerm,
      selectedConfidence: selectedConfidenceBuckets,
      onlyCritical: showOnlyCritical,
      onlyWithValue: showOnlyWithValue,
      onlyEmpty: showOnlyEmpty,
    }),
    [
      selectedConfidenceBuckets,
      showOnlyCritical,
      showOnlyWithValue,
      showOnlyEmpty,
      structuredSearchTerm,
    ],
  );

  const hasActiveStructuredFilters =
    structuredSearchTerm.trim().length > 0 ||
    selectedConfidenceBuckets.length > 0 ||
    showOnlyCritical ||
    showOnlyWithValue ||
    showOnlyEmpty;

  const resetStructuredFilters = useCallback(() => {
    setStructuredSearchInput("");
    setSelectedConfidenceBuckets([]);
    setShowOnlyCritical(false);
    setShowOnlyWithValue(false);
    setShowOnlyEmpty(false);
    structuredSearchInputRef.current?.focus();
  }, []);

  const getFilterToggleItemClass = useCallback(
    (isActive: boolean) =>
      `h-7 w-7 rounded-full border-0 p-0 transition-all ${
        isActive
          ? "bg-surfaceMuted text-text ring-1 ring-borderSubtle"
          : "bg-surface text-textSecondary shadow-none hover:bg-surfaceMuted hover:text-text"
      }`,
    [],
  );

  return {
    structuredSearchInput,
    setStructuredSearchInput,
    selectedConfidenceBuckets,
    setSelectedConfidenceBuckets,
    showOnlyCritical,
    setShowOnlyCritical,
    showOnlyWithValue,
    setShowOnlyWithValue,
    showOnlyEmpty,
    setShowOnlyEmpty,
    structuredSearchInputRef,
    structuredDataFilters,
    hasActiveStructuredFilters,
    resetStructuredFilters,
    getFilterToggleItemClass,
  };
}
