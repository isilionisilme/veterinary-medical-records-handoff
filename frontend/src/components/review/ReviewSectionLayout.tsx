import type { ReactNode } from "react";
import { ChevronDown, Info } from "lucide-react";

import { SectionBlock, SectionHeader } from "../app/Section";
import { Badge } from "../ui/badge";
import { Card, CardContent, CardHeader } from "../ui/card";
import { Separator } from "../ui/separator";
import {
  BILLING_REVIEW_FIELDS,
  CANONICAL_VISIT_METADATA_KEYS,
  FIELD_LABELS,
  MISSING_VALUE_PLACEHOLDER,
  OTHER_EXTRACTED_FIELDS_EMPTY_STATE,
  STRUCTURED_FIELD_STACK_CLASS,
  VISITS_EMPTY_STATE,
  VISITS_UNASSIGNED_HINT,
} from "../../constants/appWorkspace";
import {
  formatFieldValue,
  formatReviewKeyLabel,
  getNormalizedVisitId,
  getVisitTimestamp,
  isFieldValueEmpty,
} from "../../lib/appWorkspaceUtils";
import type {
  ReviewDisplayField,
  ReviewField,
  ReviewSelectableField,
  ReviewVisitGroup,
} from "../../types/appWorkspace";

type BuildSelectableFieldFn = (
  base: Omit<
    ReviewSelectableField,
    "hasMappingConfidence" | "confidence" | "confidenceBand" | "isMissing" | "rawField"
  >,
  rawField: ReviewField | undefined,
  isMissing: boolean,
) => ReviewSelectableField;

export type ReviewSectionLayoutContext = {
  isCanonicalContract: boolean;
  hasVisitGroups: boolean;
  validatedReviewFields: ReviewField[];
  reviewVisits: ReviewVisitGroup[];
  canonicalVisitFieldOrder: string[];
  buildSelectableField: BuildSelectableFieldFn;
  renderScalarReviewField: (field: ReviewDisplayField) => ReactNode;
  renderRepeatableReviewField: (
    field: ReviewDisplayField,
    options?: { showUnassignedHint?: boolean; hideFieldTitle?: boolean },
  ) => ReactNode;
};

