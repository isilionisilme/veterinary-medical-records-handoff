import { type Dispatch, type SetStateAction } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";

import { markDocumentReviewed, reopenDocumentReview } from "../api/documentApi";
import { type ActionFeedback } from "../components/toast/toast-types";
import { getTechnicalDetails, getUserErrorMessage } from "../lib/appWorkspaceUtils";
import {
  type DocumentDetailResponse,
  type DocumentListResponse,
  type DocumentReviewResponse,
} from "../types/appWorkspace";

type UseReviewToggleParams = {
  onActionFeedback: Dispatch<SetStateAction<ActionFeedback | null>>;
};

export function useReviewToggle({ onActionFeedback }: UseReviewToggleParams) {
  const queryClient = useQueryClient();

  const reviewToggleMutation = useMutation({
    mutationFn: async (variables: { docId: string; target: "reviewed" | "in_review" }) => {
      if (variables.target === "reviewed") {
        return markDocumentReviewed(variables.docId);
      }
      return reopenDocumentReview(variables.docId);
    },
    onSuccess: (result, variables) => {
      queryClient.setQueryData<DocumentListResponse | undefined>(
        ["documents", "list"],
        (current) => {
          if (!current) {
            return current;
          }
          return {
            ...current,
            items: current.items.map((item) =>
              item.document_id === variables.docId
                ? {
                    ...item,
                    review_status: result.review_status,
                    reviewed_at: result.reviewed_at,
                    reviewed_by: result.reviewed_by,
                  }
                : item,
            ),
          };
        },
      );
      queryClient.setQueryData<DocumentDetailResponse | undefined>(
        ["documents", "detail", variables.docId],
        (current) => {
          if (!current) {
            return current;
          }
          return {
            ...current,
            review_status: result.review_status,
            reviewed_at: result.reviewed_at,
            reviewed_by: result.reviewed_by,
          };
        },
      );
      queryClient.setQueryData<DocumentReviewResponse | undefined>(
        ["documents", "review", variables.docId],
        (current) => {
          if (!current) {
            return current;
          }
          return {
            ...current,
            review_status: result.review_status,
            reviewed_at: result.reviewed_at,
            reviewed_by: result.reviewed_by,
          };
        },
      );
      onActionFeedback({
        kind: "success",
        message:
          result.review_status === "REVIEWED"
            ? "Documento marcado como revisado."
            : "Documento reabierto para revisión.",
      });
      queryClient.invalidateQueries({ queryKey: ["documents", "list"] });
      queryClient.invalidateQueries({ queryKey: ["documents", "detail", variables.docId] });
      queryClient.invalidateQueries({ queryKey: ["documents", "review", variables.docId] });
    },
    onError: (error) => {
      onActionFeedback({
        kind: "error",
        message: getUserErrorMessage(error, "No se pudo actualizar el estado de revisión."),
        technicalDetails: getTechnicalDetails(error),
      });
    },
  });

  return { reviewToggleMutation };
}
