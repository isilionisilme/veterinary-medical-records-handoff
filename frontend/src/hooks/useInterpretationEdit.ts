import { type Dispatch, type SetStateAction, useCallback } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";

import { editRunInterpretation } from "../api/documentApi";
import { type ActionFeedback } from "../components/toast/toast-types";
import { getTechnicalDetails, getUserErrorMessage } from "../lib/appWorkspaceUtils";
import {
  type DocumentReviewResponse,
  type InterpretationChangePayload,
} from "../types/appWorkspace";

type UseInterpretationEditParams = {
  activeId: string | null;
  reviewPayload: DocumentReviewResponse | undefined;
  onActionFeedback: Dispatch<SetStateAction<ActionFeedback | null>>;
};

export function useInterpretationEdit({
  activeId,
  reviewPayload,
  onActionFeedback,
}: UseInterpretationEditParams) {
  const queryClient = useQueryClient();

  const interpretationEditMutation = useMutation({
    mutationFn: async (variables: {
      docId: string;
      runId: string;
      baseVersionNumber: number;
      changes: InterpretationChangePayload[];
      successMessage: string;
    }) =>
      editRunInterpretation(variables.runId, {
        base_version_number: variables.baseVersionNumber,
        changes: variables.changes,
      }),
    onSuccess: (result, variables) => {
      queryClient.setQueryData<DocumentReviewResponse | undefined>(
        ["documents", "review", variables.docId],
        (current) => {
          if (!current) {
            return current;
          }
          return {
            ...current,
            active_interpretation: {
              interpretation_id: result.interpretation_id,
              version_number: result.version_number,
              data: result.data,
            },
          };
        },
      );
      onActionFeedback({
        kind: "success",
        message: variables.successMessage,
      });
      queryClient.invalidateQueries({ queryKey: ["documents", "review", variables.docId] });
    },
    onError: (error) => {
      onActionFeedback({
        kind: "error",
        message: getUserErrorMessage(error, "No se pudo guardar la edición."),
        technicalDetails: getTechnicalDetails(error),
      });
    },
  });

  const submitInterpretationChanges = useCallback(
    (changes: InterpretationChangePayload[], successMessage: string) => {
      if (!activeId || !reviewPayload) {
        return;
      }
      interpretationEditMutation.mutate({
        docId: activeId,
        runId: reviewPayload.latest_completed_run.run_id,
        baseVersionNumber: reviewPayload.active_interpretation.version_number,
        changes,
        successMessage,
      });
    },
    [activeId, interpretationEditMutation, reviewPayload],
  );

  return { interpretationEditMutation, submitInterpretationChanges };
}
