import { useMemo } from "react";

import {
  BILLING_REVIEW_FIELDS,
  CANONICAL_DOCUMENT_CONCEPTS,
  CANONICAL_VISIT_METADATA_KEYS,
  CANONICAL_VISIT_SCOPED_FIELD_KEYS,
  MEDICAL_RECORD_SECTION_ORDER,
  OTHER_EXTRACTED_FIELDS_SECTION_TITLE,
  REPORT_INFO_SECTION_TITLE,
} from "../constants/appWorkspace";
import {
  getConfidenceTone,
  isFieldValueEmpty,
  resolveMappingConfidence,
} from "../lib/appWorkspaceUtils";
import { GLOBAL_SCHEMA } from "../lib/globalSchema";
import {
  type StructuredDataFilters,
  matchesStructuredDataFilters,
} from "../lib/structuredDataFilters";
import type {
  ConfidencePolicyConfig,
  DocumentReviewResponse,
  ReviewField,
  ReviewVisitGroup,
  StructuredInterpretationData,
} from "../types/appWorkspace";
import { useDisplayFieldMapping } from "./useDisplayFieldMapping";
import { useFieldExtraction } from "./useFieldExtraction";

type UseReviewDataPipelineParams = {
  documentReview: {
    data: DocumentReviewResponse | undefined;
  };
  interpretationData: StructuredInterpretationData | undefined;
  isCanonicalContract: boolean;
  hasMalformedCanonicalFieldSlots: boolean;
  reviewVisits: ReviewVisitGroup[];
  activeConfidencePolicy: ConfidencePolicyConfig | null;
  structuredDataFilters: StructuredDataFilters;
  hasActiveStructuredFilters: boolean;
};

