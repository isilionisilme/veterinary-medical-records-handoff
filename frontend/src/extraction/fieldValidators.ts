export type FieldValidationResult = {
  ok: boolean;
  normalized?: string;
  reason?: string;
};

export const CANONICAL_SPECIES_OPTIONS = [
  { value: "canino", label: "Canino" },
  { value: "felino", label: "Felino" },
] as const;

export const CANONICAL_SEX_OPTIONS = [
  { value: "macho", label: "Macho" },
  { value: "hembra", label: "Hembra" },
] as const;

const CONTROLLED_VOCAB_FIELD_KEYS = new Set(["sex", "species"]);
const DATE_FIELD_KEYS = new Set([
  "document_date",
  "visit_date",
  "admission_date",
  "discharge_date",
  "dob",
]);

function canonicalizeFieldKey(fieldKey: string): string {
  const normalized = fieldKey.trim().toLowerCase();
  if (normalized === "microchip") {
    return "microchip_id";
  }
  if (normalized === "peso") {
    return "weight";
  }
  if (normalized === "edad") {
    return "age";
  }
  if (normalized === "sexo") {
    return "sex";
  }
  if (normalized === "especie") {
    return "species";
  }
  return normalized;
}

export function isControlledVocabField(fieldKey: string): boolean {
  return CONTROLLED_VOCAB_FIELD_KEYS.has(canonicalizeFieldKey(fieldKey));
}

export function getControlledVocabOptionValues(fieldKey: string): string[] {
  const key = canonicalizeFieldKey(fieldKey);
  if (key === "sex") {
    return CANONICAL_SEX_OPTIONS.map((option) => option.value);
  }
  if (key === "species") {
    return CANONICAL_SPECIES_OPTIONS.map((option) => option.value);
  }
  return [];
}

export function normalizeControlledVocabValue(fieldKey: string, value: string): string | null {
  if (!isControlledVocabField(fieldKey)) {
    return null;
  }
  const validation = validateFieldValue(fieldKey, value);
  if (!validation.ok || typeof validation.normalized !== "string") {
    return null;
  }
  return validation.normalized;
}

function validateMicrochip(value: string): FieldValidationResult {
  const compact = value.trim().replace(/[\s-]+/g, "");
  if (!compact) {
    return { ok: false, reason: "empty" };
  }

  const leadingDigitsWithTrailingNonDigits = compact.match(/^(\d{9,15})\D+$/);
  if (leadingDigitsWithTrailingNonDigits) {
    return { ok: true, normalized: leadingDigitsWithTrailingNonDigits[1] };
  }

  if (/[a-z]/i.test(compact)) {
    return { ok: false, reason: "non-digit" };
  }
  if (!/^\d+$/.test(compact)) {
    return { ok: false, reason: "non-digit" };
  }
  if (compact.length < 9 || compact.length > 15) {
    return { ok: false, reason: "invalid-length" };
  }
  return { ok: true, normalized: compact };
}

function validateWeight(value: string): FieldValidationResult {
  const compact = value.trim();
  if (!compact) {
    return { ok: false, reason: "empty" };
  }

  const match = compact.match(/^(\d+(?:[.,]\d+)?)\s*(kg|kgs)?\s*$/i);
  if (!match) {
    return { ok: false, reason: "invalid-weight" };
  }

  const numericRaw = match[1].replace(",", ".");
  const parsed = Number.parseFloat(numericRaw);
  if (!Number.isFinite(parsed)) {
    return { ok: false, reason: "invalid-weight" };
  }

  if (parsed === 0) {
    return { ok: false, reason: "empty" };
  }

  if (parsed < 0.5 || parsed > 120) {
    return { ok: false, reason: "invalid-weight" };
  }

  return { ok: true, normalized: `${parsed} kg` };
}

function normalizeDateToIso(year: number, month: number, day: number): string | null {
  const candidate = new Date(Date.UTC(year, month - 1, day));
  if (
    candidate.getUTCFullYear() !== year ||
    candidate.getUTCMonth() !== month - 1 ||
    candidate.getUTCDate() !== day
  ) {
    return null;
  }
  return `${String(year).padStart(4, "0")}-${String(month).padStart(2, "0")}-${String(day).padStart(2, "0")}`;
}

