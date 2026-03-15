import type { ReactNode } from "react";

import { ProcessingHistorySection } from "./ProcessingHistorySection";
import type { ProcessingHistoryRun, VisitScopingMetricsResponse } from "../../types";

type TechnicalTabProps = {
  viewerModeToolbarIcons: ReactNode;
  viewerDownloadIcon: ReactNode;
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
  visitScopingMetrics: VisitScopingMetricsResponse | null;
  visitScopingIsLoading: boolean;
  visitScopingIsError: boolean;
  visitScopingErrorMessage: string;
};

export function TechnicalTab({
  viewerModeToolbarIcons,
  viewerDownloadIcon,
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
  visitScopingMetrics,
  visitScopingIsLoading,
  visitScopingIsError,
  visitScopingErrorMessage,
}: TechnicalTabProps) {
  return (
    <div className="h-full overflow-y-auto rounded-card border border-borderSubtle bg-surface p-3">
      <div className="rounded-control border border-borderSubtle bg-surface px-2 py-2">
        <div className="flex items-center justify-between gap-4">
          <div className="flex items-center gap-1">{viewerModeToolbarIcons}</div>
          <div className="flex items-center gap-1">{viewerDownloadIcon}</div>
        </div>
      </div>
      <div className="mt-3 rounded-card border border-borderSubtle bg-surface p-3">
        <ProcessingHistorySection
          activeId={activeId}
          isActiveDocumentProcessing={isActiveDocumentProcessing}
          reprocessPending={reprocessPending}
          onOpenRetryModal={onOpenRetryModal}
          processingHistoryIsLoading={processingHistoryIsLoading}
          processingHistoryIsError={processingHistoryIsError}
          processingHistoryErrorMessage={processingHistoryErrorMessage}
          processingHistoryRuns={processingHistoryRuns}
          expandedSteps={expandedSteps}
          onToggleStepDetails={onToggleStepDetails}
          formatRunHeader={formatRunHeader}
        />
      </div>
      <div className="mt-3 rounded-card border border-borderSubtle bg-surface p-3">
        <div className="flex items-center justify-between gap-2">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-muted">
            Observabilidad de visitas
          </p>
          {visitScopingMetrics && (
            <span className="text-[11px] text-textSecondary">
              Document ID:{" "}
              <code className="rounded bg-surfaceMuted px-1 py-0.5 text-[11px]">
                {visitScopingMetrics.document_id}
              </code>
            </span>
          )}
        </div>
        {!activeId && (
          <p className="mt-2 text-xs text-muted">
            Selecciona un documento para ver métricas de visit-scoping.
          </p>
        )}
        {activeId && visitScopingIsLoading && (
          <p className="mt-2 text-xs text-muted">Cargando métricas de visit-scoping...</p>
        )}
        {activeId && visitScopingIsError && (
          <p className="mt-2 text-xs text-statusError">{visitScopingErrorMessage}</p>
        )}
        {activeId && !visitScopingIsLoading && !visitScopingIsError && !visitScopingMetrics && (
          <p className="mt-2 text-xs text-muted">No hay métricas disponibles.</p>
        )}
        {visitScopingMetrics && (
          <div className="mt-3 space-y-3">
            <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-5">
              <div className="rounded-control border border-borderSubtle bg-surface p-2">
                <p className="text-[11px] text-muted">Visitas totales</p>
                <p className="text-sm font-semibold text-ink">
                  {visitScopingMetrics.summary.total_visits}
                </p>
              </div>
              <div className="rounded-control border border-borderSubtle bg-surface p-2">
                <p className="text-[11px] text-muted">Visitas asignadas</p>
                <p className="text-sm font-semibold text-ink">
                  {visitScopingMetrics.summary.assigned_visits}
                </p>
              </div>
              <div className="rounded-control border border-borderSubtle bg-surface p-2">
                <p className="text-[11px] text-muted">Visitas ancladas</p>
                <p className="text-sm font-semibold text-ink">
                  {visitScopingMetrics.summary.anchored_visits}
                </p>
              </div>
              <div className="rounded-control border border-borderSubtle bg-surface p-2">
                <p className="text-[11px] text-muted">Campos sin asignar</p>
                <p className="text-sm font-semibold text-ink">
                  {visitScopingMetrics.summary.unassigned_field_count}
                </p>
              </div>
              <div className="rounded-control border border-borderSubtle bg-surface p-2">
                <p className="text-[11px] text-muted">Raw text</p>
                <p className="text-sm font-semibold text-ink">
                  {visitScopingMetrics.summary.raw_text_available ? "Disponible" : "No disponible"}
                </p>
              </div>
            </div>
            <div className="overflow-x-auto rounded-control border border-borderSubtle">
              <table className="min-w-full text-left text-xs">
                <thead className="bg-surfaceMuted text-textSecondary">
                  <tr>
                    <th className="px-2 py-1.5 font-medium">Visita</th>
                    <th className="px-2 py-1.5 font-medium">Fecha</th>
                    <th className="px-2 py-1.5 font-medium">Campos</th>
                    <th className="px-2 py-1.5 font-medium">Anclada</th>
                    <th className="px-2 py-1.5 font-medium">Chars contexto</th>
                  </tr>
                </thead>
                <tbody>
                  {visitScopingMetrics.visits.map((visit) => (
                    <tr key={`visit-scoping-${visit.visit_index}-${visit.visit_id ?? "none"}`}>
                      <td className="border-t border-borderSubtle px-2 py-1.5 text-ink">
                        {visit.visit_id ?? `visit-${visit.visit_index}`}
                      </td>
                      <td className="border-t border-borderSubtle px-2 py-1.5 text-textSecondary">
                        {visit.visit_date ?? "—"}
                      </td>
                      <td className="border-t border-borderSubtle px-2 py-1.5 text-textSecondary">
                        {visit.field_count}
                      </td>
                      <td className="border-t border-borderSubtle px-2 py-1.5 text-textSecondary">
                        {visit.anchored_in_raw_text ? "Sí" : "No"}
                      </td>
                      <td className="border-t border-borderSubtle px-2 py-1.5 text-textSecondary">
                        {visit.raw_context_chars}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