export function useReviewDataPipeline({
  documentReview,
  interpretationData,
  isCanonicalContract,
  hasMalformedCanonicalFieldSlots,
  reviewVisits,
  activeConfidencePolicy,
  structuredDataFilters,
  hasActiveStructuredFilters,
}: UseReviewDataPipelineParams) {
  const hasVisitGroups = reviewVisits.length > 0;
  const hasUnassignedVisitGroup = reviewVisits.some(
    (visit) => visit.visit_id.trim().toLowerCase() === "unassigned",
  );

  const { validatedReviewFields, matchesByKey, buildSelectableField, explicitOtherReviewFields } =
    useFieldExtraction({
      documentReview,
      interpretationData,
      isCanonicalContract,
      reviewVisits,
      activeConfidencePolicy,
    });

  const { coreDisplayFields, otherDisplayFields } = useDisplayFieldMapping({
    isCanonicalContract,
    hasMalformedCanonicalFieldSlots,
    interpretationData,
    validatedReviewFields,
    matchesByKey,
    buildSelectableField,
    explicitOtherReviewFields,
  });

  const groupedCoreFields = useMemo(() => {
    const groups = new Map<string, typeof coreDisplayFields>();
    coreDisplayFields.forEach((field) => {
      const current = groups.get(field.section) ?? [];
      current.push(field);
      groups.set(field.section, current);
    });
    return MEDICAL_RECORD_SECTION_ORDER.filter(
      (section) => section !== OTHER_EXTRACTED_FIELDS_SECTION_TITLE,
    ).map((section) => ({
      section,
      fields: (groups.get(section) ?? []).sort((a, b) => a.order - b.order),
    }));
  }, [coreDisplayFields]);

  const canonicalVisitFieldOrder = useMemo(() => {
    const fallbackOrder = [...CANONICAL_VISIT_METADATA_KEYS, ...CANONICAL_VISIT_SCOPED_FIELD_KEYS];
    if (!isCanonicalContract || hasMalformedCanonicalFieldSlots) {
      return fallbackOrder;
    }
    const rawSlots = interpretationData?.medical_record_view?.field_slots;
    const slots = Array.isArray(rawSlots) ? rawSlots : [];
    const orderedKeys: string[] = [];
    slots.forEach((slot) => {
      if (slot.scope !== "visit") {
        return;
      }
      const canonicalKey = slot.canonical_key;
      if (!canonicalKey || BILLING_REVIEW_FIELDS.has(canonicalKey)) {
        return;
      }
      if (!orderedKeys.includes(canonicalKey)) {
        orderedKeys.push(canonicalKey);
      }
    });
    fallbackOrder.forEach((key) => {
      if (!orderedKeys.includes(key)) {
        orderedKeys.push(key);
      }
    });
    return orderedKeys;
  }, [
    hasMalformedCanonicalFieldSlots,
    interpretationData?.medical_record_view?.field_slots,
    isCanonicalContract,
  ]);

  const visibleCoreGroups = useMemo(() => {
    if (!hasActiveStructuredFilters) {
      return groupedCoreFields;
    }
    return groupedCoreFields
      .map((group) => ({
        section: group.section,
        fields: group.fields.filter((field) =>
          matchesStructuredDataFilters(field, structuredDataFilters),
        ),
      }))
      .filter((group) => group.fields.length > 0);
  }, [groupedCoreFields, hasActiveStructuredFilters, structuredDataFilters]);

  const visibleOtherDisplayFields = useMemo(
    () => (hasActiveStructuredFilters ? [] : otherDisplayFields),
    [hasActiveStructuredFilters, otherDisplayFields],
  );
  const visibleCoreFields = useMemo(
    () => visibleCoreGroups.flatMap((group) => group.fields),
    [visibleCoreGroups],
  );

  const reportSections = useMemo(() => {
    const coreSections = visibleCoreGroups.map((group) => ({
      id: `core:${group.section}`,
      title: group.section,
      fields: group.fields,
    }));
    if (hasActiveStructuredFilters) {
      return coreSections;
    }
    const extraSection = {
      id: "extra:section",
      title: OTHER_EXTRACTED_FIELDS_SECTION_TITLE,
      fields: visibleOtherDisplayFields,
    };
    const infoIndex = coreSections.findIndex(
      (section) => section.title === REPORT_INFO_SECTION_TITLE,
    );
    if (infoIndex < 0) {
      return [...coreSections, extraSection];
    }
    return [...coreSections.slice(0, infoIndex), extraSection, ...coreSections.slice(infoIndex)];
  }, [hasActiveStructuredFilters, visibleCoreGroups, visibleOtherDisplayFields]);

  const selectableReviewItems = useMemo(
    () => [...visibleCoreFields, ...visibleOtherDisplayFields].flatMap((field) => field.items),
    [visibleCoreFields, visibleOtherDisplayFields],
  );

  const detectedFieldsSummary = useMemo(() => {
    const summarizeConfidenceBands = () => {
      let low = 0;
      let medium = 0;
      let high = 0;
      let unknown = 0;
      if (!activeConfidencePolicy) {
        return { low, medium, high, unknown: 0 };
      }
      coreDisplayFields.forEach((field) => {
        const presentItems = field.items.filter((item) => !item.isMissing);
        if (presentItems.length === 0) {
          return;
        }
        if (presentItems.some((item) => item.confidenceBand === "low")) {
          low += 1;
          return;
        }
        if (presentItems.some((item) => item.confidenceBand === "medium")) {
          medium += 1;
          return;
        }
        if (presentItems.some((item) => item.confidenceBand === "high")) {
          high += 1;
          return;
        }
        unknown += 1;
      });
      return { low, medium, high, unknown };
    };
    if (isCanonicalContract) {
      const topLevelFields = (interpretationData?.fields ?? []).filter(
        (field): field is ReviewField => Boolean(field && typeof field === "object"),
      );
      const visits = reviewVisits;
      const confidenceCutoffs = activeConfidencePolicy?.band_cutoffs;
      let detected = 0;
      let low = 0;
      let medium = 0;
      let high = 0;
      let unknown = 0;
      const addDetectedConceptFromFields = (
        fields: ReviewField[],
        candidateKeys: readonly string[],
      ) => {
        const matchingWithValue = fields.filter(
          (field) => candidateKeys.includes(field.key) && !isFieldValueEmpty(field.value),
        );
        if (matchingWithValue.length === 0) {
          return;
        }
        detected += 1;
        if (!confidenceCutoffs) {
          unknown += 1;
          return;
        }
        const bestConfidence = matchingWithValue.reduce<number | null>((currentBest, field) => {
          const confidence = resolveMappingConfidence(field);
          if (confidence === null) {
            return currentBest;
          }
          if (currentBest === null || confidence > currentBest) {
            return confidence;
          }
          return currentBest;
        }, null);
        if (bestConfidence === null) {
          unknown += 1;
          return;
        }
        const tone = getConfidenceTone(bestConfidence, confidenceCutoffs);
        if (tone === "low") {
          low += 1;
          return;
        }
        if (tone === "med") {
          medium += 1;
          return;
        }
        high += 1;
      };
      CANONICAL_DOCUMENT_CONCEPTS.forEach((concept) => {
        const aliases = "aliases" in concept ? (concept.aliases ?? []) : [];
        addDetectedConceptFromFields(
          topLevelFields.filter(
            (field) => field.scope !== "visit" && !BILLING_REVIEW_FIELDS.has(field.key),
          ),
          [concept.canonicalKey, ...aliases],
        );
      });
      CANONICAL_VISIT_SCOPED_FIELD_KEYS.forEach((key) => {
        const visitFieldsForKey = visits.flatMap((visit) =>
          (visit.fields ?? []).filter(
            (field): field is ReviewField =>
              Boolean(field && typeof field === "object") && !BILLING_REVIEW_FIELDS.has(field.key),
          ),
        );
        addDetectedConceptFromFields(visitFieldsForKey, [key]);
      });
      CANONICAL_VISIT_METADATA_KEYS.forEach((key) => {
        const hasValue = visits.some((visit) => !isFieldValueEmpty(visit[key]));
        if (!hasValue) {
          return;
        }
        detected += 1;
        unknown += 1;
      });
      return {
        detected,
        total:
          CANONICAL_DOCUMENT_CONCEPTS.length +
          CANONICAL_VISIT_SCOPED_FIELD_KEYS.length +
          CANONICAL_VISIT_METADATA_KEYS.length,
        low,
        medium,
        high,
        unknown,
      };
    }
    let detected = 0;
    const total = GLOBAL_SCHEMA.length;
    const confidenceBands = summarizeConfidenceBands();
    if (!activeConfidencePolicy) {
      return {
        detected,
        total,
        low: confidenceBands.low,
        medium: confidenceBands.medium,
        high: confidenceBands.high,
        unknown: 0,
      };
    }
    coreDisplayFields.forEach((field) => {
      const presentItems = field.items.filter(
        (item) => !item.isMissing && item.confidenceBand !== null,
      );
      if (presentItems.length === 0) {
        return;
      }
      detected += 1;
      if (presentItems.some((item) => item.confidenceBand === "low")) {
        return;
      }
      if (presentItems.some((item) => item.confidenceBand === "medium")) {
        return;
      }
    });
    return {
      detected,
      total,
      low: confidenceBands.low,
      medium: confidenceBands.medium,
      high: confidenceBands.high,
      unknown: 0,
    };
  }, [
    activeConfidencePolicy,
    coreDisplayFields,
    interpretationData?.fields,
    isCanonicalContract,
    reviewVisits,
  ]);

  return {
    reportSections,
    selectableReviewItems,
    coreDisplayFields,
    otherDisplayFields,
    detectedFieldsSummary,
    reviewVisits,
    isCanonicalContract,
    hasMalformedCanonicalFieldSlots,
    hasVisitGroups,
    hasUnassignedVisitGroup,
    canonicalVisitFieldOrder,
    validatedReviewFields,
    buildSelectableField,
    visibleCoreGroups,
    visibleOtherDisplayFields,
  };
}
