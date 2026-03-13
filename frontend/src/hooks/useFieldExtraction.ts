import { useCallback, useEffect, useMemo, useRef } from "react";

import { logExtractionDebugEvent, type ExtractionDebugEvent } from "../extraction/extractionDebug";
import { validateFieldValue } from "../extraction/fieldValidators";
import { BILLING_REVIEW_FIELDS, HIDDEN_REVIEW_FIELDS } from "../constants/appWorkspace";
import {
  getConfidenceTone,
  getNormalizedVisitId,
  resolveMappingConfidence,
} from "../lib/appWorkspaceUtils";
import { GLOBAL_SCHEMA } from "../lib/globalSchema";
import type { ConfidenceBucket } from "../lib/structuredDataFilters";
import type {
  ConfidencePolicyConfig,
  DocumentReviewResponse,
  ReviewField,
  ReviewSelectableField,
  ReviewVisitGroup,
  StructuredInterpretationData,
} from "../types/appWorkspace";

type UseFieldExtractionParams = {
  documentReview: {
    data: DocumentReviewResponse | undefined;
  };
  interpretationData: StructuredInterpretationData | undefined;
  isCanonicalContract: boolean;
  reviewVisits: ReviewVisitGroup[];
  activeConfidencePolicy: ConfidencePolicyConfig | null;
};

export type BuildSelectableFieldFn = (
  base: Omit<
    ReviewSelectableField,
    "hasMappingConfidence" | "confidence" | "confidenceBand" | "isMissing" | "rawField"
  >,
  rawField: ReviewField | undefined,
  isMissing: boolean,
) => ReviewSelectableField;

