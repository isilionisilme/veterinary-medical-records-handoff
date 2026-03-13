import {
  type MouseEvent as ReactMouseEvent,
  type MutableRefObject,
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";

import { DOCS_SIDEBAR_PIN_STORAGE_KEY } from "../constants/appWorkspace";

type UseDocumentsSidebarParams = {
  activeId: string | null;
  isDragOverSidebarUpload: boolean;
  sidebarUploadDragDepthRef: MutableRefObject<number>;
};

export function useDocumentsSidebar({
  activeId,
  isDragOverSidebarUpload,
  sidebarUploadDragDepthRef,
}: UseDocumentsSidebarParams) {
  const docsHoverSidebarMediaQuery = "(min-width: 1024px) and (hover: hover) and (pointer: fine)";
  const sourcePinMediaQuery = "(min-width: 1280px)";
  const [isDesktopForDocsSidebar, setIsDesktopForDocsSidebar] = useState(false);
  const [isDocsSidebarHovered, setIsDocsSidebarHovered] = useState(false);
  const [isDocsSidebarPinned, setIsDocsSidebarPinned] = useState(() => {
    if (typeof window === "undefined") return false;
    return window.localStorage.getItem(DOCS_SIDEBAR_PIN_STORAGE_KEY) === "1";
  });
  const [isDesktopForPin, setIsDesktopForPin] = useState(false);
  const isPointerInsideDocsSidebarRef = useRef(false);
  const suppressDocsSidebarHoverUntilRef = useRef(0);
  const shouldUseHoverDocsSidebar = isDesktopForDocsSidebar;
  const shouldAutoCollapseDocsSidebar =
    shouldUseHoverDocsSidebar && Boolean(activeId) && !isDocsSidebarPinned;
  const isDocsSidebarExpanded = !shouldAutoCollapseDocsSidebar || isDocsSidebarHovered;

  useEffect(() => {
    if (typeof window === "undefined") return;
    window.localStorage.setItem(DOCS_SIDEBAR_PIN_STORAGE_KEY, isDocsSidebarPinned ? "1" : "0");
  }, [isDocsSidebarPinned]);

  useEffect(() => {
    if (typeof window.matchMedia !== "function") {
      setIsDesktopForPin(true);
      return;
    }
    const mediaQuery = window.matchMedia(sourcePinMediaQuery);
    const syncPinCapability = () => setIsDesktopForPin(mediaQuery.matches);
    syncPinCapability();
    if (typeof mediaQuery.addEventListener === "function") {
      mediaQuery.addEventListener("change", syncPinCapability);
      return () => mediaQuery.removeEventListener("change", syncPinCapability);
    }
    mediaQuery.addListener(syncPinCapability);
    return () => mediaQuery.removeListener(syncPinCapability);
  }, [sourcePinMediaQuery]);

  useEffect(() => {
    if (typeof window.matchMedia !== "function") {
      setIsDesktopForDocsSidebar(false);
      return;
    }
    const mediaQuery = window.matchMedia(docsHoverSidebarMediaQuery);
    const syncDocsSidebarCapability = () => setIsDesktopForDocsSidebar(mediaQuery.matches);
    syncDocsSidebarCapability();
    if (typeof mediaQuery.addEventListener === "function") {
      mediaQuery.addEventListener("change", syncDocsSidebarCapability);
      return () => mediaQuery.removeEventListener("change", syncDocsSidebarCapability);
    }
    mediaQuery.addListener(syncDocsSidebarCapability);
    return () => mediaQuery.removeListener(syncDocsSidebarCapability);
  }, [docsHoverSidebarMediaQuery]);

  const handleDocsSidebarMouseEnter = useCallback(
    (event: ReactMouseEvent<HTMLElement>) => {
      isPointerInsideDocsSidebarRef.current = true;
      if (Date.now() < suppressDocsSidebarHoverUntilRef.current) return;
      if (sidebarUploadDragDepthRef.current > 0 || isDragOverSidebarUpload) return;
      if (shouldAutoCollapseDocsSidebar && event.buttons === 0) setIsDocsSidebarHovered(true);
    },
    [isDragOverSidebarUpload, shouldAutoCollapseDocsSidebar, sidebarUploadDragDepthRef],
  );

  const handleDocsSidebarMouseLeave = useCallback(() => {
    isPointerInsideDocsSidebarRef.current = false;
    if (shouldAutoCollapseDocsSidebar) setIsDocsSidebarHovered(false);
  }, [shouldAutoCollapseDocsSidebar]);

  const handleToggleDocsSidebarPin = useCallback(() => {
    setIsDocsSidebarPinned((current) => {
      const next = !current;
      setIsDocsSidebarHovered(next ? true : isPointerInsideDocsSidebarRef.current);
      return next;
    });
  }, []);

  const notifySidebarUploadDrop = useCallback(() => {
    suppressDocsSidebarHoverUntilRef.current = Date.now() + 400;
  }, []);

  return {
    isDesktopForPin,
    isDocsSidebarPinned,
    shouldUseHoverDocsSidebar,
    shouldAutoCollapseDocsSidebar,
    isDocsSidebarExpanded,
    setIsDocsSidebarHovered,
    handleDocsSidebarMouseEnter,
    handleDocsSidebarMouseLeave,
    handleToggleDocsSidebarPin,
    notifySidebarUploadDrop,
  };
}
