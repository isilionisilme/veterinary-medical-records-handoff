import { FilterX, RefreshCw, Search, X } from "lucide-react";
import { type ReactNode, type RefObject } from "react";

import { CriticalIcon } from "../app/CriticalBadge";
import { IconButton } from "../app/IconButton";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { ScrollArea } from "../ui/scroll-area";
import { ToggleGroup, ToggleGroupItem } from "../ui/toggle-group";
import { Tooltip } from "../ui/tooltip";
import { type ReviewPanelState } from "../../types/appWorkspace";
import { type ConfidenceBucket } from "../../lib/structuredDataFilters";

type StructuredDataPanelProps<TSection> = {
  activeId: string | null;
  isActiveDocumentProcessing: boolean;
  isDocumentReviewed: boolean;
  reviewTogglePending: boolean;
  onToggleReviewStatus: () => void;
  reviewPanelState: ReviewPanelState;
  structuredSearchInput: string;
  structuredSearchInputRef: RefObject<HTMLInputElement>;
  setStructuredSearchInput: (value: string) => void;
  selectedConfidenceBuckets: ConfidenceBucket[];
  setSelectedConfidenceBuckets: (buckets: ConfidenceBucket[]) => void;
  activeConfidencePolicy: unknown;
  detectedFieldsSummary: Record<ConfidenceBucket, number>;
  showOnlyCritical: boolean;
  showOnlyWithValue: boolean;
  showOnlyEmpty: boolean;
  setShowOnlyCritical: (value: boolean) => void;
  setShowOnlyWithValue: (value: boolean) => void;
  setShowOnlyEmpty: (value: boolean) => void;
  getFilterToggleItemClass: (isActive: boolean) => string;
  resetStructuredFilters: () => void;
  reviewMessageInfoClass: string;
  reviewMessageMutedClass: string;
  reviewMessageWarningClass: string;
  reviewPanelMessage: string | null;
  shouldShowReviewEmptyState: boolean;
  isRetryingInterpretation: boolean;
  onRetryInterpretation: () => Promise<void>;
  hasMalformedCanonicalFieldSlots: boolean;
  hasNoStructuredFilterResults: boolean;
  reportSections: TSection[];
  renderSectionLayout: (section: TSection) => ReactNode;
  evidenceNotice: string | null;
};