export function createReviewSectionLayoutRenderer(
  ctx: ReviewSectionLayoutContext,
): (section: { id: string; title: string; fields: ReviewDisplayField[] }) => ReactNode {
  const renderCanonicalVisitEpisodes = () => {
    if (!ctx.isCanonicalContract) {
      return null;
    }

    const visitScopedFields = ctx.validatedReviewFields.filter(
      (field) => field.scope === "visit" && !BILLING_REVIEW_FIELDS.has(field.key),
    );
    const fieldsByVisitId = new Map<string, ReviewField[]>();
    visitScopedFields.forEach((field) => {
      const rawVisitId =
        typeof field.visit_group_id === "string" ? field.visit_group_id.trim() : "";
      if (rawVisitId.length === 0) {
        return;
      }
      const existing = fieldsByVisitId.get(rawVisitId) ?? [];
      existing.push(field);
      fieldsByVisitId.set(rawVisitId, existing);
    });

    const chronologicalVisits = ctx.reviewVisits
      .map((visit, index) => ({
        visit,
        originalIndex: index,
        normalizedVisitId: getNormalizedVisitId(visit, index),
      }))
      .filter((entry) => entry.normalizedVisitId.trim().toLowerCase() !== "unassigned")
      .sort((a, b) => {
        const leftDate = getVisitTimestamp(a.visit.visit_date);
        const rightDate = getVisitTimestamp(b.visit.visit_date);
        if (leftDate !== null && rightDate !== null && leftDate !== rightDate) {
          return leftDate - rightDate;
        }
        if (leftDate === null && rightDate !== null) {
          return 1;
        }
        if (leftDate !== null && rightDate === null) {
          return -1;
        }
        return a.originalIndex - b.originalIndex;
      });

    const visitBlocksAscending = chronologicalVisits.map((entry, chronologicalIndex) => {
      const visitId = entry.normalizedVisitId;
      const metadataFields: ReviewField[] = [
        {
          field_id: `visit-meta-date:${visitId}`,
          key: "visit_date",
          value: entry.visit.visit_date,
          value_type: "date",
          visit_group_id: visitId,
          scope: "visit",
          section: "visits",
          classification: "medical_record",
          domain: "clinical",
          is_critical: true,
          origin: "machine",
        },
        {
          field_id: `visit-meta-admission:${visitId}`,
          key: "admission_date",
          value: entry.visit.admission_date ?? null,
          value_type: "date",
          visit_group_id: visitId,
          scope: "visit",
          section: "visits",
          classification: "medical_record",
          domain: "clinical",
          is_critical: false,
          origin: "machine",
        },
        {
          field_id: `visit-meta-discharge:${visitId}`,
          key: "discharge_date",
          value: entry.visit.discharge_date ?? null,
          value_type: "date",
          visit_group_id: visitId,
          scope: "visit",
          section: "visits",
          classification: "medical_record",
          domain: "clinical",
          is_critical: false,
          origin: "machine",
        },
        {
          field_id: `visit-meta-reason:${visitId}`,
          key: "reason_for_visit",
          value: entry.visit.reason_for_visit ?? null,
          value_type: "string",
          visit_group_id: visitId,
          scope: "visit",
          section: "visits",
          classification: "medical_record",
          domain: "clinical",
          is_critical: false,
          origin: "machine",
        },
      ];

      const scopedVisitFields = (fieldsByVisitId.get(visitId) ?? []).filter(
        (field) =>
          !CANONICAL_VISIT_METADATA_KEYS.includes(
            field.key as (typeof CANONICAL_VISIT_METADATA_KEYS)[number],
          ),
      );

      const fieldsByKey = new Map<string, ReviewField[]>();
      [...metadataFields, ...scopedVisitFields].forEach((field) => {
        const existing = fieldsByKey.get(field.key) ?? [];
        existing.push(field);
        fieldsByKey.set(field.key, existing);
      });

      const extraKeys = Array.from(fieldsByKey.keys()).filter(
        (key) => !ctx.canonicalVisitFieldOrder.includes(key),
      );
      const orderedKeys = [...ctx.canonicalVisitFieldOrder, ...extraKeys];

      return {
        id: visitId,
        visitNumber: chronologicalIndex + 1,
        visitDate: entry.visit.visit_date,
        reasonForVisit: entry.visit.reason_for_visit,
        orderedKeys,
        fieldsByKey,
      };
    });

    const assignedVisitIdSet = new Set(
      chronologicalVisits.map((entry) => entry.normalizedVisitId.trim().toLowerCase()),
    );
    const unassignedFields = visitScopedFields.filter((field) => {
      const visitGroupId =
        typeof field.visit_group_id === "string" ? field.visit_group_id.trim() : "";
      if (!visitGroupId) {
        return true;
      }
      const normalized = visitGroupId.toLowerCase();
      if (normalized === "unassigned") {
        return true;
      }
      return !assignedVisitIdSet.has(normalized);
    });

    const unassignedByKey = new Map<string, ReviewField[]>();
    unassignedFields.forEach((field) => {
      const existing = unassignedByKey.get(field.key) ?? [];
      existing.push(field);
      unassignedByKey.set(field.key, existing);
    });
    const unassignedExtraKeys = Array.from(unassignedByKey.keys()).filter(
      (key) => !ctx.canonicalVisitFieldOrder.includes(key),
    );
    const orderedUnassignedKeys = [
      ...ctx.canonicalVisitFieldOrder.filter((key) => unassignedByKey.has(key)),
      ...unassignedExtraKeys,
    ];

    const buildDisplayField = (
      visitId: string,
      key: string,
      fields: ReviewField[],
      order: number,
    ): ReviewDisplayField => {
      const label = FIELD_LABELS[key] ?? formatReviewKeyLabel(key);
      const valueType = fields[0]?.value_type ?? (key.includes("date") ? "date" : "string");
      const isMetadataField = CANONICAL_VISIT_METADATA_KEYS.includes(
        key as (typeof CANONICAL_VISIT_METADATA_KEYS)[number],
      );

      if (!isMetadataField) {
        const presentFields = fields.filter((field) => !isFieldValueEmpty(field.value));
        const items = presentFields.map((field, itemIndex) =>
          ctx.buildSelectableField(
            {
              id: `visit:${visitId}:${key}:${itemIndex}`,
              key,
              label,
              section: "Visitas",
              order,
              valueType: field.value_type,
              displayValue: formatFieldValue(field.value, field.value_type),
              source: "core",
              evidence: field.evidence,
              repeatable: true,
            },
            field,
            false,
          ),
        );

        return {
          id: `visit-field:${visitId}:${key}`,
          key,
          label,
          section: "Visitas",
          order,
          isCritical: fields.some((field) => Boolean(field.is_critical)),
          valueType,
          repeatable: true,
          items,
          isEmptyList: items.length === 0,
          source: "core",
        };
      }

      const scalarField = fields[0];
      const hasValue = Boolean(scalarField && !isFieldValueEmpty(scalarField.value));
      const scalarItem = ctx.buildSelectableField(
        {
          id: scalarField ? `visit:${visitId}:${key}:0` : `visit:${visitId}:${key}:missing`,
          key,
          label,
          section: "Visitas",
          order,
          valueType,
          displayValue:
            scalarField && hasValue
              ? formatFieldValue(scalarField.value, scalarField.value_type)
              : MISSING_VALUE_PLACEHOLDER,
          source: "core",
          evidence: scalarField?.evidence,
          repeatable: false,
        },
        scalarField,
        !hasValue,
      );

      return {
        id: `visit-field:${visitId}:${key}`,
        key,
        label,
        section: "Visitas",
        order,
        isCritical: Boolean(scalarField?.is_critical),
        valueType,
        repeatable: false,
        items: [scalarItem],
        isEmptyList: false,
        source: "core",
      };
    };

    return (
      <div className={STRUCTURED_FIELD_STACK_CLASS}>
        {[...visitBlocksAscending].reverse().map((visitBlock) => {
          const visitFields = visitBlock.orderedKeys.map((key, fieldIndex) => {
            const fields = visitBlock.fieldsByKey.get(key) ?? [];
            return buildDisplayField(visitBlock.id, key, fields, fieldIndex + 1);
          });

          const summaryKeys = new Set(["observations", "actions"]);
          const visitDateField = visitFields.find((field) => field.key === "visit_date");
          const summaryFields = ["observations", "actions"]
            .map((summaryKey) => visitFields.find((field) => field.key === summaryKey))
            .filter((field): field is ReviewDisplayField => Boolean(field));
          const remainingFields = visitFields.filter(
            (field) => field.key !== "visit_date" && !summaryKeys.has(field.key),
          );
          const scalarClinicalFields = remainingFields.filter((field) => !field.repeatable);
          const repeatableClinicalFields = remainingFields.filter((field) => field.repeatable);
          const hasVisitDate = !isFieldValueEmpty(visitBlock.visitDate ?? null);
          const hasReasonForVisit = !isFieldValueEmpty(visitBlock.reasonForVisit ?? null);
          const visitDateLabel = hasVisitDate
            ? formatFieldValue(visitBlock.visitDate ?? null, "date")
            : "Sin fecha";

          return (
            <Card
              key={visitBlock.id}
              className="bg-surfaceMuted animate-fadein"
              data-testid={`visit-episode-${visitBlock.visitNumber}`}
            >
              <details className="group">
                <summary className="list-none cursor-pointer [&::-webkit-details-marker]:hidden">
                  <CardHeader className="space-y-2">
                    <div className="flex items-start justify-between gap-3">
                      <div className="min-w-0 space-y-1">
                        <div className="flex flex-wrap items-center gap-2">
                          <span className="text-base font-semibold text-textTitle">
                            Visita {visitBlock.visitNumber}
                          </span>
                          <span className="text-sm text-textSecondary">{visitDateLabel}</span>
                        </div>
                        <div className="flex flex-wrap gap-1.5">
                          <Badge variant={hasVisitDate ? "secondary" : "outline"}>
                            {hasVisitDate ? "Con fecha" : "Sin fecha"}
                          </Badge>
                          <Badge variant={hasReasonForVisit ? "secondary" : "outline"}>
                            {hasReasonForVisit ? "Con motivo" : "Sin motivo"}
                          </Badge>
                        </div>
                      </div>
                      <div className="mt-0.5 inline-flex items-center gap-1 text-xs text-textSecondary">
                        <span>Detalles</span>
                        <ChevronDown
                          className="h-4 w-4 transition-transform group-open:rotate-180"
                          aria-hidden="true"
                        />
                      </div>
                    </div>
                  </CardHeader>
                </summary>

                <Separator />

                <CardContent className="pt-3">
                  {visitDateField && (
                    <div data-testid={`visit-date-section-${visitBlock.visitNumber}`}>
                      {ctx.renderScalarReviewField(visitDateField)}
                    </div>
                  )}

                  <Separator className="my-2" />

                  <div
                    className="space-y-1"
                    data-testid={`visit-summary-section-${visitBlock.visitNumber}`}
                  >
                    <span className="text-sm font-semibold text-textSecondary">Resumen</span>
                    <div className="space-y-2">
                      {summaryFields.map((field) =>
                        field.repeatable
                          ? ctx.renderRepeatableReviewField(field, { hideFieldTitle: true })
                          : ctx.renderScalarReviewField(field),
                      )}
                    </div>
                  </div>

                  <Separator className="my-2" />

                  {(scalarClinicalFields.length > 0 || repeatableClinicalFields.length > 0) && (
                    <>
                      {scalarClinicalFields.length > 0 && (
                        <div className="space-y-1">
                          <span className="text-sm font-semibold text-textSecondary">
                            Campos clínicos
                          </span>
                          <div className="grid grid-cols-1 gap-x-6 gap-y-2 md:grid-cols-2">
                            {scalarClinicalFields.map((field) =>
                              ctx.renderScalarReviewField(field),
                            )}
                          </div>
                        </div>
                      )}

                      {repeatableClinicalFields.length > 0 && (
                        <div className="space-y-1">
                          <span className="text-sm font-semibold text-textSecondary">
                            Listas clínicas
                          </span>
                          <div className="space-y-2">
                            {repeatableClinicalFields.map((field) =>
                              ctx.renderRepeatableReviewField(field),
                            )}
                          </div>
                        </div>
                      )}
                    </>
                  )}
                </CardContent>
              </details>
            </Card>
          );
        })}
        {orderedUnassignedKeys.length > 0 && (
          <div
            className="rounded-card border-2 border-dashed border-accent/40 bg-surface px-4 py-4 shadow-subtle animate-fadein"
            data-testid="visit-unassigned-group"
          >
            <div className="flex items-center gap-2 mb-2">
              <Info className="h-5 w-5 text-accent" aria-hidden="true" />
              <span className="text-base font-bold text-accent">No asociadas a visita</span>
            </div>
            <p
              className="rounded-control bg-surfaceMuted px-3 py-2 text-xs text-accent"
              data-testid="visits-unassigned-hint"
            >
              {VISITS_UNASSIGNED_HINT}
            </p>
            <div className={`mt-2 ${STRUCTURED_FIELD_STACK_CLASS}`}>
              {orderedUnassignedKeys
                .map((key, fieldIndex) => {
                  const fields = unassignedByKey.get(key) ?? [];
                  if (fields.length === 0) {
                    return null;
                  }
                  const displayField = buildDisplayField("unassigned", key, fields, fieldIndex + 1);
                  return displayField.repeatable
                    ? ctx.renderRepeatableReviewField(displayField, { showUnassignedHint: false })
                    : ctx.renderScalarReviewField(displayField);
                })
                .filter((field) => field !== null)}
            </div>
          </div>
        )}
      </div>
    );
  };

  return (section: { id: string; title: string; fields: ReviewDisplayField[] }) => {
    const scalarFields = section.fields.filter((field) => !field.repeatable);
    const repeatableFields = section.fields.filter((field) => field.repeatable);
    const isExtraSection = section.id === "extra:section";
    const isEmptyExtraSection = isExtraSection && section.fields.length === 0;
    const isVisitsSection = section.title === "Visitas";
    const shouldRenderCanonicalVisitsByEpisode = isVisitsSection && ctx.isCanonicalContract;
    const isEmptyVisitsSection =
      isVisitsSection && section.fields.length === 0 && !ctx.hasVisitGroups;
    const isOwnerSection = section.title === "Propietario";
    const shouldUseSingleColumn = isOwnerSection;

    return (
      <SectionBlock
        key={section.id}
        testId={isExtraSection ? "other-extracted-fields-section" : undefined}
      >
        <SectionHeader title={section.title} />
        <div className="mt-2">
          {isEmptyExtraSection && (
            <p className="rounded-control bg-surface px-3 py-2 text-xs text-textSecondary">
              {OTHER_EXTRACTED_FIELDS_EMPTY_STATE}
            </p>
          )}
          {isEmptyVisitsSection && (
            <p className="rounded-control bg-surface px-3 py-2 text-xs text-textSecondary">
              {VISITS_EMPTY_STATE}
            </p>
          )}
          {!isEmptyExtraSection &&
            !isEmptyVisitsSection &&
            !shouldRenderCanonicalVisitsByEpisode && (
              <div
                className={
                  shouldUseSingleColumn
                    ? `grid grid-cols-1 gap-x-5 ${STRUCTURED_FIELD_STACK_CLASS}`
                    : `grid gap-x-5 ${STRUCTURED_FIELD_STACK_CLASS} lg:grid-cols-2`
                }
              >
                {scalarFields.map(ctx.renderScalarReviewField)}
              </div>
            )}
          {!isEmptyExtraSection &&
            !isEmptyVisitsSection &&
            shouldRenderCanonicalVisitsByEpisode && <>{renderCanonicalVisitEpisodes()}</>}
          {repeatableFields.length > 0 && !shouldRenderCanonicalVisitsByEpisode && (
            <div className={`mt-2 ${STRUCTURED_FIELD_STACK_CLASS}`}>
              {repeatableFields.map((field) => ctx.renderRepeatableReviewField(field))}
            </div>
          )}
        </div>
      </SectionBlock>
    );
  };
}
