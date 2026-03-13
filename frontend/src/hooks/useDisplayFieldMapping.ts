import { useMemo } from "react";

import {
  BILLING_REVIEW_FIELDS,
  CRITICAL_GLOBAL_SCHEMA_KEYS,
  FIELD_LABELS,
  HIDDEN_REVIEW_FIELDS,
  MEDICAL_RECORD_SECTION_ID_ORDER,
  MISSING_VALUE_PLACEHOLDER,
  OTHER_EXTRACTED_FIELDS_SECTION_TITLE,
  REPORT_INFO_SECTION_TITLE,
} from "../constants/appWorkspace";
import {
  clampConfidence,
  formatReviewKeyLabel,
  getReviewFieldDisplayValue,
  getLabelTooltipText,
  getUiSectionLabelFromSectionId,
  isFieldValueEmpty,
  resolveMappingConfidence,
  resolveUiSection,
  shouldHideExtractedField,
} from "../lib/appWorkspaceUtils";
import { GLOBAL_SCHEMA } from "../lib/globalSchema";
import type {
  ReviewDisplayField,
  ReviewField,
  ReviewSelectableField,
  StructuredInterpretationData,
} from "../types/appWorkspace";
import type { BuildSelectableFieldFn } from "./useFieldExtraction";

type UseDisplayFieldMappingParams = {
  isCanonicalContract: boolean;
  hasMalformedCanonicalFieldSlots: boolean;
  interpretationData: StructuredInterpretationData | undefined;
  validatedReviewFields: ReviewField[];
  matchesByKey: Map<string, ReviewField[]>;
  buildSelectableField: BuildSelectableFieldFn;
  explicitOtherReviewFields: ReviewField[];
};

