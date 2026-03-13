import { describe, expect, it } from "vitest";

import {
  CANONICAL_SPECIES_OPTIONS,
  isControlledVocabField,
  normalizeControlledVocabValue,
  validateFieldValue,
} from "./fieldValidators";

const SPECIES_VALID_VECTORS: Array<[string, string]> = [
  ["canino", "canino"],
  ["canina", "canino"],
  ["perro", "canino"],
  ["perra", "canino"],
  ["felino", "felino"],
  ["felina", "felino"],
  ["gato", "felino"],
  ["gata", "felino"],
];
const SPECIES_INVALID_VECTORS = ["equino", "lagarto"];

describe("validateFieldValue", () => {
  it("accepts and normalizes a numeric microchip", () => {
    const result = validateFieldValue("microchip_id", "985 141-000 123 456");
    expect(result).toEqual({ ok: true, normalized: "985141000123456" });
  });

  it("rejects microchip values with letters", () => {
    const result = validateFieldValue("microchip_id", "NHC 2.c AB-77");
    expect(result.ok).toBe(false);
    expect(result.reason).toBe("non-digit");
  });

  it("accepts microchip when trailing non-digits appear after a valid digit prefix", () => {
    const result = validateFieldValue("microchip_id", "00023035139 NHC");
    expect(result).toEqual({ ok: true, normalized: "00023035139" });
  });

  it("normalizes weight values to kg", () => {
    const result = validateFieldValue("weight", "7,2kg");
    expect(result).toEqual({ ok: true, normalized: "7.2 kg" });
  });

  it("accepts plausible weight values without explicit unit", () => {
    const result = validateFieldValue("weight", "7.2");
    expect(result).toEqual({ ok: true, normalized: "7.2 kg" });
  });

  it("treats zero weight as missing", () => {
    const result = validateFieldValue("weight", "0");
    expect(result.ok).toBe(false);
    expect(result.reason).toBe("empty");
  });

  it("normalizes date values to ISO", () => {
    const result = validateFieldValue("visit_date", "7/2/2026");
    expect(result).toEqual({ ok: true, normalized: "2026-02-07" });
  });

  it("normalizes visit_date with two-digit year", () => {
    const result = validateFieldValue("visit_date", "08/12/19");
    expect(result).toEqual({ ok: true, normalized: "2019-12-08" });
  });

  it("normalizes discharge_date with two-digit year", () => {
    const result = validateFieldValue("discharge_date", "5/6/20");
    expect(result).toEqual({ ok: true, normalized: "2020-06-05" });
  });

  it("normalizes document_date with two-digit year", () => {
    const result = validateFieldValue("document_date", "04/10/19");
    expect(result).toEqual({ ok: true, normalized: "2019-10-04" });
  });

  it("normalizes discharge_date in year-first slash format", () => {
    const result = validateFieldValue("discharge_date", "2020/06/05");
    expect(result).toEqual({ ok: true, normalized: "2020-06-05" });
  });

  it("normalizes controlled vocab fields", () => {
    expect(validateFieldValue("sex", "female")).toEqual({ ok: true, normalized: "hembra" });
    expect(validateFieldValue("species", "gato")).toEqual({ ok: true, normalized: "felino" });
  });

  it("normalizes species values using parity vectors", () => {
    for (const [rawValue, expected] of SPECIES_VALID_VECTORS) {
      expect(validateFieldValue("species", rawValue)).toEqual({ ok: true, normalized: expected });
    }
  });

  it("rejects unknown species values using parity vectors", () => {
    for (const rawValue of SPECIES_INVALID_VECTORS) {
      const result = validateFieldValue("species", rawValue);
      expect(result.ok).toBe(false);
    }
  });

  it("keeps species UI options aligned with validator canonical outputs", () => {
    const optionValues = CANONICAL_SPECIES_OPTIONS.map((option) => option.value);
    expect(optionValues).toEqual(["canino", "felino"]);
    for (const value of optionValues) {
      expect(validateFieldValue("species", value)).toEqual({ ok: true, normalized: value });
    }
  });

  it("accepts numeric age values between 0 and 999", () => {
    expect(validateFieldValue("age", "0")).toEqual({ ok: true, normalized: "0" });
    expect(validateFieldValue("age", "7")).toEqual({ ok: true, normalized: "7" });
    expect(validateFieldValue("age", "999")).toEqual({ ok: true, normalized: "999" });
  });

  it("rejects non-numeric or out-of-range age values", () => {
    expect(validateFieldValue("age", "7a")).toEqual({ ok: false, reason: "invalid-age" });
    expect(validateFieldValue("age", "1000")).toEqual({ ok: false, reason: "invalid-age" });
  });

  it("keeps unsupported keys as non-empty passthrough", () => {
    const result = validateFieldValue("owner_name", " Maria Perez ");
    expect(result).toEqual({ ok: true, normalized: "Maria Perez" });
  });

  it("identifies controlled vocab fields", () => {
    expect(isControlledVocabField("sex")).toBe(true);
    expect(isControlledVocabField("species")).toBe(true);
    expect(isControlledVocabField("owner_name")).toBe(false);
  });

  it("normalizes controlled vocab values only when valid", () => {
    expect(normalizeControlledVocabValue("sex", "female")).toBe("hembra");
    expect(normalizeControlledVocabValue("species", "canina")).toBe("canino");
    expect(normalizeControlledVocabValue("species", "lagarto")).toBeNull();
    expect(normalizeControlledVocabValue("owner_name", "Maria Perez")).toBeNull();
  });
});
