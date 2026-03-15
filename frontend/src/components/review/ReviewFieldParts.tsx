import type { ReactNode } from "react";
import { Pencil } from "lucide-react";

import { IconButton } from "../app/IconButton";
import { ValueSurface } from "../app/Field";
import { EMPTY_LIST_PLACEHOLDER, MISSING_VALUE_PLACEHOLDER } from "../../constants/appWorkspace";
import type { ReviewSelectableField } from "../../types";
import type { ReviewFieldRenderersContext } from "./ReviewFieldRenderers.types";

export function renderConfidenceIndicator(
  item: ReviewSelectableField,
  ariaLabel: string,
): ReactNode {
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
}

export function renderEditableFieldValue(
  ctx: Pick<
    ReviewFieldRenderersContext,
    "isDocumentReviewed" | "isInterpretationEditPending" | "onOpenFieldEditDialog"
  >,
  options: {
    item: ReviewSelectableField;
    value: string;
    isLongText: boolean;
    longTextTestId?: string;
    shortTextTestId?: string;
  },
): ReactNode {
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
}
