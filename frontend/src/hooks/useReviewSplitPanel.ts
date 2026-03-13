import {
  type CSSProperties,
  type KeyboardEvent as ReactKeyboardEvent,
  type MouseEvent as ReactMouseEvent,
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import {
  DEFAULT_REVIEW_SPLIT_RATIO,
  MIN_PDF_PANEL_WIDTH_PX,
  MIN_STRUCTURED_PANEL_WIDTH_PX,
  REVIEW_SPLIT_MIN_WIDTH_PX,
  REVIEW_SPLIT_RATIO_EPSILON,
  REVIEW_SPLIT_RATIO_STORAGE_KEY,
  SPLITTER_COLUMN_WIDTH_PX,
} from "../constants/appWorkspace";
import {
  clampReviewSplitRatio,
  reviewSplitRatioToPx,
  snapReviewSplitRatio,
  splitPxToReviewSplitRatio,
} from "../lib/appWorkspaceUtils";

type UseReviewSplitPanelParams = {
  isDocsSidebarExpanded: boolean;
  isDocsSidebarPinned: boolean;
  shouldAutoCollapseDocsSidebar: boolean;
};

export function useReviewSplitPanel({
  isDocsSidebarExpanded,
  isDocsSidebarPinned,
  shouldAutoCollapseDocsSidebar,
}: UseReviewSplitPanelParams) {
  const [reviewSplitRatio, setReviewSplitRatio] = useState(() => {
    if (typeof window === "undefined") return DEFAULT_REVIEW_SPLIT_RATIO;
    const stored = Number(window.localStorage.getItem(REVIEW_SPLIT_RATIO_STORAGE_KEY));
    if (!Number.isFinite(stored) || stored <= 0 || stored >= 1) return DEFAULT_REVIEW_SPLIT_RATIO;
    return stored;
  });
  const [isDraggingReviewSplit, setIsDraggingReviewSplit] = useState(false);
  const reviewSplitGridRef = useRef<HTMLDivElement | null>(null);
  const [reviewSplitGridElement, setReviewSplitGridElement] = useState<HTMLDivElement | null>(null);
  const reviewSplitDragStateRef = useRef<{ startX: number; startSplitPx: number } | null>(null);
  const reviewSplitRatioRef = useRef(reviewSplitRatio);

  const getReviewSplitMeasuredWidth = useCallback(() => {
    const grid = reviewSplitGridRef.current;
    return grid ? Math.max(grid.getBoundingClientRect().width, grid.scrollWidth) : 0;
  }, []);

  const clampReviewSplitToContainer = useCallback(() => {
    const containerWidth = getReviewSplitMeasuredWidth();
    if (containerWidth <= 0) return;
    setReviewSplitRatio((current) => {
      const next = clampReviewSplitRatio(current, containerWidth);
      return Math.abs(next - current) < REVIEW_SPLIT_RATIO_EPSILON ? current : next;
    });
  }, [getReviewSplitMeasuredWidth]);

  useEffect(() => {
    reviewSplitRatioRef.current = reviewSplitRatio;
  }, [reviewSplitRatio]);
  useEffect(() => {
    if (typeof window === "undefined") return;
    window.localStorage.setItem(REVIEW_SPLIT_RATIO_STORAGE_KEY, String(reviewSplitRatio));
  }, [reviewSplitRatio]);

  useEffect(() => {
    if (!isDraggingReviewSplit) return;
    const onMouseMove = (event: globalThis.MouseEvent) => {
      const dragState = reviewSplitDragStateRef.current;
      if (!dragState) return;
      const containerWidth = Math.max(getReviewSplitMeasuredWidth(), 0);
      if (containerWidth <= 0) return;
      setReviewSplitRatio(
        splitPxToReviewSplitRatio(
          dragState.startSplitPx + (event.clientX - dragState.startX),
          containerWidth,
        ),
      );
    };
    const onMouseUp = () => {
      const containerWidth = Math.max(getReviewSplitMeasuredWidth(), 0);
      setIsDraggingReviewSplit(false);
      reviewSplitDragStateRef.current = null;
      if (containerWidth > 0)
        setReviewSplitRatio((current) =>
          clampReviewSplitRatio(snapReviewSplitRatio(current), containerWidth),
        );
    };
    document.body.style.cursor = "col-resize";
    document.body.style.userSelect = "none";
    window.addEventListener("mousemove", onMouseMove);
    window.addEventListener("mouseup", onMouseUp);
    return () => {
      document.body.style.removeProperty("cursor");
      document.body.style.removeProperty("user-select");
      window.removeEventListener("mousemove", onMouseMove);
      window.removeEventListener("mouseup", onMouseUp);
    };
  }, [getReviewSplitMeasuredWidth, isDraggingReviewSplit]);

  useEffect(() => {
    if (typeof window === "undefined") return;
    const rafId = window.requestAnimationFrame(clampReviewSplitToContainer);
    const resizeObserver =
      reviewSplitGridElement && typeof ResizeObserver !== "undefined"
        ? new ResizeObserver(clampReviewSplitToContainer)
        : null;
    if (resizeObserver && reviewSplitGridElement) resizeObserver.observe(reviewSplitGridElement);
    window.addEventListener("resize", clampReviewSplitToContainer);
    return () => {
      window.cancelAnimationFrame(rafId);
      resizeObserver?.disconnect();
      window.removeEventListener("resize", clampReviewSplitToContainer);
    };
  }, [clampReviewSplitToContainer, reviewSplitGridElement]);

  useEffect(() => {
    if (typeof window === "undefined" || !reviewSplitGridRef.current) return;
    clampReviewSplitToContainer();
    let rafB: number | null = null;
    const rafA = window.requestAnimationFrame(() => {
      clampReviewSplitToContainer();
      rafB = window.requestAnimationFrame(clampReviewSplitToContainer);
    });
    const settleTimer = window.setTimeout(clampReviewSplitToContainer, 240);
    return () => {
      window.cancelAnimationFrame(rafA);
      if (rafB !== null) window.cancelAnimationFrame(rafB);
      window.clearTimeout(settleTimer);
    };
  }, [
    clampReviewSplitToContainer,
    isDocsSidebarExpanded,
    isDocsSidebarPinned,
    shouldAutoCollapseDocsSidebar,
  ]);

  const handleReviewSplitGridRef = useCallback((node: HTMLDivElement | null) => {
    reviewSplitGridRef.current = node;
    setReviewSplitGridElement(node);
  }, []);

  const resetReviewSplitRatio = useCallback(() => {
    const containerWidth = Math.max(getReviewSplitMeasuredWidth(), 0);
    if (containerWidth > 0)
      setReviewSplitRatio(clampReviewSplitRatio(DEFAULT_REVIEW_SPLIT_RATIO, containerWidth));
  }, [getReviewSplitMeasuredWidth]);

  const startReviewSplitDragging = useCallback(
    (event: ReactMouseEvent<HTMLButtonElement>) => {
      const containerWidth = Math.max(getReviewSplitMeasuredWidth(), 0);
      if (containerWidth <= 0) return;
      reviewSplitDragStateRef.current = {
        startX: event.clientX,
        startSplitPx: reviewSplitRatioToPx(reviewSplitRatioRef.current, containerWidth),
      };
      setIsDraggingReviewSplit(true);
      event.preventDefault();
    },
    [getReviewSplitMeasuredWidth],
  );

  const handleReviewSplitKeyboard = useCallback(
    (event: ReactKeyboardEvent<HTMLButtonElement>) => {
      const containerWidth = Math.max(getReviewSplitMeasuredWidth(), 0);
      if (containerWidth <= 0) return;
      const stepPx = 40;
      if (event.key === "ArrowLeft") {
        event.preventDefault();
        setReviewSplitRatio((current) =>
          splitPxToReviewSplitRatio(
            reviewSplitRatioToPx(current, containerWidth) - stepPx,
            containerWidth,
          ),
        );
        return;
      }
      if (event.key === "ArrowRight") {
        event.preventDefault();
        setReviewSplitRatio((current) =>
          splitPxToReviewSplitRatio(
            reviewSplitRatioToPx(current, containerWidth) + stepPx,
            containerWidth,
          ),
        );
        return;
      }
      if (event.key === "Home") {
        event.preventDefault();
        resetReviewSplitRatio();
      }
    },
    [getReviewSplitMeasuredWidth, resetReviewSplitRatio],
  );

  const reviewSplitLayoutStyle = useMemo<CSSProperties>(
    () => ({
      minWidth: `${REVIEW_SPLIT_MIN_WIDTH_PX}px`,
      gridTemplateColumns: `minmax(${MIN_PDF_PANEL_WIDTH_PX}px, ${reviewSplitRatio}fr) ${SPLITTER_COLUMN_WIDTH_PX}px minmax(${MIN_STRUCTURED_PANEL_WIDTH_PX}px, ${1 - reviewSplitRatio}fr)`,
    }),
    [reviewSplitRatio],
  );

  return {
    reviewSplitRatio,
    reviewSplitLayoutStyle,
    handleReviewSplitGridRef,
    resetReviewSplitRatio,
    startReviewSplitDragging,
    handleReviewSplitKeyboard,
  };
}
