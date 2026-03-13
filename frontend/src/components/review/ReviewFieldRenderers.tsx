import type {
  KeyboardEvent as ReactKeyboardEvent,
  MouseEvent as ReactMouseEvent,
  ReactNode,
} from "react";
import { Pencil } from "lucide-react";

import { ClinicAddressEnrichmentPrompt } from "./ClinicAddressEnrichmentPrompt";
import { CriticalBadge } from "../app/CriticalBadge";
import { FieldBlock, FieldRow, RepeatableList, ValueSurface } from "../app/Field";
import { IconButton } from "../app/IconButton";
import { Tooltip } from "../ui/tooltip";
import {
  EMPTY_LIST_PLACEHOLDER,
  MISSING_VALUE_PLACEHOLDER,
  STRUCTURED_FIELD_LABEL_CLASS,
  STRUCTURED_FIELD_ROW_CLASS,
  VISITS_UNASSIGNED_HINT,
} from "../../constants/appWorkspace";
import {
  clampConfidence,
  formatSignedPercent,
  getConfidenceTone,
  getStructuredFieldPrefix,
  shouldRenderLongTextValue,
  truncateText,
} from "../../lib/appWorkspaceUtils";
import type {
  ConfidencePolicyConfig,
  ReviewDisplayField,
  ReviewSelectableField,
} from "../../types/appWorkspace";

export type ReviewFieldRenderersContext = {
  activeConfidencePolicy: ConfidencePolicyConfig | null;
  isDocumentReviewed: boolean;
  isInterpretationEditPending: boolean;
  selectedFieldId: string | null;
  expandedFieldValues: Record<string, boolean>;
  hoveredFieldTriggerId: string | null;
  hoveredCriticalTriggerId: string | null;
  hasUnassignedVisitGroup: boolean;
  onOpenFieldEditDialog: (item: ReviewSelectableField) => void;
  onSelectReviewItem: (item: ReviewSelectableField) => void;
  onReviewedEditAttempt: (event: ReactMouseEvent<HTMLElement>) => void;
  onReviewedKeyboardEditAttempt: (event: ReactKeyboardEvent<HTMLElement>) => void;
  onSetExpandedFieldValues: (
    updater: (current: Record<string, boolean>) => Record<string, boolean>,
  ) => void;
  onSetHoveredFieldTriggerId: (value: string | ((current: string | null) => string | null)) => void;
  onSetHoveredCriticalTriggerId: (
    value: string | ((current: string | null) => string | null),
  ) => void;
  clinicEnrichment?: {
    state: "idle" | "loading" | "found" | "not-found" | "error";
    foundAddress: string | null;
    clinicNameValue: string | null;
    addressFieldItem: ReviewSelectableField | null;
    onSearch: () => void;
    onAccept: () => void;
    onDismiss: () => void;
  };
};

