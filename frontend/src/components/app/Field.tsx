import type { ReactNode } from "react";

import { cn } from "../../lib/utils";

export function FieldBlock({
  children,
  className,
  ariaLabel,
}: {
  children: ReactNode;
  className?: string;
  ariaLabel?: string;
}) {
  return (
    <article className={cn("px-1 py-1.5", className)} aria-label={ariaLabel}>
      {children}
    </article>
  );
}

type ValueSurfaceVariant = "short" | "long";

export function ValueSurface({
  children,
  variant,
  className,
  testId,
  ariaLabel,
}: {
  children: ReactNode;
  variant: ValueSurfaceVariant;
  className?: string;
  testId?: string;
  ariaLabel?: string;
}) {
  return (
    <div
      data-testid={testId}
      aria-label={ariaLabel}
      className={cn(
        "w-full min-w-0 rounded-md border border-borderSubtle bg-surfaceMuted text-left text-sm break-words",
        variant === "long"
          ? "px-[var(--value-padding-long-x)] py-[var(--value-padding-long-y)] leading-6 whitespace-pre-wrap min-h-[var(--long-text-min-height)] max-h-[var(--long-text-max-height)] overflow-auto"
          : "px-[var(--value-padding-short-x)] py-[var(--value-padding-short-y)]",
        className,
      )}
    >
      {children}
    </div>
  );
}

export function FieldRow({
  indicator,
  label,
  labelMeta,
  value,
  valuePlacement,
  leftTestId,
  labelTestId,
  indicatorTestId,
  valueWrapperTestId,
  className,
  ariaLabel,
}: {
  indicator?: ReactNode;
  label: ReactNode;
  labelMeta?: ReactNode;
  value: ReactNode;
  valuePlacement?: "inline" | "below-label";
  leftTestId?: string;
  labelTestId?: string;
  indicatorTestId?: string;
  valueWrapperTestId?: string;
  className?: string;
  ariaLabel?: string;
}) {
  const resolvedValuePlacement = valuePlacement ?? "inline";

  return (
    <div
      data-testid={leftTestId}
      aria-label={ariaLabel}
      className={cn(
        "grid w-full items-start grid-cols-[var(--field-row-label-col)_minmax(0,1fr)] gap-x-[var(--field-row-gap-x)]",
        className,
      )}
    >
      <div className="min-w-0 self-start">
        <div className="min-w-0 flex items-start justify-between gap-2">
          <div className="min-w-0 flex items-start gap-2">
            {indicator ? (
              <div
                data-testid={indicatorTestId}
                className="mt-[var(--dot-offset)] flex h-4 w-4 shrink-0 items-center justify-center self-start"
              >
                {indicator}
              </div>
            ) : null}
            <div data-testid={labelTestId} className="min-w-0 self-start">
              {label}
            </div>
          </div>
          {labelMeta ? (
            <div className="mt-[1px] inline-flex shrink-0 items-center gap-1.5">{labelMeta}</div>
          ) : null}
        </div>
      </div>
      <div
        data-testid={valueWrapperTestId}
        className={cn(
          "min-w-0 w-full self-start",
          resolvedValuePlacement === "below-label"
            ? "col-span-2 pl-[var(--field-row-label-indent)]"
            : "",
        )}
      >
        {value}
      </div>
    </div>
  );
}

export function RepeatableList({
  children,
  className,
}: {
  children: ReactNode;
  className?: string;
}) {
  return <div className={cn("mt-1 space-y-1", className)}>{children}</div>;
}
