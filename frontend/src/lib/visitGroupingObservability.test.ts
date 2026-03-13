import { describe, expect, it } from "vitest";

import {
  buildVisitGroupingDiagnostics,
  shouldEmitVisitGroupingDiagnostics,
} from "./visitGroupingObservability";

describe("visitGroupingObservability", () => {
  it("builds diagnostics including unassigned metrics", () => {
    const diagnostics = buildVisitGroupingDiagnostics([
      {
        visit_id: "visit-1",
        fields: [{ key: "diagnosis" }],
      },
      {
        visit_id: "unassigned",
        fields: [{ key: "symptoms" }, { key: "procedure" }],
      },
    ]);

    expect(diagnostics.visits_count).toBe(2);
    expect(diagnostics.unassigned_present).toBe(true);
    expect(diagnostics.fields_per_visit).toEqual({
      "visit-1": 1,
      unassigned: 2,
    });
    expect(diagnostics.total_visit_scoped_fields_count).toBe(3);
    expect(diagnostics.all_visit_scoped_in_unassigned).toBe(false);
  });

  it("falls back to visit_<n> key when visit_id is empty or whitespace", () => {
    const diagnostics = buildVisitGroupingDiagnostics([
      {
        visit_id: "  ",
        fields: [{ key: "diagnosis" }],
      },
      {
        visit_id: "",
        fields: [{ key: "symptoms" }, { key: "procedure" }],
      },
    ]);

    expect(diagnostics.fields_per_visit).toEqual({
      visit_1: 1,
      visit_2: 2,
    });
    expect(diagnostics.unassigned_present).toBe(false);
  });

  it("returns false in production-like mode for diagnostics emission", () => {
    expect(shouldEmitVisitGroupingDiagnostics({ DEV: false, MODE: "production" })).toBe(false);
    expect(shouldEmitVisitGroupingDiagnostics({ DEV: false, MODE: "test" })).toBe(false);
  });

  it("returns true only in non-test dev mode for diagnostics emission", () => {
    expect(shouldEmitVisitGroupingDiagnostics({ DEV: true, MODE: "development" })).toBe(true);
    expect(shouldEmitVisitGroupingDiagnostics({ DEV: true, MODE: "test" })).toBe(false);
  });
});
