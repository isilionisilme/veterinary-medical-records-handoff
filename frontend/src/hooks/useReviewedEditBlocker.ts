import {
  type KeyboardEvent as ReactKeyboardEvent,
  type MouseEvent as ReactMouseEvent,
  useCallback,
} from "react";

import { type ActionFeedback } from "../components/toast/toast-types";

type UseReviewedEditBlockerParams = {
  isDocumentReviewed: boolean;
  onActionFeedback: (feedback: ActionFeedback) => void;
};

export function useReviewedEditBlocker({
  isDocumentReviewed,
  onActionFeedback,
}: UseReviewedEditBlockerParams) {
  const handleReviewedEditAttempt = useCallback(
    (event: ReactMouseEvent<HTMLElement>) => {
      if (!isDocumentReviewed || event.button !== 0) return;
      const selectedText = window.getSelection?.()?.toString().trim() ?? "";
      if (selectedText.length > 0) return;
      onActionFeedback({ kind: "error", message: "Documento revisado: edición bloqueada." });
    },
    [isDocumentReviewed, onActionFeedback],
  );

  const handleReviewedKeyboardEditAttempt = useCallback(
    (event: ReactKeyboardEvent<HTMLElement>) => {
      if (!isDocumentReviewed) return;
      if (event.key !== "Enter" && event.key !== " ") return;
      event.preventDefault();
      onActionFeedback({ kind: "error", message: "Documento revisado: edición bloqueada." });
    },
    [isDocumentReviewed, onActionFeedback],
  );

  return { handleReviewedEditAttempt, handleReviewedKeyboardEditAttempt };
}
