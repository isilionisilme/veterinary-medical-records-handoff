import { cn } from "../../lib/utils";
import { type DocumentStatusClusterModel } from "../../lib/documentStatus";
import { Tooltip } from "../ui/tooltip";
import { Check } from "lucide-react";

type DocumentStatusChipProps = {
  status: DocumentStatusClusterModel;
  compact?: boolean;
  className?: string;
  testId?: string;
};

function toneClass(tone: DocumentStatusClusterModel["tone"]): string {
  if (tone === "success") {
    return "bg-statusSuccess";
  }
  if (tone === "warn") {
    return "bg-statusWarn";
  }
  return "bg-statusError";
}

export function DocumentStatusChip({
  status,
  compact = false,
  className,
  testId,
}: DocumentStatusChipProps) {
  return (
    <Tooltip content={status.tooltip}>
      <span
        data-testid={testId}
        role="status"
        aria-label={`Estado del documento: ${status.label}${status.hint ? `. ${status.hint}` : ""}`}
        className={cn(
          "inline-flex items-center gap-1.5 rounded-control bg-surfaceMuted px-2 py-1 text-[11px] font-semibold text-textSecondary",
          compact && "h-4 min-w-4 justify-center border-0 bg-transparent p-0",
          className,
        )}
      >
        <span
          aria-hidden="true"
          className={cn(
            "inline-flex h-2 w-2 items-center justify-center rounded-full",
            compact && "ring-2 ring-surface",
            toneClass(status.tone),
          )}
        >
          {status.icon === "check" ? <Check size={8} className="text-white" /> : null}
        </span>
        {compact ? <span className="sr-only">{status.label}</span> : <span>{status.label}</span>}
        {!compact && status.hint ? <span className="text-muted">· {status.hint}</span> : null}
      </span>
    </Tooltip>
  );
}

export const DocumentStatusCluster = DocumentStatusChip;
