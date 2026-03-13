import {
  DEFAULT_REVIEW_SPLIT_RATIO,
  HIDDEN_EXTRACTED_FIELDS,
  HIDDEN_REVIEW_FIELDS,
  LONG_TEXT_FALLBACK_THRESHOLD,
  LONG_TEXT_FIELD_KEYS,
  MEDICAL_RECORD_SECTION_ID_SET,
  MIN_PDF_PANEL_WIDTH_PX,
  MIN_STRUCTURED_PANEL_WIDTH_PX,
  MISSING_VALUE_PLACEHOLDER,
  NON_TECHNICAL_FAILURE,
  REPORT_INFO_SECTION_TITLE,
  RUN_STATE_LABELS,
  SECTION_ID_TO_UI_LABEL,
  SECTION_LABELS,
  SPLITTER_COLUMN_WIDTH_PX,
  SPLIT_SNAP_POINTS,
  VISIT_SECTION_FIELD_KEYS,
  OWNER_SECTION_FIELD_KEYS,
} from "../constants/appWorkspace";
import { formatDuration, formatShortDate, formatTime } from "./processingHistoryView";
import type {
  ConfidenceBandCutoffs,
  ConfidencePolicyConfig,
  ConfidencePolicyDiagnosticEvent,
  ConfidenceTone,
  MedicalRecordSectionId,
  ProcessingHistoryRun,
  ReviewField,
  ReviewVisitGroup,
  StructuredInterpretationData,
  UiError,
} from "../types/appWorkspace";

export function isLongTextFieldKey(fieldKey: string): boolean {
  return LONG_TEXT_FIELD_KEYS.has(fieldKey);
}

export function shouldRenderLongTextValue(fieldKey: string, value: string): boolean {
  if (isLongTextFieldKey(fieldKey)) {
    return true;
  }
  return value.includes("\n") || value.length > LONG_TEXT_FALLBACK_THRESHOLD;
}

export function getStructuredFieldPrefix(fieldKey: string): "owner" | "visit" | "core" {
  if (OWNER_SECTION_FIELD_KEYS.has(fieldKey)) {
    return "owner";
  }
  if (VISIT_SECTION_FIELD_KEYS.has(fieldKey)) {
    return "visit";
  }
  return "core";
}

export function clampNumber(value: number, min: number, max: number): number {
  return Math.min(Math.max(value, min), max);
}

export function getReviewSplitBounds(containerWidth: number): {
  availablePanelWidth: number;
  minPdfPanelWidth: number;
  maxPdfPanelWidth: number;
  canFitBothMinWidths: boolean;
} {
  const safeContainerWidth = Number.isFinite(containerWidth) ? Math.max(containerWidth, 0) : 0;
  const availablePanelWidth = Math.max(safeContainerWidth - SPLITTER_COLUMN_WIDTH_PX, 0);
  const minPdfPanelWidth = MIN_PDF_PANEL_WIDTH_PX;
  const maxPdfPanelWidth = Math.max(availablePanelWidth - MIN_STRUCTURED_PANEL_WIDTH_PX, 0);
  const canFitBothMinWidths =
    availablePanelWidth >= MIN_PDF_PANEL_WIDTH_PX + MIN_STRUCTURED_PANEL_WIDTH_PX;
  return { availablePanelWidth, minPdfPanelWidth, maxPdfPanelWidth, canFitBothMinWidths };
}

export function clampReviewSplitPx(rawSplitPx: number, containerWidth: number): number {
  const { availablePanelWidth, minPdfPanelWidth, maxPdfPanelWidth, canFitBothMinWidths } =
    getReviewSplitBounds(containerWidth);
  if (availablePanelWidth <= 0) {
    return 0;
  }
  if (!canFitBothMinWidths) {
    return clampNumber(rawSplitPx, 0, availablePanelWidth);
  }
  return clampNumber(rawSplitPx, minPdfPanelWidth, maxPdfPanelWidth);
}

