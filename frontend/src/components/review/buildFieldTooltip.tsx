import type { ReactNode } from "react";

import {
  clampConfidence,
  formatSignedPercent,
  getConfidenceTone,
} from "../../lib/appWorkspaceUtils";
import type { ReviewSelectableField } from "../../types/appWorkspace";
import type { ReviewFieldRenderersContext } from "./ReviewFieldRenderers.types";

export function buildFieldTooltip(
  ctx: ReviewFieldRenderersContext,
  item: ReviewSelectableField,
): { content: ReactNode; ariaLabel: string } {
  const manualOverrideConfidenceMessage =
    "La confianza aplica únicamente al valor originalmente detectado por el sistema. El valor actual ha sido editado y por eso no tiene confianza asociada.";
  if (!ctx.activeConfidencePolicy) {
    return {
      content: "Configuración de confianza no disponible.",
      ariaLabel: "Configuración de confianza no disponible.",
    };
  }
  if (item.rawField?.origin === "human") {
    return {
      content: manualOverrideConfidenceMessage,
      ariaLabel: manualOverrideConfidenceMessage,
    };
  }
  if (!item.hasMappingConfidence) {
    return {
      content: "Confianza de mapeo no disponible.",
      ariaLabel: "Confianza de mapeo no disponible.",
    };
  }
  const confidence = item.confidence;
  const percentage = Math.round(clampConfidence(confidence) * 100);
  const tone = getConfidenceTone(confidence, ctx.activeConfidencePolicy.band_cutoffs);
  const candidateConfidence = item.rawField?.field_candidate_confidence;
  const candidateConfidenceText =
    typeof candidateConfidence === "number" && Number.isFinite(candidateConfidence)
      ? `${Math.round(clampConfidence(candidateConfidence) * 100)}%`
      : "No disponible";
  const reviewHistoryAdjustmentRaw = item.rawField?.field_review_history_adjustment;
  const reviewHistoryAdjustment =
    typeof reviewHistoryAdjustmentRaw === "number" && Number.isFinite(reviewHistoryAdjustmentRaw)
      ? reviewHistoryAdjustmentRaw
      : 0;
  const reviewHistoryAdjustmentText = formatSignedPercent(reviewHistoryAdjustment);
  const reviewHistoryAdjustmentClass =
    reviewHistoryAdjustment > 0
      ? "text-[var(--status-success)]"
      : reviewHistoryAdjustment < 0
        ? "text-[var(--status-error)]"
        : "text-muted";
  const header = `Confianza: ${percentage}%`;
  const toneDotClass =
    tone === "high"
      ? "bg-confidenceHigh"
      : tone === "med"
        ? "bg-confidenceMed"
        : "bg-confidenceLow";
  const toneValueClass =
    tone === "high"
      ? "text-confidenceHigh"
      : tone === "med"
        ? "text-confidenceMed"
        : "text-confidenceLow";
  const evidencePageLabel = item.evidence?.page ? `Página ${item.evidence.page}` : null;
  const ariaLabelParts = [
    header,
    evidencePageLabel,
    "Indica la fiabilidad del valor detectado automáticamente.",
    "Desglose:",
    `Fiabilidad del candidato: ${candidateConfidenceText}`,
    `Ajuste por histórico de revisiones: ${reviewHistoryAdjustmentText}`,
  ].filter((part): part is string => Boolean(part));
  return {
    ariaLabel: ariaLabelParts.join(" · "),
    content: (
      <div className="min-w-[260px] space-y-1 text-[12px] leading-4">
        <div className="flex items-start justify-between gap-3">
          <p className="flex items-center gap-1.5 text-[14px] font-semibold leading-5 text-white">
            <span>Confianza:</span>
            <span className={toneValueClass}>{percentage}%</span>
            <span
              className={`inline-block h-2 w-2 rounded-full ring-1 ring-white/40 ${toneDotClass}`}
              aria-hidden="true"
            />
          </p>
          {evidencePageLabel ? (
            <span className="text-[11px] font-normal text-white/70">{evidencePageLabel}</span>
          ) : null}
        </div>
        <p className="text-[11px] leading-4 text-white/60">
          Indica la fiabilidad del valor detectado automáticamente.
        </p>
        <div className="!mt-4 space-y-0.5 text-[12px]">
          <p className="font-medium text-white/80">Desglose:</p>
          <p className="pl-3 text-white/70">
            - Fiabilidad del candidato:{" "}
            <span className={toneValueClass}>{candidateConfidenceText}</span>
          </p>
          <p className="pl-3 text-white/70">
            - Ajuste por histórico de revisiones:{" "}
            <span className={reviewHistoryAdjustmentClass}>{reviewHistoryAdjustmentText}</span>
          </p>
        </div>
      </div>
    ),
  };
}
