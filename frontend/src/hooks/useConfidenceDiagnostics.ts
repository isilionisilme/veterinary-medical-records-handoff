import { useEffect, useMemo, useRef } from "react";

import { DEBUG_CONFIDENCE_POLICY } from "../constants/appWorkspace";
import {
  emitConfidencePolicyDiagnosticEvent,
  resolveConfidencePolicy,
} from "../lib/appWorkspaceUtils";
import {
  buildVisitGroupingDiagnostics,
  shouldEmitVisitGroupingDiagnostics,
} from "../lib/visitGroupingObservability";
import type { ReviewVisitGroup, StructuredInterpretationData } from "../types/appWorkspace";

type UseConfidenceDiagnosticsParams = {
  interpretationData: StructuredInterpretationData | undefined;
  reviewVisits: ReviewVisitGroup[];
  isCanonicalContract: boolean;
};

export function useConfidenceDiagnostics({
  interpretationData,
  reviewVisits,
  isCanonicalContract,
}: UseConfidenceDiagnosticsParams) {
  const lastConfidencePolicyDocIdRef = useRef<string | null>(null);
  const loggedConfidencePolicyDiagnosticsRef = useRef<Set<string>>(new Set());
  const loggedConfidencePolicyDebugRef = useRef<Set<string>>(new Set());

  const documentConfidencePolicy = useMemo(
    () => resolveConfidencePolicy(interpretationData?.confidence_policy),
    [interpretationData?.confidence_policy],
  );
  const activeConfidencePolicy = documentConfidencePolicy?.value ?? null;
  const confidencePolicyDegradedReason = documentConfidencePolicy?.degradedReason ?? null;

  useEffect(() => {
    const documentId = interpretationData?.document_id ?? null;
    if (documentId === null) {
      return;
    }
    if (lastConfidencePolicyDocIdRef.current !== documentId) {
      loggedConfidencePolicyDiagnosticsRef.current.clear();
      lastConfidencePolicyDocIdRef.current = documentId;
    }
    if (!confidencePolicyDegradedReason) {
      return;
    }
    const eventKey = `${documentId}|${confidencePolicyDegradedReason}`;
    if (loggedConfidencePolicyDiagnosticsRef.current.has(eventKey)) {
      return;
    }
    loggedConfidencePolicyDiagnosticsRef.current.add(eventKey);
    emitConfidencePolicyDiagnosticEvent({
      event_type: "CONFIDENCE_POLICY_CONFIG_MISSING",
      document_id: documentId,
      reason: confidencePolicyDegradedReason,
    });
  }, [confidencePolicyDegradedReason, interpretationData?.document_id]);

  useEffect(() => {
    if (!DEBUG_CONFIDENCE_POLICY) {
      return;
    }
    const documentId = interpretationData?.document_id ?? null;
    if (!documentId) {
      return;
    }
    const eventKey = `${documentId}|${confidencePolicyDegradedReason ?? "valid"}`;
    if (loggedConfidencePolicyDebugRef.current.has(eventKey)) {
      return;
    }
    loggedConfidencePolicyDebugRef.current.add(eventKey);
    const rawPolicy = interpretationData?.confidence_policy;
    const sampleField =
      interpretationData?.fields.find((field) => field.key === "pet_name") ??
      interpretationData?.fields[0];
    console.info("[confidence-policy][debug]", {
      document_id: documentId,
      has_confidence_policy: Boolean(rawPolicy),
      degraded_reason: confidencePolicyDegradedReason,
      policy_version: rawPolicy?.policy_version ?? null,
      has_band_cutoffs: Boolean(rawPolicy?.band_cutoffs),
      sample_field_mapping_confidence: sampleField
        ? {
            field_key: sampleField.key,
            has_field_mapping_confidence: typeof sampleField.field_mapping_confidence === "number",
          }
        : null,
    });
  }, [confidencePolicyDegradedReason, interpretationData]);

  useEffect(() => {
    if (!isCanonicalContract || !shouldEmitVisitGroupingDiagnostics(import.meta.env)) {
      return;
    }
    const diagnostics = buildVisitGroupingDiagnostics(reviewVisits);
    console.info("[visit-grouping][diagnostic]", {
      document_id: interpretationData?.document_id ?? null,
      ...diagnostics,
    });
  }, [interpretationData?.document_id, isCanonicalContract, reviewVisits]);

  return {
    activeConfidencePolicy,
    confidencePolicyDegradedReason,
  };
}
