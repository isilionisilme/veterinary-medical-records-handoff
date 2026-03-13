import {
  getControlledVocabOptionValues,
  isControlledVocabField,
  normalizeControlledVocabValue,
} from "./fieldValidators";

type CandidateSuggestionEvidence = {
  page?: number;
  snippet?: string;
};

export type CandidateSuggestion = {
  value: string;
  confidence: number;
  evidence?: CandidateSuggestionEvidence;
};

export type DetectedCandidate = {
  value: string;
  confidence?: number;
};

export type CandidateSuggestionSections = {
  applicableSuggestions: CandidateSuggestion[];
  detectedCandidates: DetectedCandidate[];
};

type CandidateSuggestionInput = {
  value?: unknown;
  confidence?: unknown;
  evidence?: unknown;
};

function clampConfidence(value: number): number {
  return Math.min(Math.max(value, 0), 1);
}

function sanitizeEvidence(rawEvidence: unknown): CandidateSuggestionEvidence | undefined {
  if (!rawEvidence || typeof rawEvidence !== "object") {
    return undefined;
  }

  const evidence = rawEvidence as Record<string, unknown>;
  const payload: CandidateSuggestionEvidence = {};

  if (typeof evidence.page === "number" && Number.isInteger(evidence.page)) {
    payload.page = evidence.page;
  }
  if (typeof evidence.snippet === "string" && evidence.snippet.trim().length > 0) {
    payload.snippet = evidence.snippet.trim();
  }

  return Object.keys(payload).length > 0 ? payload : undefined;
}

function getSeparatorCount(value: string): number {
  const matches = value.match(/[:;]/g);
  return matches ? matches.length : 0;
}

function getNumberGroupCount(value: string): number {
  const matches = value.match(/\d+/g);
  return matches ? matches.length : 0;
}

function isGarbageDetectedCandidate(value: string): boolean {
  return value.length > 60 || getSeparatorCount(value) >= 2 || getNumberGroupCount(value) >= 2;
}

type ParsedCandidate = {
  rawValue: string;
  confidence: number | null;
  evidence: CandidateSuggestionEvidence | undefined;
  index: number;
};

type ControlledVocabNormalization = {
  normalizedValue: string;
  hasExtraContent: boolean;
};

function getNormalizedTokenValues(fieldKey: string, rawValue: string): string[] {
  const tokens = rawValue.split(/[^A-Za-zÀ-ÿ]+/).filter((token) => token.length > 0);
  const normalized = new Set<string>();

  for (const token of tokens) {
    const normalizedToken = normalizeControlledVocabValue(fieldKey, token);
    if (normalizedToken) {
      normalized.add(normalizedToken);
    }
  }

  return Array.from(normalized);
}

function parseRawCandidates(rawSuggestions: unknown): ParsedCandidate[] {
  if (!Array.isArray(rawSuggestions)) {
    return [];
  }

  const parsed: ParsedCandidate[] = [];

  rawSuggestions.forEach((rawItem, index) => {
    if (!rawItem || typeof rawItem !== "object") {
      return;
    }

    const item = rawItem as CandidateSuggestionInput;
    if (typeof item.value !== "string") {
      return;
    }

    const rawValue = item.value.trim();
    if (!rawValue) {
      return;
    }

    const confidence =
      typeof item.confidence === "number" && Number.isFinite(item.confidence)
        ? clampConfidence(item.confidence)
        : null;

    parsed.push({
      rawValue,
      confidence,
      evidence: sanitizeEvidence(item.evidence),
      index,
    });
  });

  return parsed;
}

function resolveControlledVocabNormalization(
  fieldKey: string,
  rawValue: string,
): ControlledVocabNormalization | null {
  const direct = normalizeControlledVocabValue(fieldKey, rawValue);
  if (direct) {
    const normalizedTokenValues = getNormalizedTokenValues(fieldKey, rawValue);
    const hasExtraContent =
      normalizedTokenValues.length === 1 &&
      normalizedTokenValues[0].toLowerCase() === direct.toLowerCase() &&
      rawValue.split(/[^A-Za-zÀ-ÿ]+/).filter((token) => token.length > 0).length > 1;
    return { normalizedValue: direct, hasExtraContent };
  }

  // Fallback for noisy extracted strings such as "Hembra Estado: FERTIL Peso: 0".
  // If we can map a token to a valid option, keep it as detected-only evidence.
  const normalizedTokenValues = getNormalizedTokenValues(fieldKey, rawValue);
  if (normalizedTokenValues.length !== 1) {
    // Ambiguous noisy candidate: keep strict and reject.
    return null;
  }

  return { normalizedValue: normalizedTokenValues[0], hasExtraContent: true };
}

