export type ConfidenceBucket = "low" | "medium" | "high" | "unknown";

export type StructuredFilterItem = {
  displayValue: string;
  confidence: number;
  confidenceBand: ConfidenceBucket | null;
  isMissing: boolean;
};

export type StructuredFilterField = {
  key: string;
  label: string;
  isCritical: boolean;
  repeatable: boolean;
  items: StructuredFilterItem[];
};

export type StructuredDataFilters = {
  searchTerm: string;
  selectedConfidence: ConfidenceBucket[];
  onlyCritical: boolean;
  onlyWithValue: boolean;
  onlyEmpty: boolean;
};

function hasRenderableValue(field: StructuredFilterField): boolean {
  if (field.repeatable) {
    return field.items.length > 0;
  }
  return field.items.some((item) => !item.isMissing);
}

function matchesSearch(field: StructuredFilterField, searchTerm: string): boolean {
  const normalizedTerm = searchTerm.trim().toLowerCase();
  if (!normalizedTerm) {
    return true;
  }
  if (field.label.toLowerCase().includes(normalizedTerm)) {
    return true;
  }
  if (field.key.toLowerCase().includes(normalizedTerm)) {
    return true;
  }
  return field.items.some((item) => item.displayValue.toLowerCase().includes(normalizedTerm));
}

function matchesConfidence(field: StructuredFilterField, selected: ConfidenceBucket[]): boolean {
  if (selected.length === 0) {
    return true;
  }
  const allowed = new Set(selected);
  return field.items.some((item) => {
    if (item.isMissing) {
      return false;
    }
    if (item.confidenceBand === null) {
      return allowed.has("unknown");
    }
    return allowed.has(item.confidenceBand);
  });
}

export function matchesStructuredDataFilters(
  field: StructuredFilterField,
  filters: StructuredDataFilters,
): boolean {
  if (filters.onlyCritical && !field.isCritical) {
    return false;
  }
  const hasValue = hasRenderableValue(field);
  const restrictToNonEmpty = filters.onlyWithValue && !filters.onlyEmpty;
  const restrictToEmpty = filters.onlyEmpty && !filters.onlyWithValue;

  if (restrictToNonEmpty && !hasValue) {
    return false;
  }
  if (restrictToEmpty && hasValue) {
    return false;
  }
  if (!matchesConfidence(field, filters.selectedConfidence)) {
    return false;
  }
  if (!matchesSearch(field, filters.searchTerm)) {
    return false;
  }
  return true;
}
