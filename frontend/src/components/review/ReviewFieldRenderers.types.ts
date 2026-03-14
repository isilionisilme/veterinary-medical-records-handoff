import type { KeyboardEvent as ReactKeyboardEvent, MouseEvent as ReactMouseEvent } from "react";
import type { ConfidencePolicyConfig, ReviewSelectableField } from "../../types/appWorkspace";

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
