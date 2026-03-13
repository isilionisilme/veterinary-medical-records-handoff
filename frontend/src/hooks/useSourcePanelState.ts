import { useCallback, useEffect, useState } from "react";

type SourceEvidence = {
  page: number;
  snippet: string;
};

type UseSourcePanelStateParams = {
  isDesktopForPin: boolean;
  onNotice: (message: string) => void;
};

export function useSourcePanelState({ isDesktopForPin, onNotice }: UseSourcePanelStateParams) {
  const [isSourceOpen, setIsSourceOpen] = useState(false);
  const [isSourcePinned, setIsSourcePinned] = useState(false);
  const [sourcePage, setSourcePage] = useState<number | null>(null);
  const [sourceSnippet, setSourceSnippet] = useState<string | null>(null);
  const [focusRequestId, setFocusRequestId] = useState(0);

  const openSource = () => {
    setIsSourceOpen(true);
  };

  const openFromEvidence = (evidence?: SourceEvidence) => {
    const page = evidence?.page ?? null;
    const snippetValue = evidence?.snippet?.trim();
    const normalizedSnippet = snippetValue && snippetValue.length > 0 ? snippetValue : null;

    if (!page) {
      onNotice("Sin evidencia disponible para este campo.");
      return;
    }

    setSourcePage(page);
    setSourceSnippet(normalizedSnippet);
    setFocusRequestId((current) => current + 1);
    setIsSourceOpen(true);
    onNotice(`Mostrando fuente en la página ${page}.`);
  };

  const togglePin = () => {
    if (!isDesktopForPin) {
      onNotice("Fijar solo está disponible en escritorio.");
      return;
    }
    setIsSourcePinned((current) => !current);
    setIsSourceOpen(true);
  };

  const closeOverlay = () => {
    if (isSourcePinned) {
      return;
    }
    setIsSourceOpen(false);
  };

  const reset = useCallback(() => {
    setSourcePage(null);
    setSourceSnippet(null);
    setIsSourceOpen(false);
    setIsSourcePinned(false);
  }, []);

  useEffect(() => {
    if (isDesktopForPin) {
      return;
    }
    if (isSourcePinned) {
      setIsSourcePinned(false);
    }
  }, [isDesktopForPin, isSourcePinned]);

  useEffect(() => {
    if (!isSourceOpen || isSourcePinned) {
      return;
    }

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setIsSourceOpen(false);
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isSourceOpen, isSourcePinned]);

  return {
    isSourceOpen,
    isSourcePinned,
    sourcePage,
    sourceSnippet,
    focusRequestId,
    openSource,
    openFromEvidence,
    togglePin,
    closeOverlay,
    reset,
  };
}