export function splitPxToReviewSplitRatio(splitPx: number, containerWidth: number): number {
  const { availablePanelWidth } = getReviewSplitBounds(containerWidth);
  if (availablePanelWidth <= 0) {
    return DEFAULT_REVIEW_SPLIT_RATIO;
  }
  const clampedSplitPx = clampReviewSplitPx(splitPx, containerWidth);
  return clampedSplitPx / availablePanelWidth;
}

export function reviewSplitRatioToPx(rawRatio: number, containerWidth: number): number {
  const { availablePanelWidth } = getReviewSplitBounds(containerWidth);
  const normalizedRatio = Number.isFinite(rawRatio) ? rawRatio : DEFAULT_REVIEW_SPLIT_RATIO;
  return clampReviewSplitPx(normalizedRatio * availablePanelWidth, containerWidth);
}

export function clampReviewSplitRatio(rawRatio: number, containerWidth: number): number {
  const splitPx = reviewSplitRatioToPx(rawRatio, containerWidth);
  return splitPxToReviewSplitRatio(splitPx, containerWidth);
}

export function snapReviewSplitRatio(rawRatio: number): number {
  const nearestPoint = SPLIT_SNAP_POINTS.reduce((nearest, candidate) =>
    Math.abs(candidate - rawRatio) < Math.abs(nearest - rawRatio) ? candidate : nearest,
  );

  if (Math.abs(nearestPoint - rawRatio) <= 0.03) {
    return nearestPoint;
  }

  return rawRatio;
}

export function isNetworkFetchError(error: unknown): boolean {
  if (!(error instanceof Error)) {
    return false;
  }
  const message = error.message.toLowerCase();
  return (
    error.name === "TypeError" &&
    (message.includes("failed to fetch") ||
      message.includes("networkerror") ||
      message.includes("load failed"))
  );
}

export function getUserErrorMessage(error: unknown, fallback: string): string {
  if (
    typeof error === "object" &&
    error !== null &&
    "userMessage" in error &&
    typeof (error as UiError).userMessage === "string"
  ) {
    return (error as UiError).userMessage;
  }
  if (error instanceof Error && error.message) {
    return error.message;
  }
  return fallback;
}

export function getTechnicalDetails(error: unknown): string | undefined {
  if (
    typeof error === "object" &&
    error !== null &&
    "technicalDetails" in error &&
    typeof (error as UiError).technicalDetails === "string"
  ) {
    return (error as UiError).technicalDetails;
  }
  if (error instanceof Error) {
    return error.message;
  }
  return undefined;
}

export function isConnectivityOrServerError(error: unknown): boolean {
  if (
    typeof error === "object" &&
    error !== null &&
    "technicalDetails" in error &&
    typeof (error as UiError).technicalDetails === "string"
  ) {
    const details = ((error as UiError).technicalDetails ?? "").toLowerCase();
    if (details.includes("network error calling")) {
      return true;
    }
    if (/http 5\d\d calling/.test(details)) {
      return true;
    }
  }
  return isNetworkFetchError(error);
}

export function parseFilename(contentDisposition: string | null): string | null {
  if (!contentDisposition) {
    return null;
  }
  const match = /filename="?([^";]+)"?/i.exec(contentDisposition);
  return match ? match[1] : null;
}

