import type { CandidateSuggestion } from "../extraction/candidateSuggestions";
import type { ConfidenceBucket } from "../lib/structuredDataFilters";

export type LoadResult = {
  data: ArrayBuffer;
  filename: string | null;
};

export type DocumentListItem = {
  document_id: string;
  original_filename: string;
  created_at: string;
  status: string;
  status_label: string;
  failure_type: string | null;
  review_status?: "IN_REVIEW" | "REVIEWED";
  reviewed_at?: string | null;
  reviewed_by?: string | null;
};

export type DocumentListResponse = {
  items: DocumentListItem[];
  limit: number;
  offset: number;
  total: number;
};

export type LatestRun = {
  run_id: string;
  state: string;
  failure_type: string | null;
};

export type DocumentDetailResponse = {
  document_id: string;
  original_filename: string;
  content_type: string;
  file_size: number;
  created_at: string;
  updated_at: string;
  status: string;
  status_message: string;
  failure_type: string | null;
  review_status: "IN_REVIEW" | "REVIEWED";
  reviewed_at: string | null;
  reviewed_by: string | null;
  latest_run: LatestRun | null;
};

export type ProcessingStep = {
  step_name: string;
  step_status: string;
  attempt: number;
  started_at: string | null;
  ended_at: string | null;
  error_code: string | null;
};

export type ProcessingHistoryRun = {
  run_id: string;
  state: string;
  failure_type: string | null;
  started_at: string | null;
  completed_at: string | null;
  steps: ProcessingStep[];
};

export type ProcessingHistoryResponse = {
  document_id: string;
  runs: ProcessingHistoryRun[];
};

export type VisitScopingMetricsSummary = {
  total_visits: number;
  assigned_visits: number;
  anchored_visits: number;
  unassigned_field_count: number;
  raw_text_available: boolean;
};

export type VisitScopingMetricsVisitRow = {
  visit_index: number;
  visit_id: string | null;
  visit_date: string | null;
  field_count: number;
  anchored_in_raw_text: boolean;
  raw_context_chars: number;
};

export type VisitScopingMetricsResponse = {
  document_id: string;
  run_id: string;
  summary: VisitScopingMetricsSummary;
  visits: VisitScopingMetricsVisitRow[];
};

export type RawTextArtifactResponse = {
  run_id: string;
  artifact_type: string;
  content_type: string;
  text: string;
};

export type ReviewEvidence = {
  page: number;
  snippet: string;
};

export type ConfidenceBandCutoffs = {
  low_max: number;
  mid_max: number;
};

export type ConfidencePolicyConfig = {
  policy_version: string;
  band_cutoffs: ConfidenceBandCutoffs;
};

export type ReviewField = {
  field_id: string;
  key: string;
  value: string | number | boolean | null;
  value_type: string;
  visit_group_id?: string;
  scope?: "document" | "visit";
  section?: string;
  domain?: "clinical" | "billing" | "meta" | "other" | string;
  classification?: "medical_record" | "other" | string;
  candidate_suggestions?: CandidateSuggestion[];
  field_candidate_confidence?: number | null;
  field_mapping_confidence?: number;
  text_extraction_reliability?: number | null;
  field_review_history_adjustment?: number;
  is_critical: boolean;
  origin: "machine" | "human";
  evidence?: ReviewEvidence;
};

export type ReviewVisitGroup = {
  visit_id: string;
  visit_date: string | null;
  admission_date?: string | null;
  discharge_date?: string | null;
  reason_for_visit?: string | null;
  fields: ReviewField[];
};

export type MedicalRecordSectionId =
  | "clinic"
  | "patient"
  | "owner"
  | "visits"
  | "notes"
  | "other"
  | "report_info";

export type MedicalRecordViewFieldSlot = {
  concept_id: string;
  section: MedicalRecordSectionId;
  scope: "document" | "visit";
  canonical_key: string;
  aliases?: string[];
  label_key?: string;
};

export type MedicalRecordViewTemplate = {
  version: string;
  sections: MedicalRecordSectionId[];
  field_slots: MedicalRecordViewFieldSlot[];
};

export type StructuredInterpretationData = {
  document_id: string;
  processing_run_id: string;
  created_at: string;
  schema_contract?: string;
  medical_record_view?: MedicalRecordViewTemplate;
  fields: ReviewField[];
  visits?: ReviewVisitGroup[];
  other_fields?: ReviewField[];
  confidence_policy?: ConfidencePolicyConfig;
};

export type ReviewSelectableField = {
  id: string;
  key: string;
  label: string;
  section: string;
  order: number;
  valueType: string;
  displayValue: string;
  isMissing: boolean;
  hasMappingConfidence: boolean;
  confidence: number;
  confidenceBand: ConfidenceBucket | null;
  source: "core" | "extracted";
  evidence?: ReviewEvidence;
  rawField?: ReviewField;
  visitGroupId?: string;
  repeatable: boolean;
};

export type ReviewDisplayField = {
  id: string;
  key: string;
  label: string;
  labelTooltip?: string;
  section: string;
  order: number;
  isCritical: boolean;
  valueType: string;
  repeatable: boolean;
  items: ReviewSelectableField[];
  isEmptyList: boolean;
  source: "core" | "extracted";
};

export type ReviewPanelState = "idle" | "loading" | "ready" | "no_completed_run" | "error";

export type DocumentReviewResponse = {
  document_id: string;
  latest_completed_run: {
    run_id: string;
    state: string;
    completed_at: string | null;
    failure_type: string | null;
  };
  active_interpretation: {
    interpretation_id: string;
    version_number: number;
    data: StructuredInterpretationData;
  };
  raw_text_artifact: {
    run_id: string;
    available: boolean;
  };
  review_status: "IN_REVIEW" | "REVIEWED";
  reviewed_at: string | null;
  reviewed_by: string | null;
};

export type DocumentUploadResponse = {
  document_id: string;
  status: string;
  created_at: string;
};

export type ReviewToggleResponse = {
  document_id: string;
  review_status: "IN_REVIEW" | "REVIEWED";
  reviewed_at: string | null;
  reviewed_by: string | null;
};

export type InterpretationChangePayload = {
  op: "ADD" | "UPDATE" | "DELETE";
  field_id?: string;
  key?: string;
  value?: string | number | boolean | null;
  value_type?: string;
};

export type InterpretationEditResponse = {
  run_id: string;
  interpretation_id: string;
  version_number: number;
  data: StructuredInterpretationData;
};

export type ConfidencePolicyDiagnosticEvent = {
  event_type: "CONFIDENCE_POLICY_CONFIG_MISSING";
  document_id: string | null;
  reason: "missing_policy_version" | "missing_band_cutoffs" | "invalid_band_cutoffs";
};

export type ConfidenceTone = "low" | "med" | "high";

declare global {
  interface Window {
    __confidencePolicyDiagnostics?: ConfidencePolicyDiagnosticEvent[];
  }
}

export class UiError extends Error {
  readonly userMessage: string;
  readonly technicalDetails?: string;

  constructor(userMessage: string, technicalDetails?: string) {
    super(userMessage);
    this.name = "UiError";
    this.userMessage = userMessage;
    this.technicalDetails = technicalDetails;
  }
}

export class ApiResponseError extends UiError {
  readonly errorCode?: string;
  readonly reason?: string;

  constructor(userMessage: string, technicalDetails?: string, errorCode?: string, reason?: string) {
    super(userMessage, technicalDetails);
    this.name = "ApiResponseError";
    this.errorCode = errorCode;
    this.reason = reason;
  }
}
