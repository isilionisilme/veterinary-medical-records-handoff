import { describe, expect, it } from "vitest";

import { resolveCandidateSuggestionSections } from "./candidateSuggestions";

describe("resolveCandidateSuggestionSections", () => {
  it("keeps only valid normalized suggestions and moves invalid to detected for controlled vocab fields", () => {
    const sections = resolveCandidateSuggestionSections("species", [
      { value: "canina", confidence: 0.9 },
      { value: "perro", confidence: 0.8 },
      { value: "lagarto", confidence: 0.7 },
      { value: "felino", confidence: 0.6 },
    ]);

    expect(sections.applicableSuggestions).toEqual([
      { value: "canino", confidence: 0.9, evidence: undefined },
      { value: "felino", confidence: 0.6, evidence: undefined },
    ]);
    expect(sections.detectedCandidates).toEqual([
      { value: "canina", confidence: 0.9 },
      { value: "perro", confidence: 0.8 },
      { value: "lagarto", confidence: 0.7 },
    ]);
  });

  it("applies garbage filters and detected limits for controlled vocab fields", () => {
    const sections = resolveCandidateSuggestionSections("sex", [
      { value: "desconocido", confidence: 0.9 },
      { value: "campo: valor; otro: valor", confidence: 0.8 },
      { value: "chip 1234 lote 5678", confidence: 0.85 },
      { value: "x".repeat(61), confidence: 0.7 },
      { value: "indefinido", confidence: 0.6 },
      { value: "sin dato", confidence: 0.5 },
      { value: "otro no valido", confidence: 0.4 },
      { value: "desconocido", confidence: 0.3 },
    ]);

    expect(sections.applicableSuggestions).toEqual([]);
    expect(sections.detectedCandidates).toEqual([
      { value: "desconocido", confidence: 0.9 },
      { value: "indefinido", confidence: 0.6 },
      { value: "sin dato", confidence: 0.5 },
    ]);
  });

  it("keeps valid suggestions selectable for controlled vocab fields", () => {
    const sections = resolveCandidateSuggestionSections("sex", [
      { value: "unknown", confidence: 0.8 },
      { value: " ", confidence: 0.7 },
      { value: "female", confidence: 0.5 },
      { value: "male", confidence: 0.9 },
    ]);

    expect(sections.applicableSuggestions).toEqual([
      { value: "macho", confidence: 0.9, evidence: undefined },
      { value: "hembra", confidence: 0.5, evidence: undefined },
    ]);
    expect(sections.detectedCandidates).toEqual([
      { value: "male", confidence: 0.9 },
      { value: "unknown", confidence: 0.8 },
      { value: "female", confidence: 0.5 },
    ]);
  });

  it("keeps noisy normalized sex candidates in detected and not in suggestions", () => {
    const sections = resolveCandidateSuggestionSections("sex", [
      { value: "Hembra Estado: FERTIL Peso: 0", confidence: 0.88 },
    ]);

    expect(sections.applicableSuggestions).toEqual([]);
    expect(sections.detectedCandidates).toEqual([
      { value: "Hembra Estado: FERTIL Peso: 0", confidence: 0.88 },
    ]);
  });

  it("keeps non-dropdown behavior unchanged", () => {
    const sections = resolveCandidateSuggestionSections("owner_name", [
      { value: "  Maria Perez ", confidence: 0.8 },
      { value: "Maria Perez", confidence: 0.7 },
      { value: "Ana", confidence: 0.6 },
    ]);

    expect(sections.applicableSuggestions).toEqual([
      { value: "Maria Perez", confidence: 0.8, evidence: undefined },
      { value: "Maria Perez", confidence: 0.7, evidence: undefined },
      { value: "Ana", confidence: 0.6, evidence: undefined },
    ]);
    expect(sections.detectedCandidates).toEqual([]);
  });

  it("caps results to max length", () => {
    const sections = resolveCandidateSuggestionSections(
      "owner_name",
      [
        { value: "A", confidence: 0.1 },
        { value: "B", confidence: 0.2 },
        { value: "C", confidence: 0.3 },
      ],
      2,
      3,
    );

    expect(sections.applicableSuggestions).toEqual([
      { value: "A", confidence: 0.1, evidence: undefined },
      { value: "B", confidence: 0.2, evidence: undefined },
    ]);
  });
});
