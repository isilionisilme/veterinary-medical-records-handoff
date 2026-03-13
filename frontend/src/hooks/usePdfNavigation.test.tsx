import { renderHook } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { useRef } from "react";
import { usePdfNavigation } from "./usePdfNavigation";

describe("usePdfNavigation", () => {
  it("computes snippet location and page navigation visibility", () => {
    const { result } = renderHook(() => {
      const scrollRef = useRef<HTMLDivElement | null>(document.createElement("div"));
      const pageRefs = useRef<Array<HTMLDivElement | null>>([]);

      return usePdfNavigation({
        pdfDoc: null,
        totalPages: 2,
        loading: false,
        error: null,
        fileUrl: "blob://sample",
        focusPage: 1,
        highlightSnippet: "pagina 1",
        scrollRef,
        pageRefs,
        pageTextByIndex: {
          1: "Pagina 1",
        },
      });
    });

    expect(result.current.showPageNavigation).toBe(true);
    expect(result.current.isSnippetLocated).toBe(true);
    expect(result.current.canGoBack).toBe(false);
    expect(result.current.canGoForward).toBe(true);
  });
});
