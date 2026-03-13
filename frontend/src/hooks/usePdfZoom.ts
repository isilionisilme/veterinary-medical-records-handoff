import { useEffect, useState, type RefObject } from "react";
import {
  MAX_ZOOM_LEVEL,
  MIN_ZOOM_LEVEL,
  PDF_ZOOM_STORAGE_KEY,
  ZOOM_STEP,
  clampZoomLevel,
} from "../lib/pdfDebug";

type UsePdfZoomParams = {
  scrollRef: RefObject<HTMLDivElement | null>;
};

export function usePdfZoom({ scrollRef }: UsePdfZoomParams) {
  const [zoomLevel, setZoomLevel] = useState(() => {
    if (typeof window === "undefined") {
      return 1;
    }
    const rawStored = window.localStorage.getItem(PDF_ZOOM_STORAGE_KEY);
    if (rawStored === null) {
      return 1;
    }
    const stored = Number(rawStored);
    if (!Number.isFinite(stored)) {
      return 1;
    }
    return clampZoomLevel(stored);
  });

  useEffect(() => {
    const container = scrollRef.current;
    if (!container) {
      return;
    }

    const onWheel = (event: WheelEvent) => {
      if (!event.ctrlKey) {
        return;
      }

      event.preventDefault();
      setZoomLevel((current) => {
        const direction = event.deltaY < 0 ? 1 : -1;
        return clampZoomLevel(current + direction * ZOOM_STEP);
      });
    };

    container.addEventListener("wheel", onWheel, { passive: false });
    return () => {
      container.removeEventListener("wheel", onWheel);
    };
  }, [scrollRef]);

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }
    window.localStorage.setItem(PDF_ZOOM_STORAGE_KEY, String(zoomLevel));
  }, [zoomLevel]);

  const canZoomOut = zoomLevel > MIN_ZOOM_LEVEL;
  const canZoomIn = zoomLevel < MAX_ZOOM_LEVEL;
  const zoomPercent = Math.round(zoomLevel * 100);

  const handleZoomOut = () => {
    setZoomLevel((current) => clampZoomLevel(current - ZOOM_STEP));
  };
  const handleZoomIn = () => {
    setZoomLevel((current) => clampZoomLevel(current + ZOOM_STEP));
  };
  const handleZoomFit = () => {
    setZoomLevel(1);
  };

  return {
    zoomLevel,
    setZoomLevel,
    canZoomIn,
    canZoomOut,
    zoomPercent,
    handleZoomIn,
    handleZoomOut,
    handleZoomFit,
  };
}
