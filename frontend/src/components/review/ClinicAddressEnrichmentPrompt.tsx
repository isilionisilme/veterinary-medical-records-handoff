import { Globe, Loader2, Check, X } from "lucide-react";

type ClinicAddressEnrichmentPromptProps = {
  state: "idle" | "loading" | "found" | "not-found" | "error";
  foundAddress: string | null;
  isDocumentReviewed: boolean;
  onSearch: () => void;
  onAccept: () => void;
  onDismiss: () => void;
};

export function ClinicAddressEnrichmentPrompt({
  state,
  foundAddress,
  isDocumentReviewed,
  onSearch,
  onAccept,
  onDismiss,
}: ClinicAddressEnrichmentPromptProps) {
  if (isDocumentReviewed) return null;

  if (state === "idle") {
    return (
      <div
        data-testid="clinic-address-enrichment-prompt"
        className="mt-1 flex items-center gap-2 rounded-md border border-amber-200 bg-amber-50 px-2 py-1.5 text-xs text-amber-800"
      >
        <Globe className="h-3.5 w-3.5 shrink-0" aria-hidden="true" />
        <span>No se encontró la dirección. ¿La intento buscar yo en internet?</span>
        <button
          type="button"
          data-testid="clinic-address-enrichment-search-btn"
          className="ml-auto shrink-0 rounded border border-amber-300 bg-white px-2 py-0.5 text-xs font-medium text-amber-800 hover:bg-amber-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-accent"
          onClick={onSearch}
        >
          Buscar
        </button>
      </div>
    );
  }

  if (state === "loading") {
    return (
      <div
        data-testid="clinic-address-enrichment-loading"
        className="mt-1 flex items-center gap-2 rounded-md border border-blue-200 bg-blue-50 px-2 py-1.5 text-xs text-blue-700"
      >
        <Loader2 className="h-3.5 w-3.5 shrink-0 animate-spin" aria-hidden="true" />
        <span>Buscando dirección…</span>
      </div>
    );
  }

  if (state === "found" && foundAddress) {
    return (
      <div
        data-testid="clinic-address-enrichment-found"
        className="mt-1 rounded-md border border-green-200 bg-green-50 px-2 py-1.5 text-xs text-green-800"
      >
        <div className="flex items-start gap-2">
          <Check className="mt-0.5 h-3.5 w-3.5 shrink-0" aria-hidden="true" />
          <div className="min-w-0 flex-1">
            <p className="font-medium">Dirección encontrada:</p>
            <p className="mt-0.5 break-words">{foundAddress}</p>
          </div>
        </div>
        <div className="mt-1.5 flex justify-end gap-2">
          <button
            type="button"
            data-testid="clinic-address-enrichment-reject-btn"
            className="shrink-0 rounded border border-transparent px-2 py-0.5 text-xs text-green-700 hover:bg-green-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-accent"
            onClick={onDismiss}
          >
            Descartar
          </button>
          <button
            type="button"
            data-testid="clinic-address-enrichment-accept-btn"
            className="shrink-0 rounded border border-green-300 bg-white px-2 py-0.5 text-xs font-medium text-green-800 hover:bg-green-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-accent"
            onClick={onAccept}
          >
            Usar esta dirección
          </button>
        </div>
      </div>
    );
  }

  if (state === "not-found" || state === "error") {
    return (
      <div
        data-testid="clinic-address-enrichment-not-found"
        className="mt-1 flex items-center gap-2 rounded-md border border-gray-200 bg-gray-50 px-2 py-1.5 text-xs text-gray-600"
      >
        <X className="h-3.5 w-3.5 shrink-0" aria-hidden="true" />
        <span>
          {state === "error"
            ? "Error al buscar la dirección."
            : "No se encontró la dirección de la clínica."}
        </span>
        <button
          type="button"
          className="ml-auto shrink-0 rounded border border-transparent px-1 py-0.5 text-xs text-gray-500 hover:bg-gray-100"
          onClick={onDismiss}
        >
          Cerrar
        </button>
      </div>
    );
  }

  return null;
}
