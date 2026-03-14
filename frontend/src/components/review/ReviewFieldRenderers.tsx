import type { ReactNode } from "react";

import { ClinicAddressEnrichmentPrompt } from "./ClinicAddressEnrichmentPrompt";
import { CriticalBadge } from "../app/CriticalBadge";
import { FieldBlock, FieldRow, RepeatableList } from "../app/Field";
import { Tooltip } from "../ui/tooltip";
import {
  EMPTY_LIST_PLACEHOLDER,
  STRUCTURED_FIELD_LABEL_CLASS,
  STRUCTURED_FIELD_ROW_CLASS,
  VISITS_UNASSIGNED_HINT,
} from "../../constants/appWorkspace";
import {
  getStructuredFieldPrefix,
  shouldRenderLongTextValue,
  truncateText,
} from "../../lib/appWorkspaceUtils";
import type { ReviewDisplayField } from "../../types/appWorkspace";
import { buildFieldTooltip } from "./buildFieldTooltip";
import { renderConfidenceIndicator, renderEditableFieldValue } from "./ReviewFieldParts";
import type { ReviewFieldRenderersContext } from "./ReviewFieldRenderers.types";

export type { ReviewFieldRenderersContext } from "./ReviewFieldRenderers.types";

export function createReviewFieldRenderers(ctx: ReviewFieldRenderersContext): {
  renderScalarReviewField: (field: ReviewDisplayField) => ReactNode;
  renderRepeatableReviewField: (
    field: ReviewDisplayField,
    options?: { showUnassignedHint?: boolean; hideFieldTitle?: boolean },
  ) => ReactNode;
} {
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
            const tooltip = buildFieldTooltip(ctx, item);
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
                      value={renderEditableFieldValue(ctx, {
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
    const tooltip = buildFieldTooltip(ctx, item);
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
              value={renderEditableFieldValue(ctx, {
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
