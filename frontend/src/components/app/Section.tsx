import type { ReactNode } from "react";

import { cn } from "../../lib/utils";

export function SectionBlock({
  children,
  className,
  testId,
  headingId,
  ariaLabel,
}: {
  children: ReactNode;
  className?: string;
  testId?: string;
  headingId?: string;
  ariaLabel?: string;
}) {
  return (
    <section
      data-testid={testId}
      role="region"
      aria-labelledby={headingId}
      aria-label={ariaLabel}
      className={cn("panel-shell px-4 py-4", className)}
    >
      {children}
    </section>
  );
}

export function Section({
  children,
  className,
  headingId,
  ariaLabel,
}: {
  children: ReactNode;
  className?: string;
  headingId?: string;
  ariaLabel?: string;
}) {
  return (
    <SectionBlock className={className} headingId={headingId} ariaLabel={ariaLabel}>
      {children}
    </SectionBlock>
  );
}

export function SectionHeader({
  title,
  rightSlot,
  headingId,
}: {
  title: string;
  rightSlot?: ReactNode;
  headingId?: string;
}) {
  return (
    <div className="flex items-center justify-between gap-2 pb-2">
      <h2 id={headingId} className="text-base font-semibold text-text">
        {title}
      </h2>
      {rightSlot ? <div className="shrink-0">{rightSlot}</div> : null}
    </div>
  );
}