export function resolveCandidateSuggestionSections(
  fieldKey: string,
  rawSuggestions: unknown,
  maxSuggestions = 5,
  maxDetected = 3,
): CandidateSuggestionSections {
  const parsedCandidates = parseRawCandidates(rawSuggestions);
  if (parsedCandidates.length === 0) {
    return { applicableSuggestions: [], detectedCandidates: [] };
  }

  const controlledVocabField = isControlledVocabField(fieldKey);
  if (!controlledVocabField) {
    const suggestions: CandidateSuggestion[] = [];

    for (const candidate of parsedCandidates) {
      if (suggestions.length >= maxSuggestions) {
        break;
      }
      if (candidate.confidence === null) {
        continue;
      }

      suggestions.push({
        value: candidate.rawValue,
        confidence: candidate.confidence,
        evidence: candidate.evidence,
      });
    }

    return { applicableSuggestions: suggestions, detectedCandidates: [] };
  }

  const validOptionValues = getControlledVocabOptionValues(fieldKey);
  const validOptionSet = new Set(validOptionValues.map((value) => value.toLowerCase()));
  const normalizedSuggestionMap = new Map<
    string,
    {
      value: string;
      confidence: number;
      evidence: CandidateSuggestionEvidence | undefined;
      index: number;
    }
  >();
  const detectedMap = new Map<
    string,
    { value: string; confidence: number | null; index: number }
  >();

  for (const candidate of parsedCandidates) {
    const normalization = resolveControlledVocabNormalization(fieldKey, candidate.rawValue);
    if (normalization) {
      if (!normalization.hasExtraContent) {
        const key = normalization.normalizedValue.toLowerCase();
        const current = normalizedSuggestionMap.get(key);
        const nextConfidence = candidate.confidence ?? 0;
        if (!current || nextConfidence > current.confidence) {
          normalizedSuggestionMap.set(key, {
            value: normalization.normalizedValue,
            confidence: nextConfidence,
            evidence: candidate.evidence,
            index: candidate.index,
          });
        }
      }

      if (
        !validOptionSet.has(candidate.rawValue.toLowerCase()) &&
        (!isGarbageDetectedCandidate(candidate.rawValue) || normalization.hasExtraContent)
      ) {
        const detectedKey = candidate.rawValue.toLowerCase();
        const currentDetected = detectedMap.get(detectedKey);
        if (!currentDetected) {
          detectedMap.set(detectedKey, {
            value: candidate.rawValue,
            confidence: candidate.confidence,
            index: candidate.index,
          });
        } else if (
          candidate.confidence !== null &&
          (currentDetected.confidence === null || candidate.confidence > currentDetected.confidence)
        ) {
          detectedMap.set(detectedKey, {
            value: candidate.rawValue,
            confidence: candidate.confidence,
            index: currentDetected.index,
          });
        }
      }
      continue;
    }

    if (isGarbageDetectedCandidate(candidate.rawValue)) {
      continue;
    }
    if (validOptionSet.has(candidate.rawValue.toLowerCase())) {
      continue;
    }

    const key = candidate.rawValue.toLowerCase();
    const current = detectedMap.get(key);
    if (!current) {
      detectedMap.set(key, {
        value: candidate.rawValue,
        confidence: candidate.confidence,
        index: candidate.index,
      });
      continue;
    }

    if (
      candidate.confidence !== null &&
      (current.confidence === null || candidate.confidence > current.confidence)
    ) {
      detectedMap.set(key, {
        value: candidate.rawValue,
        confidence: candidate.confidence,
        index: current.index,
      });
    }
  }

  const applicableSuggestions = Array.from(normalizedSuggestionMap.values())
    .sort((a, b) => {
      if (b.confidence !== a.confidence) {
        return b.confidence - a.confidence;
      }
      return a.index - b.index;
    })
    .slice(0, maxSuggestions)
    .map((item) => ({
      value: item.value,
      confidence: item.confidence,
      evidence: item.evidence,
    }));

  const detectedCandidates = Array.from(detectedMap.values())
    .sort((a, b) => {
      if (a.confidence !== null && b.confidence !== null) {
        return b.confidence - a.confidence;
      }
      if (a.confidence !== null) {
        return -1;
      }
      if (b.confidence !== null) {
        return 1;
      }
      return a.index - b.index;
    })
    .slice(0, maxDetected)
    .map((item) => ({
      value: item.value,
      confidence: item.confidence === null ? undefined : item.confidence,
    }));

  return { applicableSuggestions, detectedCandidates };
}

export function toApplicableCandidateSuggestions(
  fieldKey: string,
  rawSuggestions: unknown,
  maxLength = 5,
): CandidateSuggestion[] {
  return resolveCandidateSuggestionSections(fieldKey, rawSuggestions, maxLength)
    .applicableSuggestions;
}
