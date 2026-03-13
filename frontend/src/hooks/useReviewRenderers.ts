import { useMemo } from "react";

import {
  createReviewFieldRenderers,
  type ReviewFieldRenderersContext,
} from "../components/review/ReviewFieldRenderers";
import { createReviewSectionLayoutRenderer } from "../components/review/ReviewSectionLayout";
import type { ReviewField, ReviewSelectableField, ReviewVisitGroup } from "../types/appWorkspace";

type UseReviewRenderersParams = {
  activeConfidencePolicy: ReviewFieldRenderersContext["activeConfidencePolicy"];
  isDocumentReviewed: boolean;
  isInterpretationEditPending: boolean;
  selectedFieldId: string | null;
  expandedFieldValues: Record<string, boolean>;
  hoveredFieldTriggerId: string | null;
  hoveredCriticalTriggerId: string | null;
  hasUnassignedVisitGroup: boolean;
  onOpenFieldEditDialog: (item: ReviewSelectableField) => void;
  onSelectReviewItem: (item: ReviewSelectableField) => void;
  onReviewedEditAttempt: ReviewFieldRenderersContext["onReviewedEditAttempt"];
  onReviewedKeyboardEditAttempt: ReviewFieldRenderersContext["onReviewedKeyboardEditAttempt"];
  onSetExpandedFieldValues: ReviewFieldRenderersContext["onSetExpandedFieldValues"];
  onSetHoveredFieldTriggerId: ReviewFieldRenderersContext["onSetHoveredFieldTriggerId"];
  onSetHoveredCriticalTriggerId: ReviewFieldRenderersContext["onSetHoveredCriticalTriggerId"];
  clinicEnrichment?: ReviewFieldRenderersContext["clinicEnrichment"];
  isCanonicalContract: boolean;
  hasVisitGroups: boolean;
  validatedReviewFields: ReviewField[];
  reviewVisits: ReviewVisitGroup[];
  canonicalVisitFieldOrder: string[];
  buildSelectableField: (
    base: Omit<
      ReviewSelectableField,
      "hasMappingConfidence" | "confidence" | "confidenceBand" | "isMissing" | "rawField"
    >,
    rawField: ReviewField | undefined,
    isMissing: boolean,
  ) => ReviewSelectableField;
};

export function useReviewRenderers({
  activeConfidencePolicy,
  isDocumentReviewed,
  isInterpretationEditPending,
  selectedFieldId,
  expandedFieldValues,
  hoveredFieldTriggerId,
  hoveredCriticalTriggerId,
  hasUnassignedVisitGroup,
  onOpenFieldEditDialog,
  onSelectReviewItem,
  onReviewedEditAttempt,
  onReviewedKeyboardEditAttempt,
  onSetExpandedFieldValues,
  onSetHoveredFieldTriggerId,
  onSetHoveredCriticalTriggerId,
  clinicEnrichment,
  isCanonicalContract,
  hasVisitGroups,
  validatedReviewFields,
  reviewVisits,
  canonicalVisitFieldOrder,
  buildSelectableField,
}: UseReviewRenderersParams) {
  const { renderScalarReviewField, renderRepeatableReviewField } = useMemo(
    () =>
      createReviewFieldRenderers({
        activeConfidencePolicy,
        isDocumentReviewed,
        isInterpretationEditPending,
        selectedFieldId,
        expandedFieldValues,
        hoveredFieldTriggerId,
        hoveredCriticalTriggerId,
        hasUnassignedVisitGroup,
        onOpenFieldEditDialog,
        onSelectReviewItem,
        onReviewedEditAttempt,
        onReviewedKeyboardEditAttempt,
        onSetExpandedFieldValues,
        onSetHoveredFieldTriggerId,
        onSetHoveredCriticalTriggerId,
        clinicEnrichment,
      }),
    [
      activeConfidencePolicy,
      isDocumentReviewed,
      isInterpretationEditPending,
      selectedFieldId,
      expandedFieldValues,
      hoveredFieldTriggerId,
      hoveredCriticalTriggerId,
      hasUnassignedVisitGroup,
      onOpenFieldEditDialog,
      onSelectReviewItem,
      onReviewedEditAttempt,
      onReviewedKeyboardEditAttempt,
      onSetExpandedFieldValues,
      onSetHoveredFieldTriggerId,
      onSetHoveredCriticalTriggerId,
      clinicEnrichment,
    ],
  );

  const renderSectionLayout = useMemo(
    () =>
      createReviewSectionLayoutRenderer({
        isCanonicalContract,
        hasVisitGroups,
        validatedReviewFields,
        reviewVisits,
        canonicalVisitFieldOrder,
        buildSelectableField,
        renderScalarReviewField,
        renderRepeatableReviewField,
      }),
    [
      isCanonicalContract,
      hasVisitGroups,
      validatedReviewFields,
      reviewVisits,
      canonicalVisitFieldOrder,
      buildSelectableField,
      renderScalarReviewField,
      renderRepeatableReviewField,
    ],
  );

  return {
    renderScalarReviewField,
    renderRepeatableReviewField,
    renderSectionLayout,
  };
}
