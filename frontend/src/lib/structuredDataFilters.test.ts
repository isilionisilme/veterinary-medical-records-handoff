import { describe, expect, it } from "vitest";

import {
  matchesStructuredDataFilters,
  type StructuredDataFilters,
  type StructuredFilterField,
} from "./structuredDataFilters";

const baseFilters: StructuredDataFilters = {
  searchTerm: "",
  selectedConfidence: [],
  onlyCritical: false,
  onlyWithValue: false,
  onlyEmpty: false,
};

function buildField(partial: Partial<StructuredFilterField>): StructuredFilterField {
  return {
    key: "claim_id",
    label: "ID de reclamación",
    isCritical: false,
    repeatable: false,
    items: [
      {
        displayValue: "ABC-123",
        confidence: 0.82,
        confidenceBand: "high",
        isMissing: false,
      },
    ],
    ...partial,
  };
}

describe("structuredDataFilters", () => {
  it("matches search case-insensitively against label, key and rendered value", () => {
    expect(
      matchesStructuredDataFilters(buildField({ label: "Nombre del paciente" }), {
        ...baseFilters,
        searchTerm: "PACIENTE",
      }),
    ).toBe(true);

    expect(
      matchesStructuredDataFilters(buildField({ key: "pet_name" }), {
        ...baseFilters,
        searchTerm: "PET_NAME",
      }),
    ).toBe(true);

    expect(
      matchesStructuredDataFilters(
        buildField({
          items: [
            {
              displayValue: "Pancreatitis",
              confidence: 0.6,
              confidenceBand: "medium",
              isMissing: false,
            },
          ],
        }),
        { ...baseFilters, searchTerm: "pancrea" },
      ),
    ).toBe(true);
  });

  it("filters by explicit confidence bands and ignores missing items", () => {
    expect(
      matchesStructuredDataFilters(
        buildField({
          items: [{ displayValue: "x", confidence: 0.24, confidenceBand: "low", isMissing: false }],
        }),
        {
          ...baseFilters,
          selectedConfidence: ["low"],
        },
      ),
    ).toBe(true);
    expect(
      matchesStructuredDataFilters(
        buildField({
          items: [
            { displayValue: "x", confidence: 0.75, confidenceBand: "high", isMissing: false },
          ],
        }),
        {
          ...baseFilters,
          selectedConfidence: ["medium"],
        },
      ),
    ).toBe(false);

    expect(
      matchesStructuredDataFilters(
        buildField({
          items: [{ displayValue: "—", confidence: 0, confidenceBand: null, isMissing: true }],
        }),
        {
          ...baseFilters,
          selectedConfidence: ["low"],
        },
      ),
    ).toBe(false);

    expect(
      matchesStructuredDataFilters(
        buildField({
          items: [
            { displayValue: "sin score", confidence: 0, confidenceBand: null, isMissing: false },
          ],
        }),
        {
          ...baseFilters,
          selectedConfidence: ["unknown"],
        },
      ),
    ).toBe(true);

    expect(
      matchesStructuredDataFilters(
        buildField({
          items: [
            { displayValue: "sin score", confidence: 0, confidenceBand: null, isMissing: false },
          ],
        }),
        {
          ...baseFilters,
          selectedConfidence: ["medium"],
        },
      ),
    ).toBe(false);
  });

  it("treats repeatable fields as matching when any item matches and list length > 0 for onlyWithValue", () => {
    const repeatableField = buildField({
      key: "medications",
      label: "Medicación",
      repeatable: true,
      items: [
        { displayValue: "Amoxicilina", confidence: 0.41, confidenceBand: "low", isMissing: false },
        { displayValue: "Meloxicam", confidence: 0.9, confidenceBand: "high", isMissing: false },
      ],
    });

    expect(
      matchesStructuredDataFilters(repeatableField, { ...baseFilters, searchTerm: "meloxi" }),
    ).toBe(true);
    expect(
      matchesStructuredDataFilters(repeatableField, {
        ...baseFilters,
        selectedConfidence: ["high"],
      }),
    ).toBe(true);
    expect(
      matchesStructuredDataFilters(repeatableField, {
        ...baseFilters,
        onlyWithValue: true,
      }),
    ).toBe(true);

    expect(
      matchesStructuredDataFilters(
        buildField({
          repeatable: true,
          items: [],
        }),
        {
          ...baseFilters,
          onlyWithValue: true,
        },
      ),
    ).toBe(false);
  });

  it("supports empty vs non-empty restrictions and treats both-on as unrestricted", () => {
    const nonEmptyField = buildField({
      repeatable: false,
      items: [{ displayValue: "Luna", confidence: 0.8, confidenceBand: "high", isMissing: false }],
    });
    const emptyField = buildField({
      repeatable: false,
      items: [{ displayValue: "—", confidence: 0, confidenceBand: null, isMissing: true }],
    });

    expect(
      matchesStructuredDataFilters(nonEmptyField, {
        ...baseFilters,
        onlyWithValue: true,
      }),
    ).toBe(true);
    expect(
      matchesStructuredDataFilters(emptyField, {
        ...baseFilters,
        onlyWithValue: true,
      }),
    ).toBe(false);

    expect(
      matchesStructuredDataFilters(nonEmptyField, {
        ...baseFilters,
        onlyEmpty: true,
      }),
    ).toBe(false);
    expect(
      matchesStructuredDataFilters(emptyField, {
        ...baseFilters,
        onlyEmpty: true,
      }),
    ).toBe(true);

    expect(
      matchesStructuredDataFilters(nonEmptyField, {
        ...baseFilters,
        onlyWithValue: true,
        onlyEmpty: true,
      }),
    ).toBe(true);
    expect(
      matchesStructuredDataFilters(emptyField, {
        ...baseFilters,
        onlyWithValue: true,
        onlyEmpty: true,
      }),
    ).toBe(true);
  });
});
