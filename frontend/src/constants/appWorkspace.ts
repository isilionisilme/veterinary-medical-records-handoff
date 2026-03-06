import { GLOBAL_SCHEMA } from "../lib/globalSchema";
import type { MedicalRecordSectionId } from "../types/appWorkspace";

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
export const DEBUG_CONFIDENCE_POLICY = import.meta.env.VITE_DEBUG_CONFIDENCE === "true";
export const MAX_UPLOAD_SIZE_BYTES = 20 * 1024 * 1024;
export const MISSING_VALUE_PLACEHOLDER = "—";
export const EMPTY_LIST_PLACEHOLDER = "Sin elementos";
export const OTHER_EXTRACTED_FIELDS_SECTION_TITLE = "Otros campos detectados";
export const OTHER_EXTRACTED_FIELDS_EMPTY_STATE = "Sin otros campos detectados.";
export const VISITS_EMPTY_STATE = "Sin visitas detectadas.";
export const VISITS_UNASSIGNED_HINT = "Elementos detectados sin fecha/visita asociada.";
export const REPORT_INFO_SECTION_TITLE = "Detalles del informe";

export const MEDICAL_RECORD_SECTION_ID_ORDER: readonly MedicalRecordSectionId[] = [
  "clinic",
  "patient",
  "owner",
  "visits",
  "notes",
  "other",
  "report_info",
] as const;

export const MEDICAL_RECORD_SECTION_ID_SET = new Set<string>(MEDICAL_RECORD_SECTION_ID_ORDER);

export const SECTION_ID_TO_UI_LABEL: Record<MedicalRecordSectionId, string> = {
  clinic: "Centro Veterinario",
  patient: "Paciente",
  owner: "Propietario",
  visits: "Visitas",
  notes: "Notas internas",
  other: OTHER_EXTRACTED_FIELDS_SECTION_TITLE,
  report_info: REPORT_INFO_SECTION_TITLE,
};

export const MEDICAL_RECORD_SECTION_ORDER = [
  "Centro Veterinario",
  "Paciente",
  "Propietario",
  "Visitas",
  "Notas internas",
  OTHER_EXTRACTED_FIELDS_SECTION_TITLE,
  REPORT_INFO_SECTION_TITLE,
] as const;

export const DOCS_SIDEBAR_PIN_STORAGE_KEY = "docsSidebarPinned";
export const REVIEW_SPLIT_RATIO_STORAGE_KEY = "reviewSplitRatio";
export const DEFAULT_REVIEW_SPLIT_RATIO = 0.62;

export const MIN_PDF_PANEL_WIDTH_PX = 560;
export const MIN_STRUCTURED_PANEL_WIDTH_PX = 420;
export const SPLITTER_COLUMN_WIDTH_PX = 14;
export const REVIEW_SPLIT_RATIO_EPSILON = 0.0005;
export const REVIEW_SPLIT_MIN_WIDTH_PX =
  MIN_PDF_PANEL_WIDTH_PX + MIN_STRUCTURED_PANEL_WIDTH_PX + SPLITTER_COLUMN_WIDTH_PX;
export const SPLIT_SNAP_POINTS = [0.7, 0.6, 0.5] as const;

export const STRUCTURED_FIELD_ROW_CLASS = "w-full";
export const STRUCTURED_FIELD_LABEL_CLASS = "min-w-0 text-sm font-medium leading-5 break-words";
export const STRUCTURED_FIELD_STACK_CLASS = "space-y-[var(--field-row-gap-y)]";

export const LONG_TEXT_FALLBACK_THRESHOLD = 180;
export const LONG_TEXT_FIELD_KEYS = new Set([
  "treatment_plan",
  "observations",
  "actions",
  "diagnosis",
  "symptoms",
  "procedure",
  "medication",
  "reason_for_visit",
]);
export const OWNER_SECTION_FIELD_KEYS = new Set(["owner_name", "owner_address"]);
export const VISIT_SECTION_FIELD_KEYS = new Set(["visit_date", "reason_for_visit"]);

export const CANONICAL_VISIT_SCOPED_FIELD_KEYS = [
  "observations",
  "actions",
  "symptoms",
  "diagnosis",
  "procedure",
  "medication",
  "treatment_plan",
  "allergies",
  "vaccinations",
  "lab_result",
  "imaging",
] as const;