function normalizeYearToken(rawYear: string): number | null {
  const compact = rawYear.trim();
  if (!/^\d{2,4}$/.test(compact)) {
    return null;
  }
  const year = Number.parseInt(compact, 10);
  if (!Number.isFinite(year)) {
    return null;
  }
  if (compact.length === 4) {
    return year;
  }
  return year >= 70 ? 1900 + year : 2000 + year;
}

function validateDate(value: string): FieldValidationResult {
  const compact = value.trim();
  if (!compact) {
    return { ok: false, reason: "empty" };
  }

  const isoDatePrefixMatch = compact.match(/^(\d{4})-(\d{1,2})-(\d{1,2})(?:[T\s].*)?$/);
  if (isoDatePrefixMatch) {
    const year = Number.parseInt(isoDatePrefixMatch[1], 10);
    const month = Number.parseInt(isoDatePrefixMatch[2], 10);
    const day = Number.parseInt(isoDatePrefixMatch[3], 10);
    const normalized = normalizeDateToIso(year, month, day);
    if (!normalized) {
      return { ok: false, reason: "invalid-date" };
    }
    return { ok: true, normalized };
  }

  const dmyMatch = compact.match(/\b(\d{1,2})[/.-](\d{1,2})[/.-](\d{2}|\d{4})\b/);
  if (dmyMatch) {
    const day = Number.parseInt(dmyMatch[1], 10);
    const month = Number.parseInt(dmyMatch[2], 10);
    const year = normalizeYearToken(dmyMatch[3]);
    if (year === null) {
      return { ok: false, reason: "invalid-date" };
    }
    const normalized = normalizeDateToIso(year, month, day);
    if (!normalized) {
      return { ok: false, reason: "invalid-date" };
    }
    return { ok: true, normalized };
  }

  const isoMatch = compact.match(/\b(\d{4})[/.-](\d{1,2})[/.-](\d{1,2})\b/);
  if (isoMatch) {
    const year = Number.parseInt(isoMatch[1], 10);
    const month = Number.parseInt(isoMatch[2], 10);
    const day = Number.parseInt(isoMatch[3], 10);
    const normalized = normalizeDateToIso(year, month, day);
    if (!normalized) {
      return { ok: false, reason: "invalid-date" };
    }
    return { ok: true, normalized };
  }

  return { ok: false, reason: "invalid-date" };
}

function validateSex(value: string): FieldValidationResult {
  const token = value.trim().toLowerCase();
  if (!token) {
    return { ok: false, reason: "empty" };
  }
  if (["hembra", "female"].includes(token)) {
    return { ok: true, normalized: "hembra" };
  }
  if (["macho", "male"].includes(token)) {
    return { ok: true, normalized: "macho" };
  }
  return { ok: false, reason: "invalid-sex" };
}

function validateSpecies(value: string): FieldValidationResult {
  const token = value.trim().toLowerCase();
  if (!token) {
    return { ok: false, reason: "empty" };
  }
  if (["canino", "canina", "perro", "perra"].includes(token)) {
    return { ok: true, normalized: "canino" };
  }
  if (["felino", "felina", "gato", "gata"].includes(token)) {
    return { ok: true, normalized: "felino" };
  }
  return { ok: false, reason: "invalid-species" };
}

function validateAge(value: string): FieldValidationResult {
  const compact = value.trim();
  if (!compact) {
    return { ok: false, reason: "empty" };
  }

  const match = compact.match(/^(\d{1,3})$/);
  if (!match) {
    return { ok: false, reason: "invalid-age" };
  }

  const years = Number.parseInt(match[1], 10);
  if (!Number.isFinite(years)) {
    return { ok: false, reason: "invalid-age" };
  }

  return { ok: true, normalized: `${years}` };
}

export function validateFieldValue(fieldKey: string, value: string): FieldValidationResult {
  const raw = value.trim();
  if (!raw) {
    return { ok: false, reason: "empty" };
  }

  const key = canonicalizeFieldKey(fieldKey);

  if (key === "microchip_id") {
    return validateMicrochip(raw);
  }
  if (key === "weight") {
    return validateWeight(raw);
  }
  if (key === "sex") {
    return validateSex(raw);
  }
  if (key === "species") {
    return validateSpecies(raw);
  }
  if (key === "age") {
    return validateAge(raw);
  }
  if (DATE_FIELD_KEYS.has(key) || key.startsWith("fecha_")) {
    return validateDate(raw);
  }

  return { ok: true, normalized: raw };
}