export function StructuredDataPanel<TSection>({
  activeId,
  isActiveDocumentProcessing,
  isDocumentReviewed,
  reviewTogglePending,
  onToggleReviewStatus,
  reviewPanelState,
  structuredSearchInput,
  structuredSearchInputRef,
  setStructuredSearchInput,
  selectedConfidenceBuckets,
  setSelectedConfidenceBuckets,
  activeConfidencePolicy,
  detectedFieldsSummary,
  showOnlyCritical,
  showOnlyWithValue,
  showOnlyEmpty,
  setShowOnlyCritical,
  setShowOnlyWithValue,
  setShowOnlyEmpty,
  getFilterToggleItemClass,
  resetStructuredFilters,
  reviewMessageInfoClass,
  reviewMessageMutedClass,
  reviewMessageWarningClass,
  reviewPanelMessage,
  shouldShowReviewEmptyState,
  isRetryingInterpretation,
  onRetryInterpretation,
  hasMalformedCanonicalFieldSlots,
  hasNoStructuredFilterResults,
  reportSections,
  renderSectionLayout,
  evidenceNotice,
}: StructuredDataPanelProps<TSection>) {
  return (
    <aside
      data-testid="structured-column-stack"
      className="panel-shell-muted flex h-full w-full min-h-0 min-w-[420px] flex-1 flex-col gap-[var(--canvas-gap)] p-[var(--canvas-gap)]"
    >
      <div className="flex w-full flex-wrap items-center justify-between gap-3">
        <div className="min-w-[220px]">
          <h3 className="text-lg font-semibold text-textSecondary">Datos extraídos</h3>
          <p className="mt-0.5 text-xs text-textSecondary">
            Revisa y confirma los campos antes de marcar el documento como revisado.
          </p>
        </div>
        <Tooltip
          content={
            isDocumentReviewed
              ? "Reabre el documento para continuar la revisión. Puedes volver a marcarlo como revisado cuando termines."
              : "Marca este documento como revisado cuando confirmes los datos. Si lo necesitas, luego puedes reabrirlo sin problema."
          }
        >
          <span className="inline-flex">
            <Button
              type="button"
              data-testid="review-toggle-btn"
              variant={isDocumentReviewed ? "outline" : "primary"}
              size="toolbar"
              className="min-w-[168px]"
              disabled={!activeId || isActiveDocumentProcessing || reviewTogglePending}
              onClick={onToggleReviewStatus}
            >
              {reviewTogglePending ? (
                <>
                  <RefreshCw size={14} className="animate-spin" aria-hidden="true" />
                  {isDocumentReviewed ? "Reabriendo..." : "Marcando..."}
                </>
              ) : isDocumentReviewed ? (
                <>
                  <RefreshCw size={14} aria-hidden="true" />
                  Reabrir
                </>
              ) : (
                "Marcar revisado"
              )}
            </Button>
          </span>
        </Tooltip>
      </div>
      <div data-testid="structured-search-shell" className="panel-shell px-3 py-2">
        <div className="flex flex-wrap items-center gap-2">
          <label className="relative min-w-[220px] flex-1">
            <Search
              size={14}
              className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-textSecondary"
              aria-hidden="true"
            />
            <Input
              ref={structuredSearchInputRef}
              type="text"
              aria-label="Buscar en datos extraídos"
              value={structuredSearchInput}
              disabled={reviewPanelState !== "ready"}
              onChange={(event) => setStructuredSearchInput(event.target.value)}
              placeholder="Buscar campo, clave o valor"
              className="w-full rounded-control border border-borderSubtle bg-surface py-1.5 pl-9 pr-9 text-xs"
            />
            {structuredSearchInput.trim().length > 0 && (
              <div className="absolute right-2 top-1/2 -translate-y-1/2">
                <IconButton
                  label="Limpiar búsqueda"
                  tooltip="Limpiar búsqueda"
                  className="border-0 bg-transparent shadow-none hover:bg-transparent"
                  onClick={() => {
                    setStructuredSearchInput("");
                    structuredSearchInputRef.current?.focus();
                  }}
                >
                  <X size={12} aria-hidden="true" />
                </IconButton>
              </div>
            )}
          </label>
          <ToggleGroup
            type="multiple"
            value={selectedConfidenceBuckets}
            disabled={reviewPanelState !== "ready" || !activeConfidencePolicy}
            onValueChange={(values) =>
              setSelectedConfidenceBuckets(
                values.filter(
                  (value): value is ConfidenceBucket =>
                    value === "low" ||
                    value === "medium" ||
                    value === "high" ||
                    value === "unknown",
                ),
              )
            }
            aria-label="Filtros de confianza"
            className="p-0"
          >
            <Tooltip content="Valor detectado con baja fiabilidad.">
              <ToggleGroupItem
                value="low"
                aria-label={`Baja (${detectedFieldsSummary.low})`}
                className={`h-7 rounded-control border-0 px-2.5 text-xs shadow-none ${
                  selectedConfidenceBuckets.includes("low")
                    ? "bg-surfaceMuted text-text ring-1 ring-borderSubtle"
                    : "bg-surface text-textSecondary"
                }`}
              >
                <span className="inline-flex items-center gap-1.5">
                  <span
                    aria-hidden="true"
                    className="inline-block h-3 w-3 shrink-0 rounded-full bg-confidenceLow"
                  />
                  <span className="tabular-nums">{detectedFieldsSummary.low}</span>
                </span>
              </ToggleGroupItem>
            </Tooltip>
            <Tooltip content="Valor detectado con fiabilidad media.">
              <ToggleGroupItem
                value="medium"
                aria-label={`Media (${detectedFieldsSummary.medium})`}
                className={`h-7 rounded-control border-0 px-2.5 text-xs shadow-none ${
                  selectedConfidenceBuckets.includes("medium")
                    ? "bg-surfaceMuted text-text ring-1 ring-borderSubtle"
                    : "bg-surface text-textSecondary"
                }`}
              >
                <span className="inline-flex items-center gap-1.5">
                  <span
                    aria-hidden="true"
                    className="inline-block h-3 w-3 shrink-0 rounded-full bg-confidenceMed"
                  />
                  <span className="tabular-nums">{detectedFieldsSummary.medium}</span>
                </span>
              </ToggleGroupItem>
            </Tooltip>
            <Tooltip content="Valor detectado con alta fiabilidad.">
              <ToggleGroupItem
                value="high"
                aria-label={`Alta (${detectedFieldsSummary.high})`}
                className={`h-7 rounded-control border-0 px-2.5 text-xs shadow-none ${
                  selectedConfidenceBuckets.includes("high")
                    ? "bg-surfaceMuted text-text ring-1 ring-borderSubtle"
                    : "bg-surface text-textSecondary"
                }`}
              >
                <span className="inline-flex items-center gap-1.5">
                  <span
                    aria-hidden="true"
                    className="inline-block h-3 w-3 shrink-0 rounded-full bg-confidenceHigh"
                  />
                  <span className="tabular-nums">{detectedFieldsSummary.high}</span>
                </span>
              </ToggleGroupItem>
            </Tooltip>
            <Tooltip content="Valor presente, sin confianza automática asignada.">
              <ToggleGroupItem
                value="unknown"
                aria-label={`Sin confianza (${detectedFieldsSummary.unknown})`}
                className={`h-7 rounded-control border-0 px-2.5 text-xs shadow-none ${
                  selectedConfidenceBuckets.includes("unknown")
                    ? "bg-surfaceMuted text-text ring-1 ring-borderSubtle"
                    : "bg-surface text-textSecondary"
                }`}
              >
                <span className="inline-flex items-center gap-1.5">
                  <span
                    aria-hidden="true"
                    className="inline-block h-2.5 w-2.5 shrink-0 rounded-full bg-missing"
                  />
                  <span className="tabular-nums">{detectedFieldsSummary.unknown}</span>
                </span>
              </ToggleGroupItem>
            </Tooltip>
          </ToggleGroup>
          <div aria-hidden="true" className="mx-1 h-6 w-px shrink-0 self-center bg-border" />
          <ToggleGroup
            type="multiple"
            value={[
              ...(showOnlyCritical ? ["critical"] : []),
              ...(showOnlyWithValue ? ["nonEmpty"] : []),
              ...(showOnlyEmpty ? ["empty"] : []),
            ]}
            disabled={reviewPanelState !== "ready"}
            onValueChange={(values) => {
              const hasNonEmpty = values.includes("nonEmpty");
              const hasEmpty = values.includes("empty");
              setShowOnlyCritical(values.includes("critical"));
              setShowOnlyWithValue(hasNonEmpty && !hasEmpty);
              setShowOnlyEmpty(hasEmpty && !hasNonEmpty);
            }}
            aria-label="Filtros adicionales"
            className="p-0"
          >
            <Tooltip content="Mostrar campos marcados como críticos.">
              <ToggleGroupItem
                value="critical"
                aria-label="Mostrar solo campos críticos"
                className={getFilterToggleItemClass(showOnlyCritical)}
              >
                <CriticalIcon compact />
              </ToggleGroupItem>
            </Tooltip>
            <Tooltip content="Mostrar campos con algún valor.">
              <ToggleGroupItem
                value="nonEmpty"
                aria-label="Mostrar solo campos no vacíos"
                className={getFilterToggleItemClass(showOnlyWithValue)}
              >
                <span
                  aria-hidden="true"
                  className="inline-block h-3 w-3 shrink-0 rounded-full bg-text"
                />
              </ToggleGroupItem>
            </Tooltip>
            <Tooltip content="Mostrar campos vacíos.">
              <ToggleGroupItem
                value="empty"
                aria-label="Mostrar solo campos vacíos"
                className={getFilterToggleItemClass(showOnlyEmpty)}
              >
                <span
                  aria-hidden="true"
                  className="inline-block h-3 w-3 shrink-0 rounded-full border border-muted bg-surface"
                />
              </ToggleGroupItem>
            </Tooltip>
          </ToggleGroup>
          <div aria-hidden="true" className="mx-1 h-6 w-px shrink-0 self-center bg-border" />
          <IconButton
            label="Limpiar filtros"
            tooltip="Borrar filtros."
            className="border-0 bg-transparent shadow-none hover:bg-transparent"
            disabled={
              reviewPanelState !== "ready" ||
              (structuredSearchInput.trim().length === 0 &&
                selectedConfidenceBuckets.length === 0 &&
                !showOnlyCritical &&
                !showOnlyWithValue &&
                !showOnlyEmpty)
            }
            onClick={resetStructuredFilters}
          >
            <FilterX size={14} aria-hidden="true" />
          </IconButton>
        </div>
      </div>
      {reviewPanelState === "ready" && !activeConfidencePolicy && (
        <p
          data-testid="confidence-policy-degraded"
          className={reviewMessageInfoClass}
          role="status"
          aria-live="polite"
        >
          Configuración de confianza no disponible para este documento. La señal visual de confianza
          está en modo degradado.
        </p>
      )}
      <div className="flex-1 min-h-0">
        {reviewPanelState === "loading" && (
          <div
            data-testid="right-panel-scroll"
            tabIndex={0}
            aria-label="Panel de datos estructurados"
            aria-live="polite"
            className="h-full min-h-0 overflow-y-auto pr-1 space-y-2"
          >
            <p className={reviewMessageInfoClass}>{reviewPanelMessage ?? ""}</p>
            <div data-testid="review-core-skeleton" className="space-y-2">
              {Array.from({ length: 6 }).map((_, index) => (
                <div
                  key={`review-skeleton-${index}`}
                  className="animate-pulse rounded-card bg-surface p-3"
                >
                  <div className="h-3 w-1/2 rounded bg-borderSubtle" />
                  <div className="mt-2 h-2.5 w-5/6 rounded bg-borderSubtle" />
                  <div className="mt-3 h-2 w-1/3 rounded bg-borderSubtle" />
                </div>
              ))}
            </div>
          </div>
        )}
        {shouldShowReviewEmptyState && (
          <div
            data-testid="right-panel-scroll"
            className="h-full min-h-0 flex items-center justify-center"
          >
            <div className="mx-auto w-full max-w-md px-4">
              <div className="mx-auto max-w-sm text-center">
                <p className="text-base font-semibold text-ink">Interpretación no disponible</p>
                <p className="mt-2 text-xs text-textSecondary">
                  No se pudo cargar la interpretación. Comprueba tu conexión y vuelve a intentarlo.
                </p>
                <div className="mt-4 flex justify-center">
                  <Button
                    type="button"
                    disabled={!activeId || isRetryingInterpretation}
                    onClick={() => void onRetryInterpretation()}
                  >
                    {isRetryingInterpretation ? "Reintentando..." : "Reintentar"}
                  </Button>
                </div>
              </div>
            </div>
          </div>
        )}
        {reviewPanelState === "ready" && (
          <ScrollArea
            data-testid="right-panel-scroll"
            className={`h-full min-h-0 pr-1 ${isDocumentReviewed ? "opacity-80" : ""}`}
          >
            <div className="space-y-3">
              {isDocumentReviewed && (
                <p className={reviewMessageWarningClass}>
                  Documento marcado como revisado. Los datos están en modo de solo lectura.
                </p>
              )}
              {hasMalformedCanonicalFieldSlots && (
                <p
                  data-testid="canonical-contract-error"
                  className="rounded-control border border-statusWarn bg-surface px-3 py-2 text-xs text-text"
                >
                  No se puede renderizar la plantilla canónica: `medical_record_view.field_slots` es
                  inválido.
                </p>
              )}
              {!hasMalformedCanonicalFieldSlots && hasNoStructuredFilterResults && (
                <div className={reviewMessageMutedClass} role="status" aria-live="polite">
                  <p>No hay resultados con los filtros actuales.</p>
                  <div className="mt-2">
                    <Button
                      type="button"
                      variant="ghost"
                      size="toolbar"
                      onClick={resetStructuredFilters}
                    >
                      Limpiar filtros
                    </Button>
                  </div>
                </div>
              )}
              {!hasMalformedCanonicalFieldSlots &&
                reportSections.map((section) => renderSectionLayout(section))}
            </div>
          </ScrollArea>
        )}
      </div>
      {evidenceNotice && <p className={reviewMessageMutedClass}>{evidenceNotice}</p>}
    </aside>
  );
}