export const CANONICAL_VISIT_METADATA_KEYS = [
  "visit_date",
  "admission_date",
  "discharge_date",
  "reason_for_visit",
] as const;

export const CANONICAL_DOCUMENT_CONCEPTS = [
  { canonicalKey: "clinic_name" },
  { canonicalKey: "clinic_address" },
  { canonicalKey: "vet_name" },
  { canonicalKey: "nhc", aliases: ["medical_record_number"] },
  { canonicalKey: "pet_name" },
  { canonicalKey: "species" },
  { canonicalKey: "breed" },
  { canonicalKey: "sex" },
  { canonicalKey: "age" },
  { canonicalKey: "dob" },
  { canonicalKey: "microchip_id" },
  { canonicalKey: "weight" },
  { canonicalKey: "reproductive_status", aliases: ["repro_status"] },
  { canonicalKey: "owner_name" },
  { canonicalKey: "owner_address" },
  { canonicalKey: "notes" },
  { canonicalKey: "language" },
] as const;

export const HIDDEN_EXTRACTED_FIELDS = new Set([
  "document date",
  "document_date",
  "fecha de documento",
  "fecha documento",
  "fecha_documento",
  "imaging",
  "imagine",
  "imagen",
]);

export const SECTION_LABELS: Record<string, string> = {
  "Identificacion del caso": "Centro Veterinario",
  "Datos de la clínica": "Centro Veterinario",
  "Visita / episodio": "Visitas",
  Clinico: "Visitas",
  "Metadatos / revisión": REPORT_INFO_SECTION_TITLE,
};

export const FIELD_LABELS: Record<string, string> = {
  clinic_name: "Nombre",
  clinic_address: "Dirección",
  pet_name: "Nombre",
  dob: "Nacimiento",
  owner_name: "Nombre",
  owner_address: "Dirección",
  nhc: "NHC",
  medical_record_number: "NHC",
  notes: "Notas",
  language: "Idioma",
  visit_date: "Fecha de visita",
  admission_date: "Fecha de admisión",
  discharge_date: "Fecha de alta",
  reason_for_visit: "Motivo de visita",
  observations: "Observaciones",
  actions: "Acciones",
  diagnosis: "Diagnóstico",
  symptoms: "Síntomas",
  procedure: "Procedimiento",
  medication: "Medicación",
  treatment_plan: "Plan de tratamiento",
  allergies: "Alergias",
  vaccinations: "Vacunaciones",
  lab_result: "Resultado de laboratorio",
  imaging: "Imagen",
};

export const HIDDEN_REVIEW_FIELDS = new Set([
  "document_date",
  "claim_id",
  "owner_id",
  "invoice_total",
  "covered_amount",
  "non_covered_amount",
  "line_item",
]);

export const BILLING_REVIEW_FIELDS = new Set([
  "claim_id",
  "invoice_total",
  "covered_amount",
  "non_covered_amount",
  "line_item",
]);

export const CRITICAL_GLOBAL_SCHEMA_KEYS = new Set(
  GLOBAL_SCHEMA.filter((field) => field.critical).map((field) => field.key),
);

export const RUN_STATE_LABELS: Record<string, string> = {
  QUEUED: "En cola",
  RUNNING: "En curso",
  COMPLETED: "Completado",
  FAILED: "Fallido",
  TIMED_OUT: "Tiempo agotado",
};

export const NON_TECHNICAL_FAILURE: Record<string, string> = {
  EXTRACTION_FAILED: "No se pudo leer el contenido del documento.",
  INTERPRETATION_FAILED: "No se pudo interpretar la informacion del documento.",
  PROCESS_TERMINATED: "El procesamiento se interrumpio antes de terminar.",
  UNKNOWN_ERROR: "Ocurrio un problema durante el procesamiento.",
};

export const REVIEW_MESSAGE_INFO_CLASS =
  "rounded-control border border-borderSubtle bg-surface px-3 py-2 text-xs text-textSecondary";
export const REVIEW_MESSAGE_MUTED_CLASS =
  "rounded-control border border-borderSubtle bg-surfaceMuted px-3 py-2 text-xs text-textSecondary";
export const REVIEW_MESSAGE_WARNING_CLASS =
  "rounded-control border border-statusWarn bg-surface px-3 py-2 text-xs text-text";
