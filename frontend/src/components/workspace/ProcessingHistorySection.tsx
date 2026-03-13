import { useMemo, useState } from "react";

import { fetchRawText } from "../../api/documentApi";
import { explainFailure } from "../../lib/appWorkspaceUtils";
import { groupProcessingSteps } from "../../lib/processingHistory";
import {
  formatDuration,
  formatTime,
  shouldShowDetails,
  statusIcon,
} from "../../lib/processingHistoryView";
import { ApiResponseError, type ProcessingHistoryRun } from "../../types/appWorkspace";
import { Button } from "../ui/button";

type ProcessingHistorySectionProps = {
  activeId: string | null;
  isActiveDocumentProcessing: boolean;
  reprocessPending: boolean;
  onOpenRetryModal: () => void;
  processingHistoryIsLoading: boolean;
  processingHistoryIsError: boolean;
  processingHistoryErrorMessage: string;
  processingHistoryRuns: ProcessingHistoryRun[];
  expandedSteps: Record<string, boolean>;
  onToggleStepDetails: (stepKey: string) => void;
  formatRunHeader: (run: ProcessingHistoryRun) => string;
};

export function ProcessingHistorySection({
  activeId,
  isActiveDocumentProcessing,
  reprocessPending,
  onOpenRetryModal,
  processingHistoryIsLoading,
  processingHistoryIsError,
  processingHistoryErrorMessage,
  processingHistoryRuns,
  expandedSteps,
  onToggleStepDetails,
  formatRunHeader,
}: ProcessingHistorySectionProps) {
  const [expandedRunRawText, setExpandedRunRawText] = useState<Record<string, boolean>>({});
  const [runRawTextContent, setRunRawTextContent] = useState<Record<string, string>>({});
  const [runRawTextLoading, setRunRawTextLoading] = useState<Record<string, boolean>>({});
  const [runRawTextError, setRunRawTextError] = useState<Record<string, string>>({});

  const runsForDisplay = useMemo(
    () => [...processingHistoryRuns].reverse(),
    [processingHistoryRuns],
  );
  const latestRunId = runsForDisplay[0]?.run_id ?? null;

  const getRunStateClasses = (state: string): string => {
    if (state === "COMPLETED") {
      return "border-statusSuccess/30 bg-statusSuccess/10 text-statusSuccess";
    }
    if (state === "FAILED") {
      return "border-statusError/30 bg-statusError/10 text-statusError";
    }
    if (state === "TIMED_OUT") {
      return "border-statusWarn/30 bg-statusWarn/10 text-statusWarn";
    }
    if (state === "RUNNING") {
      return "border-accent/30 bg-accent/10 text-accent";
    }
    return "border-borderSubtle bg-surfaceMuted text-textSecondary";
  };

  const getRunStateLabel = (state: string): string => {
    if (state === "COMPLETED") {
      return "Completado";
    }
    if (state === "FAILED") {
      return "Fallido";
    }
    if (state === "TIMED_OUT") {
      return "Timeout";
    }
    if (state === "RUNNING") {
      return "En curso";
    }
    if (state === "QUEUED") {
      return "En cola";
    }
    return state;
  };

  const getRawTextErrorMessage = (error: unknown): string => {
    if (error instanceof ApiResponseError) {
      if (error.reason === "RAW_TEXT_NOT_READY") {
        return "El texto extraído todavía no está listo.";
      }
      if (error.reason === "RAW_TEXT_NOT_AVAILABLE") {
        return "Esta ejecución no tiene texto extraído disponible.";
      }
      if (error.errorCode === "ARTIFACT_MISSING") {
        return "El artefacto de texto extraído no está disponible (410).";
      }
      return error.userMessage;
    }
    return "No se pudo cargar el texto extraído.";
  };

  const handleToggleRunRawText = async (run: ProcessingHistoryRun): Promise<void> => {
    const isOpen = expandedRunRawText[run.run_id] ?? false;
    if (isOpen) {
      setExpandedRunRawText((current) => ({ ...current, [run.run_id]: false }));
      return;
    }

    setExpandedRunRawText((current) => ({ ...current, [run.run_id]: true }));
    if (runRawTextContent[run.run_id] || runRawTextLoading[run.run_id]) {
      return;
    }

    setRunRawTextLoading((current) => ({ ...current, [run.run_id]: true }));
    setRunRawTextError((current) => ({ ...current, [run.run_id]: "" }));
    try {
      const artifact = await fetchRawText(run.run_id);
      setRunRawTextContent((current) => ({ ...current, [run.run_id]: artifact.text }));
    } catch (error) {
      setRunRawTextError((current) => ({
        ...current,
        [run.run_id]: getRawTextErrorMessage(error),
      }));
    } finally {
      setRunRawTextLoading((current) => ({ ...current, [run.run_id]: false }));
    }
  };

  return (
    <>
      <div className="flex flex-wrap items-center justify-between gap-2">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-muted">
          Historial de procesamiento
        </p>
        <Button
          type="button"
          disabled={!activeId || isActiveDocumentProcessing || reprocessPending}
          onClick={onOpenRetryModal}
        >
          {isActiveDocumentProcessing
            ? "Procesando..."
            : reprocessPending
              ? "Reprocesando..."
              : "Reprocesar"}
        </Button>
      </div>
      {!activeId && (
        <p className="mt-2 text-xs text-muted">
          Selecciona un documento para ver los detalles técnicos.
        </p>
      )}
      {activeId && processingHistoryIsLoading && (
        <p className="mt-2 text-xs text-muted">Cargando historial...</p>
      )}
      {activeId && processingHistoryIsError && (
        <p className="mt-2 text-xs text-statusError">{processingHistoryErrorMessage}</p>
      )}
      {activeId && runsForDisplay.length === 0 && (
        <p className="mt-2 text-xs text-muted">
          No hay ejecuciones registradas para este documento.
        </p>
      )}
      {activeId && runsForDisplay.length > 0 && (
        <div className="mt-2 space-y-2">
          {runsForDisplay.map((run) => (
            <div
              key={run.run_id}
              data-testid={`processing-run-card-${run.run_id}`}
              className="rounded-card border border-borderSubtle bg-surface p-2"
            >
              <div className="flex flex-wrap items-center gap-2">
                <div className="text-xs font-semibold text-ink">{formatRunHeader(run)}</div>
                <span
                  data-testid={`processing-run-state-${run.run_id}`}
                  className={`inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[11px] font-semibold ${getRunStateClasses(run.state)}`}
                >
                  <span className="h-1.5 w-1.5 rounded-full bg-current" />
                  {getRunStateLabel(run.state)}
                </span>
                {run.run_id === latestRunId && (
                  <span className="inline-flex items-center rounded-full border border-accent/40 bg-accent/10 px-2 py-0.5 text-[11px] font-semibold text-accent">
                    Última
                  </span>
                )}
                {formatDuration(run.started_at, run.completed_at) && (
                  <span className="text-[11px] text-textSecondary">
                    Duración total: {formatDuration(run.started_at, run.completed_at)}
                  </span>
                )}
              </div>
              {run.failure_type && (
                <p className="mt-1 text-xs text-statusError">{explainFailure(run.failure_type)}</p>
              )}
              {run.state === "COMPLETED" && (
                <div className="mt-2">
                  <Button
                    type="button"
                    variant="ghost"
                    onClick={() => {
                      void handleToggleRunRawText(run);
                    }}
                  >
                    {expandedRunRawText[run.run_id]
                      ? "Ocultar texto extraído"
                      : "Ver texto extraído"}
                  </Button>
                </div>
              )}
              {run.state === "COMPLETED" && expandedRunRawText[run.run_id] && (
                <div className="mt-2 rounded-control border border-borderSubtle bg-surface p-2">
                  {runRawTextLoading[run.run_id] && (
                    <p className="text-xs text-textSecondary">Cargando texto extraído...</p>
                  )}
                  {runRawTextError[run.run_id] && (
                    <p className="text-xs text-statusError">{runRawTextError[run.run_id]}</p>
                  )}
                  {!runRawTextLoading[run.run_id] &&
                    !runRawTextError[run.run_id] &&
                    runRawTextContent[run.run_id] && (
                      <pre className="max-h-64 overflow-y-auto whitespace-pre-wrap font-mono text-xs text-textSecondary">
                        {runRawTextContent[run.run_id]}
                      </pre>
                    )}
                </div>
              )}
              <div className="mt-2 space-y-1">
                {run.steps.length === 0 && (
                  <p className="text-xs text-muted">Sin pasos registrados.</p>
                )}
                {run.steps.length > 0 &&
                  groupProcessingSteps(run.steps).map((step, index) => {
                    const stepKey = `${run.run_id}-${step.step_name}-${step.attempt}-${index}`;
                    const duration = formatDuration(step.start_time, step.end_time);
                    const startTime = formatTime(step.start_time);
                    const endTime = formatTime(step.end_time);
                    const timeRange =
                      startTime && endTime ? `${startTime} → ${endTime}` : (startTime ?? "--:--");
                    return (
                      <div key={stepKey} className="rounded-control bg-surface p-2">
                        <div className="flex flex-wrap items-center gap-2 text-xs text-muted">
                          <span
                            className={
                              step.status === "FAILED"
                                ? "text-statusError"
                                : step.status === "COMPLETED"
                                  ? "text-statusSuccess"
                                  : "text-statusWarn"
                            }
                          >
                            {statusIcon(step.status)}
                          </span>
                          <span className="font-semibold text-ink">{step.step_name}</span>
                          <span>intento {step.attempt}</span>
                          <span>{timeRange}</span>
                          {duration && <span>{duration}</span>}
                        </div>
                        {step.status === "FAILED" && (
                          <p className="mt-1 text-xs text-statusError">
                            {explainFailure(
                              step.raw_events.find((event) => event.step_status === "FAILED")
                                ?.error_code,
                            )}
                          </p>
                        )}
                        {shouldShowDetails(step) && (
                          <div className="mt-1">
                            <button
                              type="button"
                              className="text-xs font-semibold text-muted"
                              onClick={() => onToggleStepDetails(stepKey)}
                            >
                              {expandedSteps[stepKey] ? "Ocultar detalles" : "Ver detalles"}
                            </button>
                          </div>
                        )}
                        {shouldShowDetails(step) && expandedSteps[stepKey] && (
                          <div className="mt-2 space-y-1 rounded-control bg-surface p-2">
                            {step.raw_events.map((event, eventIndex) => (
                              <div
                                key={`${stepKey}-event-${eventIndex}`}
                                className="text-xs text-muted"
                              >
                                <span className="font-semibold text-ink">{event.step_status}</span>
                                <span>
                                  {event.started_at
                                    ? ` · Inicio: ${formatTime(event.started_at) ?? "--:--"}`
                                    : ""}
                                </span>
                                <span>
                                  {event.ended_at
                                    ? ` · Fin: ${formatTime(event.ended_at) ?? "--:--"}`
                                    : ""}
                                </span>
                                {event.error_code && (
                                  <span className="text-statusError">
                                    {` · ${explainFailure(event.error_code)}`}
                                  </span>
                                )}
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    );
                  })}
              </div>
            </div>
          ))}
        </div>
      )}
    </>
  );
}
