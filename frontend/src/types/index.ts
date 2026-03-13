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

export type StructuredInterpretationData = {
  document_id: string;
  processing_run_id: string;
  created_at: string;
  schema_contract?: string;
  fields: ReviewField[];
  visits?: ReviewVisitGroup[];
  other_fields?: ReviewField[];
  confidence_policy?: ConfidencePolicyConfig;
};

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