export function formatTimestamp(value: string | null | undefined): string {
  if (!value) {
    return "--";
  }
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return value;
  }
  return parsed.toLocaleString("es-ES", {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

export function isDocumentProcessing(status: string): boolean {
  return status === "PROCESSING" || status === "UPLOADED";
}

export function isProcessingTooLong(createdAt: string, status: string): boolean {
  if (!isDocumentProcessing(status)) {
    return false;
  }
  const createdAtMs = Date.parse(createdAt);
  if (Number.isNaN(createdAtMs)) {
    return false;
  }
  return Date.now() - createdAtMs > 2 * 60 * 1000;
}

export function explainFailure(failureCode: string | null | undefined): string | null {
  if (!failureCode) {
    return null;
  }
  return NON_TECHNICAL_FAILURE[failureCode] ?? "Ocurrio un problema durante el procesamiento.";
}

export function formatRunHeader(run: ProcessingHistoryRun): string {
  const runId = run.run_id;
  const dateSource = run.started_at ?? run.completed_at;
  const shortDate = formatShortDate(dateSource);
  const startTime = formatTime(run.started_at);
  const endTime = formatTime(run.completed_at);
  const duration = formatDuration(run.started_at, run.completed_at);
  const timeRange =
    startTime && endTime ? `${startTime} \u2192 ${endTime}` : (startTime ?? "--:--");
  const datePrefix = shortDate ? `${shortDate} ` : "";
  const durationPart = duration ? ` \u00b7 ${duration}` : "";
  return `Run ${runId} \u00b7 ${datePrefix}${timeRange}${durationPart} \u00b7 ${
    RUN_STATE_LABELS[run.state] ?? run.state
  }`;
}

export function formatReviewKeyLabel(key: string): string {
  return key
    .replace(/_/g, " ")
    .replace(/\s+/g, " ")
    .trim()
    .replace(/^./, (char) => char.toUpperCase());
}

export function normalizeFieldIdentifier(value: string): string {
  return value
    .trim()
    .toLowerCase()
    .replace(/[\s_-]+/g, " ")
    .replace(/[^\p{L}\p{N}\s]/gu, " ")
    .replace(/\s+/g, " ")
    .trim();
}

export function shouldHideExtractedField(key: string): boolean {
  const normalizedKey = normalizeFieldIdentifier(key);
  if (HIDDEN_EXTRACTED_FIELDS.has(normalizedKey)) {
    return true;
  }
  if (HIDDEN_REVIEW_FIELDS.has(key)) {
    return true;
  }
  const normalizedLabel = normalizeFieldIdentifier(formatReviewKeyLabel(key));
  return HIDDEN_EXTRACTED_FIELDS.has(normalizedLabel);
}

export function getUiSectionLabelFromSectionId(sectionId: string | undefined): string | null {
  if (!sectionId) {
    return null;
  }
  const normalized = sectionId.trim().toLowerCase();
  if (!MEDICAL_RECORD_SECTION_ID_SET.has(normalized)) {
    return null;
  }
  return SECTION_ID_TO_UI_LABEL[normalized as MedicalRecordSectionId];
}

export function resolveUiSection(
  field: Pick<ReviewField, "key" | "section">,
  fallbackSection: string,
): string {
  const sectionLabel = getUiSectionLabelFromSectionId(field.section);
  if (sectionLabel) {
    return sectionLabel;
  }
  if (field.key === "notes") {
    return "Notas internas";
  }
  if (field.key === "language") {
    return REPORT_INFO_SECTION_TITLE;
  }
  if (field.key === "owner_address" || field.key === "owner_name") {
    return "Propietario";
  }
  if (field.key === "nhc" || field.key === "medical_record_number") {
    return "Centro Veterinario";
  }
  const fallbackSectionLabel = getUiSectionLabelFromSectionId(fallbackSection);
  if (fallbackSectionLabel) {
    return fallbackSectionLabel;
  }
  return SECTION_LABELS[field.section ?? fallbackSection] ?? fallbackSection;
}

export function getLabelTooltipText(key: string): string | undefined {
  if (key === "nhc" || key === "medical_record_number") {
    return "Número de historial clínico";
  }
  return undefined;
}

export function clampConfidence(value: number): number {
  if (!Number.isFinite(value)) {
    return 0;
  }
  return Math.max(0, Math.min(1, value));
}

export function formatSignedPercent(value: number): string {
  const rounded = Math.round(value * 10) / 10;
  const isInteger = Number.isInteger(rounded);
  const absText = isInteger ? Math.abs(rounded).toFixed(0) : Math.abs(rounded).toFixed(1);
  if (rounded > 0) {
    return `+${absText}%`;
  }
  if (rounded < 0) {
    return `-${absText}%`;
  }
  return "0%";
}

export function getConfidenceTone(
  confidence: number,
  cutoffs: ConfidenceBandCutoffs,
): ConfidenceTone {
  const value = clampConfidence(confidence);
  if (value < cutoffs.low_max) {
    return "low";
  }
  if (value < cutoffs.mid_max) {
    return "med";
  }
  return "high";
}

export function resolveMappingConfidence(field: ReviewField): number | null {
  if (field.origin === "human") {
    return null;
  }
  const raw = field.field_mapping_confidence;
  if (typeof raw !== "number" || !Number.isFinite(raw)) {
    return null;
  }
  return clampConfidence(raw);
}

export function resolveConfidencePolicy(
  policy: StructuredInterpretationData["confidence_policy"] | undefined,
): {
  value: ConfidencePolicyConfig | null;
  degradedReason: ConfidencePolicyDiagnosticEvent["reason"] | null;
} | null {
  if (!policy) {
    return { value: null, degradedReason: "missing_policy_version" };
  }
  const policyVersion = policy.policy_version?.trim();
  if (!policyVersion) {
    return { value: null, degradedReason: "missing_policy_version" };
  }
  const cutoffs = policy.band_cutoffs;
  if (!cutoffs) {
    return { value: null, degradedReason: "missing_band_cutoffs" };
  }
  const lowMax = cutoffs.low_max;
  const midMax = cutoffs.mid_max;
  if (
    !Number.isFinite(lowMax) ||
    !Number.isFinite(midMax) ||
    lowMax < 0 ||
    midMax > 1 ||
    lowMax >= midMax
  ) {
    return { value: null, degradedReason: "invalid_band_cutoffs" };
  }
  return {
    value: {
      policy_version: policyVersion,
      band_cutoffs: {
        low_max: lowMax,
        mid_max: midMax,
      },
    },
    degradedReason: null,
  };
}

export function emitConfidencePolicyDiagnosticEvent(event: ConfidencePolicyDiagnosticEvent): void {
  if (typeof window !== "undefined") {
    const store = window.__confidencePolicyDiagnostics ?? [];
    store.push(event);
    window.__confidencePolicyDiagnostics = store;
  }
  console.warn("[confidence-policy]", event);
}

export function isFieldValueEmpty(value: unknown): boolean {
  return value === null || value === undefined || value === "";
}

export function formatFieldValue(
  value: string | number | boolean | null,
  valueType: string,
): string {
  if (isFieldValueEmpty(value)) {
    return MISSING_VALUE_PLACEHOLDER;
  }
  if (valueType === "boolean") {
    return value ? "Sí" : "No";
  }
  if (valueType === "date") {
    const parsed = new Date(String(value));
    if (!Number.isNaN(parsed.getTime())) {
      return parsed.toLocaleDateString("es-ES");
    }
  }
  return String(value);
}

export function getReviewFieldDisplayValue(field: {
  display_value?: string;
  value: string | number | boolean | null;
  value_type: string;
}): string {
  if (typeof field.display_value === "string" && field.display_value.trim().length > 0) {
    return field.display_value;
  }
  return formatFieldValue(field.value, field.value_type);
}

export function getNormalizedVisitId(visit: ReviewVisitGroup, visitIndex: number): string {
  const trimmedVisitId = visit.visit_id.trim();
  if (trimmedVisitId.length > 0) {
    return trimmedVisitId;
  }
  return `visit_${visitIndex + 1}`;
}

export function getVisitTimestamp(visitDate: string | null): number | null {
  if (!visitDate || visitDate.trim().length === 0) {
    return null;
  }
  const parsed = new Date(visitDate);
  const time = parsed.getTime();
  if (Number.isNaN(time)) {
    return null;
  }
  return time;
}

export function truncateText(text: string, limit: number): string {
  if (text.length <= limit) {
    return text;
  }
  return `${text.slice(0, limit - 1).trimEnd()}…`;
}

export function getReviewPanelMessage(reviewPanelState: string): string | null {
  if (reviewPanelState === "idle") {
    return "Selecciona un documento para empezar la revisión.";
  }
  if (reviewPanelState === "loading") {
    return "Cargando interpretación estructurada...";
  }
  if (reviewPanelState === "no_completed_run" || reviewPanelState === "error") {
    return "Interpretación no disponible";
  }
  return null;
}
