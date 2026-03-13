import { useCallback, useEffect, useState, type MouseEvent, type RefObject } from "react";
import type * as pdfjsLib from "pdfjs-dist";

type UsePdfNavigationParams = {
  pdfDoc: pdfjsLib.PDFDocumentProxy | null;
  totalPages: number;
  loading: boolean;
  error: string | null;
  fileUrl: string | ArrayBuffer | null;
  focusPage?: number | null;
  highlightSnippet?: string | null;
  focusRequestId?: number;
  scrollRef: RefObject<HTMLDivElement | null>;
  pageRefs: RefObject<Array<HTMLDivElement | null>>;
  pageTextByIndex: Record<number, string>;
};

export function usePdfNavigation({
  pdfDoc,
  totalPages,
  loading,
  error,
  fileUrl,
  focusPage = null,
  highlightSnippet = null,
  focusRequestId = 0,
  scrollRef,
  pageRefs,
  pageTextByIndex,
}: UsePdfNavigationParams) {
  const [pageNumber, setPageNumber] = useState(1);

  const scrollToPage = useCallback(
    (targetPage: number, event?: MouseEvent<HTMLButtonElement>) => {
      event?.preventDefault();
      event?.stopPropagation();
      const container = scrollRef.current;
      const pages = pageRefs.current;
      const page = pages?.[targetPage - 1];
      if (!page || !container) {
        return;
      }
      if (import.meta.env.DEV && import.meta.env.VITE_DEBUG_PDF_VIEWER === "true") {
        console.debug("[PdfViewer] navigate", {
          currentPage: pageNumber,
          targetPage,
          totalPages,
          renderedPages: Object.keys(pageTextByIndex).length,
        });
      }
      setPageNumber(targetPage);
      const containerRect = container.getBoundingClientRect();
      const pageRect = page.getBoundingClientRect();
      const targetTop = pageRect.top - containerRect.top + container.scrollTop;
      container.scrollTo({ top: targetTop, behavior: "smooth" });
    },
    [scrollRef, pageRefs, pageNumber, totalPages, pageTextByIndex],
  );

  useEffect(() => {
    setPageNumber(1);
  }, [fileUrl]);

  useEffect(() => {
    if (!focusPage || !pdfDoc || focusPage < 1 || focusPage > pdfDoc.numPages) {
      return;
    }
    scrollToPage(focusPage);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [focusPage, pdfDoc, focusRequestId]);

  useEffect(() => {
    const root = scrollRef.current;
    if (!root || totalPages === 0 || typeof IntersectionObserver === "undefined") {
      return undefined;
    }

    const ratios = new Map<number, number>();
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          const pageIndex = Number((entry.target as HTMLElement).dataset.pageIndex || "0");
          ratios.set(pageIndex, entry.intersectionRatio);
        });

        let nextPage = 0;
        let maxRatio = 0;
        ratios.forEach((ratio, index) => {
          if (ratio > maxRatio) {
            maxRatio = ratio;
            nextPage = index;
          }
        });

        if (nextPage > 0) {
          setPageNumber((current) => (current === nextPage ? current : nextPage));
        }
      },
      {
        root,
        threshold: [0, 0.25, 0.5, 0.75, 1],
      },
    );

    const pages = pageRefs.current;
    if (!pages) {
      return undefined;
    }

    pages.forEach((page) => {
      if (page) {
        observer.observe(page);
      }
    });

    return () => {
      observer.disconnect();
    };
  }, [scrollRef, pageRefs, totalPages]);

  const canGoBack = pageNumber > 1;
  const canGoForward = pageNumber < totalPages;
  const showPageNavigation = Boolean(fileUrl) && !loading && !error && totalPages > 0;
  const normalizedSnippet = (highlightSnippet ?? "").trim().toLowerCase();
  const normalizedFocusedPageText = focusPage
    ? (pageTextByIndex[focusPage] ?? "").toLowerCase()
    : "";
  const isSnippetLocated =
    Boolean(normalizedSnippet) &&
    Boolean(focusPage) &&
    normalizedFocusedPageText.includes(normalizedSnippet);

  return {
    pageNumber,
    canGoBack,
    canGoForward,
    showPageNavigation,
    isSnippetLocated,
    scrollToPage,
  };
}