export function useDisplayFieldMapping({
  isCanonicalContract,
  hasMalformedCanonicalFieldSlots,
  interpretationData,
  validatedReviewFields,
  matchesByKey,
  buildSelectableField,
  explicitOtherReviewFields,
}: UseDisplayFieldMappingParams) {
  const coreDisplayFields = useMemo(() => {
    let coreDefinitions: Array<{
      key: string;
      label: string;
      section: string;
      order: number;
      value_type: string;
      repeatable: boolean;
      critical: boolean;
      aliases?: string[];
      slotScope?: "document" | "visit";
    }> = [];
    if (isCanonicalContract) {
      if (hasMalformedCanonicalFieldSlots) {
        return [];
      }
      const rawFieldSlots = interpretationData?.medical_record_view?.field_slots;
      const fieldSlots = Array.isArray(rawFieldSlots) ? rawFieldSlots : [];
      const documentSlots = fieldSlots.filter(
        (slot) => slot.scope === "document" && !BILLING_REVIEW_FIELDS.has(slot.canonical_key),
      );
      const schemaCriticalByKey = new Map(
        GLOBAL_SCHEMA.map((definition) => [definition.key, Boolean(definition.critical)]),
      );
      const sectionOrderIndex = new Map<string, number>(
        MEDICAL_RECORD_SECTION_ID_ORDER.map((sectionId, index) => [sectionId, index]),
      );
      const slotDefinitions = documentSlots.map((slot, index) => {
        const sectionLabel =
          getUiSectionLabelFromSectionId(slot.section) ?? REPORT_INFO_SECTION_TITLE;
        const sectionIndex =
          sectionOrderIndex.get(slot.section) ?? MEDICAL_RECORD_SECTION_ID_ORDER.length;
        const slotKeys = [slot.canonical_key, ...(slot.aliases ?? [])];
        const criticalFromSchema = slotKeys.some((key) => schemaCriticalByKey.get(key));
        const criticalFromFields = validatedReviewFields.some(
          (field) => slotKeys.includes(field.key) && Boolean(field.is_critical),
        );
        const isCriticalSlot =
          CRITICAL_GLOBAL_SCHEMA_KEYS.has(slot.canonical_key) ||
          Boolean(slot.aliases?.some((alias) => CRITICAL_GLOBAL_SCHEMA_KEYS.has(alias)));
        return {
          key: slot.canonical_key,
          label: formatReviewKeyLabel(slot.canonical_key),
          section: sectionLabel,
          order: sectionIndex * 1000 + index,
          value_type: "string",
          repeatable: false,
          critical: criticalFromSchema || criticalFromFields || isCriticalSlot,
          aliases: slot.aliases,
          slotScope: "document" as const,
        };
      });
      const visitDefinitions: Array<{
        key: string;
        label: string;
        section: string;
        order: number;
        value_type: string;
        repeatable: boolean;
        critical: boolean;
        slotScope?: "document" | "visit";
      }> = [];
      const seenVisitKeys = new Set<string>();
      validatedReviewFields
        .filter((field) => field.scope === "visit" && field.classification !== "other")
        .forEach((field) => {
          if (seenVisitKeys.has(field.key)) {
            return;
          }
          seenVisitKeys.add(field.key);
          visitDefinitions.push({
            key: field.key,
            label: formatReviewKeyLabel(field.key),
            section: "Visitas",
            order: 3000 + visitDefinitions.length,
            value_type: field.value_type,
            repeatable: true,
            critical: Boolean(field.is_critical),
            slotScope: "visit",
          });
        });
      coreDefinitions = [...slotDefinitions, ...visitDefinitions];
    } else {
      const templateDefinitions = GLOBAL_SCHEMA.filter(
        (definition) => !HIDDEN_REVIEW_FIELDS.has(definition.key),
      );
      const dynamicMedicalRecordDefinitions = validatedReviewFields
        .filter((field) => {
          if (field.classification === "other") {
            return false;
          }
          if (HIDDEN_REVIEW_FIELDS.has(field.key)) {
            return false;
          }
          return !templateDefinitions.some((definition) => definition.key === field.key);
        })
        .map((field, index) => ({
          key: field.key,
          label: formatReviewKeyLabel(field.key),
          section: resolveUiSection(field, REPORT_INFO_SECTION_TITLE),
          order: 10_000 + index,
          value_type: field.value_type,
          repeatable: false,
          critical: Boolean(field.is_critical),
        }));
      coreDefinitions = [...templateDefinitions, ...dynamicMedicalRecordDefinitions];
    }
    return coreDefinitions
      .map((definition): ReviewDisplayField => {
        const uiSection =
          "section" in definition && typeof definition.section === "string"
            ? resolveUiSection(
                { key: definition.key, section: definition.section },
                definition.section,
              )
            : REPORT_INFO_SECTION_TITLE;
        const uiLabel = FIELD_LABELS[definition.key] ?? definition.label;
        const labelTooltip = getLabelTooltipText(definition.key);
        let candidates = matchesByKey.get(definition.key) ?? [];
        if (isCanonicalContract && definition.aliases && definition.aliases.length > 0) {
          const aliasCandidates = definition.aliases.flatMap(
            (alias) => matchesByKey.get(alias) ?? [],
          );
          candidates = [...candidates, ...aliasCandidates];
        }
        if (definition.repeatable) {
          const items = candidates
            .filter((candidate) => !isFieldValueEmpty(candidate.value))
            .map(
              (candidate, index): ReviewSelectableField =>
                buildSelectableField(
                  {
                    id: `core:${definition.key}:${candidate.field_id}:${index}`,
                    key: definition.key,
                    label: uiLabel,
                    section: uiSection,
                    order: definition.order,
                    valueType: candidate.value_type,
                    displayValue: getReviewFieldDisplayValue(candidate),
                    source: "core",
                    evidence: candidate.evidence,
                    repeatable: true,
                  },
                  candidate,
                  false,
                ),
            );
          return {
            id: `core:${definition.key}`,
            key: definition.key,
            label: uiLabel,
            labelTooltip,
            section: uiSection,
            order: definition.order,
            isCritical: definition.critical,
            valueType: definition.value_type,
            repeatable: true,
            items,
            isEmptyList: items.length === 0,
            source: "core",
          };
        }
        const bestCandidate = candidates
          .filter((candidate) => !isFieldValueEmpty(candidate.value))
          .sort((a, b) => {
            if (isCanonicalContract && definition.slotScope === "document") {
              const aDocumentScoped = a.scope === "document" ? 1 : 0;
              const bDocumentScoped = b.scope === "document" ? 1 : 0;
              if (aDocumentScoped !== bDocumentScoped) {
                return bDocumentScoped - aDocumentScoped;
              }
            }
            return (
              clampConfidence(resolveMappingConfidence(b) ?? -1) -
              clampConfidence(resolveMappingConfidence(a) ?? -1)
            );
          })[0];
        const displayValue = bestCandidate
          ? getReviewFieldDisplayValue(bestCandidate)
          : MISSING_VALUE_PLACEHOLDER;
        const item: ReviewSelectableField = buildSelectableField(
          {
            id: `core:${definition.key}`,
            key: definition.key,
            label: uiLabel,
            section: uiSection,
            order: definition.order,
            valueType: bestCandidate?.value_type ?? definition.value_type,
            displayValue,
            source: "core",
            evidence: bestCandidate?.evidence,
            repeatable: false,
          },
          bestCandidate,
          !bestCandidate,
        );
        return {
          id: `core:${definition.key}`,
          key: definition.key,
          label: uiLabel,
          labelTooltip,
          section: uiSection,
          order: definition.order,
          isCritical: definition.critical,
          valueType: definition.value_type,
          repeatable: false,
          items: [item],
          isEmptyList: false,
          source: "core",
        };
      })
      .sort((a, b) => a.order - b.order);
  }, [
    buildSelectableField,
    hasMalformedCanonicalFieldSlots,
    interpretationData?.medical_record_view?.field_slots,
    isCanonicalContract,
    matchesByKey,
    validatedReviewFields,
  ]);

  const otherDisplayFields = useMemo(() => {
    const coreKeys = new Set(GLOBAL_SCHEMA.map((field) => field.key));
    const grouped = new Map<string, ReviewField[]>();
    const orderedKeys: string[] = [];
    const sourceFields = isCanonicalContract ? explicitOtherReviewFields : validatedReviewFields;
    sourceFields.forEach((field) => {
      if (!isCanonicalContract && coreKeys.has(field.key)) {
        return;
      }
      if (isCanonicalContract && field.classification !== "other") {
        return;
      }
      if (!isCanonicalContract && shouldHideExtractedField(field.key)) {
        return;
      }
      if (!grouped.has(field.key)) {
        grouped.set(field.key, []);
        orderedKeys.push(field.key);
      }
      grouped.get(field.key)?.push(field);
    });
    return orderedKeys.map((key, index): ReviewDisplayField => {
      const fields = grouped.get(key) ?? [];
      const label = formatReviewKeyLabel(key);
      if (fields.length > 1) {
        const items = fields
          .filter((field) => !isFieldValueEmpty(field.value))
          .map(
            (field, itemIndex): ReviewSelectableField =>
              buildSelectableField(
                {
                  id: `extra:${field.field_id}:${itemIndex}`,
                  key,
                  label,
                  section: OTHER_EXTRACTED_FIELDS_SECTION_TITLE,
                  order: index + 1,
                  valueType: field.value_type,
                  displayValue: getReviewFieldDisplayValue(field),
                  source: "extracted",
                  evidence: field.evidence,
                  repeatable: true,
                },
                field,
                false,
              ),
          );
        return {
          id: `extra:${key}`,
          key,
          label,
          section: OTHER_EXTRACTED_FIELDS_SECTION_TITLE,
          order: index + 1,
          isCritical: false,
          valueType: fields[0]?.value_type ?? "string",
          repeatable: true,
          items,
          isEmptyList: items.length === 0,
          source: "extracted",
        };
      }
      const field = fields[0];
      const hasValue = Boolean(field && !isFieldValueEmpty(field.value));
      const displayValue = hasValue ? getReviewFieldDisplayValue(field) : MISSING_VALUE_PLACEHOLDER;
      const item: ReviewSelectableField = buildSelectableField(
        {
          id: field ? `extra:${field.field_id}:0` : `extra:${key}:missing`,
          key,
          label,
          section: OTHER_EXTRACTED_FIELDS_SECTION_TITLE,
          order: index + 1,
          valueType: field?.value_type ?? "string",
          displayValue,
          source: "extracted",
          evidence: field?.evidence,
          repeatable: false,
        },
        field,
        !hasValue,
      );
      return {
        id: `extra:${key}`,
        key,
        label,
        section: OTHER_EXTRACTED_FIELDS_SECTION_TITLE,
        order: index + 1,
        isCritical: false,
        valueType: field?.value_type ?? "string",
        repeatable: false,
        items: [item],
        isEmptyList: false,
        source: "extracted",
      };
    });
  }, [buildSelectableField, explicitOtherReviewFields, isCanonicalContract, validatedReviewFields]);

  return {
    coreDisplayFields,
    otherDisplayFields,
  };
}