export function createReviewFieldRenderers(ctx: ReviewFieldRenderersContext): {
  renderScalarReviewField: (field: ReviewDisplayField) => ReactNode;
  renderRepeatableReviewField: (
    field: ReviewDisplayField,
    options?: { showUnassignedHint?: boolean; hideFieldTitle?: boolean },
  ) => ReactNode;
} {
  const buildFieldTooltip = (
    item: ReviewSelectableField,
  ): { content: ReactNode; ariaLabel: string } => {
    const manualOverrideConfidenceMessage =
      "La confianza aplica únicamente al valor originalmente detectado por el sistema. El valor actual ha sido editado y por eso no tiene confianza asociada.";
    if (!ctx.activeConfidencePolicy) {
      return {
        content: "Configuración de confianza no disponible.",
        ariaLabel: "Configuración de confianza no disponible.",
      };
    }
    if (item.rawField?.origin === "human") {
      return {
        content: manualOverrideConfidenceMessage,
        ariaLabel: manualOverrideConfidenceMessage,
      };
    }
    if (!item.hasMappingConfidence) {
      return {
        content: "Confianza de mapeo no disponible.",
        ariaLabel: "Confianza de mapeo no disponible.",
      };
    }
    const confidence = item.confidence;
    const percentage = Math.round(clampConfidence(confidence) * 100);
    const tone = getConfidenceTone(confidence, ctx.activeConfidencePolicy.band_cutoffs);
    const candidateConfidence = item.rawField?.field_candidate_confidence;
    const candidateConfidenceText =
      typeof candidateConfidence === "number" && Number.isFinite(candidateConfidence)
        ? `${Math.round(clampConfidence(candidateConfidence) * 100)}%`
        : "No disponible";
    const reviewHistoryAdjustmentRaw = item.rawField?.field_review_history_adjustment;
    const reviewHistoryAdjustment =
      typeof reviewHistoryAdjustmentRaw === "number" && Number.isFinite(reviewHistoryAdjustmentRaw)
        ? reviewHistoryAdjustmentRaw
        : 0;
    const reviewHistoryAdjustmentText = formatSignedPercent(reviewHistoryAdjustment);
    const reviewHistoryAdjustmentClass =
      reviewHistoryAdjustment > 0
        ? "text-[var(--status-success)]"
        : reviewHistoryAdjustment < 0
          ? "text-[var(--status-error)]"
          : "text-muted";
    const header = `Confianza: ${percentage}%`;
    const toneDotClass =
      tone === "high"
        ? "bg-confidenceHigh"
        : tone === "med"
          ? "bg-confidenceMed"
          : "bg-confidenceLow";
    const toneValueClass =
      tone === "high"
        ? "text-confidenceHigh"
        : tone === "med"
          ? "text-confidenceMed"
          : "text-confidenceLow";
    const evidencePageLabel = item.evidence?.page ? `Página ${item.evidence.page}` : null;
    const ariaLabelParts = [
      header,
      evidencePageLabel,
      "Indica la fiabilidad del valor detectado automáticamente.",
      "Desglose:",
      `Fiabilidad del candidato: ${candidateConfidenceText}`,
      `Ajuste por histórico de revisiones: ${reviewHistoryAdjustmentText}`,
    ].filter((part): part is string => Boolean(part));
    return {
      ariaLabel: ariaLabelParts.join(" · "),
      content: (
        <div className="min-w-[260px] space-y-1 text-[12px] leading-4">
          <div className="flex items-start justify-between gap-3">
            <p className="flex items-center gap-1.5 text-[14px] font-semibold leading-5 text-white">
              <span>Confianza:</span>
              <span className={toneValueClass}>{percentage}%</span>
              <span
                className={`inline-block h-2 w-2 rounded-full ring-1 ring-white/40 ${toneDotClass}`}
                aria-hidden="true"
              />
            </p>
            {evidencePageLabel ? (
              <span className="text-[11px] font-normal text-white/70">{evidencePageLabel}</span>
            ) : null}
          </div>
          <p className="text-[11px] leading-4 text-white/60">
            Indica la fiabilidad del valor detectado automáticamente.
          </p>
          <div className="!mt-4 space-y-0.5 text-[12px]">
            <p className="font-medium text-white/80">Desglose:</p>
            <p className="pl-3 text-white/70">
              - Fiabilidad del candidato:{" "}
              <span className={toneValueClass}>{candidateConfidenceText}</span>
            </p>
            <p className="pl-3 text-white/70">
              - Ajuste por histórico de revisiones:{" "}
              <span className={reviewHistoryAdjustmentClass}>{reviewHistoryAdjustmentText}</span>
            </p>
          </div>
        </div>
      ),
    };
  };

  const renderConfidenceIndicator = (item: ReviewSelectableField, ariaLabel: string) => {
    const tone = item.confidenceBand === "medium" ? "med" : item.confidenceBand;
    const isEmptyValueIndicator =
      item.isMissing ||
      item.displayValue === MISSING_VALUE_PLACEHOLDER ||
      (item.repeatable && item.displayValue === EMPTY_LIST_PLACEHOLDER);
    return (
      <span data-testid={`badge-group-${item.id}`} className="inline-flex shrink-0 items-center">
        {isEmptyValueIndicator ? (
          <span
            data-testid={`confidence-indicator-${item.id}`}
            aria-label="Campo vacío"
            className="inline-block h-2.5 w-2.5 rounded-full border border-muted bg-surface"
          />
        ) : tone ? (
          <span
            data-testid={`confidence-indicator-${item.id}`}
            aria-label={ariaLabel}
            className={`inline-block h-2.5 w-2.5 rounded-full ${
              tone === "high"
                ? "bg-confidenceHigh"
                : tone === "med"
                  ? "bg-confidenceMed"
                  : "bg-confidenceLow"
            }`}
          />
        ) : (
          <span
            data-testid={`confidence-indicator-${item.id}`}
            aria-label={ariaLabel}
            className="inline-block h-2.5 w-2.5 rounded-full bg-missing"
          />
        )}
      </span>
    );
  };

  const renderEditableFieldValue = (options: {
    item: ReviewSelectableField;
    value: string;
    isLongText: boolean;
    longTextTestId?: string;
    shortTextTestId?: string;
  }) => {
    const { item, value, isLongText, longTextTestId, shortTextTestId } = options;
    const isFieldModified = item.rawField?.origin === "human";
    const isDerivedField = item.rawField?.origin === "derived";
    const modifiedValueClass = isFieldModified
      ? "!bg-amber-50 ring-1 ring-amber-300/70"
      : isDerivedField
        ? "!bg-blue-50 ring-1 ring-blue-300/70"
        : "";

    return (
      <div className="relative rounded-control">
        {isLongText ? (
          <ValueSurface
            variant="long"
            testId={longTextTestId}
            className={
              item.isMissing
                ? `italic ${ctx.isDocumentReviewed ? `text-missing ${modifiedValueClass}` : `text-missing pr-9 ${modifiedValueClass}`}`
                : ctx.isDocumentReviewed
                  ? `text-text ${modifiedValueClass}`
                  : `text-text pr-9 ${modifiedValueClass}`
            }
          >
            {value}
          </ValueSurface>
        ) : (
          <ValueSurface
            testId={shortTextTestId}
            variant="short"
            className={
              item.isMissing
                ? ctx.isDocumentReviewed
                  ? `relative italic text-missing ${modifiedValueClass}`
                  : `relative pr-9 italic text-missing ${modifiedValueClass}`
                : ctx.isDocumentReviewed
                  ? `relative text-text ${modifiedValueClass}`
                  : `relative pr-9 text-text ${modifiedValueClass}`
            }
          >
            {value}
          </ValueSurface>
        )}
        {!ctx.isDocumentReviewed && (
          <IconButton
            data-testid={`field-edit-btn-${item.id}`}
            label="Editar"
            tooltip="Editar"
            type="button"
            className="absolute right-2 top-1/2 h-7 w-7 -translate-y-1/2 rounded-md border border-transparent bg-transparent p-0 text-text opacity-55 hover:border-borderSubtle hover:bg-surface hover:opacity-100 focus-visible:border-borderSubtle focus-visible:opacity-100"
            disabled={ctx.isInterpretationEditPending}
            onClick={(event) => {
              event.preventDefault();
              event.stopPropagation();
              ctx.onOpenFieldEditDialog(item);
            }}
          >
            <Pencil className="h-4 w-4" aria-hidden="true" />
          </IconButton>
        )}
      </div>
    );
  };

  const renderRepeatableReviewField = (
    field: ReviewDisplayField,
    options?: { showUnassignedHint?: boolean; hideFieldTitle?: boolean },
  ) => {
    const countLabel = field.items.length === 1 ? "1 elemento" : `${field.items.length} elementos`;
    const shouldShowUnassignedVisitHintForField =
      options?.showUnassignedHint ?? ctx.hasUnassignedVisitGroup;
    const shouldHideFieldTitle = options?.hideFieldTitle ?? false;
    const firstUnassignedItemIndex = field.items.findIndex(
      (item) => item.visitGroupId?.trim().toLowerCase() === "unassigned",
    );
    return (
      <FieldBlock key={field.id} className="px-1 py-1">
        {!shouldHideFieldTitle && (
          <div className="flex items-center justify-between gap-2 pb-1">
            <div className="flex items-center gap-1.5">
              <p className="text-xs font-semibold text-text">{field.label}</p>
              {field.isCritical && <CriticalBadge testId={`critical-indicator-${field.key}`} />}
            </div>
            {field.items.length > 0 && (
              <span className="rounded-full bg-surfaceMuted px-2 py-0.5 text-[10px] font-semibold text-textSecondary">
                {countLabel}
              </span>
            )}
          </div>
        )}
        <RepeatableList>
          {field.isEmptyList && (
            <p className="py-0.5 text-sm italic text-missing">{EMPTY_LIST_PLACEHOLDER}</p>
          )}
          {field.items.map((item, index) => {
            const isSelected = ctx.selectedFieldId === item.id;
            const isLongText = shouldRenderLongTextValue(field.key, item.displayValue);
            const tooltip = buildFieldTooltip(item);
            const isUnassignedVisitGroup =
              shouldShowUnassignedVisitHintForField &&
              item.visitGroupId?.trim().toLowerCase() === "unassigned";
            const shouldRenderUnassignedHint =
              isUnassignedVisitGroup && index === firstUnassignedItemIndex;
            return (
              <div
                key={item.id}
                className={`px-1 py-1 ${isSelected ? "rounded-md bg-accentSoft/50" : ""}`}
              >
                {shouldRenderUnassignedHint && (
                  <p
                    className="mb-1 rounded-control bg-surface px-3 py-2 text-xs text-muted"
                    data-testid="visits-unassigned-hint"
                  >
                    {VISITS_UNASSIGNED_HINT}
                  </p>
                )}
                <Tooltip
                  content={tooltip.content}
                  open={
                    ctx.hoveredFieldTriggerId === item.id &&
                    ctx.hoveredCriticalTriggerId !== item.id
                  }
                >
                  <div
                    role="button"
                    tabIndex={0}
                    data-testid={`field-trigger-${item.id}`}
                    aria-disabled={ctx.isDocumentReviewed}
                    className={`w-full rounded-md border border-transparent px-1 py-0.5 text-left transition focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent ${
                      ctx.isDocumentReviewed
                        ? "cursor-default"
                        : "cursor-pointer hover:border-borderSubtle hover:bg-surface"
                    }`}
                    onClick={() => {
                      if (ctx.isDocumentReviewed) {
                        return;
                      }
                      ctx.onSelectReviewItem(item);
                    }}
                    onMouseEnter={() => {
                      ctx.onSetHoveredFieldTriggerId(item.id);
                    }}
                    onMouseLeave={() => {
                      ctx.onSetHoveredFieldTriggerId((current) =>
                        current === item.id ? null : current,
                      );
                      ctx.onSetHoveredCriticalTriggerId((current) =>
                        current === item.id ? null : current,
                      );
                    }}
                    onMouseUp={ctx.onReviewedEditAttempt}
                    onFocus={() => {
                      ctx.onSetHoveredFieldTriggerId(item.id);
                    }}
                    onBlur={(event) => {
                      if (event.currentTarget.contains(event.relatedTarget as Node | null)) {
                        return;
                      }
                      ctx.onSetHoveredFieldTriggerId((current) =>
                        current === item.id ? null : current,
                      );
                      ctx.onSetHoveredCriticalTriggerId((current) =>
                        current === item.id ? null : current,
                      );
                    }}
                    onKeyDown={(event) => {
                      ctx.onReviewedKeyboardEditAttempt(event);
                      if (ctx.isDocumentReviewed) {
                        return;
                      }
                      if (event.key === "Enter" || event.key === " ") {
                        event.preventDefault();
                        ctx.onSelectReviewItem(item);
                      }
                    }}
                  >
                    <FieldRow
                      indicator={renderConfidenceIndicator(item, tooltip.ariaLabel)}
                      label={
                        <p
                          className={`${STRUCTURED_FIELD_LABEL_CLASS} text-text`}
                          title={field.labelTooltip}
                        >
                          {field.label}
                        </p>
                      }
                      labelMeta={null}
                      className={STRUCTURED_FIELD_ROW_CLASS}
                      valuePlacement={isLongText ? "below-label" : "inline"}
                      value={renderEditableFieldValue({
                        item,
                        value: item.displayValue,
                        isLongText,
                      })}
                    />
                  </div>
                </Tooltip>
              </div>
            );
          })}
        </RepeatableList>
      </FieldBlock>
    );
  };

  const renderScalarReviewField = (field: ReviewDisplayField) => {
    const item = field.items[0];
    if (!item) {
      return null;
    }
    const isSelected = ctx.selectedFieldId === item.id;
    const isExpanded = Boolean(ctx.expandedFieldValues[item.id]);
    const shouldUseLongText = shouldRenderLongTextValue(field.key, item.displayValue);
    const tooltip = buildFieldTooltip(item);
    const shouldSpanFullSectionWidth = shouldUseLongText;
    const valueText = shouldUseLongText
      ? item.displayValue
      : isExpanded
        ? item.displayValue
        : truncateText(item.displayValue, 140);
    const canExpand = !shouldUseLongText && item.displayValue.length > 140;
    const styledPrefix = getStructuredFieldPrefix(field.key);
    const isFieldHovered = ctx.hoveredFieldTriggerId === item.id;
    const isCriticalHovered = ctx.hoveredCriticalTriggerId === item.id;

    return (
      <FieldBlock
        key={field.id}
        className={`px-1 py-1.5 ${shouldSpanFullSectionWidth ? "lg:col-span-2" : ""} ${
          isSelected ? "bg-accentSoft/50" : ""
        }`}
      >
        <Tooltip content={tooltip.content} open={isFieldHovered && !isCriticalHovered}>
          <div
            role="button"
            tabIndex={0}
            data-testid={`field-trigger-${item.id}`}
            aria-disabled={ctx.isDocumentReviewed}
            className={`w-full rounded-md border border-transparent px-1 py-0.5 text-left transition focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent ${
              ctx.isDocumentReviewed
                ? "cursor-default"
                : "cursor-pointer hover:border-borderSubtle hover:bg-surface"
            }`}
            onClick={() => {
              if (ctx.isDocumentReviewed) {
                return;
              }
              ctx.onSelectReviewItem(item);
            }}
            onMouseEnter={() => {
              ctx.onSetHoveredFieldTriggerId(item.id);
            }}
            onMouseLeave={() => {
              ctx.onSetHoveredFieldTriggerId((current) => (current === item.id ? null : current));
              ctx.onSetHoveredCriticalTriggerId((current) =>
                current === item.id ? null : current,
              );
            }}
            onMouseUp={ctx.onReviewedEditAttempt}
            onFocus={() => {
              ctx.onSetHoveredFieldTriggerId(item.id);
            }}
            onBlur={(event) => {
              if (event.currentTarget.contains(event.relatedTarget as Node | null)) {
                return;
              }
              ctx.onSetHoveredFieldTriggerId((current) => (current === item.id ? null : current));
              ctx.onSetHoveredCriticalTriggerId((current) =>
                current === item.id ? null : current,
              );
            }}
            onKeyDown={(event) => {
              ctx.onReviewedKeyboardEditAttempt(event);
              if (ctx.isDocumentReviewed) {
                return;
              }
              if (event.key === "Enter" || event.key === " ") {
                event.preventDefault();
                ctx.onSelectReviewItem(item);
              }
            }}
          >
            <FieldRow
              leftTestId={`${styledPrefix}-row-${field.key}`}
              labelTestId={`${styledPrefix}-label-${field.key}`}
              indicatorTestId={`${styledPrefix}-dot-${field.key}`}
              valueWrapperTestId={
                shouldUseLongText ? `field-value-${field.key}-wrapper` : undefined
              }
              indicator={renderConfidenceIndicator(item, tooltip.ariaLabel)}
              label={
                <p
                  className={`${STRUCTURED_FIELD_LABEL_CLASS} text-text`}
                  title={field.labelTooltip}
                >
                  {field.label}
                </p>
              }
              labelMeta={
                field.isCritical ? (
                  <CriticalBadge
                    testId={`critical-indicator-${field.key}`}
                    tooltipOpen={isCriticalHovered}
                    onMouseEnter={() => {
                      ctx.onSetHoveredCriticalTriggerId(item.id);
                    }}
                    onMouseLeave={() => {
                      ctx.onSetHoveredCriticalTriggerId((current) =>
                        current === item.id ? null : current,
                      );
                    }}
                  />
                ) : null
              }
              className={STRUCTURED_FIELD_ROW_CLASS}
              valuePlacement={shouldUseLongText ? "below-label" : "inline"}
              value={renderEditableFieldValue({
                item,
                value: valueText,
                isLongText: shouldUseLongText,
                longTextTestId: `field-value-${field.key}`,
                shortTextTestId: `${styledPrefix}-value-${field.key}`,
              })}
            />
          </div>
        </Tooltip>
        {canExpand && (
          <button
            type="button"
            className="mt-1 text-xs font-semibold text-muted underline underline-offset-2"
            onClick={() =>
              ctx.onSetExpandedFieldValues((current) => ({
                ...current,
                [item.id]: !current[item.id],
              }))
            }
          >
            {isExpanded ? "Ver menos" : "Ver más"}
          </button>
        )}
        {field.key === "clinic_address" &&
          item.isMissing &&
          ctx.clinicEnrichment &&
          ctx.clinicEnrichment.clinicNameValue && (
            <ClinicAddressEnrichmentPrompt
              state={ctx.clinicEnrichment.state}
              foundAddress={ctx.clinicEnrichment.foundAddress}
              isDocumentReviewed={ctx.isDocumentReviewed}
              onSearch={ctx.clinicEnrichment.onSearch}
              onAccept={ctx.clinicEnrichment.onAccept}
              onDismiss={ctx.clinicEnrichment.onDismiss}
            />
          )}
      </FieldBlock>
    );
  };

  return {
    renderScalarReviewField,
    renderRepeatableReviewField,
  };
}
