import { useCallback, useState } from "react";

import { lookupClinicAddress, type ClinicAddressLookupResponse } from "../api/documentApi";
import type { ActionFeedback } from "../components/toast/toast-types";
import { getUserErrorMessage } from "../lib/appWorkspaceUtils";
import type { InterpretationChangePayload, ReviewSelectableField } from "../types/appWorkspace";

type ClinicAddressLookupState = "idle" | "loading" | "found" | "not-found" | "error";

type UseClinicAddressLookupParams = {
  onSubmitInterpretationChanges: (
    changes: InterpretationChangePayload[],
    successMessage: string,
  ) => void;
  onActionFeedback: (feedback: ActionFeedback) => void;
};

export function useClinicAddressLookup({
  onSubmitInterpretationChanges,
  onActionFeedback,
}: UseClinicAddressLookupParams) {
  const [lookupState, setLookupState] = useState<ClinicAddressLookupState>("idle");
  const [lookupResult, setLookupResult] = useState<ClinicAddressLookupResponse | null>(null);
  const [lookupTargetField, setLookupTargetField] = useState<ReviewSelectableField | null>(null);

  const startLookup = useCallback(
    async (clinicName: string, addressField: ReviewSelectableField) => {
      setLookupState("loading");
      setLookupTargetField(addressField);
      setLookupResult(null);

      try {
        const result = await lookupClinicAddress(clinicName);
        setLookupResult(result);

        if (result.found && result.address) {
          setLookupState("found");
        } else {
          setLookupState("not-found");
          onActionFeedback({
            kind: "info",
            message: "No se encontró la dirección de la clínica.",
          });
        }
      } catch (error) {
        setLookupState("error");
        onActionFeedback({
          kind: "error",
          message: getUserErrorMessage(error, "Error al buscar la dirección de la clínica."),
        });
      }
    },
    [onActionFeedback],
  );

  const acceptLookupResult = useCallback(() => {
    if (!lookupResult?.address || !lookupTargetField) return;

    const changes: InterpretationChangePayload[] = lookupTargetField.rawField
      ? [
          {
            op: "UPDATE",
            field_id: lookupTargetField.rawField.field_id,
            value: lookupResult.address,
            value_type: "string",
          },
        ]
      : [
          {
            op: "ADD",
            key: "clinic_address",
            value: lookupResult.address,
            value_type: "string",
          },
        ];

    onSubmitInterpretationChanges(changes, "Dirección de la clínica añadida.");
    resetLookup();
  }, [lookupResult, lookupTargetField, onSubmitInterpretationChanges]);

  const dismissLookup = useCallback(() => {
    resetLookup();
  }, []);

  function resetLookup() {
    setLookupState("idle");
    setLookupResult(null);
    setLookupTargetField(null);
  }

  return {
    lookupState,
    lookupResult,
    lookupTargetField,
    startLookup,
    acceptLookupResult,
    dismissLookup,
  };
}