export function useFieldExtraction({
  documentReview,
  interpretationData,
  isCanonicalContract,
  reviewVisits,
  activeConfidencePolicy,
}: UseFieldExtractionParams) {
  const lastExtractionDebugDocIdRef = useRef<string | null>(null);
  const loggedExtractionDebugEventKeysRef = useRef<Set<string>>(new Set());

  const extractedReviewFields = useMemo(() => {
    const baseFields = interpretationData?.fields ?? [];
    if (!isCanonicalContract) {
      return baseFields;
    }
    const flattenedVisitFields = reviewVisits.flatMap((visit, visitIndex) => {
      const normalizedVisitId = getNormalizedVisitId(visit, visitIndex);
      const metadataFields: ReviewField[] = [
        {
          field_id: `visit-meta-date:${normalizedVisitId}`,
          key: "visit_date",
          value: visit.visit_date,
          value_type: "date",
          visit_group_id: normalizedVisitId,
          scope: "visit",
          section: "visits",
          classification: "medical_record",
          domain: "clinical",
          is_critical: true,
          origin: "machine",
        },
        {
          field_id: `visit-meta-admission:${normalizedVisitId}`,
          key: "admission_date",
          value: visit.admission_date ?? null,
          value_type: "date",
          visit_group_id: normalizedVisitId,
          scope: "visit",
          section: "visits",
          classification: "medical_record",
          domain: "clinical",
          is_critical: false,
          origin: "machine",
        },
        {
          field_id: `visit-meta-discharge:${normalizedVisitId}`,
          key: "discharge_date",
          value: visit.discharge_date ?? null,
          value_type: "date",
          visit_group_id: normalizedVisitId,
          scope: "visit",
          section: "visits",
          classification: "medical_record",
          domain: "clinical",
          is_critical: false,
          origin: "machine",
        },
        {
          field_id: `visit-meta-reason:${normalizedVisitId}`,
          key: "reason_for_visit",
          value: visit.reason_for_visit ?? null,
          value_type: "string",
          visit_group_id: normalizedVisitId,
          scope: "visit",
          section: "visits",
          classification: "medical_record",
          domain: "clinical",
          is_critical: false,
          origin: "machine",
        },
      ];
      const scopedFields = (visit.fields ?? []).map((field, fieldIndex) => ({
        ...field,
        field_id: field.field_id || `visit-field:${normalizedVisitId}:${field.key}:${fieldIndex}`,
        visit_group_id: normalizedVisitId,
        scope: "visit" as const,
        section: field.section ?? "visits",
      }));
      return [...metadataFields, ...scopedFields];
    });
    return [...baseFields, ...flattenedVisitFields];
  }, [interpretationData?.fields, isCanonicalContract, reviewVisits]);

  const explicitOtherReviewFields = useMemo(() => {
    if (!isCanonicalContract) {
      return [] as ReviewField[];
    }
    return (interpretationData?.other_fields ?? [])
      .filter((field) => !BILLING_REVIEW_FIELDS.has(field.key))
      .map((field, index) => ({
        ...field,
        field_id: field.field_id || `other-field:${field.key}:${index}`,
        classification: field.classification ?? "other",
        section: field.section ?? "other",
      }));
  }, [interpretationData, isCanonicalContract]);

  const validationResult = useMemo(() => {
    const fieldsByKey = new Map<string, number>();
    const acceptedFields: ReviewField[] = [];
    const debugEvents: ExtractionDebugEvent[] = [];
    const documentId = documentReview.data?.active_interpretation.data.document_id;
    extractedReviewFields.forEach((field) => {
      fieldsByKey.set(field.key, (fieldsByKey.get(field.key) ?? 0) + 1);
    });
    extractedReviewFields.forEach((field) => {
      const rawValue = field.value === null || field.value === undefined ? "" : String(field.value);
      const validation = validateFieldValue(field.key, rawValue);
      if (!validation.ok) {
        debugEvents.push({
          field: field.key,
          status: "rejected",
          raw: rawValue,
          reason: validation.reason,
          docId: documentId,
          page: field.evidence?.page,
        });
        return;
      }
      const normalizedValue = validation.normalized ?? rawValue.trim();
      acceptedFields.push({
        ...field,
        value: normalizedValue,
      });
      debugEvents.push({
        field: field.key,
        status: "accepted",
        raw: rawValue,
        normalized: normalizedValue,
        docId: documentId,
        page: field.evidence?.page,
      });
    });
    GLOBAL_SCHEMA.forEach((definition) => {
      if ((fieldsByKey.get(definition.key) ?? 0) > 0) {
        return;
      }
      if (HIDDEN_REVIEW_FIELDS.has(definition.key)) {
        return;
      }
      debugEvents.push({
        field: definition.key,
        status: "missing",
        docId: documentId,
      });
    });
    return {
      acceptedFields,
      debugEvents,
    };
  }, [documentReview.data?.active_interpretation.data.document_id, extractedReviewFields]);

  useEffect(() => {
    const documentId = documentReview.data?.active_interpretation.data.document_id ?? null;
    if (lastExtractionDebugDocIdRef.current !== documentId) {
      loggedExtractionDebugEventKeysRef.current.clear();
      lastExtractionDebugDocIdRef.current = documentId;
    }
    validationResult.debugEvents.forEach((event) => {
      const eventKey = [
        event.docId ?? "",
        event.field,
        event.status,
        event.raw ?? "",
        event.normalized ?? "",
        event.reason ?? "",
        event.page ?? "",
      ].join("|");
      if (loggedExtractionDebugEventKeysRef.current.has(eventKey)) {
        return;
      }
      loggedExtractionDebugEventKeysRef.current.add(eventKey);
      logExtractionDebugEvent(event);
    });
  }, [documentReview.data?.active_interpretation.data.document_id, validationResult.debugEvents]);

  const validatedReviewFields = validationResult.acceptedFields.filter((field) => {
    if (isCanonicalContract) {
      return !BILLING_REVIEW_FIELDS.has(field.key);
    }
    return !HIDDEN_REVIEW_FIELDS.has(field.key);
  });

  const buildSelectableField: BuildSelectableFieldFn = useCallback(
    (base, rawField, isMissing) => {
      const mappingConfidence = rawField ? resolveMappingConfidence(rawField) : null;
      let confidenceBand: ConfidenceBucket | null = null;
      if (mappingConfidence !== null && activeConfidencePolicy) {
        const tone = getConfidenceTone(mappingConfidence, activeConfidencePolicy.band_cutoffs);
        confidenceBand = tone === "med" ? "medium" : tone;
      }
      return {
        ...base,
        isMissing,
        hasMappingConfidence: mappingConfidence !== null,
        confidence: mappingConfidence ?? 0,
        confidenceBand,
        rawField,
        visitGroupId: rawField?.visit_group_id,
      };
    },
    [activeConfidencePolicy],
  );

  const matchesByKey = useMemo(() => {
    const matches = new Map<string, ReviewField[]>();
    validatedReviewFields.forEach((field) => {
      const group = matches.get(field.key) ?? [];
      group.push(field);
      matches.set(field.key, group);
    });
    return matches;
  }, [validatedReviewFields]);

  return {
    extractedReviewFields,
    validatedReviewFields,
    matchesByKey,
    buildSelectableField,
    explicitOtherReviewFields,
  };
}
