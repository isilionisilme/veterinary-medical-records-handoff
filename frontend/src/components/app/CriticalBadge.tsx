import type { MouseEvent as ReactMouseEvent } from "react";

import { Tooltip } from "../ui/tooltip";

type CriticalIconProps = {
  testId?: string;
  compact?: boolean;
};

export function CriticalIcon({ testId, compact = false }: CriticalIconProps) {
  return (
    <span
      data-testid={testId}
      role="img"
      aria-label="Campo crítico"
      className={`inline-flex items-center justify-center rounded-full border border-critical/50 font-semibold leading-none text-critical ${
        compact ? "h-3.5 min-w-3.5 px-0 text-[9px]" : "h-4 min-w-4 px-1 text-[10px]"
      }`}
    >
      !
    </span>
  );
}

type CriticalBadgeProps = {
  testId?: string;
  tooltipOpen?: boolean;
  onMouseEnter?: (event: ReactMouseEvent<HTMLSpanElement>) => void;
  onMouseLeave?: (event: ReactMouseEvent<HTMLSpanElement>) => void;
};

export function CriticalBadge({
  testId,
  tooltipOpen,
  onMouseEnter,
  onMouseLeave,
}: CriticalBadgeProps) {
  return (
    <Tooltip content="CRÍTICO" open={tooltipOpen}>
      <span aria-label="Campo crítico" onMouseEnter={onMouseEnter} onMouseLeave={onMouseLeave}>
        <CriticalIcon testId={testId} />
      </span>
    </Tooltip>
  );
}
